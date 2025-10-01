# Core模块

from .controller import COCGameController
from states.DataClasses import Detection, WindowInfo
from .ui_manager import MultiConfigManager, UIElementMapper, StateValidator
from .mode_manager import mode_manager

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