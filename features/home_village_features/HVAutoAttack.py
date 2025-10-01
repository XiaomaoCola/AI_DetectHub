#!/usr/bin/env python3
"""
主村庄功能策略实现
包含收集资源、攻击、部落都城、训练部队、升级建筑等功能

最下面有个使用注册器的模板。
"""

from typing import Dict, List, Optional, Any

from features.FeatureHandler import FeatureHandler, feature_registry
from features import FeatureType
from features.GameMode import GameMode
from core import Detection, WindowInfo
from features.home_village_features.HVClanCapital import HVClanCapital
from features.home_village_features.HVCollectResources import HVCollectResources
from features.home_village_features.HVTrainTroops import HVTrainTroops
from features.home_village_features.HVUpgradeBuildings import HVUpgradeBuildings
from states.GameState import GameState


class HVAutoAttack(FeatureHandler):
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


def register_home_village_features():
    """注册所有主村庄功能"""
    print("[FEATURES] 注册主村庄功能策略...")
    
    # 注册各种功能策略
    feature_registry.register(HVCollectResources())
    feature_registry.register(HVAutoAttack())
    feature_registry.register(HVClanCapital())
    feature_registry.register(HVTrainTroops())
    feature_registry.register(HVUpgradeBuildings())
    
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