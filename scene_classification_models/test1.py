import sys
import os
import time
import cv2
import numpy as np
from pathlib import Path
import win32gui
import win32con
import re
from mss import mss
import ctypes

# 添加父目录到路径，以便导入其他模块
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 导入场景预测器
from scene_classification_models.ScenePredictor import ScenePredictor


class COCRealtimeStateDetector:
    """COC实时状态检测器"""
    
    def __init__(self, window_keyword="BlueStacks"):
        """
        初始化实时状态检测器
        
        Args:
            window_keyword: 窗口关键词，默认BlueStacks
        """
        self.window_keyword = window_keyword
        self.scene_predictor = None
        self.sct = None
        
        # 处理高DPI缩放
        ctypes.windll.user32.SetProcessDPIAware()
        
        # 初始化组件
        self.init_components()
        
        print(f"[INFO] COC实时状态检测器已初始化")
        print(f"[INFO] 目标窗口关键词: {window_keyword}")
    
    def init_components(self):
        """初始化各个组件"""
        try:
            # 初始化场景预测器
            self.scene_predictor = ScenePredictor()
            if not self.scene_predictor.is_loaded():
                print("[ERROR] 场景分类模型加载失败")
                return False
            
            # 初始化截图工具
            self.sct = mss()
            
            print("[INFO] 所有组件初始化完成")
            return True
            
        except Exception as e:
            print(f"[ERROR] 组件初始化失败: {e}")
            return False
    
    def find_bluestacks_window(self):
        """
        查找BlueStacks窗口并置顶（基于原代码）
        
        Returns:
            tuple: (window_rect, title) 或 (None, None)
        """
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
            except Exception as e:
                print(f"[WARNING] 无法置顶窗口: {e}")
            
            # 获取客户区坐标
            rect = win32gui.GetClientRect(target_hwnd)
            pt = win32gui.ClientToScreen(target_hwnd, (0, 0))
            left, top = pt
            right, bottom = left + rect[2], top + rect[3]
            return (left, top, right, bottom), title
        else:
            return None, None
    
    def capture_screenshot(self):
        """
        截取BlueStacks窗口截图
        
        Returns:
            np.ndarray: 截图数组，失败返回None
        """
        try:
            # 查找窗口
            window_rect, title = self.find_bluestacks_window()
            if not window_rect:
                print("[ERROR] 未找到BlueStacks窗口")
                return None
            
            # 截图
            left, top, right, bottom = window_rect
            width, height = right - left, bottom - top
            
            region = {"left": left, "top": top, "width": width, "height": height}
            frame = np.array(self.sct.grab(region))[:, :, :3]  # BGRA -> BGR
            
            return frame
            
        except Exception as e:
            print(f"[ERROR] 截图失败: {e}")
            return None
    
    def detect_current_state(self):
        """
        检测当前COC状态
        
        Returns:
            dict: 检测结果
        """
        result = {
            "state": "unknown",
            "confidence": 0.0,
            "timestamp": time.time(),
            "reliable": False
        }
        
        try:
            # 截取当前画面
            screenshot = self.capture_screenshot()
            if screenshot is None:
                return result
            
            # 场景分类预测
            if self.scene_predictor and self.scene_predictor.is_loaded():
                scene, confidence = self.scene_predictor.predict_single(screenshot)
                
                result["state"] = scene
                result["confidence"] = confidence
                result["reliable"] = confidence > 0.7  # 置信度阈值
                
                return result
            else:
                print("[ERROR] 场景分类器未加载")
                return result
                
        except Exception as e:
            print(f"[ERROR] 状态检测失败: {e}")
            return result
    
    def run_realtime_detection(self, interval=2, show_preview=False):
        """
        运行实时检测
        
        Args:
            interval: 检测间隔（秒）
            show_preview: 是否显示预览窗口
        """
        print(f"[INFO] 开始实时检测，检测间隔: {interval}秒")
        print(f"[INFO] 支持的状态类别: {self.scene_predictor.get_class_names()}")
        print("[INFO] 按 Ctrl+C 停止检测")
        print("=" * 50)
        
        try:
            while True:
                # 检测当前状态
                result = self.detect_current_state()
                
                # 显示结果
                timestamp = time.strftime("%H:%M:%S", time.localtime(result["timestamp"]))
                state = result["state"]
                confidence = result["confidence"]
                reliable = "✅" if result["reliable"] else "❌"
                
                print(f"[{timestamp}] 状态: {state:15} | 置信度: {confidence:.3f} | 可靠: {reliable}")
                
                # 可选：显示预览窗口
                if show_preview:
                    screenshot = self.capture_screenshot()
                    if screenshot is not None:
                        # 调整图片大小用于显示
                        display_img = cv2.resize(screenshot, (400, 300))
                        
                        # 在图片上添加文字
                        text = f"{state} ({confidence:.2f})"
                        cv2.putText(display_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.7, (0, 255, 0) if result["reliable"] else (0, 0, 255), 2)
                        
                        cv2.imshow("COC State Detection", display_img)
                        cv2.waitKey(1)  # 非阻塞等待
                
                # 等待下次检测
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n[INFO] 检测已停止")
        finally:
            if show_preview:
                cv2.destroyAllWindows()


def main():
    """主函数"""
    print("COC夜世界实时状态检测器")
    print("=" * 30)
    
    # 创建检测器
    detector = COCRealtimeStateDetector(window_keyword="BlueStacks")
    
    # 检查初始化状态
    if not detector.scene_predictor or not detector.scene_predictor.is_loaded():
        print("[ERROR] 初始化失败，请确保模型文件存在")
        return
    
    print("\n选择模式:")
    print("1. 纯文字输出 (推荐)")
    print("2. 带预览窗口")
    
    try:
        choice = input("请选择模式 (1 或 2): ").strip()
        show_preview = choice == "2"
        
        interval = float(input("检测间隔 (秒，默认2): ") or "2")
        
    except (ValueError, KeyboardInterrupt):
        print("\n使用默认设置...")
        show_preview = False
        interval = 2
    
    print(f"\n启动实时检测...")
    
    # 开始实时检测
    detector.run_realtime_detection(interval=interval, show_preview=show_preview)


if __name__ == "__main__":
    main()