from typing import List, Dict, Any, Optional

from features import FeatureHandler, FeatureType
from features.GameMode import GameMode
from states.GameState import GameState
from states.state_machine import Detection, WindowInfo


class HVUpgradeBuildings(FeatureHandler):
    """主村庄 - 升级建筑功能策略"""

    def __init__(self):
        super().__init__(FeatureType.HV_UPGRADE_BUILDINGS, GameMode.HOME_VILLAGE)
        self.description = "自动升级主村庄建筑"
        self.cooldown_seconds = 30  # 升级建筑冷却30秒

    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以升级建筑"""
        if not self.is_enabled(config):
            return False

        if self.is_on_cooldown():
            return False

        # 检查是否有可升级的建筑
        upgrade_indicators = self.get_detections_by_class(detections, 'upgrade_available')
        return len(upgrade_indicators) > 0

    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行升级建筑"""
        print("[HV_UPGRADE] 开始升级主村庄建筑...")

        upgrade_indicators = self.get_detections_by_class(detections, 'upgrade_available')
        if upgrade_indicators:
            # 选择第一个可升级的建筑
            first_upgrade = upgrade_indicators[0]
            self._click_button(first_upgrade, window_info)
            print("[HV_UPGRADE] 点击升级按钮")
            return None

        return None

    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_UPGRADE] 点击坐标: ({abs_x}, {abs_y})")
