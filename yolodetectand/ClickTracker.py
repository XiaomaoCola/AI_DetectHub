import time
import ctypes
import re
import tkinter as tk
from tkinter import messagebox, ttk
import win32gui
import win32con
import pyautogui
import threading
from pynput import mouse


class BlueStacksClickCalibrator:
    def __init__(self, window_keyword="BlueStacks"):
        """
        BlueStacks点击坐标标定工具
        用于找到BlueStacks窗口位置，并计算点击位置在窗口中的相对坐标
        """
        self.window_keyword = window_keyword
        self.bluestacks_rect = None
        self.bluestacks_hwnd = None
        self.click_positions = []
        
        # 设置高DPI感知
        ctypes.windll.user32.SetProcessDPIAware()
        
        # 创建GUI
        self.setup_gui()
        
    def find_bluestacks_window(self):
        """仅查找BlueStacks客户区信息"""
        hwnd_list = []
        
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(self.window_keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))
        
        win32gui.EnumWindows(enum_handler, None)
        
        if hwnd_list:
            target_hwnd, title = hwnd_list[0]
            
            # 只获取客户区信息
            client_rect = win32gui.GetClientRect(target_hwnd)  # (0, 0, width, height)
            client_width = client_rect[2]
            client_height = client_rect[3]
            
            # 客户区左上角在屏幕上的位置
            client_screen_pos = win32gui.ClientToScreen(target_hwnd, (0, 0))
            client_left, client_top = client_screen_pos
            client_right = client_left + client_width
            client_bottom = client_top + client_height
            
            # 保存客户区坐标 (left, top, right, bottom)
            self.bluestacks_rect = (client_left, client_top, client_right, client_bottom)
            self.bluestacks_hwnd = target_hwnd
            
            debug_info = {
                'client_left': client_left,
                'client_top': client_top,
                'client_width': client_width,
                'client_height': client_height,
                'client_right': client_right,
                'client_bottom': client_bottom
            }
            
            return True, title, (client_left, client_top, client_right, client_bottom), debug_info
        else:
            return False, None, None, None
    
    def setup_gui(self):
        """设置GUI界面"""
        self.root = tk.Tk() # 创建主 GUI 窗口
        self.root.title("相对坐标检测工具") # 设置窗口标题
        self.root.geometry("600x700") # 设置初始窗口大小为 600 宽 × 700 高
        
        # 状态显示区域
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(status_frame, text="BlueStacks状态:").pack(anchor="w")
        self.status_label = ttk.Label(status_frame, text="未检测", foreground="red")
        self.status_label.pack(anchor="w")
        
        # 窗口信息显示
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text="窗口信息:").pack(anchor="w")
        self.info_text = tk.Text(info_frame, height=4, state="disabled")
        self.info_text.pack(fill="x")
        
        # 控制按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.detect_btn = ttk.Button(button_frame, text="检测BlueStacks窗口", command=self.detect_window)
        self.detect_btn.pack(side="left", padx=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="开始监听点击", command=self.start_listening, state="disabled")
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="停止监听", command=self.stop_listening, state="disabled")
        self.stop_btn.pack(side="left")
        
        # 说明文字
        instruction_frame = ttk.Frame(self.root)
        instruction_frame.pack(fill="x", padx=10, pady=5)
        
        instruction_text = """使用说明:
1. 先点击"检测BlueStacks窗口"按钮
2. 点击"开始监听点击"
3. 在BlueStacks中点击你想要标定的位置
4. 查看下方的相对坐标结果
5. 点击"停止监听"结束标定"""
        
        ttk.Label(instruction_frame, text=instruction_text, justify="left").pack(anchor="w")
        
        # 点击记录区域
        record_frame = ttk.Frame(self.root)
        record_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(record_frame, text="点击记录:").pack(anchor="w")
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(record_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.record_text = tk.Text(text_frame, state="disabled")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.record_text.yview)
        self.record_text.configure(yscrollcommand=scrollbar.set)
        
        self.record_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 清除按钮
        clear_btn = ttk.Button(record_frame, text="清除记录", command=self.clear_records)
        clear_btn.pack(pady=5)
        
        self.listening = False
        
    def detect_window(self):
        """检测BlueStacks窗口并显示详细信息"""
        result = self.find_bluestacks_window()
        
        if result[0]:  # found
            found, title, rect, debug_info = result
            self.status_label.config(text=f"已找到: {title}", foreground="green")
            
            left, top, right, bottom = rect
            width, height = right - left, bottom - top
            
            info = f"窗口标题: {title}\n"
            info += f"客户区左上角: ({left}, {top})\n"
            info += f"客户区大小: {width} x {height}\n"
            info += f"客户区范围: ({left}, {top}) - ({right}, {bottom})\n"
            info += f"相对坐标: (0, 0) - ({width}, {height})"
            
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            self.info_text.config(state="disabled")
            
            self.start_btn.config(state="normal")
            
            # 在控制台输出客户区信息
            print(f"\n=== BlueStacks客户区检测 ===")
            print(f"窗口: {title}")
            print(f"客户区左上角: ({debug_info['client_left']}, {debug_info['client_top']})")
            print(f"客户区大小: {debug_info['client_width']} x {debug_info['client_height']}")
            print(f"客户区右下角: ({debug_info['client_right']}, {debug_info['client_bottom']})")
            print(f"相对坐标范围: (0, 0) - ({debug_info['client_width']}, {debug_info['client_height']})")
            print("=" * 50)
            
        else:
            self.status_label.config(text="未找到BlueStacks窗口", foreground="red")
            messagebox.showerror("错误", f"未找到标题包含'{self.window_keyword}'的窗口，请确保BlueStacks已打开")
    
    def start_listening(self):
        """开始监听点击"""
        if not self.bluestacks_rect:
            messagebox.showerror("错误", "请先检测BlueStacks窗口")
            return
        
        self.listening = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.detect_btn.config(state="disabled")
        
        self.add_record("=== 开始监听点击 ===")
        self.add_record("请在BlueStacks中点击想要标定的位置")
        self.add_record("注意：只会记录BlueStacks窗口内的点击")
        
        print("\n开始监听鼠标点击...")
        print("只会记录BlueStacks窗口内的点击")
        if self.bluestacks_rect:
            print(f"BlueStacks窗口范围: {self.bluestacks_rect}")
        
        # 使用pynput监听鼠标点击
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
    
    def stop_listening(self):
        """停止监听点击"""
        self.listening = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.detect_btn.config(state="normal")
        
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        
        self.add_record("=== 停止监听 ===")
        print("停止监听鼠标点击")
    
    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理，只处理BlueStacks窗口内的点击"""
        if not self.listening or not pressed:  # 只处理按下事件
            return
        
        # 检查点击是否在BlueStacks窗口内
        if self.bluestacks_rect:
            left, top, right, bottom = self.bluestacks_rect
            if left <= x <= right and top <= y <= bottom:
                # 在主线程中处理点击
                self.root.after_idle(lambda: self.process_click(x, y))
    
    def process_click(self, screen_x, screen_y):
        """处理BlueStacks窗口内的点击事件"""
        if not self.bluestacks_rect:
            return
        
        left, top, right, bottom = self.bluestacks_rect
        window_width = right - left
        window_height = bottom - top
        
        # 计算相对坐标
        relative_x = screen_x - left
        relative_y = screen_y - top
        
        # 计算标准化相对坐标 (0-1范围)
        normalized_x = relative_x / window_width
        normalized_y = relative_y / window_height
        
        # 记录点击
        record = f"屏幕坐标: ({screen_x}, {screen_y}) -> BlueStacks相对坐标: ({relative_x}, {relative_y}) -> 标准化坐标: ({normalized_x:.4f}, {normalized_y:.4f})"
        self.add_record(record)
        
        # 保存到列表中
        self.click_positions.append({
            'screen': (screen_x, screen_y),
            'relative': (relative_x, relative_y),
            'normalized': (normalized_x, normalized_y),
            'timestamp': time.time()
        })
        
        # 在控制台也输出
        print(f"点击检测: 屏幕({screen_x}, {screen_y}) -> 相对({relative_x}, {relative_y}) -> 标准化({normalized_x:.4f}, {normalized_y:.4f})")
    
    def add_record(self, text):
        """添加记录到文本框"""
        self.record_text.config(state="normal")
        self.record_text.insert(tk.END, f"{text}\n")
        self.record_text.see(tk.END)
        self.record_text.config(state="disabled")
    
    def clear_records(self):
        """清除记录"""
        self.record_text.config(state="normal")
        self.record_text.delete(1.0, tk.END)
        self.record_text.config(state="disabled")
        self.click_positions.clear()
    
    def get_click_positions(self):
        """获取所有点击位置"""
        return self.click_positions.copy()
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


class SimpleClickDetector:
    """简化版的点击检测器，用于脚本调用"""
    
    def __init__(self, window_keyword="BlueStacks"):
        self.window_keyword = window_keyword
        ctypes.windll.user32.SetProcessDPIAware()
    
    def find_bluestacks_window(self):
        """查找BlueStacks客户区"""
        hwnd_list = []
        
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(self.window_keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))
        
        win32gui.EnumWindows(enum_handler, None)
        
        if hwnd_list:
            target_hwnd, title = hwnd_list[0]
            client_rect = win32gui.GetClientRect(target_hwnd)
            pt = win32gui.ClientToScreen(target_hwnd, (0, 0))
            left, top = pt
            right, bottom = left + client_rect[2], top + client_rect[3]
            return (left, top, right, bottom), title
        return None, None
    
    def screen_to_relative(self, screen_x, screen_y):
        """将屏幕坐标转换为BlueStacks相对坐标"""
        rect, title = self.find_bluestacks_window()
        if not rect:
            return None, "BlueStacks窗口未找到"
        
        left, top, right, bottom = rect
        
        if left <= screen_x <= right and top <= screen_y <= bottom:
            relative_x = screen_x - left
            relative_y = screen_y - top
            return (relative_x, relative_y), f"窗口: {title}"
        else:
            return None, "点击位置不在BlueStacks窗口内"
    
    def relative_to_screen(self, relative_x, relative_y):
        """将BlueStacks相对坐标转换为屏幕坐标"""
        rect, title = self.find_bluestacks_window()
        if not rect:
            return None, "BlueStacks窗口未找到"
        
        left, top, right, bottom = rect
        screen_x = left + relative_x
        screen_y = top + relative_y
        
        return (screen_x, screen_y), f"窗口: {title}"


if __name__ == "__main__":
    # 运行GUI版本
    calibrator = BlueStacksClickCalibrator()
    calibrator.run()
    
    # 也可以这样使用简化版本:
    # detector = SimpleClickDetector()
    # relative_pos, info = detector.screen_to_relative(100, 200)
    # if relative_pos:
    #     print(f"相对坐标: {relative_pos}, {info}")