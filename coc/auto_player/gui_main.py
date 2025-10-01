#!/usr/bin/env python3
"""
COC自动化程序 - GUI界面
提供友好的图形界面来管理不同的游戏模式和任务
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

from core import COCGameController
from coc.auto_player.features.GameMode import GameMode


class COCAutoGUI:
    """COC自动化程序GUI界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.controller: Optional[COCGameController] = None
        # 使用全局模式管理器
        # self.mode_manager = mode_manager (已经是全局实例)
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        self.setup_ui()
        self.setup_default_config()
        
    def setup_ui(self):
        """设置UI界面"""
        self.root.title("COC 自动化控制器 v1.0")
        self.root.geometry("800x600")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置区域
        self.create_config_section(main_frame)
        
        # 模式选择区域
        self.create_mode_section(main_frame)
        
        # 任务管理区域
        self.create_task_section(main_frame)
        
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
        mode_frame = ttk.LabelFrame(parent, text="游戏模式", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value=GameMode.HOME_VILLAGE.value)
        
        ttk.Radiobutton(mode_frame, text="主村庄 (Home Village)", 
                       variable=self.mode_var, value=GameMode.HOME_VILLAGE.value).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="建筑工人基地 (Builder Base)", 
                       variable=self.mode_var, value=GameMode.BUILDER_BASE.value).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="自动切换模式", 
                       variable=self.mode_var, value=GameMode.AUTO_SWITCH.value).pack(anchor=tk.W)
        
    def create_task_section(self, parent):
        """创建任务管理区域"""
        task_frame = ttk.LabelFrame(parent, text="任务管理", padding=10)
        task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 任务选择
        task_select_frame = ttk.Frame(task_frame)
        task_select_frame.pack(fill=tk.X)
        
        ttk.Label(task_select_frame, text="选择任务:").pack(side=tk.LEFT)
        self.task_var = tk.StringVar(value=TaskType.ATTACK_CYCLE.value)
        task_combo = ttk.Combobox(task_select_frame, textvariable=self.task_var, 
                                 values=[t.value for t in TaskType], state="readonly")
        task_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(task_select_frame, text="添加任务", command=self.add_task).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(task_select_frame, text="清空任务", command=self.clear_tasks).pack(side=tk.LEFT, padx=(5, 0))
        
        # 任务列表
        self.task_listbox = tk.Listbox(task_frame, height=6)
        self.task_listbox.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 任务描述
        task_descriptions = {
            TaskType.COLLECT_RESOURCES.value: "自动收集村庄中的资源（金币、圣水等）",
            TaskType.ATTACK_CYCLE.value: "自动进行攻击循环（找对手→攻击→投降→返回）",
            TaskType.UPGRADE_BUILDINGS.value: "自动升级建筑（需要足够资源）",
            TaskType.TRAIN_TROOPS.value: "自动训练部队",
            TaskType.CUSTOM_TASK.value: "自定义任务"
        }
        
        self.task_desc_var = tk.StringVar(value=task_descriptions[TaskType.ATTACK_CYCLE.value])
        ttk.Label(task_frame, textvariable=self.task_desc_var, wraplength=400).pack(pady=(5, 0))
        
        # 绑定任务选择事件
        def on_task_select(event):
            selected = self.task_var.get()
            self.task_desc_var.set(task_descriptions.get(selected, ""))
            
        task_combo.bind("<<ComboboxSelected>>", on_task_select)
        
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="▶ 开始", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ 停止", command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_btn = ttk.Button(control_frame, text="🔍 测试检测", command=self.test_detection)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(control_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.RIGHT)
        
    def create_log_section(self, parent):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(parent, text="运行日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_default_config(self):
        """设置默认配置"""
        self.add_default_tasks()
        
    def add_default_tasks(self):
        """添加默认任务"""
        self.add_task_to_queue(TaskType.ATTACK_CYCLE, "自动攻击循环")
        
    def browse_model(self):
        """浏览模型文件"""
        filename = filedialog.askopenfilename(
            title="选择YOLO模型文件",
            filetypes=[("PyTorch模型", "*.pt"), ("所有文件", "*.*")]
        )
        if filename:
            self.model_path_var.set(filename)
            
    def add_task(self):
        """添加任务到队列"""
        task_type_str = self.task_var.get()
        task_type = TaskType(task_type_str)
        
        task_names = {
            TaskType.COLLECT_RESOURCES: "收集资源",
            TaskType.ATTACK_CYCLE: "攻击循环", 
            TaskType.UPGRADE_BUILDINGS: "升级建筑",
            TaskType.TRAIN_TROOPS: "训练部队",
            TaskType.CUSTOM_TASK: "自定义任务"
        }
        
        task_name = task_names.get(task_type, task_type.value)
        self.add_task_to_queue(task_type, task_name)
        
    def add_task_to_queue(self, task_type: TaskType, display_name: str):
        """添加任务到队列"""
        self.mode_manager.add_task(task_type)
        self.task_listbox.insert(tk.END, f"• {display_name}")
        self.log_message(f"添加任务: {display_name}")
        
    def clear_tasks(self):
        """清空任务队列"""
        self.mode_manager.active_tasks.clear()
        self.task_listbox.delete(0, tk.END)
        self.log_message("清空所有任务")
        
    def start_automation(self):
        """开始自动化"""
        if self.is_running:
            return
            
        # 验证配置
        model_path = self.model_path_var.get().strip()
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("错误", "请选择有效的YOLO模型文件")
            return
            
        if not self.mode_manager.active_tasks:
            messagebox.showerror("错误", "请至少添加一个任务")
            return
            
        # 设置游戏模式
        selected_mode = GameMode(self.mode_var.get())
        self.mode_manager.set_mode(selected_mode)
        
        # 创建控制器
        try:
            self.controller = COCGameController(
                model_path=model_path,
                window_keyword=self.window_var.get(),
                config_path=None  # 使用默认配置路径
            )
            self.log_message("初始化控制器成功")
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
        self.log_message("自动化程序已启动")
        
    def stop_automation(self):
        """停止自动化"""
        self.is_running = False
        
        # 更新UI状态
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("已停止")
        self.log_message("自动化程序已停止")
        
    def test_detection(self):
        """测试检测功能"""
        model_path = self.model_path_var.get().strip()
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("错误", "请选择有效的YOLO模型文件")
            return
            
        self.log_message("启动检测测试...")
        
        # 在新线程中运行测试
        def run_test():
            try:
                from tools.model_tester import ModelTester
                tester = ModelTester(
                    model_path=model_path,
                    window_keyword=self.window_var.get()
                )
                tester.run_test()
            except Exception as e:
                self.log_message(f"测试失败: {e}")
                
        threading.Thread(target=run_test, daemon=True).start()
        
    def automation_worker(self):
        """自动化工作线程"""
        try:
            # 这里集成实际的自动化逻辑
            # 暂时用简单的循环模拟
            while self.is_running:
                current_task = self.mode_manager.get_current_task()
                if current_task:
                    task_type = current_task['type']
                    self.log_message(f"执行任务: {task_type.value}")
                    
                    # 模拟任务执行
                    time.sleep(5)
                    
                    self.mode_manager.complete_current_task()
                    self.log_message(f"完成任务: {task_type.value}")
                else:
                    self.log_message("所有任务已完成")
                    break
                    
                time.sleep(1)
                
        except Exception as e:
            self.log_message(f"工作线程异常: {e}")
        finally:
            self.is_running = False
            
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
    print("启动COC自动化程序GUI...")
    
    try:
        app = COCAutoGUI()
        app.run()
    except Exception as e:
        print(f"程序异常: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())