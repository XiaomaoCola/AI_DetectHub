import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import os
import sys

# 添加当前目录到路径，以便导入 renamer 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from renamer import Renamer


class RenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件批量重命名工具")
        self.root.geometry("600x500")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 文件路径选择
        ttk.Label(main_frame, text="图片文件夹路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar()
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_frame, text="浏览", command=self.browse_folder).grid(row=0, column=1)
        
        # 文件名前缀
        ttk.Label(main_frame, text="文件名前缀:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.prefix_var = tk.StringVar(value="renamed")
        ttk.Entry(main_frame, textvariable=self.prefix_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 起始编号
        ttk.Label(main_frame, text="起始编号:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.start_var = tk.StringVar(value="1")
        ttk.Entry(main_frame, textvariable=self.start_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 数字填充位数
        ttk.Label(main_frame, text="数字填充位数:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.zfill_var = tk.StringVar(value="3")
        ttk.Entry(main_frame, textvariable=self.zfill_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 文件扩展名
        ttk.Label(main_frame, text="文件扩展名:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ext_var = tk.StringVar(value=".png")
        ttk.Entry(main_frame, textvariable=self.ext_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="预览", command=self.preview_rename).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="开始重命名", command=self.execute_rename).pack(side=tk.LEFT)
        
        # 结果显示区域
        ttk.Label(main_frame, text="操作结果:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        
        # 创建滚动文本框
        self.result_text = scrolledtext.ScrolledText(main_frame, width=70, height=15)
        self.result_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 配置行权重以便文本框可以扩展
        main_frame.rowconfigure(7, weight=1)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            self.path_var.set(folder_path)
    
    def get_renamer_params(self):
        """获取重命名器参数"""
        try:
            img_dir = self.path_var.get().strip()
            prefix = self.prefix_var.get().strip()
            start = int(self.start_var.get())
            zfill = int(self.zfill_var.get())
            ext = self.ext_var.get().strip()
            
            if not img_dir:
                raise ValueError("请选择图片文件夹路径")
            if not prefix:
                raise ValueError("请输入文件名前缀")
            if not os.path.exists(img_dir):
                raise ValueError("指定的文件夹路径不存在")
                
            return img_dir, prefix, start, zfill, ext
            
        except ValueError as e:
            messagebox.showerror("参数错误", str(e))
            return None
    
    def preview_rename(self):
        """预览重命名结果"""
        params = self.get_renamer_params()
        if not params:
            return
            
        img_dir, prefix, start, zfill, ext = params
        
        # 清空结果显示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "=== 预览模式 ===\n\n")
        
        try:
            # 重定向输出到文本框
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            
            with contextlib.redirect_stdout(output_buffer):
                renamer = Renamer(
                    img_dir=img_dir,
                    prefix=prefix,
                    start=start,
                    zfill=zfill,
                    ext=ext
                )
                renamer.rename(dry_run=True)  # 预览模式
            
            # 获取输出内容并显示
            output_content = output_buffer.getvalue()
            self.result_text.insert(tk.END, output_content)
            self.result_text.insert(tk.END, "\n注意: 这只是预览，文件尚未被重命名。")
            
        except Exception as e:
            self.result_text.insert(tk.END, f"预览时发生错误: {str(e)}")
    
    def execute_rename(self):
        """执行重命名操作"""
        params = self.get_renamer_params()
        if not params:
            return
        
        img_dir, prefix, start, zfill, ext = params
        
        # 确认对话框
        result = messagebox.askyesno(
            "确认操作", 
            f"确定要重命名 {img_dir} 文件夹中的文件吗？\n\n"
            f"前缀: {prefix}\n"
            f"起始编号: {start}\n"
            f"填充位数: {zfill}\n"
            f"文件类型: {ext}\n\n"
            "此操作不可撤销！"
        )
        
        if not result:
            return
        
        # 清空结果显示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "=== 执行重命名 ===\n\n")
        
        try:
            # 重定向输出到文本框
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            
            with contextlib.redirect_stdout(output_buffer):
                renamer = Renamer(
                    img_dir=img_dir,
                    prefix=prefix,
                    start=start,
                    zfill=zfill,
                    ext=ext
                )
                renamer.rename(dry_run=False)  # 实际执行
            
            # 获取输出内容并显示
            output_content = output_buffer.getvalue()
            self.result_text.insert(tk.END, output_content)
            self.result_text.insert(tk.END, "\n重命名操作已完成！")
            
            messagebox.showinfo("操作完成", "文件重命名操作已成功完成！")
            
        except Exception as e:
            error_msg = f"重命名时发生错误: {str(e)}"
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("操作失败", error_msg)


def main():
    root = tk.Tk()
    app = RenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()