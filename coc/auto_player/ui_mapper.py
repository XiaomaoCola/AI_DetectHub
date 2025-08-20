import yaml
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from .base_state import Detection, WindowInfo


class MultiConfigManager:
    """多配置文件管理器"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"
        
        self.config_dir = Path(config_dir)
        self.main_config = self._load_main_config()
        self.state_configs = self._load_state_configs()
        self.ui_elements = self._load_ui_elements()
        
    def _load_main_config(self) -> Dict[str, Any]:
        """加载主配置文件"""
        main_config_path = self.config_dir / "main_config.yaml"
        try:
            with open(main_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"[INFO] 加载主配置: {main_config_path}")
                return config
        except Exception as e:
            print(f"[WARNING] 加载主配置文件失败: {e}")
            return self._get_default_main_config()
    
    def _load_state_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载所有状态配置文件"""
        state_configs = {}
        
        # 定义状态配置文件映射
        state_files = {
            "village": "village_config.yaml",
            "finding_opponent": "finding_config.yaml", 
            "attacking": "attacking_config.yaml",
            # 可以继续添加其他状态
        }
        
        for state_name, filename in state_files.items():
            config_path = self.config_dir / filename
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    state_configs[state_name] = config
                    print(f"[INFO] 加载{state_name}状态配置: {config_path}")
            except Exception as e:
                print(f"[WARNING] 加载状态配置失败 {filename}: {e}")
                state_configs[state_name] = self._get_default_state_config(state_name)
                
        return state_configs
        
    def _load_ui_elements(self) -> Dict[str, Any]:
        """加载UI元素配置"""
        ui_elements_path = self.config_dir / "ui_elements.yaml"
        try:
            with open(ui_elements_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"[INFO] 加载UI元素配置: {ui_elements_path}")
                return config
        except Exception as e:
            print(f"[WARNING] 加载UI元素配置失败: {e}")
            return self._get_default_ui_elements()
    
    def _get_default_main_config(self) -> Dict[str, Any]:
        """获取默认主配置"""
        return {
            "version": "1.0.0",
            "model": {"confidence_threshold": 0.6},
            "timing": {"click_duration": 0.1},
            "window": {"keyword": "BlueStacks"}
        }
    
    def _get_default_state_config(self, state_name: str) -> Dict[str, Any]:
        """获取默认状态配置"""
        return {
            "state_name": state_name,
            "timing": {"max_duration": 60},
            "indicators": {"required": [], "optional": []},
            "relative_positions": {},
            "fixed_positions": {}
        }
        
    def _get_default_ui_elements(self) -> Dict[str, Any]:
        """获取默认UI元素配置"""
        return {
            "buttons": {},
            "element_validation": {},
            "size_validation": {}
        }
    
    def get_main_config(self, key_path: str, default=None):
        """获取主配置值"""
        return self._get_config_value(self.main_config, key_path, default)
        
    def get_state_config(self, state_name: str, key_path: str, default=None):
        """获取状态配置值"""
        if state_name not in self.state_configs:
            return default
        return self._get_config_value(self.state_configs[state_name], key_path, default)
        
    def get_ui_element_config(self, key_path: str, default=None):
        """获取UI元素配置值"""
        return self._get_config_value(self.ui_elements, key_path, default)
    
    def _get_config_value(self, config: Dict, key_path: str, default=None):
        """从配置字典中获取值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_all_state_names(self) -> List[str]:
        """获取所有状态名称"""
        return list(self.state_configs.keys())
        
    def update_state_config(self, state_name: str, key_path: str, new_value: Any):
        """更新状态配置值"""
        if state_name not in self.state_configs:
            return False
            
        keys = key_path.split('.')
        config = self.state_configs[state_name]
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        # 设置值
        config[keys[-1]] = new_value
        return True
        
    def save_state_config(self, state_name: str):
        """保存状态配置到文件"""
        if state_name not in self.state_configs:
            return False
            
        state_files = {
            "village": "village_config.yaml",
            "finding_opponent": "finding_config.yaml",
            "attacking": "attacking_config.yaml"
        }
        
        if state_name not in state_files:
            return False
            
        config_path = self.config_dir / state_files[state_name]
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.state_configs[state_name], f, 
                         default_flow_style=False, allow_unicode=True)
            print(f"[INFO] 保存状态配置: {config_path}")
            return True
        except Exception as e:
            print(f"[ERROR] 保存状态配置失败 {state_name}: {e}")
            return False


class UIElementMapper:
    """UI元素映射器"""
    
    def __init__(self, config_manager: MultiConfigManager):
        self.config = config_manager
        
    def validate_detection(self, detection: Detection) -> bool:
        """验证检测结果是否符合预期尺寸"""
        # 从UI元素配置中获取尺寸验证规则
        button_config = self.config.get_ui_element_config(f"buttons.{detection.class_name}")
        if not button_config:
            return True  # 没有配置则认为有效
            
        x1, y1, x2, y2 = detection.bbox
        width = x2 - x1
        height = y2 - y1
        
        # 检查尺寸是否在合理范围内
        min_size = button_config.get("min_size", [0, 0])
        max_size = button_config.get("max_size", [9999, 9999])
        min_confidence = button_config.get("min_confidence", 0.0)
        
        size_valid = (min_size[0] <= width <= max_size[0] and 
                     min_size[1] <= height <= max_size[1])
        confidence_valid = detection.confidence >= min_confidence
        
        return size_valid and confidence_valid
    
    def filter_valid_detections(self, detections: List[Detection]) -> List[Detection]:
        """过滤出有效的检测结果"""
        return [d for d in detections if self.validate_detection(d)]
    
    def get_relative_position(self, 
                            base_detection: Detection, 
                            target_key: str,
                            state: str = None) -> Optional[Tuple[int, int]]:
        """
        根据基准检测结果和配置获取相对位置
        
        Args:
            base_detection: 基准检测结果
            target_key: 目标位置配置键
            state: 状态名称（用于查找配置）
        """
        if state:
            offset = self.config.get_state_config(state, f"relative_positions.{target_key}")
        else:
            # 尝试从主配置中获取
            offset = self.config.get_main_config(f"relative_positions.{target_key}")
            
        if not offset or len(offset) != 2:
            return None
            
        base_x, base_y = base_detection.center
        return (base_x + offset[0], base_y + offset[1])
    
    def get_fixed_position(self, 
                          position_key: str, 
                          window_info: WindowInfo,
                          state: str = None) -> Optional[Tuple[int, int]]:
        """
        获取固定位置（基于屏幕比例）
        
        Args:
            position_key: 位置配置键
            window_info: 窗口信息
            state: 状态名称
        """
        if state:
            ratio = self.config.get_state_config(state, f"fixed_positions.{position_key}")
        else:
            ratio = self.config.get_main_config(f"fixed_positions.{position_key}")
            
        if not ratio or len(ratio) != 2:
            return None
            
        x = int(window_info.width * ratio[0])
        y = int(window_info.height * ratio[1])
        return (x, y)
    
    def get_deploy_zones(self, window_info: WindowInfo, state: str = "attacking") -> List[Tuple[int, int]]:
        """获取部署区域坐标列表"""
        zones_config = self.config.get_state_config(state, "deployment.zones", [])
        zones = []
        
        for zone_config in zones_config:
            if isinstance(zone_config, dict) and "position" in zone_config:
                ratio = zone_config["position"]
                if len(ratio) == 2:
                    x = int(window_info.width * ratio[0])
                    y = int(window_info.height * ratio[1])
                    zones.append((x, y))
                    
        return zones
    
    def get_timeout(self, state: str) -> int:
        """获取状态超时时间"""
        return self.config.get_state_config(state, "timing.max_duration", 60)
    
    def get_timing(self, key: str, state: str = None) -> float:
        """获取时间配置"""
        if state:
            return self.config.get_state_config(state, f"timing.{key}", 1.0)
        else:
            return self.config.get_main_config(f"timing.{key}", 1.0)
    
    def get_deployment_config(self, key: str) -> Any:
        """获取部署配置"""
        return self.config.get_state_config("attacking", f"deployment.{key}")


class StateValidator:
    """状态验证器"""
    
    def __init__(self, config_manager: MultiConfigManager):
        self.config = config_manager
        
    def validate_state(self, state_name: str, detections: List[Detection]) -> bool:
        """验证当前检测结果是否符合指定状态"""
        indicators = self.config.get_state_config(state_name, "indicators")
        if not indicators:
            return False
            
        detection_classes = [d.class_name for d in detections]
        
        # 检查必需元素
        required = indicators.get("required", [])
        for req in required:
            if req not in detection_classes:
                return False
                
        # 检查禁止元素
        forbidden = indicators.get("forbidden", [])
        for forb in forbidden:
            if forb in detection_classes:
                return False
                
        return True
    
    def find_matching_state(self, detections: List[Detection]) -> Optional[str]:
        """根据检测结果找到匹配的状态"""
        for state_name in self.config.get_all_state_names():
            if self.validate_state(state_name, detections):
                return state_name
                
        return None