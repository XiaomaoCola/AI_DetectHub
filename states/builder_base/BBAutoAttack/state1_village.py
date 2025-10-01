#!/usr/bin/env python3
"""
State 1: 建筑工人基地村庄界面状态 (自动战斗功能)
自动战斗循环的起始状态，在村庄界面寻找并点击Attack按钮
"""

import time
from typing import List, Optional

from states.DataClasses import Detection, WindowInfo
from states.StateHandler import StateHandler
from states.GameState import GameState

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from interaction.WindowClicker import WindowClicker


class BBAutoAttackState1VillageHandler(StateHandler):
    """自动战斗 - 村庄状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.BBAutoAttack_State_1_Village)
        
        # 村庄状态特征标识
        self.village_indicators = [
            "builder_hut",              # 建筑工人小屋 (BB特有)
            "versus_battle_button",     # VS对战按钮
            "gold_mine",                # 金矿
            "elixir_collector"          # 圣水收集器
        ]
        
        # Attack按钮相关
        self.attack_button_indicators = [
            "attack",                   # Attack按钮
            "versus_battle_button"      # VS对战按钮(备用)
        ]
    

    def execute(self) -> Optional[GameState]:
        """
        执行村庄状态操作：点击Attack按钮
        """
        print("[AUTO_BATTLE_VILLAGE] 在村庄界面，点击Attack按钮")

        # 使用WindowClicker点击attack按钮
        clicker = WindowClicker()
        success = clicker.click_button("BB_attack")

        if success:
            print("[AUTO_BATTLE_VILLAGE] Attack按钮点击成功，等待界面切换")
            time.sleep(1.5)  # 等待界面切换
            return GameState.BBAutoAttack_State_2_Attack_Menu
        else:
            print("[AUTO_BATTLE_VILLAGE] Attack按钮点击失败")
            return None

    def _collect_resources(self, detections: List[Detection], window_info: WindowInfo):
        """收集村庄资源(可选功能)"""
        # 简单的资源收集逻辑
        resource_collectors = []
        resource_collectors.extend(self.get_detections_by_class(detections, "gold_mine"))
        resource_collectors.extend(self.get_detections_by_class(detections, "elixir_collector"))
        resource_collectors.extend(self.get_detections_by_class(detections, "gem_mine"))
        
        for collector in resource_collectors[:3]:  # 最多点击3个
            if collector.confidence > 0.7:  # 置信度要求
                print(f"[AUTO_BATTLE_VILLAGE] 收集资源: {collector.class_name}")
                self._click_detection(collector, window_info)
                time.sleep(0.3)
    
    def _find_attack_button(self, detections: List[Detection]) -> Optional[Detection]:
        """寻找Attack按钮"""
        # 优先寻找attack按钮
        attack_detections = self.get_detections_by_class(detections, "attack")
        if attack_detections:
            return max(attack_detections, key=lambda x: x.confidence)
        
        # 备用：VS对战按钮
        versus_detections = self.get_detections_by_class(detections, "versus_battle_button")
        if versus_detections:
            return max(versus_detections, key=lambda x: x.confidence)
            
        return None

    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[AUTO_BATTLE_VILLAGE] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()