#!/usr/bin/env python3
"""
State 1: 建筑工人基地村庄界面状态 (自动战斗功能)
自动战斗循环的起始状态，在村庄界面寻找并点击Attack按钮
"""

import time
from typing import List, Optional

from states.state_machine import Detection, WindowInfo
from states.StateHandler import StateHandler
from states.GameState import GameState


class BBAutoAttackState_1_VillageHandler(StateHandler):
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
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为建筑工人基地村庄状态(自动战斗)
        特征：有builder_hut等村庄建筑，且没有其他战斗相关UI
        """
        # 检查村庄特征
        has_village_elements = any(self.get_detections_by_class(detections, indicator)
                                 for indicator in self.village_indicators)
        
        # 确保不在其他战斗状态
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_battle_ui = len(self.get_detections_by_class(detections, "surrender_button")) > 0
        has_okay_button = len(self.get_detections_by_class(detections, "okay")) > 0
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        
        return (has_village_elements and 
                not has_find_now and 
                not has_battle_ui and 
                not has_okay_button and 
                not has_return_home)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行村庄状态操作：寻找并点击Attack按钮
        """
        print("[AUTO_BATTLE_VILLAGE] 在村庄界面，准备开始自动战斗")
        
        # 收集资源(可选)
        self._collect_resources(detections, window_info)
        
        # 寻找Attack按钮
        attack_detection = self._find_attack_button(detections)
        if attack_detection:
            print("[AUTO_BATTLE_VILLAGE] 找到Attack按钮，点击进入攻击菜单")
            self._click_detection(attack_detection, window_info)
            time.sleep(1.5)  # 等待界面切换
            return GameState.AUTO_BATTLE_ATTACK_MENU
        
        # 如果没找到Attack按钮，尝试其他方式
        versus_button = self.get_best_detection(detections, "versus_battle_button")
        if versus_button:
            print("[AUTO_BATTLE_VILLAGE] 找到VS对战按钮，点击进入")
            self._click_detection(versus_button, window_info)
            time.sleep(1.5)
            return GameState.AUTO_BATTLE_ATTACK_MENU
            
        # 等待
        print("[AUTO_BATTLE_VILLAGE] 未找到Attack按钮，继续等待...")
        time.sleep(2)
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