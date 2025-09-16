#!/usr/bin/env python3
"""
建筑工人基地(Builder Base)的VS对战状态处理器
专门处理建筑工人基地模式下的实时VS对战逻辑
"""

import time
import random
from typing import List, Optional

from states.state_machine import StateHandler, GameState, Detection, WindowInfo


class BuilderBaseVersusBattleHandler(StateHandler):
    """建筑工人基地VS对战状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.ATTACKING)  # 使用通用的攻击状态
        self.max_duration = 180  # VS对战最多持续3分钟
        
        # VS对战特征标识
        self.vs_battle_indicators = [
            "vs_battle_ui",         # VS对战界面
            "battle_timer",         # 对战计时器
            "opponent_base",        # 对手基地
            "battle_machine",       # 战斗机器
            "star_count"            # 星数显示
        ]
        
        # 部署相关（Builder Base特有）
        self.troops_deployed = 0
        self.max_troops = 18        # Builder Base兵力限制
        self.deploy_interval = 0.5  # 更快的部署间隔
        self.last_deploy_time = 0
        self.battle_machine_deployed = False
        
        # VS对战部署策略
        self.deploy_strategy = "smart"  # smart, aggressive, defensive
        
        # 部署区域（针对Builder Base优化）
        self.deploy_zones = [
            (0.2, 0.8),   # 左下
            (0.5, 0.8),   # 中下  
            (0.8, 0.8),   # 右下
            (0.15, 0.6),  # 左中
            (0.85, 0.6),  # 右中
        ]
        
        # 战斗机器位置
        self.battle_machine_zone = (0.2, 0.8)
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为Builder Base VS对战状态
        特征：有VS对战UI且没有find_now（已进入对战）
        """
        # 检查是否有VS对战的特征标识
        has_vs_battle_ui = any(self.get_detections_by_class(detections, indicator)
                              for indicator in self.vs_battle_indicators)
        
        # 确保不是村庄状态
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        
        return has_vs_battle_ui and not has_find_now
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行Builder Base VS对战操作
        """
        print(f"[BUILDER_BASE_VS] VS对战中 - 已部署 {self.troops_deployed}/{self.max_troops} 兵力")
        
        current_time = time.time()
        
        # 优先部署战斗机器
        if not self.battle_machine_deployed:
            self._deploy_battle_machine(detections, window_info)
        
        # 检查是否应该结束对战
        if self._should_end_battle(current_time):
            print("[BUILDER_BASE_VS] 对战结束条件满足")
            return self._end_battle(detections, window_info)
        
        # 根据策略部署部队
        if self._can_deploy_troops(current_time):
            self._execute_deployment_strategy(detections, window_info)
        
        return None  # 继续对战状态
    
    def _deploy_battle_machine(self, detections: List[Detection], window_info: WindowInfo):
        """部署战斗机器（优先）"""
        battle_machine_detection = self.get_best_detection(detections, "battle_machine")
        if battle_machine_detection:
            # 点击战斗机器
            self._click_detection(battle_machine_detection, window_info)
            time.sleep(0.2)
            
            # 在指定位置部署
            x = int(window_info.width * self.battle_machine_zone[0])
            y = int(window_info.height * self.battle_machine_zone[1])
            self._click_position((x, y), window_info)
            
            print("[BUILDER_BASE_VS] 战斗机器已部署")
            self.battle_machine_deployed = True
            self.last_deploy_time = time.time()
    
    def _execute_deployment_strategy(self, detections: List[Detection], window_info: WindowInfo):
        """根据策略执行部署"""
        if self.deploy_strategy == "smart":
            self._smart_deployment(detections, window_info)
        elif self.deploy_strategy == "aggressive":
            self._aggressive_deployment(detections, window_info)
        else:
            self._defensive_deployment(detections, window_info)
    
    def _smart_deployment(self, detections: List[Detection], window_info: WindowInfo):
        """智能部署策略"""
        # 优先在检测到的有利位置部署
        empty_spaces = self.get_detections_by_class(detections, "empty_space")
        if empty_spaces:
            # 选择最佳位置（可以添加更复杂的逻辑）
            target = max(empty_spaces, key=lambda x: x.confidence)
            self._click_detection(target, window_info)
            print(f"[BUILDER_BASE_VS] 智能部署第{self.troops_deployed + 1}个兵")
        else:
            # 使用预设的最佳区域
            zone = self.deploy_zones[min(self.troops_deployed, len(self.deploy_zones) - 1)]
            x = int(window_info.width * zone[0])
            y = int(window_info.height * zone[1])
            self._click_position((x, y), window_info)
            print(f"[BUILDER_BASE_VS] 预设区域智能部署第{self.troops_deployed + 1}个兵")
        
        self._update_deployment_state()
    
    def _aggressive_deployment(self, detections: List[Detection], window_info: WindowInfo):
        """激进部署策略"""
        # 快速集中部署
        zone = random.choice(self.deploy_zones[:3])  # 优先选择前方位置
        x = int(window_info.width * zone[0])
        y = int(window_info.height * zone[1])
        
        # 添加随机偏移
        x += random.randint(-30, 30)
        y += random.randint(-20, 20)
        
        self._click_position((x, y), window_info)
        print(f"[BUILDER_BASE_VS] 激进部署第{self.troops_deployed + 1}个兵")
        self._update_deployment_state()
    
    def _defensive_deployment(self, detections: List[Detection], window_info: WindowInfo):
        """防守反击策略"""
        # 分散部署，稳妥推进
        zone = self.deploy_zones[self.troops_deployed % len(self.deploy_zones)]
        x = int(window_info.width * zone[0])
        y = int(window_info.height * zone[1])
        self._click_position((x, y), window_info)
        print(f"[BUILDER_BASE_VS] 防守部署第{self.troops_deployed + 1}个兵")
        self._update_deployment_state()
    
    def _update_deployment_state(self):
        """更新部署状态"""
        self.troops_deployed += 1
        self.last_deploy_time = time.time()
        time.sleep(0.1)  # 短暂延迟
    
    def _should_end_battle(self, current_time: float) -> bool:
        """判断是否应该结束对战"""
        # 条件1：已部署所有兵力
        if self.troops_deployed >= self.max_troops:
            return True
            
        # 条件2：长时间没有部署
        if current_time - self.last_deploy_time > 25:  # 25秒没有部署
            return True
            
        # 条件3：检测到胜利/失败条件（可以扩展）
        return False
    
    def _can_deploy_troops(self, current_time: float) -> bool:
        """判断是否可以部署部队"""
        if self.troops_deployed >= self.max_troops:
            return False
            
        if current_time - self.last_deploy_time < self.deploy_interval:
            return False
            
        return True
    
    def _end_battle(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """结束VS对战"""
        # VS对战通常会自动结束，这里主要是等待结果
        print("[BUILDER_BASE_VS] VS对战即将结束，等待结果...")
        time.sleep(3)
        
        # 返回村庄状态等待下一轮
        return GameState.VILLAGE
    
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
        """重置VS对战状态"""
        self.troops_deployed = 0
        self.last_deploy_time = 0
        self.battle_machine_deployed = False
        self.reset_retry_count()