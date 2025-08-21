# Core模块

from .controller import COCGameController
from .state_machine import GameState, Detection, WindowInfo, StateHandler, StateHandlerRegistry
from .ui_manager import MultiConfigManager, UIElementMapper, StateValidator
from .game_modes import GameMode, GameModeManager
# TaskScheduler 相关导入已删除 - 简化为 Mode → State 架构

__version__ = "1.0.0"
__all__ = [
    "COCGameController",
    "GameState",
    "Detection", 
    "WindowInfo",
    "StateHandler",
    "StateHandlerRegistry",
    "MultiConfigManager",
    "UIElementMapper",
    "StateValidator",
    "GameMode",
    "GameModeManager"
]