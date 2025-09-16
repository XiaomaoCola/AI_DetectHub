#!/usr/bin/env python3
"""
主村庄功能策略实现
包含收集资源、攻击、部落都城、训练部队、升级建筑等功能
"""

import time
from typing import Dict, List, Optional, Any

from .base import FeatureStrategy, FeatureType, GameMode, feature_registry
from core import Detection, WindowInfo, GameState


class HVCollectResourcesStrategy(FeatureStrategy):
    """主村庄 - 收集资源功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.HV_COLLECT_RESOURCES, GameMode.HOME_VILLAGE)
        self.description = "自动收集主村庄中的资源（金币、圣水、暗黑重油）"
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
        print("[HV_COLLECT] 开始收集主村庄资源...")
        
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
                print(f"[HV_COLLECT] 收集 {resource_name}")
                time.sleep(0.5)  # 短暂等待避免点击过快
                
        if resources_collected > 0:
            print(f"[HV_COLLECT] 完成，共收集 {resources_collected} 个资源")
        else:
            print("[HV_COLLECT] 没有找到可收集的资源")
            
        return None  # 保持当前状态
        
    def _click_resource(self, detection: Detection, window_info: WindowInfo):
        """点击资源收集器"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_COLLECT] 点击坐标: ({abs_x}, {abs_y})")


class HVAttackStrategy(FeatureStrategy):
    """主村庄 - 攻击功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.HV_ATTACK, GameMode.HOME_VILLAGE)
        self.description = "自动进行主村庄攻击循环（找对手→攻击→返回）"
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
        print("[HV_ATTACK] 开始主村庄攻击流程...")
        
        attack_button = self.get_best_detection(detections, 'attack_button')
        if attack_button:
            self._click_button(attack_button, window_info)
            print("[HV_ATTACK] 点击攻击按钮，转换到找对手状态")
            return GameState.FINDING_OPPONENT
            
        return None
        
    def _is_army_ready(self, detections: List[Detection]) -> bool:
        """检查军队是否准备就绪"""
        army_indicators = self.get_detections_by_class(detections, 'army_full_indicator')
        return len(army_indicators) > 0
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_ATTACK] 点击坐标: ({abs_x}, {abs_y})")


class HVClanCapitalStrategy(FeatureStrategy):
    """主村庄 - 部落都城功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.HV_CLAN_CAPITAL, GameMode.HOME_VILLAGE)
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
        print("[HV_CLAN_CAPITAL] 进入部落都城...")
        
        clan_capital_button = self.get_best_detection(detections, 'clan_capital_button')
        if clan_capital_button:
            self._click_button(clan_capital_button, window_info)
            print("[HV_CLAN_CAPITAL] 点击部落都城按钮")
            return None
            
        return None
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_CLAN_CAPITAL] 点击坐标: ({abs_x}, {abs_y})")


class HVTrainTroopsStrategy(FeatureStrategy):
    """主村庄 - 训练部队功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.HV_TRAIN_TROOPS, GameMode.HOME_VILLAGE)
        self.description = "自动训练主村庄部队"
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
        print("[HV_TRAIN] 开始训练主村庄部队...")
        
        barracks_button = self.get_best_detection(detections, 'barracks_button')
        if barracks_button:
            self._click_button(barracks_button, window_info)
            print("[HV_TRAIN] 点击兵营按钮")
            return None
            
        return None
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_TRAIN] 点击坐标: ({abs_x}, {abs_y})")


class HVUpgradeBuildingsStrategy(FeatureStrategy):
    """主村庄 - 升级建筑功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.HV_UPGRADE_BUILDINGS, GameMode.HOME_VILLAGE)
        self.description = "自动升级主村庄建筑"
        self.cooldown_seconds = 30  # 升级建筑冷却30秒
        
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以升级建筑"""
        if not self.is_enabled(config):
            return False
            
        if self.is_on_cooldown():
            return False
            
        # 检查是否有可升级的建筑
        upgrade_indicators = self.get_detections_by_class(detections, 'upgrade_available')
        return len(upgrade_indicators) > 0
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行升级建筑"""
        print("[HV_UPGRADE] 开始升级主村庄建筑...")
        
        upgrade_indicators = self.get_detections_by_class(detections, 'upgrade_available')
        if upgrade_indicators:
            # 选择第一个可升级的建筑
            first_upgrade = upgrade_indicators[0]
            self._click_button(first_upgrade, window_info)
            print("[HV_UPGRADE] 点击升级按钮")
            return None
            
        return None
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_UPGRADE] 点击坐标: ({abs_x}, {abs_y})")


def register_home_village_features():
    """注册所有主村庄功能"""
    print("[FEATURES] 注册主村庄功能策略...")
    
    # 注册各种功能策略
    feature_registry.register(HVCollectResourcesStrategy())
    feature_registry.register(HVAttackStrategy())
    feature_registry.register(HVClanCapitalStrategy())
    feature_registry.register(HVTrainTroopsStrategy())
    feature_registry.register(HVUpgradeBuildingsStrategy())
    
    # 设置默认执行顺序（收集资源优先，攻击其次）
    default_order = [
        FeatureType.HV_COLLECT_RESOURCES,
        FeatureType.HV_TRAIN_TROOPS,
        FeatureType.HV_UPGRADE_BUILDINGS,
        FeatureType.HV_ATTACK,
        FeatureType.HV_CLAN_CAPITAL
    ]
    feature_registry.set_execution_order(GameMode.HOME_VILLAGE, default_order)
    
    print("[FEATURES] 主村庄功能策略注册完成")