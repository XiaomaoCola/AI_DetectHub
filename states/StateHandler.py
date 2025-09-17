from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from states.GameState import GameState
from states.state_machine import StateTask, Detection, WindowInfo


class StateHandler(ABC):
    """状态处理器抽象基类"""

    def __init__(self, state_type: GameState):
        self.state_type = state_type
        self.max_duration = 60  # 状态最大持续时间
        self.retry_count = 0
        self.max_retries = 3
        self.tasks: List[StateTask] = []  # 状态任务列表

    @abstractmethod
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断当前检测结果是否属于这个状态

        Args:
            detections: 检测结果列表

        Returns:
            bool: 是否可以处理当前状态
        """
        pass

    def add_task(self, task: StateTask):
        """添加状态任务"""
        self.tasks.append(task)
        # 按优先级排序
        self.tasks.sort(key=lambda x: x.priority, reverse=True)

    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行当前状态的操作 - 检查所有任务并执行第一个满足条件的

        Args:
            detections: 检测结果列表
            window_info: 窗口信息

        Returns:
            Optional[GameState]: 下一个状态，None表示保持当前状态
        """
        print(f"[{self.state_type.value.upper()}] 检查 {len(self.tasks)} 个可用任务...")

        # 按优先级顺序检查每个任务
        for task in self.tasks:
            if task.condition(detections):
                print(f"[{self.state_type.value.upper()}] 执行任务: {task.name} - {task.description}")
                next_state = task.action(detections, window_info)
                if next_state:
                    print(f"[{self.state_type.value.upper()}] 任务完成，转换到状态: {next_state.value}")
                return next_state

        print(f"[{self.state_type.value.upper()}] 没有满足条件的任务，保持当前状态")
        return None

    def get_detections_by_class(self, detections: List[Detection], class_name: str) -> List[Detection]:
        """根据类别名获取检测结果"""
        return [d for d in detections if d.class_name == class_name]

    def get_best_detection(self, detections: List[Detection], class_name: str) -> Optional[Detection]:
        """获取指定类别中置信度最高的检测结果"""
        candidates = self.get_detections_by_class(detections, class_name)
        return max(candidates, key=lambda x: x.confidence) if candidates else None

    def calculate_relative_position(self,
                                  base_detection: Detection,
                                  offset: Tuple[int, int]) -> Tuple[int, int]:
        """根据基准检测结果计算相对位置"""
        base_x, base_y = base_detection.center
        offset_x, offset_y = offset
        return (base_x + offset_x, base_y + offset_y)

    def is_timeout(self, start_time: float, current_time: float) -> bool:
        """检查是否超时"""
        return (current_time - start_time) > self.max_duration

    def reset_retry_count(self):
        """重置重试计数"""
        self.retry_count = 0

    def increment_retry_count(self) -> bool:
        """增加重试计数，返回是否超过最大重试次数"""
        self.retry_count += 1
        return self.retry_count >= self.max_retries
