# States模块 - 按游戏模式分离的状态处理器

# 主村庄(Home Village)状态处理器
from .home_village import HomeVillageHandler
from .home_village.finding_opponent import HomeVillageFindingOpponentHandler
from .home_village.attacking import HomeVillageAttackingHandler

# 建筑工人基地(Builder Base)状态处理器
from .builder_base import (
    BuilderBaseVillageHandler,
    BuilderBaseFindingOpponentHandler,
    BuilderBaseVersusBattleHandler,
    # 自动战斗功能状态处理器
    BBAutoAttackState1VillageHandler,
    AttackMenuHandler,
    BattleSceneHandler,
    SurrenderMenuHandler,
    ReturnHomeHandler
)

__all__ = [
    # 主村庄状态处理器
    "HomeVillageHandler",
    "HomeVillageFindingOpponentHandler", 
    "HomeVillageAttackingHandler",
    # 建筑工人基地基础状态处理器
    "BuilderBaseVillageHandler",
    "BuilderBaseFindingOpponentHandler",
    "BuilderBaseVersusBattleHandler",
    # 建筑工人基地自动战斗功能状态处理器
    "BBAutoAttackState1VillageHandler",
    "AttackMenuHandler",
    "BattleSceneHandler",
    "SurrenderMenuHandler",
    "ReturnHomeHandler"
]