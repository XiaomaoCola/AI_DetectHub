#!/usr/bin/env python3
"""
State 4: 投降菜单状态 (自动战斗功能)
下完兵出现Surrender按钮后点击投降
"""

import time
from typing import List, Optional

from ....state_machine import StateHandler, GameState, Detection, WindowInfo


class SurrenderMenuHandler(StateHandler):
    """自动战斗 - 投降菜单状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.AUTO_BATTLE_SURRENDER)
        
        # 投降菜单特征标识
        self.surrender_indicators = [
            "surrender_button",         # 投降按钮 (关键标识)
            "battle_timer",             # 战斗计时器 (还在战斗中)
            "opponent_base",            # 对手基地 (还在战斗界面)
            "vs_battle_ui"              # VS对战UI
        ]
        
        # 点击配置
        self.last_click_time = 0
        self.max_wait_time = 30
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为投降菜单状态
        特征：有投降按钮，且还在战斗界面
        """
        # 检查关键标识：投降按钮
        has_surrender_button = len(self.get_detections_by_class(detections, "surrender_button")) > 0
        
        # 检查是否还在战斗界面
        has_battle_elements = any(self.get_detections_by_class(detections, indicator)
                                for indicator in ["battle_timer", "opponent_base", "vs_battle_ui"])
        
        # 确保不在其他状态
        has_okay_button = len(self.get_detections_by_class(detections, "okay")) > 0
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        
        return (has_surrender_button and 
                has_battle_elements and
                not has_okay_button and 
                not has_return_home and
                not has_find_now)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行投降菜单操作：点击投降按钮
        """
        print("[AUTO_BATTLE_SURRENDER] 检测到投降按钮，准备投降")
        
        current_time = time.time()
        
        # 寻找投降按钮
        surrender_button = self.get_best_detection(detections, "surrender_button")
        if surrender_button:
            # 避免重复点击
            if current_time - self.last_click_time > 2:
                print("[AUTO_BATTLE_SURRENDER] 点击投降按钮")
                self._click_detection(surrender_button, window_info)
                self.last_click_time = current_time
                time.sleep(2)  # 等待投降确认界面出现
                return GameState.AUTO_BATTLE_CONFIRM_OKAY
        
        # 备用方案：使用固定位置点击投降
        if current_time - self.last_click_time > 5:
            print("[AUTO_BATTLE_SURRENDER] 使用固定位置点击投降")
            surrender_pos = (int(window_info.width * 0.9), int(window_info.height * 0.1))
            self._click_position(surrender_pos, window_info)
            self.last_click_time = current_time
            time.sleep(2)
            return GameState.AUTO_BATTLE_CONFIRM_OKAY
        
        # 检查是否意外进入其他状态
        transition_state = self._check_state_transition(detections)
        if transition_state:
            return transition_state
        
        # 继续等待
        print("[AUTO_BATTLE_SURRENDER] 等待投降按钮响应...")
        time.sleep(1)
        return None
    
    def _check_state_transition(self, detections: List[Detection]) -> Optional[GameState]:
        """检查是否意外进入其他状态"""
        # 检查是否已进入确认界面
        has_okay = len(self.get_detections_by_class(detections, "okay")) > 0
        if has_okay:
            print("[AUTO_BATTLE_SURRENDER] 检测到确认界面")
            return GameState.AUTO_BATTLE_CONFIRM_OKAY
        
        # 检查是否直接跳到返回界面
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        if has_return_home:
            print("[AUTO_BATTLE_SURRENDER] 直接进入返回界面")
            return GameState.AUTO_BATTLE_RETURN_HOME
        
        # 检查是否回到村庄
        has_village = any(self.get_detections_by_class(detections, indicator)
                         for indicator in ["builder_hut", "gold_mine"])
        if has_village:
            print("[AUTO_BATTLE_SURRENDER] 直接返回村庄")
            return GameState.AUTO_BATTLE_VILLAGE
        
        return None
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[AUTO_BATTLE_SURRENDER] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()
    
    def _click_position(self, position: tuple, window_info: WindowInfo):
        """点击指定位置"""
        screen_x = window_info.left + position[0]
        screen_y = window_info.top + position[1]
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()