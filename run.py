#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import argparse
import importlib.util
import inspect
import concurrent.futures
from tqdm import tqdm 
from concurrent.futures import ProcessPoolExecutor  # 使用进程池而不是线程池

# 添加 GUI 相关导入
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import math

def scan_file_for_scenes(file_path):
    """扫描指定的 Python 文件，查找所有继承自 Scene 的类"""
    try:
        # 获取文件的绝对路径
        abs_path = os.path.abspath(file_path)
        
        # 加载模块
        spec = importlib.util.spec_from_file_location("temp_module", abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找所有继承自 Scene 的类
        scenes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name != "Scene" and hasattr(obj, "construct"):
                # 检查是否是 Scene 的子类
                if any(base.__name__ == "Scene" for base in obj.__mro__):
                    # 检查是否是抽象基类或工具类
                    if not name.startswith('_') and not name in [
                        'ThreeDScene', 'MovingCameraScene', 'VectorScene', 
                        'ZoomedScene', 'SpecialThreeDScene', 'LinearTransformationScene'
                    ]:
                        scenes.append(name)
        
        return scenes
    except Exception as e:
        print(f"扫描文件 {file_path} 时出错: {e}")
        return []

def scan_directory_for_files():
    """扫描当前目录下的所有 .py 文件"""
    py_files = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file != 'run.py':
            py_files.append(file)
    return py_files

def show_gui():
    """显示图形界面配置表单"""
    # 创建主窗口
    root = tk.Tk()
    root.title("Manim 动画渲染工具")
    root.geometry("700x600")  # 调整为更宽的窗口以适应左右布局
    root.resizable(True, True)
    
    # 处理窗口关闭事件
    def on_closing():
        # 确保所有子窗口也被关闭
        for widget in root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        root.destroy()
        # 确保程序完全退出
        os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 设置样式
    style = ttk.Style()
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
    style.configure("TButton", font=("Arial", 10))
    style.configure("Header.TLabel", font=("Arial", 12, "bold"))
    style.configure("Title.TLabel", font=("Arial", 16, "bold"))
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding="20 20 20 20", style="TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题和全局折叠按钮框架
    title_frame = ttk.Frame(main_frame)
    title_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 标题
    title_label = ttk.Label(title_frame, text="Manim 动画渲染配置 ✨", style="Title.TLabel")
    title_label.pack(side=tk.LEFT, pady=(0, 10))
    
    # 全局折叠/展开按钮框架
    global_buttons_frame = ttk.Frame(title_frame)
    global_buttons_frame.pack(side=tk.RIGHT)
    
    # 创建配置变量
    config = {
        "file": tk.StringVar(value=""),
        "scenes": [],
        "selected_scenes": [],
        "quality": tk.StringVar(value="h"),
        "preview": tk.BooleanVar(value=False),
        "transparent": tk.BooleanVar(value=False),
        "save_last_frame": tk.BooleanVar(value=False),
        "gif": tk.BooleanVar(value=False),
        "parallel": tk.BooleanVar(value=False),
        "max_workers": tk.IntVar(value=os.cpu_count()),
        "use_manim_multiprocessing": tk.BooleanVar(value=False)
    }
    
    # 创建左右分栏
    left_panel = ttk.Frame(main_frame)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    right_panel = ttk.Frame(main_frame)
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # 文件选择部分 (左侧)
    file_frame = ttk.LabelFrame(left_panel, text="文件选择 📁", padding="10 10 10 10")
    file_frame.pack(fill=tk.X, pady=10)
    
    # 扫描当前目录下的 Python 文件
    py_files = scan_directory_for_files()
    
    # 文件下拉菜单
    file_label = ttk.Label(file_frame, text="选择要渲染的文件:")
    file_label.pack(anchor=tk.W)
    
    file_combo = ttk.Combobox(file_frame, textvariable=config["file"], values=py_files, state="readonly")
    file_combo.pack(fill=tk.X, pady=5)
    if py_files:
        file_combo.current(0)
    
    # 添加刷新按钮
    def refresh_files():
        py_files = scan_directory_for_files()
        file_combo['values'] = py_files
        if py_files and not config["file"].get() in py_files:
            file_combo.current(0)
    
    refresh_button = ttk.Button(file_frame, text="刷新文件列表 🔄", command=refresh_files)
    refresh_button.pack(anchor=tk.E, pady=5)
    
    # 场景选择部分 (左侧)
    scene_frame = ttk.LabelFrame(left_panel, text="场景选择 🎬", padding="10 10 10 10")
    scene_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 创建一个变量来跟踪场景列表是否展开
    scene_expanded = tk.BooleanVar(value=True)  # 默认展开
    
    # 折叠/展开按钮
    def toggle_scene_list():
        if scene_expanded.get():
            scene_content_frame.pack_forget()
            toggle_button.config(text="展开场景列表 ⬇️")
            scene_expanded.set(False)
        else:
            scene_content_frame.pack(fill=tk.BOTH, expand=True)
            toggle_button.config(text="收起场景列表 ⬆️")
            scene_expanded.set(True)
    
    toggle_button = ttk.Button(scene_frame, text="收起场景列表 ⬆️", command=toggle_scene_list)
    toggle_button.pack(anchor=tk.W, pady=(0, 5))
    
    # 场景列表框和相关控件的容器 - 移动到按钮之后
    scene_content_frame = ttk.Frame(scene_frame)
    scene_content_frame.pack(fill=tk.BOTH, expand=True)  # 默认显示
    
    # 场景列表框
    scene_label = ttk.Label(scene_content_frame, text="选择要渲染的场景:")
    scene_label.pack(anchor=tk.W)
    
    # 创建一个框架包含列表框和滚动条
    scene_list_frame = ttk.Frame(scene_content_frame)
    scene_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    scene_listbox = tk.Listbox(scene_list_frame, selectmode=tk.MULTIPLE, height=8)
    scene_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scene_scrollbar = ttk.Scrollbar(scene_list_frame, orient=tk.VERTICAL, command=scene_listbox.yview)
    scene_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scene_listbox.config(yscrollcommand=scene_scrollbar.set)
    
    # 全选和取消全选按钮
    scene_buttons_frame = ttk.Frame(scene_content_frame)
    scene_buttons_frame.pack(fill=tk.X, pady=5)
    
    def select_all_scenes():
        scene_listbox.selection_set(0, tk.END)
    
    def deselect_all_scenes():
        scene_listbox.selection_clear(0, tk.END)
    
    select_all_button = ttk.Button(scene_buttons_frame, text="全选 ✅", command=select_all_scenes)
    select_all_button.pack(side=tk.LEFT, padx=(0, 5))
    
    deselect_all_button = ttk.Button(scene_buttons_frame, text="取消全选 ❌", command=deselect_all_scenes)
    deselect_all_button.pack(side=tk.LEFT)
    
    # 质量选择部分 (右侧)
    quality_frame = ttk.LabelFrame(right_panel, text="渲染质量 🎨", padding="10 10 10 10")
    quality_frame.pack(fill=tk.X, pady=10)
    
    # 创建一个变量来跟踪质量选项是否展开
    quality_expanded = tk.BooleanVar(value=True)  # 默认展开
    
    # 折叠/展开按钮
    def toggle_quality_options():
        if quality_expanded.get():
            quality_content_frame.pack_forget()
            quality_toggle_button.config(text="展开质量选项 ⬇️")
            quality_expanded.set(False)
        else:
            quality_content_frame.pack(fill=tk.X, expand=True)
            quality_toggle_button.config(text="收起质量选项 ⬆️")
            quality_expanded.set(True)
    
    quality_toggle_button = ttk.Button(quality_frame, text="收起质量选项 ⬆️", command=toggle_quality_options)
    quality_toggle_button.pack(anchor=tk.W, pady=(0, 5))
    
    # 质量选项内容框架 - 移动到按钮之后
    quality_content_frame = ttk.Frame(quality_frame)
    quality_content_frame.pack(fill=tk.X, expand=True)  # 默认显示
    
    # 质量单选按钮
    quality_label = ttk.Label(quality_content_frame, text="选择渲染质量:")
    quality_label.pack(anchor=tk.W)
    
    ttk.Radiobutton(quality_content_frame, text="快速预览 (480p15) 🚀", variable=config["quality"], value="l").pack(anchor=tk.W)
    ttk.Radiobutton(quality_content_frame, text="中等画质 (720p30) ⚡", variable=config["quality"], value="m").pack(anchor=tk.W)
    ttk.Radiobutton(quality_content_frame, text="高质量 (1080p60) ✨", variable=config["quality"], value="h").pack(anchor=tk.W)
    ttk.Radiobutton(quality_content_frame, text="4K (2160p60) 💎", variable=config["quality"], value="k").pack(anchor=tk.W)
    
    # 多进程选项部分 (右侧)
    process_frame = ttk.LabelFrame(right_panel, text="多进程选项 🧵", padding="10 10 10 10")
    process_frame.pack(fill=tk.X, pady=10)
    
    # 创建一个变量来跟踪多进程选项是否展开
    process_expanded = tk.BooleanVar(value=True)  # 默认展开
    
    # 折叠/展开按钮
    def toggle_process_options():
        if process_expanded.get():
            process_content_frame.pack_forget()
            process_toggle_button.config(text="展开多进程选项 ⬇️")
            process_expanded.set(False)
        else:
            process_content_frame.pack(fill=tk.X, expand=True)
            process_toggle_button.config(text="收起多进程选项 ⬆️")
            process_expanded.set(True)
    
    process_toggle_button = ttk.Button(process_frame, text="收起多进程选项 ⬆️", command=toggle_process_options)
    process_toggle_button.pack(anchor=tk.W, pady=(0, 5))
    
    # 多进程选项内容框架 - 移动到按钮之后
    process_content_frame = ttk.Frame(process_frame)
    process_content_frame.pack(fill=tk.X, expand=True)  # 默认显示
    
    # 多进程复选框和相关逻辑
    def update_workers_state(*args):
        # 如果启用了并行渲染，启用进程数选择
        if config["parallel"].get():
            workers_spinbox.config(state="normal")
            cpu_button.config(state="normal")
        else:
            workers_spinbox.config(state="disabled")
            cpu_button.config(state="disabled")
    
    # 创建复选框并绑定变量
    parallel_checkbox = ttk.Checkbutton(
        process_content_frame, 
        text="使用多进程渲染多个场景 🚀", 
        variable=config["parallel"],
        command=update_workers_state
    )
    parallel_checkbox.pack(anchor=tk.W)
    
    # 进程数选择
    workers_frame = ttk.Frame(process_content_frame)
    workers_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(workers_frame, text="进程数:").pack(side=tk.LEFT)
    workers_spinbox = ttk.Spinbox(workers_frame, from_=1, to=32, textvariable=config["max_workers"], width=5)
    workers_spinbox.pack(side=tk.LEFT, padx=5)
    workers_spinbox.config(state="disabled")  # 默认禁用
    
    # 添加自动设置为CPU核心数的按钮
    def set_cpu_count():
        # 获取逻辑处理器数量（包括超线程）
        logical_cores = os.cpu_count()
        # 设置为逻辑处理器数量
        config["max_workers"].set(logical_cores*2)
    
    # 获取逻辑处理器数量
    logical_cores = os.cpu_count()
    # 估计物理核心数（通常是逻辑处理器数量的一半，但不总是如此）
    physical_cores = max(1, logical_cores // 2)
    
    cpu_button = ttk.Button(
        workers_frame, 
        text=f"设为逻辑处理器数({logical_cores*2}) 💻", 
        command=set_cpu_count
    )
    cpu_button.pack(side=tk.LEFT, padx=5)
    cpu_button.config(state="disabled")  # 默认禁用
    
    # 添加说明文本
    mp_info_label = ttk.Label(
        process_content_frame, 
        text=f"提示: 多进程渲染可以同时渲染多个场景，提高效率。推荐使用 {physical_cores}-{logical_cores} 个进程。",
        font=("Arial", 9, "italic"),
        foreground="#666666"
    )
    mp_info_label.pack(anchor=tk.W, pady=(5, 0))
    
    # 初始调用一次更新状态
    update_workers_state()
    
    # 更新场景列表的函数
    def update_scene_list(*args):
        selected_file = config["file"].get()
        if selected_file:
            # 清空列表框
            scene_listbox.delete(0, tk.END)
            
            # 扫描文件中的场景
            scenes = scan_file_for_scenes(selected_file)
            config["scenes"] = scenes
            
            # 添加到列表框
            for scene in scenes:
                scene_listbox.insert(tk.END, scene)
    
    # 当文件选择改变时更新场景列表
    config["file"].trace_add("write", update_scene_list)
    
    # 如果已经有文件，立即更新场景列表
    if config["file"].get():
        update_scene_list()
    
    # 渲染按钮
    def start_render():
        # 获取选中的场景
        selected_indices = scene_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告 ⚠️", "请至少选择一个场景进行渲染")
            return
        
        selected_scenes = [config["scenes"][i] for i in selected_indices]
        
        # 构建选项字典
        options = {
            "quality": config["quality"].get(),
            "scenes": selected_scenes,
            "preview": config["preview"].get(),
            "transparent": config["transparent"].get(),
            "save_last_frame": config["save_last_frame"].get(),
            "gif": config["gif"].get(),
            "file": config["file"].get(),
            "parallel": config["parallel"].get(),
            "max_workers": config["max_workers"].get(),
            "use_manim_multiprocessing": config["use_manim_multiprocessing"].get()
        }
        
        # 显示确认对话框
        quality_names = {
            "l": "低质量 (480p15)",
            "m": "中等质量 (720p30)",
            "h": "高质量 (1080p60)",
            "k": "4K质量 (2160p60)"
        }
        
        confirm_message = f"确认要渲染以下内容吗？\n\n" \
                          f"📁 文件: {options['file']}\n" \
                          f"🎬 场景: {', '.join(selected_scenes)}\n" \
                          f"🎨 质量: {quality_names[options['quality']]}\n\n" \
                          f"⚙️ 其他选项:\n" \
                          f"{'✅' if options['preview'] else '❌'} 渲染后预览\n" \
                          f"{'✅' if options['transparent'] else '❌'} 透明背景\n" \
                          f"{'✅' if options['save_last_frame'] else '❌'} 只保存最后一帧\n" \
                          f"{'✅' if options['gif'] else '❌'} 导出GIF\n" \
                          f"{'✅' if options['parallel'] else '❌'} 多进程渲染 ({options['max_workers']}进程)\n" \
                          f"{'✅' if options['use_manim_multiprocessing'] else '❌'} Manim内部多进程"
        
        if not messagebox.askyesno("确认渲染 🚀", confirm_message):
            return
        
        # 隐藏主窗口
        root.withdraw()
        
        # 创建控制台输出窗口
        console_window = tk.Toplevel(root)
        console_window.title("渲染进度 🔄")
        console_window.geometry("800x600")
        console_window.configure(background="black")
        
        # 处理控制台窗口关闭事件
        def on_console_closing():
            console_window.destroy()
            root.deiconify()  # 显示主窗口
        
        console_window.protocol("WM_DELETE_WINDOW", on_console_closing)
        
        # 创建文本框显示输出
        output_frame = ttk.Frame(console_window)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        output_text = tk.Text(output_frame, wrap=tk.WORD, bg="black", fg="white")
        output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        output_text.config(yscrollcommand=scrollbar.set)
        
        # 重定向标准输出到文本框
        class TextRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget
                self.buffer = ""
            
            def write(self, string):
                self.buffer += string
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)  # 确保自动滚动到最新内容
                self.text_widget.update_idletasks()  # 强制更新UI
            
            def flush(self):
                pass
        
        # 保存原始的标准输出
        old_stdout = sys.stdout
        sys.stdout = TextRedirector(output_text)
        
        # 在新线程中运行渲染
        def run_render():
            try:
                # 创建进度条框架
                progress_frame = ttk.Frame(console_window)
                progress_frame.pack(fill=tk.X, padx=20, pady=10)
                
                # 创建总进度条
                ttk.Label(progress_frame, text="总体进度:", foreground="white", background="black").pack(anchor=tk.W)
                overall_progress_var = tk.DoubleVar(value=0)
                overall_progress_bar = ttk.Progressbar(
                    progress_frame, 
                    variable=overall_progress_var, 
                    length=400, 
                    mode='determinate'
                )
                overall_progress_bar.pack(fill=tk.X, pady=(0, 10))
                
                # 创建当前场景进度条
                ttk.Label(progress_frame, text="当前场景:", foreground="white", background="black").pack(anchor=tk.W)
                scene_progress_var = tk.DoubleVar(value=0)
                scene_progress_bar = ttk.Progressbar(
                    progress_frame, 
                    variable=scene_progress_var, 
                    length=400, 
                    mode='determinate'
                )
                scene_progress_bar.pack(fill=tk.X)
                
                # 创建进度文本标签
                progress_text = tk.StringVar(value="准备中...")
                progress_label = ttk.Label(
                    progress_frame, 
                    textvariable=progress_text, 
                    foreground="white", 
                    background="black"
                )
                progress_label.pack(anchor=tk.W, pady=(5, 0))
                
                # 添加进度更新函数
                def update_progress(scene, progress, status="渲染中"):
                    if scene == "所有场景":
                        # 确保在主线程中更新 UI
                        console_window.after(0, lambda: overall_progress_var.set(progress))
                        console_window.after(0, lambda: progress_text.set(f"总进度: {progress}% - {status}"))
                    else:
                        # 确保在主线程中更新 UI
                        console_window.after(0, lambda: scene_progress_var.set(progress))
                        console_window.after(0, lambda: progress_text.set(f"[{scene}] {status}: {progress}% 完成"))
                    
                    # 确保刷新 GUI
                    console_window.after(0, lambda: console_window.update())
                
                # 修改 render_with_options 函数，传入进度更新回调
                result = render_with_options(options, update_progress)
                
                # 如果渲染成功，显示简单的成功消息和返回按钮
                if isinstance(result, dict):
                    # 创建一个简单的框架
                    result_frame = ttk.Frame(console_window)
                    result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                    
                    # 显示结果信息
                    if result["status"] == 0:
                        # 成功信息
                        success_label = ttk.Label(
                            result_frame,
                            text="🎉 渲染成功!",
                            font=("Arial", 18, "bold"),
                            foreground="#4CAF50"
                        )
                        success_label.pack(pady=10)
                        
                        info_text = f"已成功渲染 {result['successful_scenes']}/{result['total_scenes']} 个场景"
                    else:
                        # 失败信息
                        error_label = ttk.Label(
                            result_frame,
                            text="❌ 渲染过程中出现错误",
                            font=("Arial", 18, "bold"),
                            foreground="#FF5252"
                        )
                        error_label.pack(pady=10)
                        
                        info_text = f"只有 {result['successful_scenes']}/{result['total_scenes']} 个场景成功渲染"
                    
                    # 显示详细信息
                    info_label = ttk.Label(
                        result_frame,
                        text=info_text,
                        font=("Arial", 12)
                    )
                    info_label.pack(pady=5)
                    
                    # 添加返回按钮
                    return_button = ttk.Button(
                        result_frame,
                        text="返回主界面",
                        command=lambda: [console_window.destroy(), root.deiconify()],
                        padding=10
                    )
                    return_button.pack(pady=20)
                else:
                    # 处理非字典结果（可能是旧版本的返回值）
                    error_frame = ttk.Frame(console_window)
                    error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                    
                    error_label = ttk.Label(
                        error_frame,
                        text="❌ 渲染过程中出现未知错误",
                        font=("Arial", 18, "bold"),
                        foreground="#FF5252"
                    )
                    error_label.pack(pady=10)
                    
                    # 添加返回按钮
                    return_button = ttk.Button(
                        error_frame,
                        text="返回主界面",
                        command=lambda: [console_window.destroy(), root.deiconify()],
                        padding=10
                    )
                    return_button.pack(pady=20)
            except Exception as e:
                print(f"\n❌ 渲染过程中发生错误: {e}")
                # 恢复标准输出
                sys.stdout = old_stdout
                
                # 添加错误信息和返回按钮
                console_window.after(0, lambda: 
                    ttk.Button(console_window, text="返回主界面", command=lambda: [console_window.destroy(), root.deiconify()]).pack(pady=10))
        
        import threading
        render_thread = threading.Thread(target=run_render)
        render_thread.daemon = True
        render_thread.start()
    
    # 按钮框架 (右下角)
    button_frame = ttk.Frame(right_panel)
    button_frame.pack(side=tk.BOTTOM, anchor=tk.SE, pady=20)
    
    # 自定义按钮样式
    style.configure("Render.TButton", 
                   font=("Arial", 13, "bold"), 
                   padding=10,
                   background="#4CAF50")  # 绿色背景
    style.configure("Exit.TButton", 
                   font=("Arial", 13, "bold"), 
                   padding=10)
    
    # 渲染按钮
    render_button = ttk.Button(button_frame, 
                              text="🚀开始渲染", 
                              command=start_render, 
                              style="Render.TButton",
                              width=10)
    render_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # 退出按钮
    exit_button = ttk.Button(button_frame, 
                            text="退出", 
                            command=root.destroy, 
                            style="Exit.TButton",
                            width=4)
    exit_button.pack(side=tk.LEFT)
    
    # 运行主循环
    root.mainloop()
    
    return None  # GUI 模式不返回选项

def render_with_options(options, progress_callback=None):
    """使用给定的选项进行渲染"""
    # 质量映射
    quality_map = {
        "l": ("低质量", "-ql"),
        "m": ("中等质量", "-qm"),
        "h": ("高质量", "-qh"),
        "k": ("4K质量", "-qk")
    }
    
    quality_name, quality_flag = quality_map[options["quality"]]
    
    print(f"\n🚀 开始编译 Manim 动画... [{quality_name}]")
    if options["parallel"] and options["max_workers"] > 1:
        print(f"🧵 使用 {options['max_workers']} 个进程并行渲染")
    
    # 设置要渲染的场景
    scenes = options["scenes"]
    
    # 添加 --quiet 标志来减少输出
    quiet_flag = "--log_to_file"  # 将日志写入文件而不是控制台
    
    # 添加进度显示
    total_scenes = len(scenes)
    successful_scenes = 0
    failed_scenes = 0
    
    start_time = time.time()
    
    # 检查是否有场景可渲染
    if total_scenes == 0:
        print("\n❌ 没有找到可渲染的场景！")
        return 1
    
    # 多进程渲染
    if options["parallel"] and options["max_workers"] > 1 and total_scenes > 1:
        # 只有多个场景时才使用多进程
        try:
            results = []
            with ProcessPoolExecutor(max_workers=min(options["max_workers"], total_scenes)) as executor:
                # 提交所有任务
                future_to_scene = {
                    executor.submit(
                        render_scene, 
                        scene, 
                        options, 
                        quality_flag, 
                        quiet_flag, 
                        i+1, 
                        total_scenes,
                        progress_callback
                    ): scene for i, scene in enumerate(scenes)
                }
                
                # 处理完成的任务
                for future in concurrent.futures.as_completed(future_to_scene):
                    try:
                        result = future.result()
                        results.append(result)
                        if result["success"]:
                            successful_scenes += 1
                        else:
                            failed_scenes += 1
                        print(result["output"])
                        
                        # 更新总体进度
                        if progress_callback:
                            overall_progress = int((len(results) / total_scenes) * 100)
                            progress_callback("所有场景", overall_progress, "总进度")
                    except Exception as exc:
                        print(f"任务生成异常: {exc}")
                        failed_scenes += 1
        except Exception as e:
            print(f"多进程渲染失败: {e}")
            print("回退到单进程渲染...")
            # 回退到单进程渲染
            for i, scene in enumerate(scenes, 1):
                result = render_scene(scene, options, quality_flag, quiet_flag, i, total_scenes, progress_callback)
                if result["success"]:
                    successful_scenes += 1
                else:
                    failed_scenes += 1
                print(result["output"])
                
                # 更新总体进度
                if progress_callback:
                    overall_progress = int(((i) / total_scenes) * 100)
    else:
        # 单进程渲染
        for i, scene in enumerate(scenes, 1):
            result = render_scene(scene, options, quality_flag, quiet_flag, i, total_scenes, progress_callback)
            if result["success"]:
                successful_scenes += 1
            else:
                failed_scenes += 1
            print(result["output"])
            
            # 更新总体进度
            if progress_callback:
                overall_progress = int(((i) / total_scenes) * 100)
                progress_callback("所有场景", overall_progress, "总进度")
    
    # 计算总时间
    total_time = time.time() - start_time
    minutes, seconds = divmod(total_time, 60)
    
    print("\n" + "="*60)
    print(f"🎉 渲染完成! {successful_scenes}/{total_scenes} 场景成功")
    if failed_scenes > 0:
        print(f"❌ {failed_scenes} 个场景渲染失败")
    print(f"⏱️ 总用时: {int(minutes)}分{int(seconds)}秒")
    
    # 根据质量确定输出路径
    resolution_map = {
        "l": "480p15",
        "m": "720p30",
        "h": "1080p60",
        "k": "2160p60"
    }
    
    # 获取文件名（不含路径和扩展名）
    file_basename = os.path.basename(options['file'])
    file_name_without_ext = os.path.splitext(file_basename)[0]
    
    output_path = f"media/videos/{file_name_without_ext}/{resolution_map[options['quality']]}/"
    print(f"📂 输出位置: {output_path}")
    print("="*60)
    
    # 返回更详细的结果
    return {
        "status": 0 if failed_scenes == 0 else 1,
        "successful_scenes": successful_scenes,
        "failed_scenes": failed_scenes,
        "total_scenes": total_scenes,
        "output_path": output_path
    }

def render_scene(scene, options, quality_flag, quiet_flag, scene_index, total_scenes, progress_callback=None):
    """渲染单个场景的函数，用于多线程处理"""
    output_info = f"\n[{scene_index}/{total_scenes}] 🎬 渲染: {scene}\n"
    
    # 构建命令
    command = ["manim", quality_flag, quiet_flag, options["file"], scene]
    
    # 添加其他选项
    if options["preview"]:
        command.append("-p")
    if options["transparent"]:
        command.append("-t")
    if options["save_last_frame"]:
        command.append("-s")
    if options["gif"]:
        command.append("--gif")
    
    try:
        # 确保必要的目录存在
        os.makedirs("media/images", exist_ok=True)
        
        # 获取文件名（不含路径和扩展名）
        file_basename = os.path.basename(options['file'])
        file_name_without_ext = os.path.splitext(file_basename)[0]
        
        # 确保特定文件的媒体目录存在
        os.makedirs(f"media/images/{file_name_without_ext}", exist_ok=True)
        os.makedirs(f"media/videos/{file_name_without_ext}", exist_ok=True)
        
        # 在多进程环境中，tqdm可能会有问题，所以我们使用简单的进度指示
        output_info += f"   开始渲染场景 {scene}...\n"
        
        # 如果有进度回调，初始化进度为0
        if progress_callback:
            progress_callback(scene, 0, "准备中")
        
        # 使用 Popen 来执行命令
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 简化的进度更新
        if progress_callback:
            import time
            import threading
            
            def update_progress_thread():
                # 使用更简单的进度逻辑
                steps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
                for progress in steps:
                    if process.poll() is not None:
                        break  # 如果进程已结束，停止更新
                    time.sleep(1)  # 每秒更新一次
                    progress_callback(scene, progress, "渲染中")
            
            # 启动进度更新线程
            progress_thread = threading.Thread(target=update_progress_thread)
            progress_thread.daemon = True
            progress_thread.start()
        
        # 等待进程完成
        stdout, stderr = process.communicate()
        
        # 完成进度
        if progress_callback:
            progress_callback(scene, 100, "已完成" if process.returncode == 0 else "失败")
        
        if process.returncode == 0:
            success = True
        else:
            success = False
            output_info += f"   ❌ 渲染失败，返回代码: {process.returncode}\n"
            
            # 显示更详细的错误信息
            error_found = False
            for line in stderr.split('\n'):
                if line.strip() and ("ERROR" in line or "Error" in line or "Exception" in line):
                    output_info += f"   🔴 {line.strip()}\n"
                    error_found = True
            
            # 如果没有找到明确的错误信息，显示最后几行stderr
            if not error_found and stderr.strip():
                output_info += "   🔴 错误详情:\n"
                last_lines = stderr.strip().split('\n')[-5:]  # 获取最后5行
                for line in last_lines:
                    if line.strip():
                        output_info += f"   🔴 {line.strip()}\n"
        
        return {
            "scene": scene,
            "success": success,
            "output": output_info
        }
            
    except Exception as e:
        return {
            "scene": scene,
            "success": False,
            "output": f"   ❌ 执行出错: {e}"
        }

def main():
    """
    运行 Manim 动画，以指定质量编译 scene.py 文件
    """
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 使用命令行参数
        parser = argparse.ArgumentParser(description="Manim 动画渲染工具")
        
        # 质量选项
        quality_group = parser.add_argument_group("质量选项")
        quality_group.add_argument("-ql", "--quality_low", action="store_const", const="l", dest="quality",
                            help="低质量(480p15)")
        quality_group.add_argument("-qm", "--quality_medium", action="store_const", const="m", dest="quality",
                            help="中等质量(720p30)")
        quality_group.add_argument("-qh", "--quality_high", action="store_const", const="h", dest="quality",
                            help="高质量(1080p60) [默认]")
        quality_group.add_argument("-qk", "--quality_4k", action="store_const", const="k", dest="quality",
                            help="4K质量(2160p60)")
        parser.set_defaults(quality="h")
        
        # 场景选项
        parser.add_argument("scenes", nargs="*", default=[],
                            help="要渲染的场景名称，多个场景用空格分隔")
        
        # 其他选项
        parser.add_argument("-p", "--preview", action="store_true",
                            help="渲染后自动预览")
        parser.add_argument("-f", "--file", default="scene.py",
                            help="指定要渲染的文件 (默认: scene.py)")
        parser.add_argument("--transparent", action="store_true",
                            help="渲染透明背景")
        parser.add_argument("--save_last_frame", action="store_true",
                            help="只保存最后一帧")
        parser.add_argument("--gif", action="store_true",
                            help="同时导出 GIF 格式")
        parser.add_argument("--scan", action="store_true",
                            help="扫描文件中的场景并列出")
        parser.add_argument("--parallel", action="store_true",
                            help="使用多线程并行渲染")
        parser.add_argument("--workers", type=int, default=os.cpu_count(),
                            help=f"设置线程数 (默认: {os.cpu_count()})")
        parser.add_argument("--manim-multiprocessing", action="store_true",
                            help="启用 Manim 内部多进程渲染")
        parser.add_argument("--gui", action="store_true",
                            help="启用图形界面模式")
        
        args = parser.parse_args()
        
        # 如果指定了 GUI 模式，则显示图形界面
        if args.gui:
            show_gui()
            return 0
        
        # 如果指定了扫描选项，则扫描文件并退出
        if args.scan:
            scenes = scan_file_for_scenes(args.file)
            if scenes:
                print(f"\n在 {args.file} 中找到以下场景:")
                for i, scene in enumerate(scenes, 1):
                    print(f"  {i}. {scene}")
            else:
                print(f"\n在 {args.file} 中没有找到场景类！")
            return 0
        
        # 如果没有指定场景，则扫描文件获取所有场景
        if not args.scenes:
            args.scenes = scan_file_for_scenes(args.file)
            if not args.scenes:
                print(f"\n❌ 在 {args.file} 中没有找到场景类！")
                return 1
        
        options = vars(args)
        options["parallel"] = args.parallel
        options["max_workers"] = args.workers
        options["use_manim_multiprocessing"] = args.manim_multiprocessing
        
        return render_with_options(options)
    else:
        # 默认使用图形界面
        show_gui()
        return 0

if __name__ == "__main__":
    sys.exit(main())
