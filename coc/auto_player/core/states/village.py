import time
import pyautogui
from typing import List, Optional

from ..state_machine import StateHandler, GameState, Detection, WindowInfo, StateTask


class VillageHandler(StateHandler):
    """村庄状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.VILLAGE)
        
        # 村庄状态的特征标识
        self.required_indicators = ["find_now"]  # Builder Base特有的find_now按钮
        self.optional_indicators = ["attack"]    # 可能存在的attack按钮
        
        # 相对位置配置
        self.attack_offset_from_find_now = (0, -50)  # attack按钮相对于find_now的位置
        
        # 初始化任务
        self._setup_tasks()
        
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为村庄状态
        村庄状态特征：有find_now按钮（Builder Base独有）
        """
        find_now_detections = self.get_detections_by_class(detections, "find_now")
        return len(find_now_detections) > 0
    
    def _setup_tasks(self):
        """设置村庄状态的任务"""
        
        # 任务1: 开始攻击 (优先级最高)
        start_attack_task = StateTask(
            name="start_attack",
            description="点击attack按钮开始攻击循环",
            condition=lambda detections: len(self.get_detections_by_class(detections, "attack")) > 0,
            action=self._start_attack_action,
            priority=10
        )
        self.add_task(start_attack_task)
        
        # 任务2: 收集资源 (中等优先级)
        collect_resources_task = StateTask(
            name="collect_resources", 
            description="收集村庄中的资源",
            condition=lambda detections: self._has_collectible_resources(detections),
            action=self._collect_resources_action,
            priority=5
        )
        self.add_task(collect_resources_task)
        
        # 任务3: 通过find_now计算attack位置 (低优先级备用方案)
        attack_by_find_now_task = StateTask(
            name="attack_by_find_now",
            description="通过find_now按钮计算attack按钮位置",
            condition=lambda detections: len(self.get_detections_by_class(detections, "find_now")) > 0,
            action=self._attack_by_find_now_action,
            priority=3
        )
        self.add_task(attack_by_find_now_task)
        
        # 任务4: 默认等待 (最低优先级)
        wait_task = StateTask(
            name="wait",
            description="等待新的机会出现",
            condition=lambda detections: True,  # 总是满足条件
            action=self._wait_action,
            priority=1
        )
        self.add_task(wait_task)
    
    def _has_collectible_resources(self, detections: List[Detection]) -> bool:
        """检查是否有可收集的资源"""
        # 这里可以检测各种资源建筑上的收集标识
        # 例如：金币矿、圣水收集器等建筑上的收集提示
        resource_indicators = ["collect_gold", "collect_elixir", "collect_dark_elixir"]
        for indicator in resource_indicators:
            if self.get_detections_by_class(detections, indicator):
                return True
        return False
    
    def _start_attack_action(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """开始攻击任务"""
        attack_detection = self.get_best_detection(detections, "attack")
        if attack_detection:
            print("[VILLAGE] 直接检测到attack按钮")
            self._click_detection(attack_detection, window_info)
            time.sleep(2)  # 等待界面切换
            return GameState.FINDING_OPPONENT
        return None
    
    def _collect_resources_action(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """收集资源任务"""
        print("[VILLAGE] 收集资源...")
        
        # 收集各种资源
        resource_indicators = ["collect_gold", "collect_elixir", "collect_dark_elixir"]
        collected_any = False
        
        for indicator in resource_indicators:
            resource_detections = self.get_detections_by_class(detections, indicator)
            for detection in resource_detections[:3]:  # 最多收集3个
                self._click_detection(detection, window_info)
                time.sleep(0.5)  # 收集间隔
                collected_any = True
        
        if collected_any:
            print("[VILLAGE] 资源收集完成")
            time.sleep(1)
        
        return None  # 收集完继续留在村庄状态
    
    def _attack_by_find_now_action(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """通过find_now计算attack位置"""
        find_now_detection = self.get_best_detection(detections, "find_now")
        if find_now_detection:
            print("[VILLAGE] 通过find_now按钮计算attack位置")
            attack_pos = self.calculate_relative_position(
                find_now_detection, 
                self.attack_offset_from_find_now
            )
            self._click_position(attack_pos, window_info)
            time.sleep(2)
            return GameState.FINDING_OPPONENT
        return None
    
    def _wait_action(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """等待任务"""
        print("[VILLAGE] 等待中...")
        time.sleep(1)
        return None
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        print(f"[CLICK] 点击检测目标: {detection.class_name} "
              f"at ({screen_x}, {screen_y}), conf: {detection.confidence:.2f}")
        
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()
    
    def _click_position(self, position: tuple, window_info: WindowInfo, is_relative: bool = True):
        """点击指定位置"""
        if is_relative:
            # 相对于窗口的坐标
            screen_x = window_info.left + position[0]
            screen_y = window_info.top + position[1]
        else:
            # 窗口内的绝对坐标
            screen_x = window_info.left + position[0]  
            screen_y = window_info.top + position[1]
            
        print(f"[CLICK] 点击计算位置: ({screen_x}, {screen_y})")
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        pyautogui.click()