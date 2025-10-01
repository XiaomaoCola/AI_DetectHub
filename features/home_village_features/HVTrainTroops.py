from typing import List, Dict, Any, Optional

from features import FeatureHandler, FeatureType
from features.GameMode import GameMode
from states.GameState import GameState
from states.DataClasses import Detection, WindowInfo


class HVTrainTroops(FeatureHandler):
    """主村庄 - 训练部队功能策略"""

    def __init__(self):
        super().__init__(FeatureType.HV_TRAIN_TROOPS, GameMode.HOME_VILLAGE)
        self.description = "自动训练主村庄部队"
        self.cooldown_seconds = 20  # 训练部队冷却20秒

    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以训练部队"""
        if not self.is_enabled(config):
            return False

        if self.is_on_cooldown():
            return False

        # 检查是否有兵营按钮
        barracks_button = self.get_best_detection(detections, 'barracks_button')
        return barracks_button is not None

    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行训练部队"""
        print("[HV_TRAIN] 开始训练主村庄部队...")

        barracks_button = self.get_best_detection(detections, 'barracks_button')
        if barracks_button:
            self._click_button(barracks_button, window_info)
            print("[HV_TRAIN] 点击兵营按钮")
            return None

        return None

    def _click_button(self, detection: Detection, window_info: WindowInfo):
        """点击按钮"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_TRAIN] 点击坐标: ({abs_x}, {abs_y})")
