"""
ModelAndButtonRegionManager - 简单的模型和配置管理器

使用get_model_and_region_configs函数，
参数为模型名字，直接返回模型和对应的区域。

无需输入绝对路径，就可直接引用模型和其对应的区域yaml。
"""

from pathlib import Path
import yaml
from ultralytics import YOLO


class ModelAndButtonRegionManager:
    def __init__(self, base_dir=None):
        """
        模型管理器：根据模型名自动加载 YOLO 模型和对应的区域配置（yaml 文件）
        """
        # 1. 自动定位项目目录
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent
        
        # 2. 设定两个子路径：模型权重 + 配置文件
        self.weights_dir = self.base_dir / "weights"
        self.configs_dir = self.base_dir / "region_configs"
        
        # 3. 初始化模型与配置缓存
        self.models = {}  # {name: YOLO model}
        self.configs = {}  # {name: dict from yaml}
        
        # 4. 预加载所有配置
        self._load_all_configs()
    
    def _load_all_configs(self):
        """预加载所有yaml配置文件"""
        for config_path in self.configs_dir.glob("*.yaml"):
            name = config_path.stem  # e.g., builder_base_1
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                self.configs[name] = cfg
    
    def get_model_and_region_configs(self, name):
        """
        获取模型和对应配置
        
        Args:
            name: 模型逻辑名，如 'builder_base_1'
            
        Returns:
            tuple: (YOLO_model, config_dict)
        """
        if name not in self.models:
            model_path = self.weights_dir / f"{name}.pt"
            if not model_path.exists():
                raise FileNotFoundError(f"未找到模型权重文件: {model_path}")
            self.models[name] = YOLO(str(model_path))
        
        if name not in self.configs:
            raise FileNotFoundError(f"未找到模型配置文件: {name}.yaml")
        
        return self.models[name], self.configs[name]


def main():
    """使用示例"""
    manager = ModelAndButtonRegionManager()
    
    # 获取模型和配置
    model, config = manager.get_model_and_region_configs("builder_base_1")
    
    print(f"模型: {model}")
    print(f"配置: {config}")


if __name__ == "__main__":
    main()