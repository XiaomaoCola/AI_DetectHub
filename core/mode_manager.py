#!/usr/bin/env python3
"""
游戏模式管理器
支持Home Village和Builder Base两种模式的切换和管理
"""

from typing import Dict, List, Optional, Any

from coc.auto_player.features.base import GameMode, feature_registry
from coc.auto_player.features.home_village_features import register_home_village_features
from coc.auto_player.features.builder_base_features import register_builder_base_features
from states.state_machine import Detection


class ModeManager:
    """游戏模式管理器"""
    
    def __init__(self):
        self.current_mode: Optional[GameMode] = None
        self.mode_configs: Dict[GameMode, Dict[str, Any]] = {
            GameMode.HOME_VILLAGE: {
                # Home Village 默认配置
                'hv_collect_resources': True,
                'hv_attack': True,
                'hv_clan_capital': False,
                'hv_train_troops': False,
                'hv_upgrade_buildings': False,
                'check_army_ready': True
            },
            GameMode.BUILDER_BASE: {
                # Builder Base 默认配置
                'bb_collect_resources': True,
                'bb_attack': True, 
                'bb_upgrade_buildings': False,
                'check_army_ready': True
            }
        }
        
        # 注册所有功能策略
        self._register_all_features()
        
    def _register_all_features(self):
        """注册所有模式的功能策略"""
        print("[MODE_MANAGER] 注册所有功能策略...")
        register_home_village_features()
        register_builder_base_features()
        print("[MODE_MANAGER] 功能策略注册完成")
        
    def set_mode(self, mode: GameMode):
        """设置当前游戏模式"""
        if mode != self.current_mode:
            print(f"[MODE_MANAGER] 切换游戏模式: {self.current_mode} -> {mode}")
            self.current_mode = mode
        else:
            print(f"[MODE_MANAGER] 保持当前模式: {mode}")
            
    def get_current_mode(self) -> Optional[GameMode]:
        """获取当前游戏模式"""
        return self.current_mode
        
    def detect_mode_from_ui(self, detections: List[Detection]) -> Optional[GameMode]:
        """根据UI检测结果自动识别游戏模式"""
        
        # Builder Base 特征：find_now按钮
        find_now_detections = [d for d in detections if d.class_name == "find_now"]
        if find_now_detections:
            return GameMode.BUILDER_BASE
            
        # Home Village 特征：可以根据特有的UI元素判断
        # 例如：clan_capital_button, 特定的建筑等
        clan_capital_detections = [d for d in detections if d.class_name == "clan_capital_button"]
        if clan_capital_detections:
            return GameMode.HOME_VILLAGE
            
        # 如果有attack按钮但没有find_now，通常是Home Village
        attack_detections = [d for d in detections if d.class_name == "attack"]
        if attack_detections and not find_now_detections:
            return GameMode.HOME_VILLAGE
            
        return None
        
    def auto_detect_and_set_mode(self, detections: List[Detection]) -> bool:
        """自动检测并设置游戏模式"""
        detected_mode = self.detect_mode_from_ui(detections)
        if detected_mode:
            self.set_mode(detected_mode)
            return True
        return False
        
    def get_mode_config(self, mode: Optional[GameMode] = None) -> Dict[str, Any]:
        """获取指定模式的配置"""
        target_mode = mode or self.current_mode
        if target_mode is None:
            return {}
        return self.mode_configs.get(target_mode, {})
        
    def update_mode_config(self, config: Dict[str, Any], mode: Optional[GameMode] = None):
        """更新指定模式的配置"""
        target_mode = mode or self.current_mode
        if target_mode is None:
            print("[MODE_MANAGER] 警告: 当前模式为空，无法更新配置")
            return
            
        self.mode_configs[target_mode].update(config)
        print(f"[MODE_MANAGER] 更新 {target_mode.value} 配置: {config}")
        
    def get_available_features(self, mode: Optional[GameMode] = None) -> List[Dict[str, str]]:
        """获取指定模式的可用功能列表"""
        target_mode = mode or self.current_mode
        if target_mode is None:
            return []
        return feature_registry.get_available_features(target_mode)
        
    def execute_current_mode_features(self, detections: List[Detection], window_info) -> Optional:
        """执行当前模式下的功能"""
        if self.current_mode is None:
            print("[MODE_MANAGER] 警告: 当前模式为空，无法执行功能")
            return None
            
        current_config = self.get_mode_config()
        return feature_registry.execute_features(
            self.current_mode, 
            detections, 
            window_info, 
            current_config
        )
        
    def get_mode_display_name(self, mode: GameMode) -> str:
        """获取模式的显示名称"""
        display_names = {
            GameMode.HOME_VILLAGE: "主村庄 (Home Village)",
            GameMode.BUILDER_BASE: "建筑工人基地 (Builder Base)"
        }
        return display_names.get(mode, mode.value)
        
    def get_all_modes(self) -> List[GameMode]:
        """获取所有支持的游戏模式"""
        return list(self.mode_configs.keys())
        
    def is_mode_active(self, mode: GameMode) -> bool:
        """检查指定模式是否为当前活动模式"""
        return self.current_mode == mode
        
    def get_mode_summary(self) -> Dict[str, Any]:
        """获取当前模式的摘要信息"""
        if self.current_mode is None:
            return {
                'current_mode': None,
                'display_name': "未设置",
                'enabled_features': [],
                'total_features': 0
            }
            
        config = self.get_mode_config()
        enabled_features = [key for key, value in config.items() if value is True]
        available_features = self.get_available_features()
        
        return {
            'current_mode': self.current_mode,
            'display_name': self.get_mode_display_name(self.current_mode),
            'enabled_features': enabled_features,
            'total_features': len(available_features),
            'config': config
        }
        
    def reset_to_defaults(self, mode: Optional[GameMode] = None):
        """重置指定模式的配置为默认值"""
        target_mode = mode or self.current_mode
        if target_mode is None:
            print("[MODE_MANAGER] 警告: 当前模式为空，无法重置配置")
            return
            
        if target_mode == GameMode.HOME_VILLAGE:
            self.mode_configs[target_mode] = {
                'hv_collect_resources': True,
                'hv_attack': True,
                'hv_clan_capital': False,
                'hv_train_troops': False,
                'hv_upgrade_buildings': False,
                'check_army_ready': True
            }
        elif target_mode == GameMode.BUILDER_BASE:
            self.mode_configs[target_mode] = {
                'bb_collect_resources': True,
                'bb_attack': True,
                'bb_upgrade_buildings': False,
                'check_army_ready': True
            }
            
        print(f"[MODE_MANAGER] 重置 {target_mode.value} 配置为默认值")


# 全局模式管理器实例
mode_manager = ModeManager()