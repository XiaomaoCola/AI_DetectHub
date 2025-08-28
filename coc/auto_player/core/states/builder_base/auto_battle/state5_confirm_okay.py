#!/usr/bin/env python3
"""
State 5: 确认Okay状态 (自动战斗功能)
点完Surrender后出现确认对话框，点击Okay按钮确认投降
"""

import time
from typing import List, Optional

from ....state_machine import StateHandler, GameState, Detection, WindowInfo


class ConfirmOkayHandler(StateHandler):
    """自动战斗 - 确认Okay状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.AUTO_BATTLE_CONFIRM_OKAY)
        
        # 确认对话框特征标识
        self.confirm_indicators = [
            "okay",                     # Okay按钮 (关键标识)
            "confirm_dialog",           # 确认对话框
            "surrender_confirm_text",   # 投降确认文字
            "yes_button",               # Yes按钮 (备用)
            "confirm_button"            # Confirm按钮 (备用)
        ]
        
        # 点击配置
        self.last_click_time = 0
        self.max_wait_time = 20
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为确认Okay状态
        特征：有Okay按钮或确认对话框
        """
        # 检查关键标识：Okay按钮或确认对话框
        has_okay = len(self.get_detections_by_class(detections, "okay")) > 0
        has_confirm_dialog = any(self.get_detections_by_class(detections, indicator)
                               for indicator in ["confirm_dialog", "yes_button", "confirm_button"])
        
        # 确保不在其他状态
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_village_buildings = any(self.get_detections_by_class(detections, indicator)
                                  for indicator in ["builder_hut", "gold_mine"])
        
        return ((has_okay or has_confirm_dialog) and
                not has_return_home and
                not has_find_now and
                not has_village_buildings)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行确认操作：点击Okay按钮确认投降
        """
        print("[AUTO_BATTLE_CONFIRM] 在投降确认界面")
        
        current_time = time.time()
        
        # 优先寻找Okay按钮
        okay_button = self.get_best_detection(detections, "okay")
        if okay_button:
            if current_time - self.last_click_time > 1.5:
                print("[AUTO_BATTLE_CONFIRM] 点击Okay按钮确认投降")
                self._click_detection(okay_button, window_info)
                self.last_click_time = current_time
                time.sleep(2)  # 等待界面切换
                return GameState.AUTO_BATTLE_RETURN_HOME
        
        # 备用方案：寻找其他确认按钮
        confirm_buttons = []
        confirm_buttons.extend(self.get_detections_by_class(detections, "yes_button"))
        confirm_buttons.extend(self.get_detections_by_class(detections, "confirm_button"))
        
        if confirm_buttons and current_time - self.last_click_time > 2:
            best_button = max(confirm_buttons, key=lambda x: x.confidence)
            print(f"[AUTO_BATTLE_CONFIRM] 点击确认按钮: {best_button.class_name}")
            self._click_detection(best_button, window_info)
            self.last_click_time = current_time
            time.sleep(2)
            return GameState.AUTO_BATTLE_RETURN_HOME
        
        # 最后备用方案：使用固定位置点击
        if current_time - self.last_click_time > 5:
            print("[AUTO_BATTLE_CONFIRM] 使用固定位置点击确认")
            # Okay按钮通常在屏幕中央偏下
            okay_pos = (int(window_info.width * 0.5), int(window_info.height * 0.6))
            self._click_position(okay_pos, window_info)
            self.last_click_time = current_time
            time.sleep(2)
            return GameState.AUTO_BATTLE_RETURN_HOME
        
        # 检查是否意外进入其他状态
        transition_state = self._check_state_transition(detections)
        if transition_state:
            return transition_state
        
        # 继续等待
        print("[AUTO_BATTLE_CONFIRM] 等待Okay按钮...")
        time.sleep(1)
        return None
    
    def _check_state_transition(self, detections: List[Detection]) -> Optional[GameState]:
        """检查是否意外进入其他状态"""
        # 检查是否已进入返回界面
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        if has_return_home:
            print("[AUTO_BATTLE_CONFIRM] 检测到返回界面")
            return GameState.AUTO_BATTLE_RETURN_HOME
        
        # 检查是否直接回到村庄
        has_village = any(self.get_detections_by_class(detections, indicator)
                         for indicator in ["builder_hut", "gold_mine"])
        if has_village:
            print("[AUTO_BATTLE_CONFIRM] 直接返回村庄")
            return GameState.AUTO_BATTLE_VILLAGE
        
        # 检查是否回到攻击菜单
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        if has_find_now:
            print("[AUTO_BATTLE_CONFIRM] 回到攻击菜单")
            return GameState.AUTO_BATTLE_ATTACK_MENU
        
        return None
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[AUTO_BATTLE_CONFIRM] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
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