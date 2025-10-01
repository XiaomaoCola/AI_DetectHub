from typing import List, Dict, Any, Optional

from features import FeatureHandler, FeatureType
from features.GameMode import GameMode
from states.GameState import GameState
from states.state_machine import Detection, WindowInfo


class BBUpgradeBuildings(FeatureHandler):
    """建筑工人基地 - 升级建筑功能策略"""

    def __init__(self):
        super().__init__(FeatureType.BB_UPGRADE_BUILDINGS, GameMode.BUILDER_BASE)
        self.description = "自动升级建筑工人基地建筑"
        self.cooldown_seconds = 30  # 升级建筑冷却30秒

    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以升级建筑"""
        if not self.is_enabled(config):
            return False

        if self.is_on_cooldown():
            return False

        # 检查是否有可升级的建筑
        upgrade_indicators = self.get_detections_by_class(detections, 'bb_upgrade_available')
        if upgrade_indicators:
            return True

        # 也检查通用的升级指示器
        generic_upgrade = self.get_detections_by_class(detections, 'upgrade_available')
        return len(generic_upgrade) > 0

    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行升级建筑"""
        print("[BB_UPGRADE] 开始升级建筑工人基地建筑...")

        # 优先查找建筑工人基地专用的升级指示器
        bb_upgrade_indicators = self.get_detections_by_class(detections, 'bb_upgrade_available')
        if bb_upgrade_indicators:
            first_upgrade = bb_upgrade_indicators[0]
            self._click_button(first_upgrade, window_info)
            print("[BB_UPGRADE] 点击建筑工人基地升级按钮")
            return None

        # 如果没有专用指示器，使用通用的
        generic_upgrade = self.get_detections_by_class(detections, 'upgrade_available')
        if generic_upgrade:
            first_upgrade = generic_upgrade[0]
            self._click_button(first_upgrade, window_info)
            print("[BB_UPGRADE] 点击通用升级按钮")
            return None

        return None

    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[BB_UPGRADE] 点击坐标: ({abs_x}, {abs_y})")
