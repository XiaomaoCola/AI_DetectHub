#!/usr/bin/env python3
"""
COC自动化程序 - 简化GUI界面
只保留 Mode 选择功能，遵循 Mode → State 架构
"""

import sys
import threading
import time
from pathlib import Path
from typing import Optional

# GUI相关导入
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import tkinter.scrolledtext as scrolledtext
except ImportError:
    print("[ERROR] 请安装tkinter: pip install tk")
    sys.exit(1)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core import COCGameController, GameMode


class COCSimpleGUI:
    """COC自动化程序简化GUI界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.controller: Optional[COCGameController] = None
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        self.root.title("COC 自动化控制器 - 简化版")
        self.root.geometry("700x500")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置区域
        self.create_config_section(main_frame)
        
        # 模式选择区域
        self.create_mode_section(main_frame)
        
        # 控制按钮区域
        self.create_control_section(main_frame)
        
        # 日志区域
        self.create_log_section(main_frame)
        
    def create_config_section(self, parent):
        """创建配置区域"""
        config_frame = ttk.LabelFrame(parent, text="基础配置", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 模型路径
        ttk.Label(config_frame, text="YOLO模型路径:").grid(row=0, column=0, sticky=tk.W)
        self.model_path_var = tk.StringVar(value="D:/python-project/AI_DetectHub/runs/detect/train/weights/best.pt")
        model_entry = ttk.Entry(config_frame, textvariable=self.model_path_var, width=50)
        model_entry.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        ttk.Button(config_frame, text="浏览", command=self.browse_model).grid(row=0, column=2, padx=(5, 0))
        
        # 窗口关键词
        ttk.Label(config_frame, text="游戏窗口:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.window_var = tk.StringVar(value="BlueStacks")
        ttk.Entry(config_frame, textvariable=self.window_var, width=20).grid(row=1, column=1, padx=(5, 0), sticky=tk.W, pady=(5, 0))
        
    def create_mode_section(self, parent):
        """创建模式选择区域"""
        mode_frame = ttk.LabelFrame(parent, text="游戏模式选择", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value=GameMode.BUILDER_BASE.value)
        
        # 模式选择
        mode_info_frame = ttk.Frame(mode_frame)
        mode_info_frame.pack(fill=tk.X)
        
        ttk.Radiobutton(mode_info_frame, text="🏠 主村庄 (Home Village)", 
                       variable=self.mode_var, value=GameMode.HOME_VILLAGE.value).pack(anchor=tk.W, pady=2)
        ttk.Label(mode_info_frame, text="     • 传统攻击循环、收集资源、训练部队", 
                 foreground="gray").pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Radiobutton(mode_info_frame, text="🏗️ 建筑工人基地 (Builder Base)", 
                       variable=self.mode_var, value=GameMode.BUILDER_BASE.value).pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(mode_info_frame, text="     • 夜世界攻击、收集资源、升级建筑", 
                 foreground="gray").pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Radiobutton(mode_info_frame, text="🔄 自动切换模式", 
                       variable=self.mode_var, value=GameMode.AUTO_SWITCH.value).pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(mode_info_frame, text="     • 程序自动检测当前界面并切换模式", 
                 foreground="gray").pack(anchor=tk.W, padx=(20, 0))
        
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="▶ 开始自动化", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ 停止", command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_btn = ttk.Button(control_frame, text="🔍 测试检测", command=self.test_detection)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(side=tk.RIGHT)
        
    def create_log_section(self, parent):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(parent, text="运行日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_model(self):
        """浏览模型文件"""
        filename = filedialog.askopenfilename(
            title="选择YOLO模型文件",
            filetypes=[("PyTorch模型", "*.pt"), ("所有文件", "*.*")]
        )
        if filename:
            self.model_path_var.set(filename)
            
    def start_automation(self):
        """开始自动化"""
        if self.is_running:
            return
            
        # 验证配置
        model_path = self.model_path_var.get().strip()
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("错误", "请选择有效的YOLO模型文件")
            return
            
        # 创建控制器
        try:
            self.controller = COCGameController(
                model_path=model_path,
                window_keyword=self.window_var.get(),
                config_path=None  # 使用默认配置路径
            )
            
            # 设置游戏模式
            selected_mode = GameMode(self.mode_var.get())
            self.controller.mode_manager.set_mode(selected_mode)
            
            self.log_message(f"初始化控制器成功，模式: {selected_mode.value}")
        except Exception as e:
            messagebox.showerror("错误", f"初始化失败: {e}")
            return
            
        # 启动工作线程
        self.is_running = True
        self.worker_thread = threading.Thread(target=self.automation_worker, daemon=True)
        self.worker_thread.start()
        
        # 更新UI状态
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("运行中...")
        self.log_message("🚀 自动化程序已启动")
        
    def stop_automation(self):
        """停止自动化"""
        self.is_running = False
        
        # 更新UI状态
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("已停止")
        self.log_message("⏹ 自动化程序已停止")
        
    def test_detection(self):
        """测试检测功能"""
        model_path = self.model_path_var.get().strip()
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("错误", "请选择有效的YOLO模型文件")
            return
            
        self.log_message("🔍 启动检测测试...")
        
        # 在新线程中运行测试
        def run_test():
            try:
                # 检查是否存在model_tester
                tester_path = Path(__file__).parent / "tools" / "model_tester.py"
                if tester_path.exists():
                    from tools.model_tester import ModelTester
                    tester = ModelTester(
                        model_path=model_path,
                        window_keyword=self.window_var.get()
                    )
                    tester.run_test()
                else:
                    self.log_message("⚠️ model_tester.py 不存在，请手动测试")
            except Exception as e:
                self.log_message(f"❌ 测试失败: {e}")
                
        threading.Thread(target=run_test, daemon=True).start()
        
    def automation_worker(self):
        """自动化工作线程 - 简化版"""
        try:
            self.log_message("🔧 初始化自动化控制器...")
            
            # 使用控制器的run方法（这是原本的实现）
            if self.controller:
                self.controller.run()
            
        except Exception as e:
            self.log_message(f"❌ 工作线程异常: {e}")
        finally:
            self.is_running = False
            # 在主线程中更新UI
            self.root.after(0, self.stop_automation)
            
    def log_message(self, message: str):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 在主线程中更新UI
        self.root.after(0, self._update_log, log_entry)
        
    def _update_log(self, log_entry: str):
        """更新日志显示（主线程）"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # 滚动到底部
        self.log_text.config(state=tk.DISABLED)
        
        # 限制日志长度
        lines = self.log_text.get("1.0", tk.END).split("\n")
        if len(lines) > 100:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", f"{len(lines)-50}.0")
            self.log_text.config(state=tk.DISABLED)
        
    def run(self):
        """运行GUI"""
        # 添加关闭事件处理
        def on_closing():
            if self.is_running:
                result = messagebox.askokcancel("退出", "程序正在运行，确定要退出吗？")
                if result:
                    self.stop_automation()
                    self.root.destroy()
            else:
                self.root.destroy()
                
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_automation()
            
        # 清理资源
        if self.worker_thread and self.worker_thread.is_alive():
            self.is_running = False
            self.worker_thread.join(timeout=2)


def main():
    """主函数"""
    print("启动COC自动化程序简化GUI...")
    
    try:
        app = COCSimpleGUI()
        app.run()
    except Exception as e:
        print(f"程序异常: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())