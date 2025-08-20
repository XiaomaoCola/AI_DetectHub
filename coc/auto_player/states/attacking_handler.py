import time
import random
from typing import List, Optional

from ..base_state import StateHandler, GameState, Detection, WindowInfo


class AttackingHandler(StateHandler):
    """攻击状态处理器"""
    
    def __init__(self):
        super().__init__(GameState.ATTACKING)
        self.max_duration = 45  # 攻击最多持续45秒
        
        # 攻击状态特征标识
        self.attack_indicators = [
            "enemy_base",       # 敌方基地
            "troop_panel",      # 部队面板
            "battle_timer",     # 战斗计时器
            "surrender_button"  # 投降按钮
        ]
        
        # 部署相关
        self.troops_deployed = 0
        self.max_troops = 10
        self.deploy_interval = 0.8  # 部署间隔
        self.last_deploy_time = 0
        
        # 部署区域（相对于屏幕的比例）
        self.deploy_zones = [
            (0.3, 0.7),   # 左下
            (0.5, 0.8),   # 中下  
            (0.7, 0.7),   # 右下
            (0.2, 0.5),   # 左中
            (0.8, 0.5),   # 右中
        ]
    
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为攻击状态
        特征：有投降按钮或其他战斗UI元素
        """
        # 检查是否有攻击状态的特征标识
        for indicator in self.attack_indicators:
            if self.get_detections_by_class(detections, indicator):
                return True
                
        # 如果没有村庄和寻找对手的特征，可能在攻击状态
        has_find_now = len(self.get_detections_by_class(detections, "find_now")) > 0
        has_village_ui = has_find_now  # 简化判断
        
        return not has_village_ui
    
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行攻击状态操作：部署部队
        """
        print(f"[ATTACKING] 攻击状态 - 已部署 {self.troops_deployed}/{self.max_troops} 个兵")
        
        current_time = time.time()
        
        # 检查是否应该投降
        if self._should_surrender(current_time):
            print("[ATTACKING] 准备投降")
            return self._try_surrender(detections, window_info)
        
        # 部署部队
        if self._can_deploy_troops(current_time):
            self._deploy_troops(detections, window_info)
        
        return None  # 继续攻击状态
    
    def _should_surrender(self, current_time: float) -> bool:
        """判断是否应该投降"""
        # 条件1：已部署足够的兵力
        if self.troops_deployed >= self.max_troops:
            return True
            
        # 条件2：攻击时间过长
        if current_time - self.last_deploy_time > 15:  # 15秒没有部署
            return True
            
        # 条件3：达到最大攻击时间
        # 这里需要在主控制器中传入state_start_time
        return False
    
    def _can_deploy_troops(self, current_time: float) -> bool:
        """判断是否可以部署部队"""
        if self.troops_deployed >= self.max_troops:
            return False
            
        if current_time - self.last_deploy_time < self.deploy_interval:
            return False
            
        return True
    
    def _deploy_troops(self, detections: List[Detection], window_info: WindowInfo):
        """部署部队"""
        # 方式1：在检测到的空地部署
        empty_spaces = self.get_detections_by_class(detections, "empty_space")
        if empty_spaces:
            target = random.choice(empty_spaces)  # 随机选择一个空地
            self._click_detection(target, window_info)
            print(f"[DEPLOY] 在检测到的空地部署第{self.troops_deployed + 1}个兵")
        else:
            # 方式2：在预设区域部署
            zone = random.choice(self.deploy_zones)
            x = int(window_info.width * zone[0])
            y = int(window_info.height * zone[1])
            self._click_position((x, y), window_info)
            print(f"[DEPLOY] 在预设区域 {zone} 部署第{self.troops_deployed + 1}个兵")
        
        self.troops_deployed += 1
        self.last_deploy_time = time.time()
        time.sleep(0.2)  # 短暂延迟
    
    def _try_surrender(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """尝试投降"""
        surrender_detection = self.get_best_detection(detections, "surrender_button")
        if surrender_detection:
            print("[ATTACKING] 找到投降按钮，开始投降")
            self._click_detection(surrender_detection, window_info)
            time.sleep(1)
            return GameState.SURRENDERING
        else:
            # 使用相对位置点击投降按钮（通常在右上角）
            surrender_pos = (int(window_info.width * 0.9), int(window_info.height * 0.1))
            print("[ATTACKING] 使用预设位置投降")
            self._click_position(surrender_pos, window_info)
            time.sleep(1)
            return GameState.SURRENDERING
    
    def _click_detection(self, detection: Detection, window_info: WindowInfo):
        """点击检测到的目标"""
        screen_x = window_info.left + detection.center[0]
        screen_y = window_info.top + detection.center[1]
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.05)
        pyautogui.click()
    
    def _click_position(self, position: tuple, window_info: WindowInfo):
        """点击指定位置"""
        screen_x = window_info.left + position[0]
        screen_y = window_info.top + position[1]
        
        import pyautogui
        pyautogui.moveTo(screen_x, screen_y, duration=0.05)
        pyautogui.click()
        
    def reset_attack_state(self):
        """重置攻击状态（开始新的攻击时调用）"""
        self.troops_deployed = 0
        self.last_deploy_time = 0
        self.reset_retry_count()