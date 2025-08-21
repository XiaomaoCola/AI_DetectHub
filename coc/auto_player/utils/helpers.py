"""
通用工具函数模块
"""

import time
import cv2
import numpy as np
from typing import Tuple, List
from pathlib import Path


def ensure_directory(path: str) -> Path:
    """确保目录存在，如果不存在则创建"""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def format_duration(seconds: float) -> str:
    """格式化时间长度为可读字符串"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def calculate_center(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """计算边界框的中心点"""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) // 2, (y1 + y2) // 2)


def calculate_area(bbox: Tuple[int, int, int, int]) -> int:
    """计算边界框的面积"""
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)


def is_point_in_bbox(point: Tuple[int, int], bbox: Tuple[int, int, int, int]) -> bool:
    """检查点是否在边界框内"""
    x, y = point
    x1, y1, x2, y2 = bbox
    return x1 <= x <= x2 and y1 <= y <= y2


def resize_image_keep_aspect(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """保持宽高比调整图像大小"""
    target_width, target_height = target_size
    h, w = image.shape[:2]
    
    # 计算缩放比例
    scale = min(target_width / w, target_height / h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    # 调整大小
    resized = cv2.resize(image, (new_w, new_h))
    
    # 创建目标大小的黑色背景
    result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    # 居中放置调整后的图像
    y_offset = (target_height - new_h) // 2
    x_offset = (target_width - new_w) // 2
    result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return result


def draw_fps(image: np.ndarray, fps: float, position: Tuple[int, int] = (10, 30)) -> np.ndarray:
    """在图像上绘制FPS信息"""
    fps_text = f"FPS: {fps:.1f}"
    cv2.putText(image, fps_text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 255, 0), 2)
    return image


def safe_division(a: float, b: float, default: float = 0.0) -> float:
    """安全除法，避免除零错误"""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


class FPSCounter:
    """FPS计数器"""
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.frame_count = 0
        self.last_time = time.time()
        self.current_fps = 0.0
        
    def update(self) -> float:
        """更新FPS计数并返回当前FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        elapsed = current_time - self.last_time
        if elapsed >= self.update_interval:
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_time = current_time
            
        return self.current_fps
        
    def get_fps(self) -> float:
        """获取当前FPS"""
        return self.current_fps


class Timer:
    """简单计时器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        self.end_time = None
        
    def stop(self) -> float:
        """停止计时并返回经过的时间"""
        if self.start_time is None:
            return 0.0
        self.end_time = time.time()
        return self.end_time - self.start_time
        
    def elapsed(self) -> float:
        """获取经过的时间（不停止计时）"""
        if self.start_time is None:
            return 0.0
        current_time = self.end_time or time.time()
        return current_time - self.start_time
        
    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.end_time = None