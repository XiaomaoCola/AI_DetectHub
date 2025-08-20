import time
import ctypes
import re
from typing import List, Tuple

import cv2
import numpy as np
from mss import mss
from ultralytics import YOLO
import win32gui


class ModelTester:
    def __init__(self, model_path, window_keyword="BlueStacks", conf_thres=0.5):
        self.model_path = model_path
        self.window_keyword = window_keyword
        self.conf_thres = conf_thres
        
        # 处理高DPI缩放
        ctypes.windll.user32.SetProcessDPIAware()
        
        # 初始化
        self.model = None
        self.sct = None
        
        # 类别名称映射（从data.yaml读取）
        self.class_names = {
            0: "attack",
            1: "find_now"
        }
        
        # 为每个类别分配不同颜色
        self.colors = [
            (0, 255, 0),      # 绿色 - attack
            (255, 0, 0),      # 蓝色 - find_now
            (0, 0, 255),      # 红色 - 其他类别
            (255, 255, 0),    # 青色
            (255, 0, 255),    # 紫色
            (0, 255, 255),    # 黄色
            (128, 0, 255),    # 紫红色
            (255, 128, 0),    # 橙色
        ]

    def find_window_rect(self, keyword: str):
        """查找并返回BlueStacks窗口的客户区坐标"""
        hwnd_list = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))

        win32gui.EnumWindows(enum_handler, None)

        if hwnd_list:
            target_hwnd, _ = hwnd_list[0]
        else:
            return None

        rect = win32gui.GetClientRect(target_hwnd)
        pt = win32gui.ClientToScreen(target_hwnd, (0, 0))
        left, top = pt
        right, bottom = left + rect[2], top + rect[3]
        return (left, top, right, bottom), target_hwnd

    def detect_all_objects(self, frame) -> List[Tuple]:
        """检测画面中的所有目标对象，返回所有检测结果"""
        results = self.model.predict(frame, imgsz=640, conf=self.conf_thres, verbose=False)[0]
        
        detections = []
        
        if results.boxes is not None and len(results.boxes) > 0:
            xyxy = results.boxes.xyxy.cpu().numpy().astype(int)
            cls = results.boxes.cls.cpu().numpy().astype(int)
            conf = results.boxes.conf.cpu().numpy()
            
            for (x1, y1, x2, y2), c, p in zip(xyxy, cls, conf):
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'class_id': int(c),
                    'confidence': float(p),
                    'class_name': self.class_names.get(int(c), f"class_{int(c)}")
                })
        
        # 按置信度排序
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        return detections

    def draw_detections(self, frame, detections: List[Tuple]):
        """在画面上绘制所有检测结果"""
        overlay = frame.copy()
        
        # 统计每个类别的检测数量
        class_counts = {}
        
        for det in detections:
            bbox = det['bbox']
            class_id = det['class_id']
            confidence = det['confidence']
            class_name = det['class_name']
            
            x1, y1, x2, y2 = bbox
            
            # 选择颜色
            color = self.colors[class_id % len(self.colors)]
            
            # 绘制边界框
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            label = f"{class_name} {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # 标签背景
            cv2.rectangle(overlay, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # 标签文字
            cv2.putText(overlay, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # 统计数量
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # 显示统计信息
        info_y = 25
        cv2.putText(overlay, f"Total detections: {len(detections)}", 
                   (8, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        info_y += 25
        cv2.putText(overlay, f"Confidence threshold: {self.conf_thres}", 
                   (8, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # 显示各类别统计
        info_y += 30
        for class_name, count in class_counts.items():
            cv2.putText(overlay, f"{class_name}: {count}", 
                       (8, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            info_y += 20
        
        # 显示帮助信息
        help_y = overlay.shape[0] - 60
        help_text = [
            "Controls:",
            "ESC - Exit",
            "+/- - Adjust confidence threshold",
            "SPACE - Pause/Resume"
        ]
        
        for i, text in enumerate(help_text):
            cv2.putText(overlay, text, (8, help_y + i * 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return overlay

    def run_test(self):
        """运行模型测试"""
        print("[INFO] 启动模型测试器...")
        print(f"[INFO] 模型路径: {self.model_path}")
        print("[INFO] 加载YOLO模型...")
        
        try:
            self.model = YOLO(self.model_path)
            print(f"[INFO] 模型加载成功，类别数: {len(self.model.names)}")
            
            # 更新类别名称映射
            if hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
                print(f"[INFO] 类别映射: {self.class_names}")
        except Exception as e:
            print(f"[ERROR] 模型加载失败: {e}")
            return

        self.sct = mss()

        # 查找游戏窗口
        window_info = self.find_window_rect(self.window_keyword)
        if not window_info:
            print(f"[ERROR] 未找到标题包含 '{self.window_keyword}' 的窗口")
            return

        (L, T, R, B), hwnd = window_info
        W, H = R - L, B - T
        print(f"[INFO] 游戏窗口: ({L},{T})-({R},{B}) size={W}x{H}")
        print("[INFO] 控制键: ESC=退出, +/-=调整置信度, SPACE=暂停")

        paused = False
        fps_counter = 0
        fps_start_time = time.time()

        while True:
            try:
                if not paused:
                    # 截取游戏画面
                    region = {"left": L, "top": T, "width": W, "height": H}
                    frame = np.array(self.sct.grab(region))[:, :, :3]

                    # 检测所有目标
                    detections = self.detect_all_objects(frame)

                    # 绘制检测结果
                    display_frame = self.draw_detections(frame, detections)
                    
                    # 计算FPS
                    fps_counter += 1
                    current_time = time.time()
                    if current_time - fps_start_time >= 1.0:
                        fps = fps_counter / (current_time - fps_start_time)
                        fps_start_time = current_time
                        fps_counter = 0
                        
                        # 显示FPS
                        cv2.putText(display_frame, f"FPS: {fps:.1f}", 
                                   (display_frame.shape[1] - 120, 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.imshow("Model Tester - All Detections", display_frame)

                    # 动态更新窗口坐标
                    window_info = self.find_window_rect(self.window_keyword)
                    if window_info:
                        (L, T, R, B), _ = window_info
                        W, H = R - L, B - T

                # 处理按键
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC - 退出
                    break
                elif key == ord('+') or key == ord('='):  # 增加置信度
                    self.conf_thres = min(0.95, self.conf_thres + 0.05)
                    print(f"[INFO] 置信度调整为: {self.conf_thres:.2f}")
                elif key == ord('-'):  # 降低置信度
                    self.conf_thres = max(0.1, self.conf_thres - 0.05)
                    print(f"[INFO] 置信度调整为: {self.conf_thres:.2f}")
                elif key == ord(' '):  # 空格 - 暂停/继续
                    paused = not paused
                    print(f"[INFO] {'暂停' if paused else '继续'}")

            except Exception as e:
                print(f"[ERROR] 发生错误: {e}")
                time.sleep(1)
                continue

        cv2.destroyAllWindows()
        print("[INFO] 测试结束")


if __name__ == "__main__":
    # 创建测试器实例
    tester = ModelTester(
        model_path=r"D:\python-project\AI_DetectHub\runs\detect\train\weights\best.pt",
        window_keyword="BlueStacks",
        conf_thres=0.5  # 起始置信度阈值
    )
    
    # 运行测试
    tester.run_test()