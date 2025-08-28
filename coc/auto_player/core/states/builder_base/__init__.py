#!/usr/bin/env python3
"""
建筑工人基地(Builder Base)状态处理器模块
"""

from .village import BuilderBaseVillageHandler
from .finding_opponent import BuilderBaseFindingOpponentHandler
from .versus_battle import BuilderBaseVersusBattleHandler

# 自动战斗功能状态处理器
from .auto_battle import (
    AutoBattleVillageHandler,
    AttackMenuHandler,
    BattleSceneHandler,
    SurrenderMenuHandler,
    ConfirmOkayHandler,
    ReturnHomeHandler
)

__all__ = [
    # 基础状态处理器
    'BuilderBaseVillageHandler',
    'BuilderBaseFindingOpponentHandler', 
    'BuilderBaseVersusBattleHandler',
    # 自动战斗功能状态处理器
    'AutoBattleVillageHandler',
    'AttackMenuHandler',
    'BattleSceneHandler',
    'SurrenderMenuHandler',
    'ConfirmOkayHandler',
    'ReturnHomeHandler'
]