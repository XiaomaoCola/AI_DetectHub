from enum import Enum


class FeatureType(Enum):
    """功能类型枚举"""
    # Home Village 功能
    HV_COLLECT_RESOURCES = "hv_collect_resources"
    HV_ATTACK = "hv_attack"
    HV_CLAN_CAPITAL = "hv_clan_capital"
    HV_TRAIN_TROOPS = "hv_train_troops"
    HV_UPGRADE_BUILDINGS = "hv_upgrade_buildings"

    # Builder Base 功能
    BB_COLLECT_RESOURCES = "bb_collect_resources"
    BB_ATTACK = "bb_attack"
    BB_UPGRADE_BUILDINGS = "bb_upgrade_buildings"
