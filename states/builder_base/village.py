#!/usr/bin/env python3
"""
建筑工人基地(Builder Base)的村庄状态处理器
专门处理建筑工人基地模式下的村庄状态逻辑
"""

import time
import pyautogui
from typing import List, Optional, Dict, Any

from coc.auto_player.features.base import GameMode
from states.state_machine import StateHandler, Detection, WindowInfo
from states.GameState import GameState
from core.mode_manager import mode_manager


class BuilderBaseVillageHandler(StateHandler):
    """建筑工人基地村庄状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.VILLAGE)
        
        # 建筑工人基地特有的识别标识
        self.builder_base_indicators = [
            "find_now"  # Find Now按钮 (BB特有)
        ]
        
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为建筑工人基地的村庄状态
        特征：有find_now按钮（Builder Base特有）
        """
        find_now_detections = self.get_detections_by_class(detections, "find_now")
        return len(find_now_detections) > 0
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行建筑工人基地村庄状态逻辑
        """
        print(f"[BUILDER_BASE] 执行建筑工人基地功能...")
        
        # 设置为建筑工人基地模式
        mode_manager.set_mode(GameMode.BUILDER_BASE)
        current_mode = mode_manager.get_current_mode()
        
        print(f"[BUILDER_BASE] 当前模式: {mode_manager.get_mode_display_name(current_mode)}")
        
        # 使用模式管理器执行建筑工人基地功能
        result = mode_manager.execute_current_mode_features(detections, window_info)
        
        # 如果没有功能执行，使用备用逻辑
        if result is None:
            result = self._fallback_logic(detections, window_info)
            
        return result
        
    def _fallback_logic(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """建筑工人基地的备用逻辑"""
        print("[BUILDER_BASE] 执行备用逻辑...")
        
        # Builder Base备用逻辑：通过find_now计算attack位置
        find_now_detections = self.get_detections_by_class(detections, "find_now")
        if find_now_detections:
            find_now_button = max(find_now_detections, key=lambda x: x.confidence)
            # 计算attack按钮位置（通常在find_now上方）
            attack_pos = self._calculate_attack_position(find_now_button)
            self._click_position(attack_pos, window_info)
            print("[BUILDER_BASE] 通过find_now计算attack位置，转换到找对手状态")
            return GameState.FINDING_OPPONENT
            
        # 默认等待
        print("[BUILDER_BASE] 等待中...")
        time.sleep(1)
        return None
        
    def _calculate_attack_position(self, find_now_detection: Detection) -> tuple:
        """根据find_now按钮计算attack按钮位置"""
        find_x, find_y = find_now_detection.center
        # attack按钮通常在find_now上方50像素
        attack_x = find_x
        attack_y = find_y - 50
        return (attack_x, attack_y)
        
    def update_mode_config(self, new_config: Dict[str, Any]):
        """更新建筑工人基地功能配置"""
        mode_manager.update_mode_config(new_config, GameMode.BUILDER_BASE)
        
    def get_available_features(self):
        """获取建筑工人基地可用功能列表"""
        return mode_manager.get_available_features(GameMode.BUILDER_BASE)
        
    def _click_position(self, position: tuple, window_info: WindowInfo, is_relative: bool = True):
        """点击指定位置"""
        if is_relative:
            screen_x = window_info.left + position[0]
            screen_y = window_info.top + position[1]
        else:
            screen_x = window_info.left + position[0]  
            screen_y = window_info.top + position[1]
            
        print(f"[BUILDER_BASE] 点击位置: ({screen_x}, {screen_y})")
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()