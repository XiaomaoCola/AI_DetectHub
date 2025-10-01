# Core模块

from .controller import COCGameController
from states.state_machine import Detection, WindowInfo
from states.StateHandlerRegistry import StateHandlerRegistry
from states.StateHandler import StateHandler
from states.GameState import GameState
from .ui_manager import MultiConfigManager, UIElementMapper, StateValidator
from .mode_manager import mode_manager
from coc.auto_player.features.GameMode import GameMode

# TaskScheduler 相关导入已删除 - 简化为 Mode → State 架构

__version__ = "1.0.0"
__all__ = [
    "COCGameController",
    "Detection",
    "WindowInfo",
    "MultiConfigManager",
    "UIElementMapper",
    "StateValidator",
    "mode_manager"
]