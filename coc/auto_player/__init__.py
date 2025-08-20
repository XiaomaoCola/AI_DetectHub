# COC Auto Player 模块

from .game_controller import COCGameController
from .base_state import GameState, Detection, WindowInfo
from .ui_mapper import MultiConfigManager, UIElementMapper, StateValidator

__version__ = "1.0.0"
__all__ = [
    "COCGameController",
    "GameState", 
    "Detection",
    "WindowInfo",
    "MultiConfigManager",
    "UIElementMapper", 
    "StateValidator"
]