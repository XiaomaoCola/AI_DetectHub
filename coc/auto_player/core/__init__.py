# Core模块

from .controller import COCGameController
from .state_machine import GameState, Detection, WindowInfo, StateHandler, StateHandlerRegistry
from .ui_manager import MultiConfigManager, UIElementMapper, StateValidator
from .game_modes import GameMode, TaskType, GameModeManager
from .task_scheduler import TaskScheduler, Task, CollectResourcesTask, AttackCycleTask, UpgradeBuildingsTask

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
    "TaskType", 
    "GameModeManager",
    "TaskScheduler",
    "Task",
    "CollectResourcesTask",
    "AttackCycleTask", 
    "UpgradeBuildingsTask"
]