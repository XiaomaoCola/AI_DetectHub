"""
使用这个模块的话，需要初始化RegionCalculator这个模块，因为参数里包含从这个模块得到的结果。

需要的参数是：
1. config_name: 配置的名称。
1. config_path: 这是config_name为空时，可以设置yaml的路径。
2. detections： 从RegionCalculator这个模块里获得的。
3. class_id
"""

import yaml
import os
import sys
from pathlib import Path
from RegionCalculator import RegionCalculator

class RegionJudge:
    def __init__(self, config_name=None, config_path="region_config.yaml"):
        """
        初始化区域判断器
        
        Args:
            config_name: 配置名称 (如 "builder_base_1")，优先使用
            config_path: 配置文件路径，config_name为空时使用
        """
        self.region_calculator = RegionCalculator()
        
        # 如果提供了config_name，使用ModelAndButtonRegionManager获取配置
        if config_name:
            project_root = Path(__file__).parent.parent
            sys.path.append(str(project_root))
            from yolo_models_and_region_configs.ModelAndButtonRegionManager import ModelAndButtonRegionManager
            
            manager = ModelAndButtonRegionManager()
            model, config = manager.get_model_and_region_configs(config_name)
            
            # 直接使用配置数据，不需要文件路径
            self.config_path = None
            self.regions = config.get('regions', {})
            self.class_names = config.get('class_names', {})
            print(f"[INFO] 已加载配置 '{config_name}'，共{len(self.regions)}个区域")
        else:
            # 使用原来的路径方式
            self.config_path = config_path
            self.regions = {}
            self.class_names = {}
            self.load_config()
    
    def load_config(self):
        """从yaml文件加载区域配置"""
        if not self.config_path:
            print("[INFO] 配置已通过config_name加载，跳过文件加载")
            return
            
        if not os.path.exists(self.config_path):
            print(f"[ERROR] 配置文件不存在: {self.config_path}")
            return
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.regions = config.get('regions', {})
                self.class_names = config.get('class_names', {})
                print(f"[INFO] 已加载配置，共{len(self.regions)}个区域")
        except Exception as e:
            print(f"[ERROR] 加载配置文件失败: {e}")
    
    def is_class_in_region(self, detections, class_id):
        """
        判断指定类别ID的检测框是否在配置的区域内
        
        Args:
            detections: YOLO检测结果列表
            class_id: 要检查的类别ID (int)
            
        Returns:
            bool: True表示有该类别的框在对应区域内，False表示没有
        """
        # 检查配置中是否有这个类别
        if class_id not in self.regions:
            print(f"[WARNING] 配置中没有找到类别{class_id}的区域定义")
            return False
        
        # 获取区域配置
        region_config = self.regions[class_id]
        norm_left = region_config['left']
        norm_top = region_config['top'] 
        norm_right = region_config['right']
        norm_bottom = region_config['bottom']
        
        # 转换标准坐标到相对坐标
        region_coords = self.region_calculator.get_region_coords(norm_left, norm_top, norm_right, norm_bottom)
        if not region_coords:
            return False
        
        region_left, region_top, region_right, region_bottom = region_coords
        
        # 获取类别名称用于输出
        class_name = self.class_names.get(class_id, f"class_{class_id}")
        
        # 检查是否有指定类别的框在区域内
        for detection in detections:
            if detection['class_name'] == class_name:
                box_x1, box_y1, box_x2, box_y2 = detection['coords']
                
                # 检测框的左上角要大于等于区域左上角，右下角要小于等于区域右下角
                if (box_x1 >= region_left and box_y1 >= region_top and 
                    box_x2 <= region_right and box_y2 <= region_bottom):
                    print(f"[JUDGE] {class_name}(id:{class_id})在区域内: 框{detection['coords']} -> 区域{region_coords}")
                    return True
                else:
                    print(f"[JUDGE] {class_name}(id:{class_id})不在区域内: 框{detection['coords']} vs 区域{region_coords}")
        
        print(f"[JUDGE] 未找到{class_name}(id:{class_id})在对应区域内")
        return False


def test():
    """测试函数"""
    from RegionGetFromYolo import RegionGetFromYolo
    
    # 创建检测器和判断器
    detector = RegionGetFromYolo(model_name="builder_base_1")
    judge = RegionJudge(config_name="builder_base_1")
    
    print("=== 当前配置 ===")
    print(f"区域配置: {judge.regions}")
    print(f"类别映射: {judge.class_names}")
    
    # 获取检测结果
    print("\n开始检测...")
    detections = detector.get_all_detections()
    
    if detections:
        print(f"\n检测到{len(detections)}个目标:")
        for detection in detections:
            print(f"  {detection['class_name']}: {detection['coords']} (置信度: {detection['confidence']:.2f})")
        
        # 测试判断
        print(f"\n=== 开始判断 ===")
        
        # 测试attack (类别0)
        print(f"\n测试: attack(类别0)是否在配置区域内?")
        result_attack = judge.is_class_in_region(detections, 0)
        print(f"结果: {result_attack}")
        
        # 测试find_now (类别1)  
        print(f"\n测试: find_now(类别1)是否在配置区域内?")
        result_find_now = judge.is_class_in_region(detections, 1)
        print(f"结果: {result_find_now}")
        
    else:
        print("未检测到任何目标")


if __name__ == "__main__":
    test()