"""
任务调度系统
管理复杂的游戏任务序列和条件判断
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import time

from .state_machine import Detection, WindowInfo, GameState


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 等待执行
    RUNNING = "running"        # 正在执行  
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 执行失败
    PAUSED = "paused"          # 暂停
    CANCELLED = "cancelled"    # 已取消


class TaskCondition(ABC):
    """任务条件抽象基类"""
    
    @abstractmethod
    def check(self, detections: List[Detection], window_info: WindowInfo) -> bool:
        """检查条件是否满足"""
        pass


class DetectionCondition(TaskCondition):
    """基于检测结果的条件"""
    
    def __init__(self, class_name: str, min_confidence: float = 0.5, required: bool = True):
        self.class_name = class_name
        self.min_confidence = min_confidence
        self.required = required
        
    def check(self, detections: List[Detection], window_info: WindowInfo) -> bool:
        found = any(d.class_name == self.class_name and d.confidence >= self.min_confidence 
                   for d in detections)
        return found if self.required else not found


class TimeCondition(TaskCondition):
    """基于时间的条件"""
    
    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.start_time = None
        
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        
    def check(self, detections: List[Detection], window_info: WindowInfo) -> bool:
        if self.start_time is None:
            self.start()
        return time.time() - self.start_time >= self.delay_seconds


class Task(ABC):
    """任务抽象基类"""
    
    def __init__(self, name: str, priority: int = 1):
        self.name = name
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.prerequisites: List[TaskCondition] = []
        self.completion_conditions: List[TaskCondition] = []
        
    def add_prerequisite(self, condition: TaskCondition):
        """添加前置条件"""
        self.prerequisites.append(condition)
        
    def add_completion_condition(self, condition: TaskCondition):
        """添加完成条件"""
        self.completion_conditions.append(condition)
        
    def can_start(self, detections: List[Detection], window_info: WindowInfo) -> bool:
        """检查是否可以开始执行"""
        return all(cond.check(detections, window_info) for cond in self.prerequisites)
        
    def is_completed(self, detections: List[Detection], window_info: WindowInfo) -> bool:
        """检查是否已完成"""
        if not self.completion_conditions:
            return self.status == TaskStatus.COMPLETED
        return all(cond.check(detections, window_info) for cond in self.completion_conditions)
        
    @abstractmethod
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行任务"""
        pass
        
    def start(self):
        """开始执行任务"""
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        
    def complete(self):
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.end_time = time.time()
        
    def fail(self, error_message: str = None):
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.end_time = time.time()
        self.error_message = error_message


class CollectResourcesTask(Task):
    """收集资源任务"""
    
    def __init__(self):
        super().__init__("收集资源", priority=3)
        self.collected_count = 0
        self.max_collections = 5
        
        # 添加完成条件：收集足够数量或没有更多收集器
        self.add_completion_condition(
            DetectionCondition("collector", required=False)  # 没有收集器时完成
        )
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        # 查找可收集的资源
        collectors = [d for d in detections if 'collector' in d.class_name.lower()]
        
        if collectors and self.collected_count < self.max_collections:
            # 点击第一个收集器
            collector = collectors[0]
            # 这里添加点击逻辑
            print(f"[COLLECT] 收集资源 {collector.class_name}")
            self.collected_count += 1
            return GameState.VILLAGE
            
        elif self.collected_count >= self.max_collections:
            self.complete()
            print(f"[COLLECT] 收集完成，共收集 {self.collected_count} 个")
            
        return GameState.VILLAGE


class AttackCycleTask(Task):
    """攻击循环任务"""
    
    def __init__(self, max_attacks: int = 3):
        super().__init__("攻击循环", priority=5)
        self.max_attacks = max_attacks
        self.current_attacks = 0
        self.attack_phase = "start"  # start, finding, attacking, surrendering, returning
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        if self.attack_phase == "start":
            # 查找attack按钮
            attack_btn = next((d for d in detections if d.class_name == "attack"), None)
            if attack_btn:
                print("[ATTACK] 开始攻击循环")
                self.attack_phase = "finding"
                return GameState.FINDING_OPPONENT
                
        elif self.attack_phase == "finding":
            # 等待找到对手
            if any(d.class_name == "surrender_button" for d in detections):
                self.attack_phase = "attacking"
                return GameState.ATTACKING
                
        elif self.attack_phase == "attacking":
            # 攻击阶段，等待投降
            time.sleep(10)  # 简单等待
            self.attack_phase = "surrendering"
            return GameState.SURRENDERING
            
        elif self.attack_phase == "surrendering":
            # 投降后等待返回
            self.attack_phase = "returning"
            return GameState.RETURNING
            
        elif self.attack_phase == "returning":
            # 返回村庄，开始下一轮
            self.current_attacks += 1
            if self.current_attacks >= self.max_attacks:
                self.complete()
                print(f"[ATTACK] 攻击循环完成，共 {self.current_attacks} 次")
            else:
                self.attack_phase = "start"
            return GameState.VILLAGE
            
        return None


class UpgradeBuildingsTask(Task):
    """升级建筑任务"""
    
    def __init__(self, building_types: List[str] = None):
        super().__init__("升级建筑", priority=2)
        self.building_types = building_types or ["cannon", "archer_tower", "mortar"]
        self.upgraded_count = 0
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        # 查找可升级的建筑
        for building_type in self.building_types:
            buildings = [d for d in detections if building_type in d.class_name.lower()]
            if buildings:
                print(f"[UPGRADE] 升级 {building_type}")
                self.upgraded_count += 1
                # 这里添加升级逻辑
                break
        else:
            self.complete()
            print(f"[UPGRADE] 建筑升级完成，共升级 {self.upgraded_count} 个")
            
        return GameState.VILLAGE


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.current_task: Optional[Task] = None
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
    def add_task(self, task: Task):
        """添加任务"""
        self.tasks.append(task)
        # 按优先级排序
        self.tasks.sort(key=lambda t: t.priority, reverse=True)
        print(f"[SCHEDULER] 添加任务: {task.name} (优先级: {task.priority})")
        
    def remove_task(self, task: Task):
        """移除任务"""
        if task in self.tasks:
            self.tasks.remove(task)
            print(f"[SCHEDULER] 移除任务: {task.name}")
            
    def get_next_task(self, detections: List[Detection], window_info: WindowInfo) -> Optional[Task]:
        """获取下一个可执行的任务"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING and task.can_start(detections, window_info):
                return task
        return None
        
    def execute_current_task(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """执行当前任务"""
        if self.current_task is None:
            # 获取新任务
            self.current_task = self.get_next_task(detections, window_info)
            if self.current_task:
                self.current_task.start()
                print(f"[SCHEDULER] 开始执行任务: {self.current_task.name}")
            else:
                return None
                
        # 检查当前任务是否完成
        if self.current_task.is_completed(detections, window_info):
            self.current_task.complete()
            self.completed_tasks.append(self.current_task)
            self.tasks.remove(self.current_task)
            print(f"[SCHEDULER] 任务完成: {self.current_task.name}")
            self.current_task = None
            return self.execute_current_task(detections, window_info)
            
        # 执行当前任务
        try:
            return self.current_task.execute(detections, window_info)
        except Exception as e:
            print(f"[SCHEDULER] 任务执行失败: {self.current_task.name} - {e}")
            self.current_task.fail(str(e))
            self.failed_tasks.append(self.current_task)
            self.tasks.remove(self.current_task)
            self.current_task = None
            return None
            
    def get_status_summary(self) -> Dict[str, int]:
        """获取任务状态摘要"""
        return {
            "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "running": len([t for t in self.tasks if t.status == TaskStatus.RUNNING]),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks)
        }
        
    def clear_completed_tasks(self):
        """清空已完成的任务"""
        self.completed_tasks.clear()
        
    def clear_all_tasks(self):
        """清空所有任务"""
        self.tasks.clear()
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.current_task = None