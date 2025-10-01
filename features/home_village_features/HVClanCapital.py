from typing import List, Dict, Any, Optional

from features import FeatureHandler, FeatureType
from features.GameMode import GameMode
from states.GameState import GameState
from states.DataClasses import Detection, WindowInfo


class HVClanCapital(FeatureHandler):
    """主村庄 - 部落都城功能策略"""

    def __init__(self):
        super().__init__(FeatureType.HV_CLAN_CAPITAL, GameMode.HOME_VILLAGE)
        self.description = "自动进入部落都城进行相关操作"
        self.cooldown_seconds = 30  # 部落都城冷却30秒

    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以进入部落都城"""
        if not self.is_enabled(config):
            return False

        if self.is_on_cooldown():
            return False

        # 检查是否有部落都城按钮
        clan_capital_button = self.get_best_detection(detections, 'clan_capital_button')
        return clan_capital_button is not None

    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行部落都城操作"""
        print("[HV_CLAN_CAPITAL] 进入部落都城...")

        clan_capital_button = self.get_best_detection(detections, 'clan_capital_button')
        if clan_capital_button:
            self._click_button(clan_capital_button, window_info)
            print("[HV_CLAN_CAPITAL] 点击部落都城按钮")
            return None

        return None

    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_CLAN_CAPITAL] 点击坐标: ({abs_x}, {abs_y})")
