#!/usr/bin/env python3
"""
建筑工人基地功能策略实现
包含收集资源、升级建筑、进攻等功能（相对简单）

最下面有个使用注册器的模板。
"""

from typing import Dict, List, Optional, Any

from features.FeatureHandler import FeatureHandler, feature_registry
from features import FeatureType
from features.GameMode import GameMode
from core import Detection, WindowInfo
from features.builder_base_features.BBCollectResources import BBCollectResources
from features.builder_base_features.BBUpgradeBuildings import BBUpgradeBuildings
from states.GameState import GameState


class BBAutoAttack(FeatureHandler):
    """建筑工人基地 - 攻击功能策略"""
    
    def __init__(self):
        super().__init__(FeatureType.BB_ATTACK, GameMode.BUILDER_BASE)
        self.description = "自动进行建筑工人基地攻击（通过find_now按钮）"
        self.cooldown_seconds = 15  # 攻击冷却15秒
        
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以攻击"""
        if not self.is_enabled(config):
            return False
            
        if self.is_on_cooldown():
            return False
            
        # Builder Base特有：检查find_now按钮
        find_now_button = self.get_best_detection(detections, 'find_now')
        if not find_now_button:
            return False
            
        # 检查建筑工人基地军队是否准备就绪（可选条件）
        if config.get('check_army_ready', True):
            return self._is_bb_army_ready(detections)
            
        return True
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行攻击"""
        print("[BB_ATTACK] 开始建筑工人基地攻击流程...")
        
        # 首先尝试直接检测attack按钮
        attack_button = self.get_best_detection(detections, 'attack')
        if attack_button:
            self._click_button(attack_button, window_info)
            print("[BB_ATTACK] 直接点击attack按钮，转换到找对手状态")
            return GameState.FINDING_OPPONENT
        
        # 如果没有直接的attack按钮，通过find_now计算位置
        find_now_button = self.get_best_detection(detections, 'find_now')
        if find_now_button:
            # 计算attack按钮相对于find_now的位置（根据实际UI调整）
            attack_pos = self._calculate_attack_position(find_now_button)
            self._click_position(attack_pos, window_info)
            print("[BB_ATTACK] 通过find_now计算attack位置，转换到找对手状态")
            return GameState.FINDING_OPPONENT
            
        return None
        
    def _is_bb_army_ready(self, detections: List[Detection]) -> bool:
        """检查建筑工人基地军队是否准备就绪"""
        # 检查建筑工人基地特有的军队指示器
        bb_army_indicators = self.get_detections_by_class(detections, 'bb_army_ready')
        if bb_army_indicators:
            return True
            
        # 也可以检查通用的军队指示器
        army_indicators = self.get_detections_by_class(detections, 'army_full_indicator')
        return len(army_indicators) > 0
        
    def _calculate_attack_position(self, find_now_detection: Detection) -> tuple:
        """根据find_now按钮计算attack按钮位置"""
        # 这个偏移量需要根据实际的UI布局调整
        find_x, find_y = find_now_detection.center
        attack_x = find_x  # 通常在同一水平线
        attack_y = find_y - 50  # attack按钮通常在find_now上方
        return (attack_x, attack_y)
        
    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[BB_ATTACK] 点击坐标: ({abs_x}, {abs_y})")
        
    def _click_position(self, position: tuple, window_info: WindowInfo):
        """点击指定位置"""
        x, y = position
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[BB_ATTACK] 点击计算位置: ({abs_x}, {abs_y})")


def register_builder_base_features():
    """注册所有建筑工人基地功能"""
    print("[FEATURES] 注册建筑工人基地功能策略...")
    
    # 注册各种功能策略
    feature_registry.register(BBCollectResources())
    feature_registry.register(BBAutoAttack())
    feature_registry.register(BBUpgradeBuildings())
    
    # 设置默认执行顺序（收集资源优先，升级建筑其次，攻击最后）
    default_order = [
        FeatureType.BB_COLLECT_RESOURCES,
        FeatureType.BB_UPGRADE_BUILDINGS,
        FeatureType.BB_ATTACK
    ]
    feature_registry.set_execution_order(GameMode.BUILDER_BASE, default_order)
    
    print("[FEATURES] 建筑工人基地功能策略注册完成")