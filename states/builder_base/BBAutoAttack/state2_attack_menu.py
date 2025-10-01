#!/usr/bin/env python3
"""
State 2: 攻击菜单状态 (自动战斗功能)  
点过Attack后出现Find Now按钮的界面，点击Find Now开始匹配
"""

import time
from typing import List, Optional

from states.DataClasses import Detection, WindowInfo
from states.StateHandler import StateHandler
from states.GameState import GameState


class AttackMenuHandler(StateHandler):
    """自动战斗 - 攻击菜单状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.BBAutoAttack_State_2_Attack_Menu)
        
        # 攻击菜单特征标识
        self.attack_menu_indicators = [
            "find_now",                 # Find Now按钮 (关键标识)
            "attack",                   # Attack按钮 (可能还在)
            "troop_selection_ui",       # 部队选择界面
            "battle_strategy_ui"        # 战术选择界面
        ]
        
        # 等待时间配置
        self.max_wait_time = 30  # 最多等待30秒
        self.last_click_time = 0
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为攻击菜单状态
        特征：有Find Now按钮，且不在战斗或其他界面
        """
        # 检查关键标识：Find Now按钮
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        
        # 确保不在其他状态
        has_battle_ui = len(self.get_detections_by_class(detections, "surrender_button")) > 0
        has_okay_button = len(self.get_detections_by_class(detections, "okay")) > 0
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        has_village_buildings = any(self.get_detections_by_class(detections, indicator)
                                  for indicator in ["builder_hut", "gold_mine"])
        
        return (has_find_now and 
                not has_battle_ui and 
                not has_okay_button and 
                not has_return_home and
                not has_village_buildings)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行攻击菜单操作：点击Find Now按钮开始匹配
        """
        print("[AUTO_BATTLE_ATTACK_MENU] 在攻击菜单界面")
        
        current_time = time.time()
        
        # 检查部队配置(可选)
        self._check_troop_configuration(detections, window_info)
        
        # 寻找并点击Find Now按钮
        find_now_detection = self.get_best_detection(detections, "find_now")
        if find_now_detection:
            # 避免重复点击
            if current_time - self.last_click_time > 3:
                print("[AUTO_BATTLE_ATTACK_MENU] 找到Find Now按钮，开始匹配对手")
                self._click_detection(find_now_detection, window_info)
                self.last_click_time = current_time
                time.sleep(2)  # 等待匹配开始
                return GameState.AUTO_BATTLE_BATTLE_SCENE
        
        # 检查是否意外进入其他状态
        if self._check_state_transition(detections):
            return self._handle_unexpected_transition(detections)
        
        # 继续等待
        print("[AUTO_BATTLE_ATTACK_MENU] 等待Find Now按钮...")
        time.sleep(1)
        return None
    
    def _check_troop_configuration(self, detections: List[Detection], window_info: WindowInfo):
        """检查部队配置(可选功能)"""
        # 检查是否有部队选择UI
        troop_ui = self.get_detections_by_class(detections, "troop_selection_ui")
        if troop_ui:
            print("[AUTO_BATTLE_ATTACK_MENU] 检测到部队选择界面")
            # 这里可以添加部队配置逻辑
            # 比如选择特定的部队组合
    
    def _check_state_transition(self, detections: List[Detection]) -> bool:
        """检查是否意外进入其他状态"""
        # 检查是否已经进入战斗
        has_battle_indicators = (
            len(self.get_detections_by_class(detections, "surrender_button")) > 0 or
            len(self.get_detections_by_class(detections, "battle_timer")) > 0 or
            len(self.get_detections_by_class(detections, "opponent_base")) > 0
        )
        
        # 检查是否回到村庄
        has_village_indicators = any(self.get_detections_by_class(detections, indicator)
                                   for indicator in ["builder_hut", "gold_mine"])
        
        return has_battle_indicators or has_village_indicators
    
    def _handle_unexpected_transition(self, detections: List[Detection]) -> Optional[GameState]:
        """处理意外的状态转换"""
        # 如果进入战斗
        if len(self.get_detections_by_class(detections, "surrender_button")) > 0:
            print("[AUTO_BATTLE_ATTACK_MENU] 意外进入战斗状态")
            return GameState.AUTO_BATTLE_BATTLE_SCENE
            
        # 如果回到村庄
        if any(self.get_detections_by_class(detections, indicator)
               for indicator in ["builder_hut", "gold_mine"]):
            print("[AUTO_BATTLE_ATTACK_MENU] 意外返回村庄")
            return GameState.BBAutoAttack_State_1_Village
            
        return None
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[AUTO_BATTLE_ATTACK_MENU] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()