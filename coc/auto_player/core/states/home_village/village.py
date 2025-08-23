#!/usr/bin/env python3
"""
主村庄(Home Village)的村庄状态处理器
专门处理主村庄模式下的村庄状态逻辑
"""

import time
import pyautogui
from typing import List, Optional, Dict, Any

from ....features.base import GameMode
from ...state_machine import StateHandler, GameState, Detection, WindowInfo
from ...mode_manager import mode_manager


class HomeVillageHandler(StateHandler):
    """主村庄村庄状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.VILLAGE)
        
        # 主村庄特有的识别标识
        self.home_village_indicators = [
            "clan_capital_button",   # 部落都城按钮 (HV特有)
            "attack",               # 攻击按钮 (通用，但HV没有find_now)
            "barracks_button"       # 兵营按钮
        ]
        
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为主村庄的村庄状态
        特征：有主村庄特有的UI元素，且没有Builder Base特征
        """
        # 检查是否有主村庄特有元素
        has_hv_elements = False
        for indicator in self.home_village_indicators:
            if self.get_detections_by_class(detections, indicator):
                has_hv_elements = True
                break
                
        # 检查是否没有Builder Base特征
        find_now_detections = self.get_detections_by_class(detections, "find_now")
        has_bb_elements = len(find_now_detections) > 0
        
        # 主村庄：有HV元素且没有BB元素，或者有攻击按钮但没有find_now
        attack_detections = self.get_detections_by_class(detections, "attack")
        has_attack_without_findnow = len(attack_detections) > 0 and not has_bb_elements
        
        return has_hv_elements or has_attack_without_findnow
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行主村庄村庄状态逻辑
        """
        print(f"[HOME_VILLAGE] 执行主村庄功能...")
        
        # 设置为主村庄模式
        mode_manager.set_mode(GameMode.HOME_VILLAGE)
        current_mode = mode_manager.get_current_mode()
        
        print(f"[HOME_VILLAGE] 当前模式: {mode_manager.get_mode_display_name(current_mode)}")
        
        # 使用模式管理器执行主村庄功能
        result = mode_manager.execute_current_mode_features(detections, window_info)
        
        # 如果没有功能执行，使用备用逻辑
        if result is None:
            result = self._fallback_logic(detections, window_info)
            
        return result
        
    def _fallback_logic(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """主村庄的备用逻辑"""
        print("[HOME_VILLAGE] 执行备用逻辑...")
        
        # 主村庄备用逻辑：直接点击攻击按钮
        attack_detections = self.get_detections_by_class(detections, "attack")
        if attack_detections:
            attack_button = max(attack_detections, key=lambda x: x.confidence)
            self._click_position(attack_button.center, window_info)
            print("[HOME_VILLAGE] 点击攻击按钮，转换到找对手状态")
            return GameState.FINDING_OPPONENT
            
        # 默认等待
        print("[HOME_VILLAGE] 等待中...")
        time.sleep(1)
        return None
        
    def update_mode_config(self, new_config: Dict[str, Any]):
        """更新主村庄功能配置"""
        mode_manager.update_mode_config(new_config, GameMode.HOME_VILLAGE)
        
    def get_available_features(self):
        """获取主村庄可用功能列表"""
        return mode_manager.get_available_features(GameMode.HOME_VILLAGE)
        
    def _click_position(self, position: tuple, window_info: WindowInfo, is_relative: bool = True):
        """点击指定位置"""
        if is_relative:
            screen_x = window_info.left + position[0]
            screen_y = window_info.top + position[1]
        else:
            screen_x = window_info.left + position[0]  
            screen_y = window_info.top + position[1]
            
        print(f"[HOME_VILLAGE] 点击位置: ({screen_x}, {screen_y})")
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()