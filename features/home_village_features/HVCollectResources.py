import time
from typing import List, Dict, Any, Optional

from features import FeatureHandler, FeatureType
from features.GameMode import GameMode
from states.GameState import GameState
from states.state_machine import Detection, WindowInfo


class HVCollectResources(FeatureHandler):
    """主村庄 - 收集资源功能策略"""

    def __init__(self):
        super().__init__(FeatureType.HV_COLLECT_RESOURCES, GameMode.HOME_VILLAGE)
        self.description = "自动收集主村庄中的资源（金币、圣水、暗黑重油）"
        self.cooldown_seconds = 10  # 收集资源冷却10秒

    def can_execute(self, detections: List[Detection], config: Dict[str, Any]) -> bool:
        """检查是否可以收集资源"""
        if not self.is_enabled(config):
            return False

        if self.is_on_cooldown():
            return False

        # 检查是否有可收集的资源
        collectible_resources = ['gold_collector', 'elixir_collector', 'dark_elixir_collector']
        for resource_type in collectible_resources:
            if self.get_detections_by_class(detections, resource_type):
                return True

        return False

    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行收集资源"""
        print("[HV_COLLECT] 开始收集主村庄资源...")

        # 收集各种资源
        resources_collected = 0
        collectible_resources = [
            ('gold_collector', '金币收集器'),
            ('elixir_collector', '圣水收集器'),
            ('dark_elixir_collector', '暗黑重油收集器')
        ]

        for resource_class, resource_name in collectible_resources:
            resource_detections = self.get_detections_by_class(detections, resource_class)
            for detection in resource_detections:
                self._click_resource(detection, window_info)
                resources_collected += 1
                print(f"[HV_COLLECT] 收集 {resource_name}")
                time.sleep(0.5)  # 短暂等待避免点击过快

        if resources_collected > 0:
            print(f"[HV_COLLECT] 完成，共收集 {resources_collected} 个资源")
        else:
            print("[HV_COLLECT] 没有找到可收集的资源")

        return None  # 保持当前状态

    def _click_resource(self, detection: Detection, window_info: WindowInfo):
        """点击资源收集器"""
        x, y = detection.center
        abs_x = window_info.left + x
        abs_y = window_info.top + y
        print(f"[HV_COLLECT] 点击坐标: ({abs_x}, {abs_y})")
