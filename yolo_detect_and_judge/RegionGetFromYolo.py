"""
这个模块用于从指定窗口（默认是 BlueStacks，可以改动，有个参数window_keyword）中截图，
并使用 YOLO 模型（YOLOv8）进行目标检测。
注意：这个模块只适用与YOLO，并不适用于其他的图像检测模型。

需要的参数是：
1. model_path： YOLO模型路径
2. window_keyword： 窗口关键词
3. conf_thres： 置信度阈值

这个程序的运行方式：
1. 查找目标窗口并置顶
2. 截图窗口内容
3. 使用指定的 YOLO 模型进行物体检测（这里是可以改模型位置的）
4. 返回检测框的位置、类别名、置信度等信息

然后这个程序返回结果的特征是：
- 返回所有识别出来的方框，而不是一个类返回一个那种；
- 检测结果为列表形式，包含所有检测框；
- 每个元素为字典，结构如下：
  {
      'class_name': str,
      'coords': (x1, y1, x2, y2),
      'confidence': float,
      'index': int
  }
"""

import ctypes
import re
import cv2
import numpy as np
import time
from mss import mss
from ultralytics import YOLO
import win32gui
import win32con
import sys
from pathlib import Path

class RegionGetFromYolo:
    def __init__(self, model_name=None, model_path=None, window_keyword="BlueStacks", conf_thres=0.55):
        """
        初始化YOLO区域检测器
        
        Args:
            model_name: 模型名称 (如 "builder_base_1")，优先使用
            model_path: YOLO模型路径 (绝对路径)，model_name为空时使用
            window_keyword: 窗口关键词
            conf_thres: 置信度阈值
        """
        # 如果提供了model_name，使用ModelAndButtonRegionManager
        if model_name:
            project_root = Path(__file__).parent.parent
            sys.path.append(str(project_root))
            from yolo_models_and_region_configs.ModelAndButtonRegionManager import ModelAndButtonRegionManager
            
            manager = ModelAndButtonRegionManager()
            model, config = manager.get_model_and_region_configs(model_name)
            self.model_path = None  # 直接使用已加载的模型
            self.model = model
        else:
            # 使用原来的路径方式
            self.model_path = model_path or r"A:\Projects\AI_DetectHub\runs\detect\train\weights\best.pt"
            self.model = None
            
        self.window_keyword = window_keyword
        self.conf_thres = conf_thres
        
        # 处理高DPI缩放
        ctypes.windll.user32.SetProcessDPIAware()
        
        # 初始化
        self.sct = None
        self.class_names = {}  # 存储类别ID到名称的映射
    
    def find_bluestacks_window(self):
        """查找BlueStacks窗口并置顶"""
        hwnd_list = []
        
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(self.window_keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))
        
        win32gui.EnumWindows(enum_handler, None)
        
        if hwnd_list:
            target_hwnd, title = hwnd_list[0]
            
            # 将BlueStacks窗口置顶
            try:
                win32gui.SetForegroundWindow(target_hwnd)
                win32gui.SetWindowPos(target_hwnd, win32con.HWND_TOP, 0, 0, 0, 0, 
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
                time.sleep(0.1)  # 等待窗口置顶完成
                print(f"[INFO] BlueStacks窗口已置顶: {title}")
            except Exception as e:
                print(f"[WARNING] 无法置顶窗口: {e}")
            
            # 获取客户区
            rect = win32gui.GetClientRect(target_hwnd)
            pt = win32gui.ClientToScreen(target_hwnd, (0, 0))
            left, top = pt
            right, bottom = left + rect[2], top + rect[3]
            return (left, top, right, bottom), title
        else:
            return None, None

    def load_model(self):
        """加载YOLO模型"""
        if self.model is None:
            print(f"[INFO] 加载模型: {self.model_path}")
            self.model = YOLO(self.model_path)

        # ✅ 始终从模型里补 class_names，不依赖之前赋值
        if not self.class_names and hasattr(self.model, 'names'):
            self.class_names = self.model.names
            print(f"[INFO] 模型类别: {self.class_names}")

        if self.sct is None:
            self.sct = mss()
    
    def capture_and_detect(self):
        """
        截取BlueStacks窗口并进行YOLO检测
        
        Returns:
            dict: 检测结果，格式为 {类别名: (左上x, 左上y, 右下x, 右下y), ...}
                 如果没有检测到或失败，返回空字典
        """
        # 查找窗口
        window_rect, title = self.find_bluestacks_window()
        if not window_rect:
            print("[ERROR] 未找到BlueStacks窗口")
            return {}
        
        # 加载模型
        self.load_model()
        
        # 截图
        left, top, right, bottom = window_rect
        width, height = right - left, bottom - top
        
        region = {"left": left, "top": top, "width": width, "height": height}
        frame = np.array(self.sct.grab(region))[:, :, :3]  # BGRA -> BGR
        
        # YOLO检测
        results = self.model.predict(frame, imgsz=640, conf=self.conf_thres, verbose=False)[0]
        
        # 解析检测结果 - 返回所有检测框
        detections = []
        if results.boxes is not None and len(results.boxes) > 0:
            xyxy = results.boxes.xyxy.cpu().numpy().astype(int)  # 坐标
            cls = results.boxes.cls.cpu().numpy().astype(int)    # 类别ID
            conf = results.boxes.conf.cpu().numpy()             # 置信度
            
            for i, ((x1, y1, x2, y2), class_id, confidence) in enumerate(zip(xyxy, cls, conf)):
                # 获取类别名称
                class_name = self.class_names.get(class_id, f"class_{class_id}")
                
                # 相对坐标（相对于BlueStacks窗口）
                relative_coords = (x1, y1, x2, y2)
                
                # 添加到检测列表，包含所有信息
                detection_info = {
                    'class_name': class_name,
                    'coords': relative_coords,
                    'confidence': confidence,
                    'index': i  # 检测框序号
                }
                detections.append(detection_info)
                print(f"[DETECT] {class_name}_{i}: {relative_coords} (confidence: {confidence:.2f})")
        
        return detections
    
    def get_all_detections(self):
        """
        获取所有检测结果的便捷方法
        
        Returns:
            list: [{'class_name': '类别名', 'coords': (x1,y1,x2,y2), 'confidence': 0.9, 'index': 0}, ...]
        """
        return self.capture_and_detect()


def main():
    """测试函数"""
    detector = RegionGetFromYolo(model_name="builder_base_1")
    
    print("开始检测BlueStacks窗口中的目标...")
    detections = detector.get_all_detections()
    
    if detections:
        print(f"\n=== 检测结果 (共{len(detections)}个目标) ===")
        for detection in detections:
            class_name = detection['class_name']
            coords = detection['coords']
            confidence = detection['confidence']
            index = detection['index']
            x1, y1, x2, y2 = coords
            print(f"{class_name}_{index}: 左上角({x1}, {y1}) -> 右下角({x2}, {y2}) [置信度: {confidence:.2f}]")
    else:
        print("未检测到任何目标")


if __name__ == "__main__":
    main()