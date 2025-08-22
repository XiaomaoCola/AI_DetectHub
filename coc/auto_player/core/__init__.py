# Core模块

from .controller import COCGameController
from .state_machine import GameState, Detection, WindowInfo, StateHandler, StateHandlerRegistry
from .ui_manager import MultiConfigManager, UIElementMapper, StateValidator
from .mode_manager import mode_manager
from ..features.base import GameMode
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
    "mode_manager"
]