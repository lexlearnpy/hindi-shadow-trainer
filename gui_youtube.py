"""
YouTube学习界面模块
YouTube Learning Interface Module

现代化的YouTube视频学习界面，支持完整流程
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from pathlib import Path

# Import from main_gui for colors
from main_gui import COLORS, CardFrame, ModernButton
from font_manager import font_manager


class YouTubeFrame(tk.Frame):
    """YouTube学习框架"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, bg=COLORS['bg_dark'])
        self.main_app = main_app
        
        # 初始化组件
        self.youtube_handler = None
        self.translator = None
        self.whisper_engine = None
        
        # 当前处理状态
        self.video_info = None
        self.segments = []
        self.selected_segments = []
        
        self.create_ui()
        
    def create_ui(self):
        """创建UI"""
        # 标题
        title_frame = tk.Frame(self, bg=COLORS['bg_dark'])
        title_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(title_frame, text="🎬 YouTube学习模式", 
                font=('Microsoft YaHei', 28, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_dark']).pack()
        
        # 主内容区 - 左右分栏
        content_frame = tk.Frame(self, bg=COLORS['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 左侧：输入和进度
        left_frame = tk.Frame(content_frame, bg=COLORS['bg_dark'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_input_section(left_frame)
        self.create_progress_section(left_frame)
        
        # 右侧：结果列表
        right_frame = tk.Frame(content_frame, bg=COLORS['bg_dark'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_results_section(right_frame)
        
    def create_input_section(self, parent):
        """创建输入区域"""
        # 输入卡片
        input_card = tk.Frame(parent, bg=COLORS['bg_card'],
                             highlightbackground=COLORS['border'],
                             highlightthickness=1)
        input_card.pack(fill=tk.X, pady=10)
        
        inner = tk.Frame(input_card, bg=COLORS['bg_card'])
        inner.pack(padx=30, pady=30)
        
        # URL输入
        tk.Label(inner, text="YouTube视频链接", 
                font=('Microsoft YaHei', 14, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_card']).pack(anchor='w')
        
        self.url_entry = tk.Entry(inner, font=('Segoe UI', 12),
                                 bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                 insertbackground=COLORS['text_primary'],
                                 relief=tk.FLAT, width=50)
        self.url_entry.pack(fill=tk.X, pady=10, ipady=8)
        self.url_entry.insert(0, "https://youtu.be/rRyb3Cm0eT0")  # 默认测试链接
        
        # 按钮区
        btn_frame = tk.Frame(inner, bg=COLORS['bg_card'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        ModernButton(btn_frame, "🔍 分析视频", 
                    command=self.start_analysis,
                    bg_color=COLORS['primary'], width=180).pack(side=tk.LEFT, padx=5)
        
        # 视频信息标签
        self.video_info_label = tk.Label(inner, text="", 
                                        font=('Segoe UI', 11),
                                        fg=COLORS['text_secondary'], 
                                        bg=COLORS['bg_card'],
                                        wraplength=500)
        self.video_info_label.pack(fill=tk.X, pady=10)
        
    def create_progress_section(self, parent):
        """创建进度显示区域"""
        # 进度卡片
        self.progress_card = tk.Frame(parent, bg=COLORS['bg_card'],
                                     highlightbackground=COLORS['border'],
                                     highlightthickness=1)
        self.progress_card.pack(fill=tk.X, pady=10)
        self.progress_card.pack_forget()  # 初始隐藏
        
        inner = tk.Frame(self.progress_card, bg=COLORS['bg_card'])
        inner.pack(padx=30, pady=30)
        
        tk.Label(inner, text="处理进度", 
                font=('Microsoft YaHei', 16, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_card']).pack(anchor='w')
        
        # 进度项
        self.progress_items = []
        steps = [
            ("📥 下载音频", "download"),
            ("🎯 Whisper转录", "transcribe"),
            ("✂️  自动分段", "segment"),
            ("🌍 翻译", "translate"),
        ]
        
        for text, key in steps:
            item_frame = tk.Frame(inner, bg=COLORS['bg_card'])
            item_frame.pack(fill=tk.X, pady=8)
            
            label = tk.Label(item_frame, text=text, 
                           font=('Segoe UI', 11),
                           fg=COLORS['text_secondary'], 
                           bg=COLORS['bg_card'])
            label.pack(side=tk.LEFT)
            
            status = tk.Label(item_frame, text="等待中", 
                            font=('Segoe UI', 10),
                            fg=COLORS['text_muted'], 
                            bg=COLORS['bg_card'])
            status.pack(side=tk.RIGHT)
            
            self.progress_items.append({
                'key': key,
                'label': label,
                'status': status
            })
        
        # 总体进度条
        self.progress_bar = ttk.Progressbar(inner, mode='determinate', 
                                           length=500)
        self.progress_bar.pack(fill=tk.X, pady=15)
        
        # 状态信息
        self.status_label = tk.Label(inner, text="准备就绪", 
                                    font=('Segoe UI', 10),
                                    fg=COLORS['text_secondary'], 
                                    bg=COLORS['bg_card'])
        self.status_label.pack(anchor='w')
        
    def create_results_section(self, parent):
        """创建结果列表区域"""
        # 结果卡片
        results_card = tk.Frame(parent, bg=COLORS['bg_card'],
                               highlightbackground=COLORS['border'],
                               highlightthickness=1)
        results_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 标题栏
        header = tk.Frame(results_card, bg=COLORS['bg_card'])
        header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header, text="识别结果", 
                font=('Microsoft YaHei', 16, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_card']).pack(side=tk.LEFT)
        
        # 操作按钮
        btn_frame = tk.Frame(header, bg=COLORS['bg_card'])
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="全选", font=('Segoe UI', 9),
                 bg=COLORS['bg_card'], fg=COLORS['accent'],
                 activebackground=COLORS['bg_card_hover'],
                 bd=0, cursor='hand2',
                 command=self.select_all).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="反选", font=('Segoe UI', 9),
                 bg=COLORS['bg_card'], fg=COLORS['accent'],
                 activebackground=COLORS['bg_card_hover'],
                 bd=0, cursor='hand2',
                 command=self.invert_selection).pack(side=tk.LEFT, padx=5)
        
        # 滚动列表
        list_frame = tk.Frame(results_card, bg=COLORS['bg_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Canvas + Scrollbar
        self.canvas = tk.Canvas(list_frame, bg=COLORS['bg_card'], 
                               highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", 
                                command=self.canvas.yview)
        
        self.results_frame = tk.Frame(self.canvas, bg=COLORS['bg_card'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), 
                                                      window=self.results_frame, 
                                                      anchor="nw",
                                                      width=self.canvas.winfo_width())
        
        self.results_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # 生成按钮
        self.generate_btn = ModernButton(results_card, 
                                        "✨ 生成学习卡片", 
                                        command=self.generate_cards,
                                        bg_color=COLORS['success'],
                                        width=300)
        self.generate_btn.pack(pady=20)
        self.generate_btn.pack_forget()  # 初始隐藏
        
    def on_frame_configure(self, event=None):
        """更新canvas滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        """更新canvas窗口宽度"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def update_progress(self, step_key, status, progress_value=None):
        """更新进度"""
        for item in self.progress_items:
            if item['key'] == step_key:
                if status == 'running':
                    item['status'].config(text="进行中...", fg=COLORS['accent'])
                    item['label'].config(fg=COLORS['text_primary'])
                elif status == 'done':
                    item['status'].config(text="✓ 完成", fg=COLORS['success'])
                    item['label'].config(fg=COLORS['text_secondary'])
                elif status == 'error':
                    item['status'].config(text="✗ 失败", fg=COLORS['error'])
                    item['label'].config(fg=COLORS['error'])
                break
        
        if progress_value is not None:
            self.progress_bar['value'] = progress_value
            
    def set_status(self, text):
        """设置状态文本"""
        self.status_label.config(text=text)
        self.update()
        
    def start_analysis(self):
        """开始分析视频"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入YouTube视频链接")
            return
            
        # 显示进度卡片（在输入区域和结果区域之间）
        if not self.progress_card.winfo_viewable():
            self.progress_card.pack(fill=tk.X, pady=10, after=self.url_entry.master.master)
        
        # 重置进度
        for item in self.progress_items:
            item['status'].config(text="等待中", fg=COLORS['text_muted'])
            item['label'].config(fg=COLORS['text_secondary'])
        self.progress_bar['value'] = 0
        
        # 在新线程中处理
        thread = threading.Thread(target=self.process_video, args=(url,))
        thread.daemon = True
        thread.start()
        
    def process_video(self, url):
        """处理视频（后台线程）"""
        try:
            # 初始化组件
            from modules.youtube_handler import YouTubeHandler, check_ffmpeg, setup_ffmpeg_path
            from modules.translator import HindiTranslator
            from modules.whisper_engine import WhisperEngine
            from modules.database import VocabDatabase
            
            # 检查并设置FFmpeg
            if not check_ffmpeg():
                self.after(0, lambda: self.set_status("正在安装FFmpeg..."))
                from install_ffmpeg import install_ffmpeg
                if install_ffmpeg():
                    setup_ffmpeg_path()
            
            self.youtube_handler = YouTubeHandler()
            self.translator = HindiTranslator()
            self.db = VocabDatabase()
            
            # 1. 下载音频
            self.after(0, lambda: self.update_progress('download', 'running', 10))
            self.after(0, lambda: self.set_status("正在下载音频..."))
            self.video_info = self.youtube_handler.download_audio(url)
            
            self.after(0, lambda: self.video_info_label.config(
                text=f"📹 {self.video_info['title']}\n⏱️ 时长: {self.video_info['duration']}秒"
            ))
            self.after(0, lambda: self.update_progress('download', 'done', 25))
            
            # 2. Whisper转录
            self.after(0, lambda: self.update_progress('transcribe', 'running', 30))
            self.after(0, lambda: self.set_status("正在加载Whisper模型（首次需要下载）..."))
            self.whisper_engine = WhisperEngine()
            
            self.after(0, lambda: self.set_status("正在转录音频（这可能需要几分钟）..."))
            hindi_text = self.whisper_engine.transcribe(self.video_info['audio_path'])
            
            self.after(0, lambda: self.update_progress('transcribe', 'done', 60))
            
            # 3. 自动分段（简化版：整段作为一个片段）
            self.after(0, lambda: self.update_progress('segment', 'running', 65))
            self.after(0, lambda: self.set_status("正在分段..."))
            
            # 这里简化处理，实际应该按句子分割
            self.segments = [{
                'start': 0,
                'end': self.video_info['duration'],
                'text': hindi_text
            }]
            
            self.after(0, lambda: self.update_progress('segment', 'done', 75))
            
            # 4. 翻译
            self.after(0, lambda: self.update_progress('translate', 'running', 80))
            self.after(0, lambda: self.set_status("正在翻译..."))
            
            for segment in self.segments:
                result = self.translator.translate_full(segment['text'])
                segment.update(result)
            
            self.after(0, lambda: self.update_progress('translate', 'done', 100))
            self.after(0, lambda: self.set_status("处理完成！"))
            
            # 显示结果
            self.after(0, self.show_results)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("错误", f"处理失败: {str(e)}"))
            self.after(0, lambda: self.set_status(f"错误: {str(e)}"))
            
    def show_results(self):
        """显示处理结果"""
        # 清空现有内容
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        self.selected_segments = []
        
        # 添加每个片段
        for i, segment in enumerate(self.segments):
            self.create_segment_item(i, segment)
            
        # 显示生成按钮
        self.generate_btn.pack(pady=20)
        
    def create_segment_item(self, index, segment):
        """创建片段条目"""
        item_frame = tk.Frame(self.results_frame, bg=COLORS['bg_card_hover'],
                             highlightbackground=COLORS['border'],
                             highlightthickness=1)
        item_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 复选框
        var = tk.BooleanVar(value=True)
        self.selected_segments.append((var, segment))
        
        check = tk.Checkbutton(item_frame, variable=var,
                              bg=COLORS['bg_card_hover'],
                              activebackground=COLORS['bg_card_hover'],
                              selectcolor=COLORS['primary'])
        check.pack(side=tk.LEFT, padx=10)
        
        # 内容
        content = tk.Frame(item_frame, bg=COLORS['bg_card_hover'])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 印地语（使用印地语字体）
        hindi_font = font_manager.get_hindi_font(size=18, bold=True)
        tk.Label(content, text=segment['hindi'], 
                font=hindi_font,
                fg=COLORS['text_primary'], 
                bg=COLORS['bg_card_hover'],
                wraplength=400).pack(anchor='w')
        
        # 转写
        tk.Label(content, text=segment['transliteration'], 
                font=('Segoe UI', 11),
                fg=COLORS['accent'], 
                bg=COLORS['bg_card_hover']).pack(anchor='w')
        
        # 英语和中文
        tk.Label(content, text=f"{segment['english']} | {segment['chinese']}", 
                font=('Microsoft YaHei', 10),
                fg=COLORS['text_secondary'], 
                bg=COLORS['bg_card_hover'],
                wraplength=400).pack(anchor='w')
        
    def select_all(self):
        """全选"""
        for var, _ in self.selected_segments:
            var.set(True)
            
    def invert_selection(self):
        """反选"""
        for var, _ in self.selected_segments:
            var.set(not var.get())
            
    def generate_cards(self):
        """生成学习卡片"""
        selected = [(var.get(), seg) for var, seg in self.selected_segments if var.get()]
        
        if not selected:
            messagebox.showwarning("警告", "请至少选择一个片段")
            return
            
        # 保存到数据库
        count = 0
        for _, segment in selected:
            try:
                segment_path = self.youtube_handler.extract_segment(
                    self.video_info['audio_path'],
                    segment['start'],
                    segment['end']
                )
                
                lesson_id = self.db.add_youtube_lesson(
                    video_url=self.video_info.get('video_id', ''),
                    video_title=self.video_info['title'],
                    segment_path=segment_path,
                    start_time=segment['start'],
                    end_time=segment['end'],
                    hindi_text=segment['hindi'],
                    transliteration=segment['transliteration'],
                    english_text=segment['english'],
                    chinese_text=segment['chinese']
                )
                count += 1
            except Exception as e:
                print(f"保存片段失败: {e}")
                
        messagebox.showinfo("成功", f"已生成 {count} 张学习卡片！\n可以在复习模式中找到它们。")
