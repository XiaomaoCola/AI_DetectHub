import time
import pyautogui
from typing import List, Optional

from ..state_machine import StateHandler, GameState, Detection, WindowInfo


class VillageHandler(StateHandler):
    """村庄状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.VILLAGE)
        
        # 村庄状态的特征标识
        self.required_indicators = ["find_now"]  # Builder Base特有的find_now按钮
        self.optional_indicators = ["attack"]    # 可能存在的attack按钮
        
        # 相对位置配置
        self.attack_offset_from_find_now = (0, -50)  # attack按钮相对于find_now的位置
        
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为村庄状态
        村庄状态特征：有find_now按钮（Builder Base独有）
        """
        find_now_detections = self.get_detections_by_class(detections, "find_now")
        return len(find_now_detections) > 0
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行村庄状态操作：点击attack按钮开始攻击
        """
        print("[VILLAGE] 在村庄状态，准备开始攻击...")
        
        # 方式1: 直接检测attack按钮
        attack_detection = self.get_best_detection(detections, "attack")
        if attack_detection:
            print("[VILLAGE] 直接检测到attack按钮")
            self._click_detection(attack_detection, window_info)
            time.sleep(2)  # 等待界面切换
            return GameState.FINDING_OPPONENT
        
        # 方式2: 通过find_now按钮计算attack按钮位置
        find_now_detection = self.get_best_detection(detections, "find_now")
        if find_now_detection:
            print("[VILLAGE] 通过find_now按钮计算attack位置")
            attack_pos = self.calculate_relative_position(
                find_now_detection, 
                self.attack_offset_from_find_now
            )
            self._click_position(attack_pos, window_info)
            time.sleep(2)
            return GameState.FINDING_OPPONENT
        
        # 方式3: 使用预设的固定位置（备用方案）
        print("[VILLAGE] 使用备用方案：固定位置点击")
        backup_pos = (window_info.width // 2, window_info.height // 3)
        self._click_position(backup_pos, window_info, is_relative=False)
        time.sleep(2)
        return GameState.FINDING_OPPONENT
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[CLICK] 点击检测目标: {detection.class_name} "
              f"at ({screen_x}, {screen_y}), conf: {detection.confidence:.2f}")
        
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()
    
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