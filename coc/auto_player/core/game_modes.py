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


# TaskType 已删除 - 简化为纯 Mode → State 架构


class GameModeManager:
    """游戏模式管理器 - 简化版，只管理模式切换"""
    
    def __init__(self):
        self.current_mode = GameMode.HOME_VILLAGE
        self.mode_handlers = {}
        
    def set_mode(self, mode: GameMode):
        """设置当前游戏模式"""
        print(f"[MODE] 切换到模式: {mode.value}")
        self.current_mode = mode
        
    def get_current_mode(self) -> GameMode:
        """获取当前模式"""
        return self.current_mode
        
    def auto_detect_mode(self, detections: list) -> Optional[GameMode]:
        """根据检测结果自动判断模式"""
        # 检测主村庄特征
        has_shop = any(d.class_name == "shop_button" for d in detections)
        has_find_now = any(d.class_name == "find_now" for d in detections)
        has_clock_tower = any(d.class_name == "clock_tower" for d in detections)
        
        if has_find_now or has_clock_tower:
            return GameMode.BUILDER_BASE
        elif has_shop and not has_find_now:
            return GameMode.HOME_VILLAGE
        else:
            return None  # 无法确定，保持当前模式


class ModeHandler(ABC):
    """模式处理器抽象基类 - 简化版"""
    
    def __init__(self, mode: GameMode):
        self.mode = mode
        
    @abstractmethod
    def can_handle_mode(self, detections: list) -> bool:
        """判断是否可以处理当前模式"""
        pass
        
    @abstractmethod
    def switch_to_mode(self, detections: list, window_info: WindowInfo) -> bool:
        """切换到此模式"""
        pass


class HomeVillageHandler(ModeHandler):
    """主村庄模式处理器 - 简化版"""
    
    def __init__(self):
        super().__init__(GameMode.HOME_VILLAGE)
        
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


class BuilderBaseHandler(ModeHandler):
    """建筑工人基地模式处理器 - 简化版"""
    
    def __init__(self):
        super().__init__(GameMode.BUILDER_BASE)
        
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