from enum import Enum


class GameState(Enum):
    """游戏状态枚举"""
    # 基础状态，即home_village的状态
    VILLAGE = "village"
    FINDING_OPPONENT = "finding_opponent"
    ATTACKING = "attacking"
    SURRENDERING = "surrendering"
    CONFIRMING = "confirming"
    RETURNING = "returning"
    ERROR = "error"

    # 建筑工人基地自动战斗功能状态
    BBAutoAttack_State_1_Village = "builder_base_auto_attack_stage_1_village"   # State 1: 夜世界村庄界面
    BBAutoAttack_State_2_Attack_Menu = "builder_base_auto_attack_stage_2_attack_menu"      # State 2: 攻击菜单(Find Now)
    AUTO_BATTLE_BATTLE_SCENE = "auto_battle_battle_scene"    # State 3: 战斗场景
    AUTO_BATTLE_SURRENDER = "auto_battle_surrender_menu"  # State 4: 投降菜单
    AUTO_BATTLE_CONFIRM_OKAY = "auto_battle_confirm_okay"    # State 5: 确认Okay
    AUTO_BATTLE_RETURN_HOME = "auto_battle_return_home"      # State 6: 返回主页
