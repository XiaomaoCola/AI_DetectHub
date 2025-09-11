import torch
from torchvision import transforms, models
from torch import nn
import cv2
import numpy as np
from pathlib import Path
import json
from typing import List, Tuple, Optional, Union
import os


class ScenePredictor:
    """COC场景分类预测器"""
    
    def __init__(self, model_path: str = "coc_scene_classifier.pt", 
                 config_path: str = "classifier_config.json"):
        """
        初始化预测器
        
        Args:
            model_path: 模型文件路径
            config_path: 配置文件路径
        """
        self.model_path = model_path
        self.config_path = config_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 模型相关属性
        self.model = None
        self.class_names = []
        self.num_classes = 0
        self.img_size = 224
        self.transform = None
        
        # 自动加载模型
        self.load_model()
    
    def load_model(self) -> bool:
        """加载模型和配置"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.model_path):
                print(f"[ERROR] 模型文件不存在: {self.model_path}")
                return False
            
            # 加载模型数据
            model_data = torch.load(self.model_path, map_location=self.device)
            
            self.class_names = model_data["class_names"]
            self.num_classes = model_data["num_classes"]
            self.img_size = model_data.get("img_size", 224)
            
            # 构建模型结构
            self.model = models.resnet18(pretrained=False)
            self.model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(self.model.fc.in_features, self.num_classes)
            )
            
            # 加载权重
            self.model.load_state_dict(model_data["model_state"])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # 设置预处理变换
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            print(f"[INFO] 模型加载成功")
            print(f"[INFO] 设备: {self.device}")
            print(f"[INFO] 类别: {self.class_names}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 模型加载失败: {e}")
            return False
    
    def preprocess_image(self, image: Union[np.ndarray, str]) -> torch.Tensor:
        """
        预处理图像
        
        Args:
            image: 输入图像 (numpy数组或文件路径)
            
        Returns:
            torch.Tensor: 预处理后的张量
        """
        if isinstance(image, str):
            # 从文件路径加载图像
            image = cv2.imread(image)
            if image is None:
                raise ValueError(f"无法加载图像: {image}")
        
        # OpenCV默认是BGR，转换为RGB
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 应用变换
        if self.transform:
            image_tensor = self.transform(image).unsqueeze(0)  # 添加batch维度
        else:
            raise RuntimeError("模型未正确加载，transform为None")
        
        return image_tensor.to(self.device)
    
    def predict(self, image: Union[np.ndarray, str], 
                top_k: int = 1) -> List[Tuple[str, float]]:
        """
        预测图像场景
        
        Args:
            image: 输入图像 (numpy数组或文件路径)
            top_k: 返回前k个预测结果
            
        Returns:
            List[Tuple[str, float]]: [(类别名, 置信度), ...]
        """
        if self.model is None:
            raise RuntimeError("模型未正确加载")
        
        try:
            # 预处理图像
            input_tensor = self.preprocess_image(image)
            
            # 预测
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                
                # 获取前k个结果
                top_probs, top_indices = torch.topk(probabilities, top_k)
                
                results = []
                for i in range(top_k):
                    class_idx = top_indices[0][i].item()
                    confidence = top_probs[0][i].item()
                    class_name = self.class_names[class_idx]
                    results.append((class_name, confidence))
                
                return results
                
        except Exception as e:
            print(f"[ERROR] 预测失败: {e}")
            return []
    
    def predict_single(self, image: Union[np.ndarray, str]) -> Tuple[str, float]:
        """
        预测单个结果
        
        Args:
            image: 输入图像
            
        Returns:
            Tuple[str, float]: (最可能的类别名, 置信度)
        """
        results = self.predict(image, top_k=1)
        if results:
            return results[0]
        else:
            return ("unknown", 0.0)
    
    def get_class_names(self) -> List[str]:
        """获取所有类别名称"""
        return self.class_names.copy()
    
    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
    
    def predict_from_screenshot(self, window_region: Tuple[int, int, int, int]) -> Tuple[str, float]:
        """
        从屏幕截图预测（配合你的截图功能使用）
        
        Args:
            window_region: 窗口区域 (left, top, right, bottom)
            
        Returns:
            Tuple[str, float]: (场景类别, 置信度)
        """
        try:
            from mss import mss
            
            left, top, right, bottom = window_region
            region = {"left": left, "top": top, "width": right - left, "height": bottom - top}
            
            with mss() as sct:
                screenshot = np.array(sct.grab(region))[:, :, :3]  # BGRA -> BGR
                
            return self.predict_single(screenshot)
            
        except Exception as e:
            print(f"[ERROR] 截图预测失败: {e}")
            return ("unknown", 0.0)


class COCSceneDetector:
    """COC场景检测器 - 整合YOLO和场景分类"""
    
    def __init__(self, scene_predictor: ScenePredictor, yolo_detector=None):
        """
        初始化COC场景检测器
        
        Args:
            scene_predictor: 场景分类预测器
            yolo_detector: YOLO检测器（可选）
        """
        self.scene_predictor = scene_predictor
        self.yolo_detector = yolo_detector
    
    def detect_scene(self, image: Union[np.ndarray, str], 
                     confidence_threshold: float = 0.7) -> dict:
        """
        综合检测场景
        
        Args:
            image: 输入图像
            confidence_threshold: 置信度阈值
            
        Returns:
            dict: 检测结果
        """
        result = {
            "scene_class": "unknown",
            "confidence": 0.0,
            "reliable": False,
            "yolo_detections": []
        }
        
        # 场景分类
        scene_class, confidence = self.scene_predictor.predict_single(image)
        result["scene_class"] = scene_class
        result["confidence"] = confidence
        result["reliable"] = confidence > confidence_threshold
        
        # 如果有YOLO检测器，也运行YOLO检测
        if self.yolo_detector:
            try:
                yolo_results = self.yolo_detector.get_all_detections()
                result["yolo_detections"] = yolo_results
            except:
                pass
        
        return result


def main():
    """示例使用"""
    # 创建预测器
    predictor = ScenePredictor("coc_scene_classifier.pt")
    
    if predictor.is_loaded():
        print("模型加载成功，可以开始预测")
        print(f"支持的场景类别: {predictor.get_class_names()}")
        
        # 示例：预测图片文件
        # result = predictor.predict_single("test_image.jpg")
        # print(f"预测结果: {result}")
        
    else:
        print("模型加载失败")


if __name__ == "__main__":
    main()