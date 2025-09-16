#!/usr/bin/env python3
"""
建筑工人基地(Builder Base)的寻找对手状态处理器
专门处理建筑工人基地模式下的VS对战匹配逻辑
"""

import time
from typing import List, Optional

from states.state_machine import StateHandler, GameState, Detection, WindowInfo


class BuilderBaseFindingOpponentHandler(StateHandler):
    """建筑工人基地寻找对手状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.FINDING_OPPONENT)
        self.max_duration = 60  # 建筑工人基地匹配最多等待60秒
        
        # VS对战匹配特征标识
        self.vs_finding_indicators = [
            "searching_text",        # "Searching..." 文字
            "vs_matchmaking_ui",     # VS匹配界面
            "cancel_button",         # 取消按钮
            "loading_spinner",       # 加载动画
            "trophy_display"         # 奖杯显示
        ]
        
        # 进入VS对战的标识
        self.vs_battle_ready_indicators = [
            "vs_battle_ui",          # VS对战界面
            "opponent_base",         # 对手基地
            "battle_timer",          # 对战计时器
            "deployment_ready",      # 部署准备就绪
            "battle_machine"         # 战斗机器
        ]
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为建筑工人基地寻找对手状态
        特征：有VS匹配UI且有find_now特征（Builder Base特征）
        """
        # 检查Builder Base特征
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        
        # 方式1: 检测VS匹配的特征元素，且有Builder Base特征
        has_vs_finding_ui = any(self.get_detections_by_class(detections, indicator) 
                               for indicator in self.vs_finding_indicators)
        
        # 方式2: 有attack按钮且有find_now（Builder Base匹配中）
        has_attack = len(self.get_detections_by_class(detections, "attack")) > 0
        
        return (has_vs_finding_ui and has_find_now) or (has_attack and has_find_now)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行建筑工人基地VS对战匹配：等待找到对手
        """
        print("[BUILDER_BASE_FINDING] 正在匹配VS对战对手...")
        
        # 检查是否已经进入VS对战
        if self._is_vs_battle_ready(detections):
            print("[BUILDER_BASE_FINDING] 匹配成功，进入VS对战！")
            return GameState.ATTACKING  # 使用统一的攻击状态，由具体handler区分
        
        # 检查是否需要重新匹配
        cancel_detection = self.get_best_detection(detections, "cancel_button")
        if cancel_detection and self.retry_count < self.max_retries:
            print("[BUILDER_BASE_FINDING] 匹配时间过长，重新匹配...")
            self._click_detection(cancel_detection, window_info)
            time.sleep(1)
            
            # 重新开始匹配
            self._restart_vs_battle_matching(detections, window_info)
            self.increment_retry_count()
            return None
        
        # 继续等待匹配
        print("[BUILDER_BASE_FINDING] 继续等待VS对战匹配...")
        time.sleep(2)
        return None
    
    def _is_vs_battle_ready(self, detections: List[Detection]) -> bool:
        """检查是否准备好进入VS对战"""
        for indicator in self.vs_battle_ready_indicators:
            if self.get_detections_by_class(detections, indicator):
                return True
        
        # 简单判断：如果没有匹配UI但还有Builder Base特征，可能已经进入VS对战
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_matching_ui = any(self.get_detections_by_class(detections, ind) 
                             for ind in self.vs_finding_indicators)
        
        # 注意：Builder Base的特殊情况，可能需要更精确的判断
        return not has_matching_ui and not has_find_now
    
    def _restart_vs_battle_matching(self, detections: List[Detection], window_info: WindowInfo):
        """重新开始VS对战匹配"""
        # 尝试通过find_now重新开始匹配
        find_now_detection = self.get_best_detection(detections, "find_now")
        if find_now_detection:
            # 先点击find_now返回村庄
            self._click_detection(find_now_detection, window_info)
            time.sleep(1)
            
            # 然后重新点击attack按钮（通过计算位置）
            attack_pos = self._calculate_attack_position(find_now_detection)
            self._click_position(attack_pos, window_info)
        else:
            # 备用方案：点击预设的重试区域
            retry_pos = (int(window_info.width * 0.5), int(window_info.height * 0.6))
            self._click_position(retry_pos, window_info)
    
    def _calculate_attack_position(self, find_now_detection: Detection) -> tuple:
        """根据find_now按钮计算attack按钮位置"""
        find_x, find_y = find_now_detection.center
        # attack按钮通常在find_now上方50像素
        attack_x = find_x
        attack_y = find_y - 50
        return (attack_x, attack_y)
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[BUILDER_BASE_FINDING] 点击: {detection.class_name} at ({screen_x}, {screen_y})")
        
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