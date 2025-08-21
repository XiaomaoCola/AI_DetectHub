from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class GameState(Enum):
    """游戏状态枚举"""
    VILLAGE = "village"
    FINDING_OPPONENT = "finding_opponent"
    ATTACKING = "attacking" 
    SURRENDERING = "surrendering"
    CONFIRMING = "confirming"
    RETURNING = "returning"
    ERROR = "error"


@dataclass
class Detection:
    """检测结果数据类"""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    class_name: str
    confidence: float
    center: Tuple[int, int] = None
    
    def __post_init__(self):
        if self.center is None:
            x1, y1, x2, y2 = self.bbox
            self.center = ((x1 + x2) // 2, (y1 + y2) // 2)


@dataclass 
class WindowInfo:
    """窗口信息数据类"""
    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int


class StateHandler(ABC):
    """状态处理器抽象基类"""
    
    def __init__(self, state_type: GameState):
        self.state_type = state_type
        self.max_duration = 60  # 状态最大持续时间
        self.retry_count = 0
        self.max_retries = 3
        
    @abstractmethod
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断当前检测结果是否属于这个状态
        
        Args:
            detections: 检测结果列表
            
        Returns:
            bool: 是否可以处理当前状态
        """
        pass
    
    @abstractmethod
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行当前状态的操作
        
        Args:
            detections: 检测结果列表
            window_info: 窗口信息
            
        Returns:
            Optional[GameState]: 下一个状态，None表示保持当前状态
        """
        pass
    
    def get_detections_by_class(self, detections: List[Detection], class_name: str) -> List[Detection]:
        """根据类别名获取检测结果"""
        return [d for d in detections if d.class_name == class_name]
    
    def get_best_detection(self, detections: List[Detection], class_name: str) -> Optional[Detection]:
        """获取指定类别中置信度最高的检测结果"""
        candidates = self.get_detections_by_class(detections, class_name)
        return max(candidates, key=lambda x: x.confidence) if candidates else None
    
    def calculate_relative_position(self, 
                                  base_detection: Detection, 
                                  offset: Tuple[int, int]) -> Tuple[int, int]:
        """根据基准检测结果计算相对位置"""
        base_x, base_y = base_detection.center
        offset_x, offset_y = offset
        return (base_x + offset_x, base_y + offset_y)
    
    def is_timeout(self, start_time: float, current_time: float) -> bool:
        """检查是否超时"""
        return (current_time - start_time) > self.max_duration
        
    def reset_retry_count(self):
        """重置重试计数"""
        self.retry_count = 0
        
    def increment_retry_count(self) -> bool:
        """增加重试计数，返回是否超过最大重试次数"""
        self.retry_count += 1
        return self.retry_count >= self.max_retries


class StateHandlerRegistry:
    """状态处理器注册表"""
    
    def __init__(self):
        self._handlers: Dict[GameState, StateHandler] = {}
        
    def register(self, handler: StateHandler):
        """注册状态处理器"""
        self._handlers[handler.state_type] = handler
        
    def get_handler(self, state: GameState) -> Optional[StateHandler]:
        """获取状态处理器"""
        return self._handlers.get(state)
        
    def find_current_state(self, detections: List[Detection]) -> Optional[GameState]:
        """根据检测结果找到当前状态"""
        for state, handler in self._handlers.items():
            if handler.can_handle(detections):
                return state
        return None
        
    def get_all_states(self) -> List[GameState]:
        """获取所有注册的状态"""
        return list(self._handlers.keys())