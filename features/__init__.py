#!/usr/bin/env python3
"""
功能策略模块
提供可扩展的游戏功能管理系统
"""

from .base import FeatureStrategy
from .FeatureRegistry import FeatureRegistry
from .FeatureType import FeatureType
from features.home_village_features.home_village_features import register_home_village_features
from features.builder_base_features.builder_base_features import register_builder_base_features

# 导出主要类和函数
__all__ = [
    'FeatureStrategy',
    'FeatureType', 
    'FeatureRegistry',
    'register_home_village_features',
    'register_builder_base_features'
]