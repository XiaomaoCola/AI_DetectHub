from typing import Dict, Optional, List

from states.GameState import GameState
from states.StateHandler import StateHandler
from states.state_machine import Detection


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
