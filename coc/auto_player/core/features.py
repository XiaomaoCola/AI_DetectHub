#!/usr/bin/env python3
"""
功能策略模式实现
提供可扩展的功能管理系统
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
import time

from .state_machine import Detection, WindowInfo, GameState


class FeatureType(Enum):
    """功能类型枚举"""
    COLLECT_RESOURCES = "collect_resources"
    ATTACK = "attack" 
    CLAN_CAPITAL = "clan_capital"
    TRAIN_TROOPS = "train_troops"
    UPGRADE_BUILDINGS = "upgrade_buildings"


class FeatureStrategy(ABC):
    """功能策略抽象基类"""
    
    def __init__(self, feature_type: FeatureType):
        self.feature_type = feature_type
        self.name = feature_type.value
        self.description = ""
        self.last_execution_time = 0
        self.cooldown_seconds = 5  # 默认冷却时间5秒
        
    @abstractmethod
    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """
        判断是否可以执行此功能
        
        Args:
            detections: 当前检测结果
            config: 用户配置（包含功能开关状态）
            
        Returns:
            bool: 是否可以执行
        """
        pass
        
    @abstractmethod 
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行功能
        
        Args:
            detections: 当前检测结果
            window_info: 窗口信息
            
        Returns:
            Optional[GameState]: 执行后的目标状态，None表示保持当前状态
        """
        pass
        
    def is_enabled(self, config: Dict[str, Any]) -> bool:
        """检查功能是否启用"""
        return config.get(self.name, False)
        
    def is_on_cooldown(self) -> bool:
        """检查是否在冷却期"""
        return (time.time() - self.last_execution_time) < self.cooldown_seconds
        
    def update_execution_time(self):
        """更新最后执行时间"""
        self.last_execution_time = time.time()
        
    def get_detections_by_class(self, detections: List[Detection], class_name: str) -> List[Detection]:
        """根据类别名获取检测结果"""
        return [d for d in detections if d.class_name == class_name]
        
    def get_best_detection(self, detections: List[Detection], class_name: str) -> Optional[Detection]:
        """获取指定类别中置信度最高的检测结果"""
        candidates = self.get_detections_by_class(detections, class_name)
        return max(candidates, key=lambda x: x.confidence) if candidates else None


class FeatureRegistry:
    """功能策略注册表"""
    
    def __init__(self):
        self._strategies: Dict[FeatureType, FeatureStrategy] = {}
        self._execution_order: List[FeatureType] = []
        
    def register(self, strategy: FeatureStrategy):
        """注册功能策略"""
        self._strategies[strategy.feature_type] = strategy
        if strategy.feature_type not in self._execution_order:
            self._execution_order.append(strategy.feature_type)
        print(f"[FEATURES] 注册功能策略: {strategy.name}")
        
    def unregister(self, feature_type: FeatureType):
        """注销功能策略"""
        if feature_type in self._strategies:
            del self._strategies[feature_type]
            self._execution_order.remove(feature_type)
            print(f"[FEATURES] 注销功能策略: {feature_type.value}")
            
    def get_strategy(self, feature_type: FeatureType) -> Optional[FeatureStrategy]:
        """获取功能策略"""
        return self._strategies.get(feature_type)
        
    def get_all_strategies(self) -> List[FeatureStrategy]:
        """获取所有注册的策略"""
        return list(self._strategies.values())
        
    def execute_features(self, 
                        detections: List[Detection], 
                        window_info: WindowInfo,
                        config: Dict[str, Any]) -> Optional[GameState]:
        """
        按顺序执行启用的功能
        
        Args:
            detections: 检测结果
            window_info: 窗口信息  
            config: 用户配置
            
        Returns:
            Optional[GameState]: 第一个执行成功的功能返回的状态
        """
        executed_count = 0
        
        for feature_type in self._execution_order:
            strategy = self._strategies.get(feature_type)
            if not strategy:
                continue
                
            # 检查功能是否启用
            if not strategy.is_enabled(config):
                continue
                
            # 检查冷却期
            if strategy.is_on_cooldown():
                continue
                
            # 检查执行条件
            if not strategy.can_execute(detections, config):
                continue
                
            # 执行功能
            print(f"[FEATURES] 执行功能: {strategy.name} - {strategy.description}")
            try:
                result = strategy.execute(detections, window_info)
                strategy.update_execution_time()
                executed_count += 1
                
                # 如果功能返回了状态转换，立即返回
                if result:
                    print(f"[FEATURES] 功能 {strategy.name} 触发状态转换: {result.value}")
                    return result
                    
            except Exception as e:
                print(f"[FEATURES] 功能 {strategy.name} 执行失败: {e}")
                continue
        
        if executed_count == 0:
            print("[FEATURES] 没有可执行的功能")
        else:
            print(f"[FEATURES] 执行了 {executed_count} 个功能")
            
        return None
        
    def set_execution_order(self, order: List[FeatureType]):
        """设置功能执行顺序"""
        # 只保留已注册的功能
        self._execution_order = [ft for ft in order if ft in self._strategies]
        print(f"[FEATURES] 更新执行顺序: {[ft.value for ft in self._execution_order]}")
        
    def get_execution_order(self) -> List[FeatureType]:
        """获取当前执行顺序"""
        return self._execution_order.copy()
        
    def get_available_features(self) -> List[Dict[str, str]]:
        """获取可用功能列表（用于GUI）"""
        features = []
        for strategy in self._strategies.values():
            features.append({
                'type': strategy.feature_type.value,
                'name': strategy.name,
                'description': strategy.description
            })
        return features


# 全局功能注册表实例
feature_registry = FeatureRegistry()