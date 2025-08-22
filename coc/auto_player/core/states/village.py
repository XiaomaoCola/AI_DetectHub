import time
import pyautogui
from typing import List, Optional, Dict, Any

from ..state_machine import StateHandler, GameState, Detection, WindowInfo
from ..features import feature_registry
from ..village_features import register_village_features


class VillageHandler(StateHandler):
    """村庄状态处理器 - 使用策略模式"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(GameState.VILLAGE)
        
        # 功能配置（用户可通过GUI设置）
        self.config = config or {
            'collect_resources': True,
            'attack': True, 
            'clan_capital': False,
            'train_troops': False,
            'check_army_ready': True
        }
        
        # 注册村庄功能策略
        register_village_features()
        
        # 村庄状态的特征标识
        self.required_indicators = ["find_now"]  # Builder Base特有的find_now按钮  
        self.optional_indicators = ["attack"]    # 可能存在的attack按钮
        
    def can_handle(self, detections: List[Detection]) -> bool:
        """
        判断是否为村庄状态
        村庄状态特征：有find_now按钮（Builder Base独有）
        """
        find_now_detections = self.get_detections_by_class(detections, "find_now")
        return len(find_now_detections) > 0
        
    def execute(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """
        执行村庄状态逻辑 - 使用策略模式
        """
        print(f"[VILLAGE] 使用策略模式执行村庄功能...")
        
        # 使用功能注册表执行启用的功能
        result = feature_registry.execute_features(detections, window_info, self.config)
        
        # 如果没有策略返回状态转换，使用备用逻辑
        if result is None:
            result = self._fallback_logic(detections, window_info)
            
        return result
        
    def _fallback_logic(self, detections: List[Detection], window_info: WindowInfo) -> Optional[GameState]:
        """备用逻辑：当策略模式无法处理时的降级方案"""
        print("[VILLAGE] 执行备用逻辑...")
        
        # 通过find_now计算attack位置（备用方案）
        if self.config.get('attack', False):
            find_now_detection = self.get_best_detection(detections, "find_now")
            if find_now_detection:
                print("[VILLAGE] 通过find_now按钮计算attack位置")
                attack_pos = self.calculate_relative_position(
                    find_now_detection, 
                    (0, -50)  # attack按钮相对于find_now的位置
                )
                self._click_position(attack_pos, window_info)
                time.sleep(2)
                return GameState.FINDING_OPPONENT
                
        # 默认等待
        print("[VILLAGE] 等待中...")
        time.sleep(1)
        return None
        
    def update_config(self, new_config: Dict[str, Any]):
        """更新功能配置"""
        self.config.update(new_config)
        print(f"[VILLAGE] 配置已更新: {self.config}")
        
    def get_available_features(self):
        """获取可用功能列表（用于GUI）"""
        return feature_registry.get_available_features()
    
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