#!/usr/bin/env python3
"""
主村庄(Home Village)的寻找对手状态处理器
专门处理主村庄模式下的寻找对手逻辑
"""

import time
from typing import List, Optional

from states.state_machine import StateHandler, GameState, Detection, WindowInfo


class HomeVillageFindingOpponentHandler(StateHandler):
    """主村庄寻找对手状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.FINDING_OPPONENT)
        self.max_duration = 45  # 主村庄寻找对手最多等待45秒
        
        # 状态特征标识
        self.finding_indicators = [
            "searching_text",    # "Searching for opponent" 文字
            "cancel_button",     # 取消按钮
            "loading_spinner"    # 加载动画
        ]
        
        # 进入攻击状态的标识
        self.attack_ready_indicators = [
            "enemy_base",        # 敌方基地
            "troop_panel",       # 部队面板
            "deploy_area",       # 部署区域
            "battle_ui",         # 战斗UI
            "surrender_button"   # 投降按钮
        ]
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为主村庄寻找对手状态
        特征：有attack按钮但没有find_now按钮（主村庄特征）
        """
        # 方式1: 有attack按钮但没有find_now（说明已经离开主村庄）
        has_attack = len(self.get_detections_by_class(detections, "attack")) > 0
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        
        if has_attack and not has_find_now:
            return True
            
        # 方式2: 检测寻找对手的特征元素，且没有Builder Base特征
        has_finding_ui = any(self.get_detections_by_class(detections, indicator) 
                           for indicator in self.finding_indicators)
        
        return has_finding_ui and not has_find_now
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行主村庄寻找对手状态操作：等待找到对手
        """
        print("[HOME_VILLAGE_FINDING] 正在寻找对手...")
        
        # 检查是否已经找到对手并进入攻击状态
        if self._is_attack_ready(detections):
            print("[HOME_VILLAGE_FINDING] 找到对手，进入主村庄攻击状态！")
            return GameState.ATTACKING
        
        # 检查是否有取消按钮（可能需要重新搜索）
        cancel_detection = self.get_best_detection(detections, "cancel_button")
        if cancel_detection and self.retry_count < self.max_retries:
            print("[HOME_VILLAGE_FINDING] 搜索时间过长，重新搜索...")
            self._click_detection(cancel_detection, window_info)
            time.sleep(1)
            # 重新点击攻击按钮
            attack_detection = self.get_best_detection(detections, "attack")
            if attack_detection:
                self._click_detection(attack_detection, window_info)
            self.increment_retry_count()
            return None  # 保持当前状态
        
        # 继续等待
        print("[HOME_VILLAGE_FINDING] 继续等待匹配对手...")
        time.sleep(2)
        return None  # 保持当前状态
    
    def _is_attack_ready(self, detections: List[Detection]) -> bool:
        """检查是否准备好攻击（主村庄版本）"""
        for indicator in self.attack_ready_indicators:
            if self.get_detections_by_class(detections, indicator):
                return True
        
        # 简单判断：如果没有find_now和搜索相关的UI，可能已经进入攻击界面
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_finding_ui = any(self.get_detections_by_class(detections, ind) 
                           for ind in self.finding_indicators)
        
        return not has_find_now and not has_finding_ui
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[HOME_VILLAGE_FINDING] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()