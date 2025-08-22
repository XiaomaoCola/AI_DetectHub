#!/usr/bin/env python3
"""
村庄功能策略实现
包含收集资源、攻击、部落都城等功能
"""

import time
from typing import Dict, List, Optional, Any

from .features import FeatureStrategy, FeatureType, feature_registry
from .state_machine import Detection, WindowInfo, GameState


class CollectResourcesStrategy(FeatureStrategy):
    """收集资源功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.COLLECT_RESOURCES)
        self.description = "自动收集村庄中的资源（金币、圣水等）"
        self.cooldown_seconds = 10  # 收集资源冷却10秒
        
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以收集资源"""
        if not self.is_enabled(config):
            return False
            
        if self.is_on_cooldown():
            return False
            
        # 检查是否有可收集的资源
        collectible_resources = ['gold_collector', 'elixir_collector', 'dark_elixir_collector']
        for resource_type in collectible_resources:
            if self.get_detections_by_class(detections, resource_type):
                return True
                
        return False
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行收集资源"""
        print("[COLLECT] 开始收集资源...")
        
        # 收集各种资源
        resources_collected = 0
        collectible_resources = [
            ('gold_collector', '金币收集器'),
            ('elixir_collector', '圣水收集器'), 
            ('dark_elixir_collector', '暗黑重油收集器')
        ]
        
        for resource_class, resource_name in collectible_resources:
            resource_detections = self.get_detections_by_class(detections, resource_class)
            for detection in resource_detections:
                self._click_resource(detection, window_info)
                resources_collected += 1
                print(f"[COLLECT] 收集 {resource_name}")
                time.sleep(0.5)  # 短暂等待避免点击过快
                
        if resources_collected > 0:
            print(f"[COLLECT] 完成，共收集 {resources_collected} 个资源")
        else:
            print("[COLLECT] 没有找到可收集的资源")
            
        return None  # 保持当前状态
        
    def _click_resource(self, detection: Detection, window_info: WindowInfo):
        """点击资源收集器"""
        # 这里应该调用实际的点击功能
        # 暂时用打印模拟
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[COLLECT] 点击坐标: ({abs_x}, {abs_y})")


class AttackStrategy(FeatureStrategy):
    """攻击功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.ATTACK)
        self.description = "自动进行攻击循环（找对手→攻击→返回）"
        self.cooldown_seconds = 15  # 攻击冷却15秒
        
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以攻击"""
        if not self.is_enabled(config):
            return False
            
        if self.is_on_cooldown():
            return False
            
        # 检查是否有攻击按钮
        attack_button = self.get_best_detection(detections, 'attack_button')
        if not attack_button:
            return False
            
        # 检查军队是否准备就绪（可选条件）
        if config.get('check_army_ready', True):
            return self._is_army_ready(detections)
            
        return True
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行攻击"""
        print("[ATTACK] 开始攻击流程...")
        
        attack_button = self.get_best_detection(detections, 'attack_button')
        if attack_button:
            self._click_button(attack_button, window_info)
            print("[ATTACK] 点击攻击按钮，转换到找对手状态")
            return GameState.FINDING_OPPONENT
            
        return None
        
    def _is_army_ready(self, detections: List[Detection]) -> bool:
        """检查军队是否准备就绪"""
        # 检查军队容量指示器
        army_indicators = self.get_detections_by_class(detections, 'army_full_indicator')
        return len(army_indicators) > 0
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[ATTACK] 点击坐标: ({abs_x}, {abs_y})")


class ClanCapitalStrategy(FeatureStrategy):
    """部落都城功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.CLAN_CAPITAL)
        self.description = "自动进入部落都城进行相关操作"
        self.cooldown_seconds = 30  # 部落都城冷却30秒
        
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以进入部落都城"""
        if not self.is_enabled(config):
            return False
            
        if self.is_on_cooldown():
            return False
            
        # 检查是否有部落都城按钮
        clan_capital_button = self.get_best_detection(detections, 'clan_capital_button')
        return clan_capital_button is not None
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行部落都城操作"""
        print("[CLAN_CAPITAL] 进入部落都城...")
        
        clan_capital_button = self.get_best_detection(detections, 'clan_capital_button')
        if clan_capital_button:
            self._click_button(clan_capital_button, window_info)
            print("[CLAN_CAPITAL] 点击部落都城按钮")
            # 这里可能需要新的状态来处理部落都城逻辑
            return None
            
        return None
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[CLAN_CAPITAL] 点击坐标: ({abs_x}, {abs_y})")


class TrainTroopsStrategy(FeatureStrategy):
    """训练部队功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.TRAIN_TROOPS)
        self.description = "自动训练部队"
        self.cooldown_seconds = 20  # 训练部队冷却20秒
        
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以训练部队"""
        if not self.is_enabled(config):
            return False
            
        if self.is_on_cooldown():
            return False
            
        # 检查是否有兵营按钮
        barracks_button = self.get_best_detection(detections, 'barracks_button')
        return barracks_button is not None
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行训练部队"""
        print("[TRAIN] 开始训练部队...")
        
        barracks_button = self.get_best_detection(detections, 'barracks_button')
        if barracks_button:
            self._click_button(barracks_button, window_info)
            print("[TRAIN] 点击兵营按钮")
            # 这里需要更复杂的训练逻辑
            return None
            
        return None
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[TRAIN] 点击坐标: ({abs_x}, {abs_y})")


def register_village_features():
    """注册所有村庄功能"""
    print("[FEATURES] 注册村庄功能策略...")
    
    # 注册各种功能策略
    feature_registry.register(CollectResourcesStrategy())
    feature_registry.register(AttackStrategy())
    feature_registry.register(ClanCapitalStrategy())
    feature_registry.register(TrainTroopsStrategy())
    
    # 设置默认执行顺序（收集资源优先，攻击其次）
    default_order = [
        FeatureType.COLLECT_RESOURCES,
        FeatureType.TRAIN_TROOPS,
        FeatureType.ATTACK,
        FeatureType.CLAN_CAPITAL
    ]
    feature_registry.set_execution_order(default_order)
    
    print("[FEATURES] 村庄功能策略注册完成")