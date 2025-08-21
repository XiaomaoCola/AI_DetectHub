"""
游戏模式管理器
处理不同的游戏模式：Home Village vs Builder Base
"""

from enum import Enum
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from .state_machine import GameState, Detection, WindowInfo


class GameMode(Enum):
    """游戏模式枚举"""
    HOME_VILLAGE = "home_village"      # 主村庄模式
    BUILDER_BASE = "builder_base"      # 建筑工人基地模式
    AUTO_SWITCH = "auto_switch"        # 自动切换模式


class TaskType(Enum):
    """任务类型枚举"""
    COLLECT_RESOURCES = "collect_resources"    # 收集资源
    ATTACK_CYCLE = "attack_cycle"             # 攻击循环
    UPGRADE_BUILDINGS = "upgrade_buildings"    # 升级建筑
    TRAIN_TROOPS = "train_troops"             # 训练部队
    CUSTOM_TASK = "custom_task"               # 自定义任务


class GameModeManager:
    """游戏模式管理器"""
    
    def __init__(self):
        self.current_mode = GameMode.HOME_VILLAGE
        self.active_tasks = []
        self.mode_handlers = {}
        
    def set_mode(self, mode: GameMode):
        """设置当前游戏模式"""
        print(f"[MODE] 切换到模式: {mode.value}")
        self.current_mode = mode
        
    def add_task(self, task_type: TaskType, priority: int = 1, **kwargs):
        """添加任务到队列"""
        task = {
            'type': task_type,
            'priority': priority,
            'params': kwargs,
            'status': 'pending'
        }
        self.active_tasks.append(task)
        # 按优先级排序
        self.active_tasks.sort(key=lambda x: x['priority'], reverse=True)
        
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """获取当前任务"""
        for task in self.active_tasks:
            if task['status'] == 'pending':
                return task
        return None
        
    def complete_current_task(self):
        """完成当前任务"""
        current_task = self.get_current_task()
        if current_task:
            current_task['status'] = 'completed'
            print(f"[TASK] 完成任务: {current_task['type'].value}")
            
    def clear_completed_tasks(self):
        """清理已完成的任务"""
        self.active_tasks = [t for t in self.active_tasks if t['status'] != 'completed']


class ModeHandler(ABC):
    """模式处理器抽象基类"""
    
    def __init__(self, mode: GameMode):
        self.mode = mode
        self.task_handlers = {}
        
    @abstractmethod
    def can_handle_mode(self, detections: list) -> bool:
        """判断是否可以处理当前模式"""
        pass
        
    @abstractmethod
    def switch_to_mode(self, detections: list, window_info: WindowInfo) -> bool:
        """切换到此模式"""
        pass
        
    def execute_task(self, task: Dict[str, Any], detections: list, window_info: WindowInfo):
        """执行任务"""
        task_type = task['type']
        if task_type in self.task_handlers:
            return self.task_handlers[task_type](task, detections, window_info)
        else:
            print(f"[WARNING] 未找到任务处理器: {task_type.value}")
            return None


class HomeVillageHandler(ModeHandler):
    """主村庄模式处理器"""
    
    def __init__(self):
        super().__init__(GameMode.HOME_VILLAGE)
        self.task_handlers = {
            TaskType.COLLECT_RESOURCES: self.collect_resources,
            TaskType.ATTACK_CYCLE: self.attack_cycle,
            TaskType.TRAIN_TROOPS: self.train_troops
        }
        
    def can_handle_mode(self, detections: list) -> bool:
        """检测是否在主村庄"""
        # 主村庄特征：有shop按钮、没有clock tower等
        has_shop = any(d.class_name == "shop_button" for d in detections)
        has_clock_tower = any(d.class_name == "clock_tower" for d in detections)
        return has_shop and not has_clock_tower
        
    def switch_to_mode(self, detections: list, window_info: WindowInfo) -> bool:
        """切换到主村庄"""
        # 点击主村庄按钮或执行切换操作
        home_button = next((d for d in detections if d.class_name == "home_village_button"), None)
        if home_button:
            # 执行点击操作
            print("[MODE] 切换到主村庄")
            return True
        return False
        
    def collect_resources(self, task, detections, window_info):
        """收集资源任务"""
        print("[HOME_VILLAGE] 执行资源收集")
        # 查找金币收集器、圣水收集器等
        collectors = [d for d in detections if 'collector' in d.class_name.lower()]
        if collectors:
            # 点击收集器
            return GameState.VILLAGE  # 保持村庄状态
        return None
        
    def attack_cycle(self, task, detections, window_info):
        """攻击循环任务"""
        print("[HOME_VILLAGE] 开始攻击循环")
        attack_button = next((d for d in detections if d.class_name == "attack"), None)
        if attack_button:
            return GameState.FINDING_OPPONENT
        return None
        
    def train_troops(self, task, detections, window_info):
        """训练部队任务"""
        print("[HOME_VILLAGE] 训练部队")
        # 训练部队的逻辑
        return GameState.VILLAGE


class BuilderBaseHandler(ModeHandler):
    """建筑工人基地模式处理器"""
    
    def __init__(self):
        super().__init__(GameMode.BUILDER_BASE)
        self.task_handlers = {
            TaskType.COLLECT_RESOURCES: self.collect_resources,
            TaskType.ATTACK_CYCLE: self.attack_cycle,
            TaskType.UPGRADE_BUILDINGS: self.upgrade_buildings
        }
        
    def can_handle_mode(self, detections: list) -> bool:
        """检测是否在建筑工人基地"""
        # 建筑工人基地特征：有find_now按钮、clock tower等
        has_find_now = any(d.class_name == "find_now" for d in detections)
        has_clock_tower = any(d.class_name == "clock_tower" for d in detections)
        return has_find_now or has_clock_tower
        
    def switch_to_mode(self, detections: list, window_info: WindowInfo) -> bool:
        """切换到建筑工人基地"""
        builder_button = next((d for d in detections if d.class_name == "builder_base_button"), None)
        if builder_button:
            print("[MODE] 切换到建筑工人基地")
            return True
        return False
        
    def collect_resources(self, task, detections, window_info):
        """收集资源任务"""
        print("[BUILDER_BASE] 执行资源收集")
        # 查找建筑工人基地的收集器
        return GameState.VILLAGE
        
    def attack_cycle(self, task, detections, window_info):
        """夜世界攻击循环"""
        print("[BUILDER_BASE] 开始夜世界攻击")
        find_now_button = next((d for d in detections if d.class_name == "find_now"), None)
        attack_button = next((d for d in detections if d.class_name == "attack"), None)
        
        if find_now_button and attack_button:
            return GameState.FINDING_OPPONENT
        return None
        
    def upgrade_buildings(self, task, detections, window_info):
        """升级建筑任务"""
        print("[BUILDER_BASE] 升级建筑")
        return GameState.VILLAGE