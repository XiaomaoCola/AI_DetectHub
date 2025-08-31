#!/usr/bin/env python3
"""
建筑工人基地自动战斗功能状态处理器模块
包含完整的战斗循环：村庄 -> 攻击 -> 匹配 -> 战斗 -> 投降 -> 确认 -> 返回
"""

from .state1_village import AutoBattleVillageHandler
from .state2_attack_menu import AttackMenuHandler  
from .state3_battle_scene import BattleSceneHandler
from .state4_surrender import SurrenderMenuHandler
from .state5_confirm_okay import ConfirmOkayHandler
from .state6_return_home import ReturnHomeHandler

__all__ = [
    'AutoBattleVillageHandler',
    'AttackMenuHandler',
    'BattleSceneHandler', 
    'SurrenderMenuHandler',
    'ConfirmOkayHandler',
    'ReturnHomeHandler'
]