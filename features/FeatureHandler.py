#!/usr/bin/env python3
"""
功能策略基础模块
定义功能策略的基类和注册表
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import time

from features import FeatureType, FeatureRegistry
from features.GameMode import GameMode
from core import Detection, WindowInfo
from states.GameState import GameState


class FeatureHandler(ABC):
    """功能策略抽象基类"""
    
    def __init__(self, feature_type: FeatureType, game_mode: GameMode):
        self.feature_type = feature_type
        self.game_mode = game_mode
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


# 全局功能注册表实例
feature_registry = FeatureRegistry()