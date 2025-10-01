#!/usr/bin/env python3
"""
State 3: 战斗场景状态 (自动战斗功能)
点完Find Now进入战斗画面，进行自动部署直到可以投降
"""

import time
import random
from typing import List, Optional

from states.DataClasses import Detection, WindowInfo
from states.StateHandler import StateHandler
from states.GameState import GameState


class BattleSceneHandler(StateHandler):
    """自动战斗 - 战斗场景状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.AUTO_BATTLE_BATTLE_SCENE)
        
        # 战斗场景特征标识
        self.battle_indicators = [
            "opponent_base",            # 对手基地
            "battle_timer",             # 战斗计时器 
            "troop_deployment_area",    # 部队部署区域
            "battle_machine",           # 战斗机器
            "vs_battle_ui"              # VS对战UI
        ]
        
        # 部署配置
        self.troops_deployed = 0
        self.max_troops = 18            # Builder Base最大兵力
        self.deploy_interval = 0.6      # 部署间隔
        self.last_deploy_time = 0
        self.battle_machine_deployed = False
        
        # 部署区域(Builder Base优化)
        self.deploy_zones = [
            (0.2, 0.8),   # 左下角
            (0.5, 0.85),  # 中下方
            (0.8, 0.8),   # 右下角
            (0.15, 0.6),  # 左中部
            (0.85, 0.6),  # 右中部
            (0.3, 0.7),   # 左中下
            (0.7, 0.7),   # 右中下
        ]
        
        # 战斗机器位置
        self.battle_machine_zone = (0.3, 0.8)
        
        # 投降条件
        self.min_troops_before_surrender = 12  # 至少部署12个兵才能投降
        self.max_battle_time = 45              # 最大战斗时间(秒)
        self.battle_start_time = None
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为战斗场景状态
        特征：有对手基地、战斗计时器等战斗UI，但还没有投降按钮
        """
        # 检查战斗场景特征
        has_battle_elements = any(self.get_detections_by_class(detections, indicator)
                                for indicator in self.battle_indicators)
        
        # 检查是否还没有投降按钮(说明还在部署阶段)
        has_surrender = len(self.get_detections_by_class(detections, "surrender_button")) > 0
        
        # 确保不在其他状态
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_okay_button = len(self.get_detections_by_class(detections, "okay")) > 0
        has_return_home = len(self.get_detections_by_class(detections, "return_home")) > 0
        
        return (has_battle_elements and 
                not has_find_now and 
                not has_okay_button and 
                not has_return_home)
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行战斗场景操作：自动部署部队
        """
        if self.battle_start_time is None:
            self.battle_start_time = time.time()
            print("[AUTO_BATTLE_SCENE] 进入战斗场景，开始自动部署")
        
        current_time = time.time()
        battle_duration = current_time - self.battle_start_time
        
        print(f"[AUTO_BATTLE_SCENE] 战斗中 - 已部署 {self.troops_deployed}/{self.max_troops} 兵力 (时长: {battle_duration:.1f}s)")
        
        # 检查是否可以投降
        if self._should_surrender(current_time, detections):
            return self._try_to_surrender(detections)
        
        # 优先部署战斗机器
        if not self.battle_machine_deployed:
            if self._deploy_battle_machine(detections, window_info):
                return None
        
        # 部署普通部队
        if self._can_deploy_troops(current_time):
            self._deploy_troops(detections, window_info)
        
        return None
    
    def _should_surrender(self, current_time: float, detections: List[Detection]) -> bool:
        """判断是否应该投降"""
        # 条件1: 检测到投降按钮且已部署足够兵力
        has_surrender_button = len(self.get_detections_by_class(detections, "surrender_button")) > 0
        enough_troops = self.troops_deployed >= self.min_troops_before_surrender
        
        if has_surrender_button and enough_troops:
            return True
        
        # 条件2: 已部署所有兵力
        if self.troops_deployed >= self.max_troops:
            return True
        
        # 条件3: 战斗时间过长
        battle_duration = current_time - (self.battle_start_time or current_time)
        if battle_duration > self.max_battle_time:
            return True
        
        # 条件4: 长时间没有部署(可能卡住了)
        if current_time - self.last_deploy_time > 20:  # 20秒没部署
            return True
            
        return False
    
    def _try_to_surrender(self, detections: List[Detection]) -> Optional[GameState]:
        """尝试投降"""
        surrender_button = self.get_best_detection(detections, "surrender_button")
        if surrender_button:
            print("[AUTO_BATTLE_SCENE] 找到投降按钮，准备投降")
            return GameState.AUTO_BATTLE_SURRENDER
        else:
            print("[AUTO_BATTLE_SCENE] 满足投降条件但未找到投降按钮，继续等待")
            return None
    
    def _deploy_battle_machine(self, detections: List[Detection], window_info: WindowInfo) -> bool:
        """部署战斗机器"""
        battle_machine = self.get_best_detection(detections, "battle_machine")
        if battle_machine:
            print("[AUTO_BATTLE_SCENE] 部署战斗机器")
            # 先点击战斗机器
            self._click_detection(battle_machine, window_info)
            time.sleep(0.3)
            
            # 在指定区域部署
            x = int(window_info.width * self.battle_machine_zone[0])
            y = int(window_info.height * self.battle_machine_zone[1])
            self._click_position((x, y), window_info)
            
            self.battle_machine_deployed = True
            self.last_deploy_time = time.time()
            time.sleep(0.5)
            return True
        return False
    
    def _can_deploy_troops(self, current_time: float) -> bool:
        """判断是否可以部署部队"""
        if self.troops_deployed >= self.max_troops:
            return False
            
        if current_time - self.last_deploy_time < self.deploy_interval:
            return False
            
        return True
    
    def _deploy_troops(self, detections: List[Detection], window_info: WindowInfo):
        """部署部队"""
        # 智能部署：优先在检测到的空地部署
        empty_spaces = self.get_detections_by_class(detections, "empty_space")
        if empty_spaces and random.random() < 0.7:  # 70%概率使用检测到的空地
            target = random.choice(empty_spaces)
            self._click_detection(target, window_info)
            print(f"[AUTO_BATTLE_SCENE] 在空地部署第{self.troops_deployed + 1}个兵")
        else:
            # 使用预设区域部署
            zone = random.choice(self.deploy_zones)
            x = int(window_info.width * zone[0])
            y = int(window_info.height * zone[1])
            
            # 添加随机偏移避免重复点击
            x += random.randint(-20, 20)
            y += random.randint(-15, 15)
            
            self._click_position((x, y), window_info)
            print(f"[AUTO_BATTLE_SCENE] 在预设区域部署第{self.troops_deployed + 1}个兵 at {zone}")
        
        self.troops_deployed += 1
        self.last_deploy_time = time.time()
        time.sleep(0.2)
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.05)
        pyautogui.click()
    
    def _click_position(self, position: tuple, window_info: WindowInfo):
        """点击指定位置"""
        screen_x = window_info.left + position[0]
        screen_y = window_info.top + position[1]
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.05)
        pyautogui.click()
    
    def reset_battle_state(self):
        """重置战斗状态"""
        self.troops_deployed = 0
        self.last_deploy_time = 0
        self.battle_machine_deployed = False
        self.battle_start_time = None
        self.reset_retry_count()