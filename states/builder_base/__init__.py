#!/usr/bin/env python3
"""
建筑工人基地(Builder Base)状态处理器模块
"""

from .village import BuilderBaseVillageHandler
from .finding_opponent import BuilderBaseFindingOpponentHandler
from .versus_battle import BuilderBaseVersusBattleHandler

# 自动战斗功能状态处理器
from .BBAutoAttack import (
    BBAutoAttackState_1_VillageHandler,
    AttackMenuHandler,
    BattleSceneHandler,
    SurrenderMenuHandler,
    ReturnHomeHandler
)

__all__ = [
    # 基础状态处理器
    'BuilderBaseVillageHandler',
    'BuilderBaseFindingOpponentHandler', 
    'BuilderBaseVersusBattleHandler',
    # 自动战斗功能状态处理器
    'BBAutoAttackState_1_VillageHandler',
    'AttackMenuHandler',
    'BattleSceneHandler',
    'SurrenderMenuHandler',
    'ReturnHomeHandler'
]