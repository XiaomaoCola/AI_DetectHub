# COC Auto Player 模块

from core import (
    COCGameController,
    Detection,
    WindowInfo,
    MultiConfigManager,
    UIElementMapper, 
    StateValidator
)
from states.GameState import GameState

__version__ = "1.0.0"
__all__ = [
    "COCGameController",
    "Detection",
    "WindowInfo",
    "MultiConfigManager",
    "UIElementMapper", 
    "StateValidator"
]