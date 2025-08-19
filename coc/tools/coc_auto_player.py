import time
import ctypes
import re
from enum import Enum
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
import pyautogui
from mss import mss
from ultralytics import YOLO
import win32gui
import win32con

# 下面这段代码是基于如下提示词生成的：
# 现在我的代码已经实现识别和点击功能，我现在在做的coc的项目是自动识别按钮然后点击，然后放兵，然后返回城镇，就这样循环，不是home village，是base village，夜世界。
# 一开始点击attack，然后找到对手之后识别空地，从而放兵，放完兵点击surrender,然后点击okay然后点击return village回城，然后下一轮循环。要实现我说的这些功能，怎么写代码比较好


class GameState(Enum):
    VILLAGE = "village"           # 在城镇，寻找attack按钮
    FINDING_OPPONENT = "finding"  # 寻找对手中
    ATTACKING = "attacking"       # 攻击状态，放兵
    SURRENDERING = "surrendering" # 投降状态
    CONFIRMING = "confirming"     # 确认对话框
    RETURNING = "returning"       # 返回村庄
    ERROR = "error"               # 错误状态


class COCAutoPlayer:
    def __init__(self, model_path=None, window_keyword="BlueStacks", conf_thres=0.6):
        self.model_path = model_path or r"D:\python-project\AI_DetectHub\runs\detect\train2\weights\best.pt"
        self.window_keyword = window_keyword
        self.conf_thres = conf_thres
        
        # 类别ID映射 - 需要根据你的模型训练结果调整
        self.class_ids = {
            'attack_button': 0,
            'empty_space': 1, 
            'surrender_button': 2,
            'okay_button': 3,
            'return_village_button': 4
        }
        
        # 游戏状态
        self.current_state = GameState.VILLAGE
        self.state_start_time = time.time()
        self.max_state_duration = 60  # 单个状态最大持续时间（秒）
        
        # 攻击相关
        self.troops_deployed = 0
        self.max_troops = 10  # 最大放兵数量
        self.deploy_interval = 0.5  # 放兵间隔
        self.last_deploy_time = 0
        
        # 统计信息
        self.battle_count = 0
        self.total_start_time = time.time()
        
        # 处理高DPI缩放
        ctypes.windll.user32.SetProcessDPIAware()
        
        # 初始化
        self.model = None
        self.sct = None

    def find_window_rect(self, keyword: str):
        """查找并返回BlueStacks窗口的客户区坐标"""
        hwnd_list = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))

        win32gui.EnumWindows(enum_handler, None)

        if hwnd_list:
            target_hwnd, _ = hwnd_list[0]
        else:
            return None

        rect = win32gui.GetClientRect(target_hwnd)
        pt = win32gui.ClientToScreen(target_hwnd, (0, 0))
        left, top = pt
        right, bottom = left + rect[2], top + rect[3]
        return (left, top, right, bottom), target_hwnd

    def detect_objects(self, frame) -> Dict[str, List[Tuple]]:
        """检测画面中的所有目标对象"""
        results = self.model.predict(frame, imgsz=640, conf=self.conf_thres, verbose=False)[0]

        detections = {cls_name: [] for cls_name in self.class_ids.keys()}
        
        if results.boxes is not None and len(results.boxes) > 0:
            xyxy = results.boxes.xyxy.cpu().numpy().astype(int)
            cls = results.boxes.cls.cpu().numpy().astype(int)
            conf = results.boxes.conf.cpu().numpy()
            
            for (x1, y1, x2, y2), c, p in zip(xyxy, cls, conf):
                for cls_name, cls_id in self.class_ids.items():
                    if c == cls_id:
                        detections[cls_name].append((float(p), x1, y1, x2, y2))
                        break
        
        # 按置信度排序
        for cls_name in detections:
            detections[cls_name].sort(key=lambda x: x[0], reverse=True)
            
        return detections

    def click_target(self, detection: Tuple, window_offset: Tuple[int, int], delay: float = 0.1):
        """点击检测到的目标"""
        conf, x1, y1, x2, y2 = detection
        xc, yc = (x1 + x2) // 2, (y1 + y2) // 2
        
        # 转换为屏幕坐标
        L, T = window_offset
        screen_x, screen_y = L + xc, T + yc
        
        print(f"[CLICK] 点击坐标: ({screen_x}, {screen_y}), 置信度: {conf:.2f}")
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()
        time.sleep(delay)

    def handle_village_state(self, detections: Dict, window_offset: Tuple[int, int]):
        """处理村庄状态 - 寻找并点击attack按钮"""
        if detections['attack_button']:
            print("[STATE] 找到attack按钮，准备攻击")
            self.click_target(detections['attack_button'][0], window_offset, delay=2.0)
            self.current_state = GameState.FINDING_OPPONENT
            self.state_start_time = time.time()
            return True
        return False

    def handle_finding_state(self, detections: Dict, window_offset: Tuple[int, int]):
        """处理寻找对手状态"""
        # 如果找到空地，说明已经进入攻击界面
        if detections['empty_space']:
            print("[STATE] 找到对手，开始攻击")
            self.current_state = GameState.ATTACKING
            self.state_start_time = time.time()
            self.troops_deployed = 0
            return True
        
        # 如果还在寻找对手，等待
        print("[STATE] 正在寻找对手...")
        return False

    def handle_attacking_state(self, detections: Dict, window_offset: Tuple[int, int]):
        """处理攻击状态 - 在空地放兵"""
        current_time = time.time()
        
        # 检查是否已经放完兵或超时
        if (self.troops_deployed >= self.max_troops or 
            current_time - self.state_start_time > 30):
            print(f"[STATE] 放兵完成 ({self.troops_deployed}个) 或超时，准备投降")
            self.current_state = GameState.SURRENDERING
            self.state_start_time = time.time()
            return True
        
        # 放兵逻辑
        if (detections['empty_space'] and 
            current_time - self.last_deploy_time > self.deploy_interval):
            
            # 选择一个空地放兵
            target = detections['empty_space'][0]
            print(f"[DEPLOY] 放第{self.troops_deployed + 1}个兵")
            self.click_target(target, window_offset, delay=0.2)
            
            self.troops_deployed += 1
            self.last_deploy_time = current_time
            return True
            
        return False

    def handle_surrendering_state(self, detections: Dict, window_offset: Tuple[int, int]):
        """处理投降状态 - 点击surrender按钮"""
        if detections['surrender_button']:
            print("[STATE] 找到surrender按钮，开始投降")
            self.click_target(detections['surrender_button'][0], window_offset, delay=1.0)
            self.current_state = GameState.CONFIRMING
            self.state_start_time = time.time()
            return True
        return False

    def handle_confirming_state(self, detections: Dict, window_offset: Tuple[int, int]):
        """处理确认状态 - 点击okay按钮"""
        if detections['okay_button']:
            print("[STATE] 找到okay按钮，确认操作")
            self.click_target(detections['okay_button'][0], window_offset, delay=1.0)
            self.current_state = GameState.RETURNING
            self.state_start_time = time.time()
            return True
        return False

    def handle_returning_state(self, detections: Dict, window_offset: Tuple[int, int]):
        """处理返回状态 - 点击return village按钮"""
        if detections['return_village_button']:
            print("[STATE] 找到return village按钮，返回村庄")
            self.click_target(detections['return_village_button'][0], window_offset, delay=3.0)
            self.current_state = GameState.VILLAGE
            self.state_start_time = time.time()
            self.battle_count += 1
            print(f"[INFO] 第{self.battle_count}场战斗完成")
            return True
        return False

    def check_state_timeout(self):
        """检查状态是否超时"""
        if time.time() - self.state_start_time > self.max_state_duration:
            print(f"[WARNING] 状态 {self.current_state.value} 超时，重置到村庄状态")
            self.current_state = GameState.VILLAGE
            self.state_start_time = time.time()
            return True
        return False

    def draw_debug_info(self, frame, detections: Dict):
        """在画面上绘制调试信息"""
        overlay = frame.copy()
        
        # 绘制检测框
        colors = {
            'attack_button': (0, 255, 0),      # 绿色
            'empty_space': (255, 0, 0),        # 蓝色  
            'surrender_button': (0, 0, 255),   # 红色
            'okay_button': (255, 255, 0),      # 青色
            'return_village_button': (255, 0, 255)  # 紫色
        }
        
        for cls_name, det_list in detections.items():
            if det_list:
                color = colors.get(cls_name, (255, 255, 255))
                for conf, x1, y1, x2, y2 in det_list:
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(overlay, f"{cls_name} {conf:.2f}", 
                              (x1, max(0, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, color, 1)
        
        # 状态信息
        status_text = [
            f"State: {self.current_state.value}",
            f"Battle: {self.battle_count}",
            f"Troops: {self.troops_deployed}/{self.max_troops}",
            f"Runtime: {int(time.time() - self.total_start_time)}s"
        ]
        
        for i, text in enumerate(status_text):
            cv2.putText(overlay, text, (8, 25 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return overlay

    def run_auto_player(self):
        """运行自动游戏主循环"""
        print("[INFO] 启动COC夜世界自动攻击...")
        print("[INFO] 加载YOLO模型...")
        self.model = YOLO(self.model_path)
        self.sct = mss()

        # 查找游戏窗口
        window_info = self.find_window_rect(self.window_keyword)
        if not window_info:
            print(f"[ERROR] 未找到标题包含 '{self.window_keyword}' 的窗口")
            return

        (L, T, R, B), hwnd = window_info
        W, H = R - L, B - T
        print(f"[INFO] 游戏窗口: ({L},{T})-({R},{B}) size={W}x{H}")
        print("[INFO] 按 ESC 键退出程序")

        while True:
            try:
                # 截取游戏画面
                region = {"left": L, "top": T, "width": W, "height": H}
                frame = np.array(self.sct.grab(region))[:, :, :3]

                # 检测所有目标
                detections = self.detect_objects(frame)

                # 根据当前状态执行相应操作
                if self.current_state == GameState.VILLAGE:
                    self.handle_village_state(detections, (L, T))
                elif self.current_state == GameState.FINDING_OPPONENT:
                    self.handle_finding_state(detections, (L, T))
                elif self.current_state == GameState.ATTACKING:
                    self.handle_attacking_state(detections, (L, T))
                elif self.current_state == GameState.SURRENDERING:
                    self.handle_surrendering_state(detections, (L, T))
                elif self.current_state == GameState.CONFIRMING:
                    self.handle_confirming_state(detections, (L, T))
                elif self.current_state == GameState.RETURNING:
                    self.handle_returning_state(detections, (L, T))

                # 检查状态超时
                self.check_state_timeout()

                # 绘制调试信息
                debug_frame = self.draw_debug_info(frame, detections)
                cv2.imshow("COC Auto Player", debug_frame)

                # 检查退出键
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break

                # 动态更新窗口坐标
                window_info = self.find_window_rect(self.window_keyword)
                if window_info:
                    (L, T, R, B), _ = window_info
                    W, H = R - L, B - T

            except Exception as e:
                print(f"[ERROR] 发生错误: {e}")
                time.sleep(1)
                continue

        cv2.destroyAllWindows()
        print(f"[INFO] 程序结束，共完成 {self.battle_count} 场战斗")


if __name__ == "__main__":
    # 使用示例
    player = COCAutoPlayer(
        model_path=r"D:\python-project\AI_DetectHub\runs\detect\train2\weights\best.pt",
        window_keyword="BlueStacks",
        conf_thres=0.6
    )
    player.run_auto_player()