#!/usr/bin/env python3
"""
建筑工人基地自动战斗功能状态处理器模块
包含完整的战斗循环：村庄 -> 攻击 -> 战斗 -> 投降确认 -> 返回村庄
"""

from .state1_village import BBAutoAttackState_1_VillageHandler
from .state2_attack_menu import AttackMenuHandler  
from .state3_battle_scene import BattleSceneHandler
from .state4_surrender_confirm import SurrenderMenuHandler
from .state5_return_home import ReturnHomeHandler

__all__ = [
    'BBAutoAttackState_1_VillageHandler',
    'AttackMenuHandler',
    'BattleSceneHandler', 
    'SurrenderMenuHandler',
    'ReturnHomeHandler'
]