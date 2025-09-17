from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass

from states.GameState import GameState


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


@dataclass
class StateTask:
    """状态任务数据类"""
    name: str
    description: str
    condition: Callable[[List[Detection]], bool]  # 执行条件检查函数
    action: Callable[[List[Detection], WindowInfo], Optional[GameState]]  # 执行函数
    priority: int = 0  # 优先级，数字越高优先级越高


