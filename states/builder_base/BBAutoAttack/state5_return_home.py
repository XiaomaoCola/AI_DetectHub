#!/usr/bin/env python3
"""
State 6: 返回主页状态 (自动战斗功能)  
点完Okay后出现Return Home按钮，点击返回村庄完成战斗循环
"""

import time
from typing import List, Optional

from states.state_machine import Detection, WindowInfo
from states.StateHandler import StateHandler
from states.GameState import GameState


class ReturnHomeHandler(StateHandler):
    """自动战斗 - 返回主页状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.AUTO_BATTLE_RETURN_HOME)
        
        # 返回界面特征标识
        self.return_indicators = [
            "return_home",              # Return Home按钮 (关键标识)
            "battle_result_ui",         # 战斗结果界面
            "victory_defeat_text",      # 胜利/失败文字
            "stars_earned",             # 获得星数
            "resources_gained",         # 获得资源
            "trophies_change"           # 奖杯变化
        ]
        
        # 点击配置
        self.last_click_time = 0
        self.max_wait_time = 30
        
        # 结果统计
        self.battle_completed = False
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为返回主页状态
        特征：有Return Home按钮或战斗结果界面
        """
        # 检查关键标识：Return Home按钮
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        
        # 检查战斗结果界面
        has_result_ui = any(self.get_detections_by_class(detections, indicator)
                          for indicator in ["battle_result_ui", "victory_defeat_text", 
                                          "stars_earned", "resources_gained"])
        
        # 确保不在其他状态
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_okay_button = len(self.get_detections_by_class(detections, "okay")) > 0
        has_village_buildings = any(self.get_detections_by_class(detections, indicator)
                                  for indicator in ["builder_hut", "gold_mine"])
        
        return ((has_return_home or has_result_ui) and
                not has_find_now and
                not has_okay_button and
                not has_village_buildings)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行返回操作：点击Return Home按钮回到村庄
        """
        print("[AUTO_BATTLE_RETURN] 在战斗结果界面")
        
        current_time = time.time()
        
        # 收集战斗结果(可选)
        if not self.battle_completed:
            self._collect_battle_results(detections)
            self.battle_completed = True
        
        # 寻找Return Home按钮
        return_home_button = self.get_best_detection(detections, "return_home")
        if return_home_button:
            if current_time - self.last_click_time > 2:
                print("[AUTO_BATTLE_RETURN] 点击Return Home按钮返回村庄")
                self._click_detection(return_home_button, window_info)
                self.last_click_time = current_time
                time.sleep(2)  # 等待返回村庄
                return GameState.BBAutoAttack_State_1_Village  # 完成循环，回到State 1
        
        # 备用方案：点击屏幕中央区域(通常有返回按钮)
        if current_time - self.last_click_time > 5:
            print("[AUTO_BATTLE_RETURN] 使用固定位置点击返回")
            # Return Home按钮通常在屏幕中下方
            return_pos = (int(window_info.width * 0.5), int(window_info.height * 0.7))
            self._click_position(return_pos, window_info)
            self.last_click_time = current_time
            time.sleep(2)
            return GameState.BBAutoAttack_State_1_Village
        
        # 检查是否意外进入其他状态
        transition_state = self._check_state_transition(detections)
        if transition_state:
            return transition_state
        
        # 继续等待
        print("[AUTO_BATTLE_RETURN] 等待Return Home按钮...")
        time.sleep(1)
        return None
    
    def _collect_battle_results(self, detections: List[Detection]):
        """收集战斗结果信息(可选功能)"""
        print("[AUTO_BATTLE_RETURN] 收集战斗结果...")
        
        # 检查胜利/失败
        victory_text = self.get_detections_by_class(detections, "victory_defeat_text")
        if victory_text:
            print(f"[AUTO_BATTLE_RETURN] 战斗结果: {victory_text[0].class_name}")
        
        # 检查获得星数
        stars = self.get_detections_by_class(detections, "stars_earned")
        if stars:
            print(f"[AUTO_BATTLE_RETURN] 获得星数: {len(stars)}")
        
        # 检查资源获得
        resources = self.get_detections_by_class(detections, "resources_gained")
        if resources:
            print(f"[AUTO_BATTLE_RETURN] 获得资源: {len(resources)}种")
        
        # 检查奖杯变化
        trophies = self.get_detections_by_class(detections, "trophies_change")
        if trophies:
            print(f"[AUTO_BATTLE_RETURN] 奖杯变化: {trophies[0].class_name}")
    
    def _check_state_transition(self, detections: List[Detection]) -> Optional[GameState]:
        """检查是否意外进入其他状态"""
        # 检查是否已回到村庄
        has_village = any(self.get_detections_by_class(detections, indicator)
                         for indicator in ["builder_hut", "gold_mine", "versus_battle_button"])
        if has_village:
            print("[AUTO_BATTLE_RETURN] 检测到村庄界面")
            return GameState.BBAutoAttack_State_1_Village
        
        # 检查是否回到攻击菜单
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        if has_find_now:
            print("[AUTO_BATTLE_RETURN] 回到攻击菜单")
            return GameState.AUTO_BATTLE_ATTACK_MENU
        
        # 检查是否还有确认界面
        has_okay = len(self.get_detections_by_class(detections, "okay")) > 0
        if has_okay:
            print("[AUTO_BATTLE_RETURN] 检测到确认界面")
            return GameState.AUTO_BATTLE_CONFIRM_OKAY
        
        return None
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[AUTO_BATTLE_RETURN] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
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
    
    def reset_return_state(self):
        """重置返回状态"""
        self.battle_completed = False
        self.last_click_time = 0
        self.reset_retry_count()