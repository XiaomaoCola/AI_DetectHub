import time
import pyautogui
from typing import List, Optional, Dict, Any

from ..state_machine import StateHandler, GameState, Detection, WindowInfo
from ..mode_manager import mode_manager


class VillageHandler(StateHandler):
    """村庄状态处理器 - 支持多模式的功能策略"""
    
    def __init__(self):
        super().__init__(GameState.VILLAGE)
        
        # 村庄状态的特征标识 
        self.village_indicators = ["find_now", "attack", "clan_capital_button"]  # 村庄相关按钮
        
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为村庄状态
        村庄状态特征：有村庄相关的UI元素
        """
        # 检查是否有村庄相关的UI元素
        for indicator in self.village_indicators:
            if self.get_detections_by_class(detections, indicator):
                return True
        return False
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行村庄状态逻辑 - 使用多模式功能策略
        """
        print(f"[VILLAGE] 执行村庄功能...")
        
        # 自动检测并设置游戏模式
        mode_detected = mode_manager.auto_detect_and_set_mode(detections)
        current_mode = mode_manager.get_current_mode()
        
        if current_mode is None:
            print("[VILLAGE] 警告: 无法识别当前游戏模式")
            return self._fallback_logic(detections, window_info)
        
        print(f"[VILLAGE] 当前模式: {mode_manager.get_mode_display_name(current_mode)}")
        
        # 使用模式管理器执行当前模式下的功能
        result = mode_manager.execute_current_mode_features(detections, window_info)
        
        # 如果没有功能执行或状态转换，使用备用逻辑
        if result is None:
            result = self._fallback_logic(detections, window_info)
            
        return result
        
    def _fallback_logic(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """备用逻辑：当策略模式无法处理时的降级方案"""
        print("[VILLAGE] 执行备用逻辑...")
        
        # 通过find_now计算attack位置（备用方案）
        if self.config.get('attack', False):
            find_now_detection = self.get_best_detection(detections, "find_now")
            if find_now_detection:
                print("[VILLAGE] 通过find_now按钮计算attack位置")
                attack_pos = self.calculate_relative_position(
                    find_now_detection, 
                    (0, -50)  # attack按钮相对于find_now的位置
                )
                self._click_position(attack_pos, window_info)
                time.sleep(2)
                return GameState.FINDING_OPPONENT
                
        # 默认等待
        print("[VILLAGE] 等待中...")
        time.sleep(1)
        return None
        
    def update_mode_config(self, new_config: Dict[str, Any], mode=None):
        """更新指定模式的功能配置"""
        mode_manager.update_mode_config(new_config, mode)
        
    def get_available_features(self, mode=None):
        """获取可用功能列表（用于GUI）"""
        return mode_manager.get_available_features(mode)
        
    def get_current_mode_summary(self):
        """获取当前模式摘要"""
        return mode_manager.get_mode_summary()
    
    def _click_position(self, position: tuple, window_info: WindowInfo, is_relative: bool = True):
        """点击指定位置"""
        if is_relative:
            # 相对于窗口的坐标
            screen_x = window_info.left + position[0]
            screen_y = window_info.top + position[1]
        else:
            # 窗口内的绝对坐标
            screen_x = window_info.left + position[0]  
            screen_y = window_info.top + position[1]
            
        print(f"[CLICK] 点击计算位置: ({screen_x}, {screen_y})")
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()