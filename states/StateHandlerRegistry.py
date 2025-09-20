from typing import Dict, Optional, List

from states.GameState import GameState
from states.StateHandler import StateHandler


class StateHandlerRegistry:
    """状态处理器注册表 - 简化版"""

    def __init__(self):
        # 创建一个字典，key 是 GameState，value 是 StateHandler。
        # self._handlers = {}，
        self._handlers: Dict[GameState, StateHandler] = {}

    def register(self, handler: StateHandler):
        """注册状态处理器"""
        self._handlers[handler.state_type] = handler

    def get_handler(self, state: GameState) -> Optional[StateHandler]:
        """获取状态处理器"""
        return self._handlers.get(state)

    def get_all_states(self) -> List[GameState]:
        """获取所有注册的状态"""
        return list(self._handlers.keys())
