import time
import ctypes
import re
from typing import List, Optional
import cv2
import numpy as np
from mss import mss
from ultralytics import YOLO
import win32gui

from .state_machine import GameState, Detection, WindowInfo, StateHandlerRegistry
from .states.village import VillageHandler
from .states.finding import FindingOpponentHandler  
from .states.attacking import AttackingHandler
from .ui_manager import MultiConfigManager, UIElementMapper, StateValidator
from .mode_manager import mode_manager
from ..features.base import GameMode


class COCGameController:
    """COC游戏主控制器"""
    
    def __init__(self, 
                 model_path: str,
                 window_keyword: str = "BlueStacks",
                 config_path: str = None,
                 initial_mode: GameMode = None):
        
        # 基础配置
        self.model_path = model_path
        self.window_keyword = window_keyword
        
        # 设置初始游戏模式
        if initial_mode:
            mode_manager.set_mode(initial_mode)
        
        # 初始化配置管理器
        self.config_manager = MultiConfigManager(config_path)
        self.ui_mapper = UIElementMapper(self.config_manager)
        self.state_validator = StateValidator(self.config_manager)
        
        # 初始化YOLO模型
        self.model = None
        self.sct = None
        
        # 状态管理
        self.current_state = GameState.VILLAGE
        self.state_start_time = time.time()
        self.previous_state = None
        
        # 注册状态处理器
        self.state_registry = StateHandlerRegistry()
        self._register_handlers()
        
        # 统计信息
        self.battle_count = 0
        self.session_start_time = time.time()
        self.error_count = 0
        
        # 处理高DPI缩放
        ctypes.windll.user32.SetProcessDPIAware()
        
    def _register_handlers(self):
        """注册所有状态处理器"""
        handlers = [
            VillageHandler(),  # 使用新的模式系统
            FindingOpponentHandler(),
            AttackingHandler(),
            # 可以继续添加其他状态处理器
        ]
        
        for handler in handlers:
            self.state_registry.register(handler)
            
    def set_game_mode(self, mode: GameMode):
        """设置游戏模式"""
        mode_manager.set_mode(mode)
        print(f"[CONTROLLER] 设置游戏模式: {mode_manager.get_mode_display_name(mode)}")
        
    def get_current_mode(self) -> GameMode:
        """获取当前游戏模式"""
        return mode_manager.get_current_mode()
        
    def update_mode_config(self, new_config: dict, mode: GameMode = None):
        """更新指定模式的功能配置"""
        mode_manager.update_mode_config(new_config, mode)
        print(f"[CONTROLLER] 模式配置已更新")
        
    def get_available_features(self, mode: GameMode = None):
        """获取指定模式的可用功能列表"""
        return mode_manager.get_available_features(mode)
        
    def get_all_modes(self):
        """获取所有支持的游戏模式"""
        return mode_manager.get_all_modes()
        
    def get_mode_summary(self):
        """获取当前模式摘要"""
        return mode_manager.get_mode_summary()
            
    def initialize(self):
        """初始化控制器"""
        print("[INFO] 初始化COC自动控制器...")
        
        # 加载YOLO模型
        try:
            print(f"[INFO] 加载模型: {self.model_path}")
            self.model = YOLO(self.model_path)
            print(f"[INFO] 模型加载成功，类别: {self.model.names}")
        except Exception as e:
            print(f"[ERROR] 模型加载失败: {e}")
            return False
            
        # 初始化屏幕截图
        self.sct = mss()
        
        # 查找游戏窗口
        window_info = self._find_game_window()
        if not window_info:
            print(f"[ERROR] 未找到游戏窗口: {self.window_keyword}")
            return False
            
        print(f"[INFO] 游戏窗口: {window_info.left},{window_info.top} "
              f"size={window_info.width}x{window_info.height}")
        return True
        
    def _find_game_window(self) -> Optional[WindowInfo]:
        """查找游戏窗口"""
        hwnd_list = []
        
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(self.window_keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))
                    
        win32gui.EnumWindows(enum_handler, None)
        
        if not hwnd_list:
            return None
            
        hwnd, _ = hwnd_list[0]
        rect = win32gui.GetClientRect(hwnd)
        pt = win32gui.ClientToScreen(hwnd, (0, 0))
        
        return WindowInfo(
            left=pt[0],
            top=pt[1], 
            right=pt[0] + rect[2],
            bottom=pt[1] + rect[3],
            width=rect[2],
            height=rect[3]
        )
        
    def _capture_screen(self, window_info: WindowInfo) -> np.ndarray:
        """截取游戏画面"""
        region = {
            "left": window_info.left,
            "top": window_info.top,
            "width": window_info.width,
            "height": window_info.height
        }
        return np.array(self.sct.grab(region))[:, :, :3]  # BGRA -> BGR
        
    def _detect_objects(self, frame: np.ndarray) -> List[Detection]:
        """检测游戏中的对象"""
        conf_threshold = self.config_manager.get_main_config("model.confidence_threshold", 0.6)
        results = self.model.predict(frame, conf=conf_threshold, verbose=False)[0]
        
        detections = []
        if results.boxes is not None and len(results.boxes) > 0:
            xyxy = results.boxes.xyxy.cpu().numpy().astype(int)
            cls = results.boxes.cls.cpu().numpy().astype(int)
            conf = results.boxes.conf.cpu().numpy()
            
            for (x1, y1, x2, y2), c, p in zip(xyxy, cls, conf):
                class_name = self.model.names.get(c, f"class_{c}")
                detection = Detection(
                    bbox=(x1, y1, x2, y2),
                    class_name=class_name,
                    confidence=float(p)
                )
                detections.append(detection)
                
        # 过滤有效检测结果
        return self.ui_mapper.filter_valid_detections(detections)
        
    def _determine_state(self, detections: List[Detection]) -> GameState:
        """根据检测结果判断当前游戏状态"""
        # 方式1：使用状态验证器
        state_name = self.state_validator.find_matching_state(detections)
        if state_name:
            return GameState(state_name)
            
        # 方式2：使用状态处理器的can_handle方法
        detected_state = self.state_registry.find_current_state(detections)
        if detected_state:
            return detected_state
            
        # 默认保持当前状态
        return self.current_state
        
    def _handle_state_transition(self, new_state: GameState):
        """处理状态转换"""
        if new_state != self.current_state:
            print(f"[STATE] {self.current_state.value} -> {new_state.value}")
            
            # 特殊处理：开始新的攻击时重置攻击状态
            if new_state == GameState.ATTACKING:
                handler = self.state_registry.get_handler(new_state)
                if hasattr(handler, 'reset_attack_state'):
                    handler.reset_attack_state()
                    
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_start_time = time.time()
            
            # 完成一轮循环的统计
            if new_state == GameState.VILLAGE and self.previous_state == GameState.RETURNING:
                self.battle_count += 1
                print(f"[INFO] 完成第 {self.battle_count} 场战斗")
                
    def _check_state_timeout(self) -> bool:
        """检查状态是否超时"""
        timeout = self.ui_mapper.get_timeout(self.current_state.value)
        elapsed = time.time() - self.state_start_time
        
        if elapsed > timeout:
            print(f"[WARNING] 状态 {self.current_state.value} 超时 ({elapsed:.1f}s)")
            self._handle_timeout()
            return True
        return False
        
    def _handle_timeout(self):
        """处理超时情况"""
        self.error_count += 1
        
        # 简单的超时处理：重置到村庄状态
        print("[INFO] 超时处理：重置到村庄状态")
        self.current_state = GameState.VILLAGE
        self.state_start_time = time.time()
        
    def _draw_debug_info(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """绘制调试信息"""
        overlay = frame.copy()
        
        # 颜色配置
        colors = {
            'attack': (0, 255, 0),
            'find_now': (255, 0, 0),
            'default': (255, 255, 255)
        }
        
        # 绘制检测框
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            color = colors.get(detection.class_name, colors['default'])
            
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            
            label = f"{detection.class_name} {detection.confidence:.2f}"
            cv2.putText(overlay, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 状态信息
        info_lines = [
            f"State: {self.current_state.value}",
            f"Battles: {self.battle_count}",
            f"Errors: {self.error_count}",
            f"Runtime: {int(time.time() - self.session_start_time)}s"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(overlay, line, (10, 30 + i*25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                       
        return overlay
        
    def run(self):
        """运行自动控制器"""
        if not self.initialize():
            return
            
        print("[INFO] 开始自动游戏循环...")
        print("[INFO] 按ESC键退出")
        
        try:
            while True:
                # 获取游戏窗口信息（支持窗口移动）
                window_info = self._find_game_window()
                if not window_info:
                    print("[WARNING] 游戏窗口丢失，继续尝试...")
                    time.sleep(1)
                    continue
                    
                # 截取游戏画面
                frame = self._capture_screen(window_info)
                
                # 检测游戏对象
                detections = self._detect_objects(frame)
                
                # 判断游戏状态
                detected_state = self._determine_state(detections)
                self._handle_state_transition(detected_state)
                
                # 检查超时
                if self._check_state_timeout():
                    continue
                    
                # 执行当前状态的操作
                handler = self.state_registry.get_handler(self.current_state)
                if handler:
                    next_state = handler.execute(detections, window_info)
                    if next_state:
                        self._handle_state_transition(next_state)
                        
                # 显示调试信息
                debug_frame = self._draw_debug_info(frame, detections)
                cv2.imshow("COC Auto Controller", debug_frame)
                
                # 检查退出键
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] 用户中断")
        except Exception as e:
            print(f"[ERROR] 运行时错误: {e}")
        finally:
            cv2.destroyAllWindows()
            self._print_session_summary()
            
    def _print_session_summary(self):
        """打印会话总结"""
        runtime = time.time() - self.session_start_time
        print(f"\n[SESSION SUMMARY]")
        print(f"总运行时间: {runtime:.1f}秒")
        print(f"完成战斗: {self.battle_count}场")
        print(f"错误次数: {self.error_count}次")
        if self.battle_count > 0:
            print(f"平均每场战斗时间: {runtime/self.battle_count:.1f}秒")