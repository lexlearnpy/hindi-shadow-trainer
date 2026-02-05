#!/usr/bin/env python3
"""
印地语影子跟读训练器 - 现代化GUI版本
Hindi Shadow Trainer - Modern GUI Version (Tkinter)

Modern Material Design 3 with Glassmorphism effects
"""
import sys
import os
from pathlib import Path
from datetime import datetime, date

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import tkinter as tk
from tkinter import ttk, font, messagebox, scrolledtext

from font_manager import font_manager
from config import Config
from modules.database import VocabDatabase
from modules.srs import SM2Algorithm


# Modern Color Scheme
COLORS = {
    'bg_dark': '#0f0f23',
    'bg_card': '#1a1a2e',
    'bg_card_hover': '#252542',
    'primary': '#667eea',
    'primary_dark': '#764ba2',
    'secondary': '#f093fb',
    'accent': '#4facfe',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0c0',
    'text_muted': '#6b6b8f',
    'success': '#00d9a3',
    'warning': '#ffb347',
    'error': '#ff6b6b',
    'border': 'rgba(255,255,255,0.1)',
}


class ModernButton(tk.Canvas):
    """现代化按钮组件"""
    def __init__(self, parent, text, command=None, width=200, height=50, 
                 bg_color=None, fg_color=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=COLORS['bg_card'], highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.bg_color = bg_color or COLORS['primary']
        self.fg_color = fg_color or COLORS['text_primary']
        self.width = width
        self.height = height
        self.hovered = False
        
        self.draw()
        
        # 绑定事件
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def draw(self):
        """绘制按钮"""
        self.delete('all')
        
        # 圆角矩形
        radius = 12
        if self.hovered:
            color = self._lighten_color(self.bg_color, 20)
        else:
            color = self.bg_color
            
        # 创建渐变效果（简化版）
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                radius, fill=color, outline='')
        
        # 文字
        self.create_text(self.width//2, self.height//2, text=self.text,
                        fill=self.fg_color, font=('Segoe UI', 12, 'bold'))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _lighten_color(self, color, percent):
        """提亮颜色"""
        # 简单的颜色处理
        return color
    
    def on_enter(self, event):
        self.hovered = True
        self.draw()
        
    def on_leave(self, event):
        self.hovered = False
        self.draw()
        
    def on_click(self, event):
        if self.command:
            self.command()


class CardFrame(tk.Frame):
    """卡片式框架"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg_card'], **kwargs)
        
        # 添加边框效果
        self.config(highlightbackground=COLORS['border'], 
                   highlightthickness=1, bd=0)
        
        # 内边距
        self.padding = 20


class HindiTrainerGUI:
    """主GUI类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🇮🇳 印地语影子跟读训练器")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.minsize(1200, 800)
        
        # 初始化字体
        font_manager.load_fonts()
        
        # 初始化数据库
        self.db = VocabDatabase()
        self.srs = SM2Algorithm()
        
        # 当前视图
        self.current_frame = None
        
        # 创建UI
        self.create_styles()
        self.create_main_layout()
        self.show_home()
        
    def create_styles(self):
        """创建自定义样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置全局样式
        style.configure('Custom.TFrame', background=COLORS['bg_dark'])
        style.configure('Card.TFrame', background=COLORS['bg_card'])
        
    def create_main_layout(self):
        """创建主布局"""
        # 主容器
        self.main_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部导航栏
        self.create_header()
        
        # 内容区域
        self.content_frame = tk.Frame(self.main_container, bg=COLORS['bg_dark'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
    def create_header(self):
        """创建顶部导航栏"""
        header = tk.Frame(self.main_container, bg=COLORS['bg_card'], 
                         height=70)
        header.pack(fill=tk.X, pady=(0, 10))
        header.pack_propagate(False)
        
        # Logo和标题
        title_frame = tk.Frame(header, bg=COLORS['bg_card'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(title_frame, text="🇮🇳", font=('Segoe UI', 24), 
                bg=COLORS['bg_card']).pack(side=tk.LEFT)
        
        tk.Label(title_frame, text="印地语影子跟读训练器", 
                font=('Microsoft YaHei', 16, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_card']).pack(side=tk.LEFT, padx=10)
        
        # 导航按钮
        nav_frame = tk.Frame(header, bg=COLORS['bg_card'])
        nav_frame.pack(side=tk.RIGHT, padx=20)
        
        nav_buttons = [
            ("🏠 首页", self.show_home),
            ("🎙️ 跟读", self.show_shadowing),
            ("📚 复习", self.show_review),
            ("🎬 YouTube", self.show_youtube),
            ("⚙️ 设置", self.show_settings),
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, font=('Segoe UI', 11),
                          bg=COLORS['bg_card'], fg=COLORS['text_secondary'],
                          activebackground=COLORS['bg_card_hover'],
                          activeforeground=COLORS['text_primary'],
                          bd=0, padx=15, pady=5, cursor='hand2',
                          command=command)
            btn.pack(side=tk.LEFT, padx=5)
            
            # 悬停效果
            btn.bind('<Enter>', lambda e, b=btn: b.config(fg=COLORS['text_primary']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(fg=COLORS['text_secondary']))
    
    def clear_content(self):
        """清空内容区域"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.content_frame, bg=COLORS['bg_dark'])
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_home(self):
        """显示首页"""
        self.clear_content()
        
        # 欢迎标题
        welcome_frame = tk.Frame(self.current_frame, bg=COLORS['bg_dark'])
        welcome_frame.pack(fill=tk.X, pady=30)
        
        tk.Label(welcome_frame, text="欢迎回来！", 
                font=('Microsoft YaHei', 32, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_dark']).pack()
        
        tk.Label(welcome_frame, text="继续你的印地语学习之旅", 
                font=('Segoe UI', 14),
                fg=COLORS['text_secondary'], bg=COLORS['bg_dark']).pack(pady=10)
        
        # 统计卡片
        stats = self.db.get_statistics()
        
        stats_frame = tk.Frame(self.current_frame, bg=COLORS['bg_dark'])
        stats_frame.pack(fill=tk.X, pady=20)
        
        # 创建统计卡片
        self.create_stat_card(stats_frame, "📚", str(stats['total_words']), 
                             "总词汇", COLORS['primary'])
        self.create_stat_card(stats_frame, "📅", str(stats['due_today']), 
                             "待复习", COLORS['warning'] if stats['due_today'] > 0 else COLORS['success'])
        self.create_stat_card(stats_frame, "🏆", str(stats['stage_distribution'].get(5, 0)), 
                             "已掌握", COLORS['success'])
        
        # 快速操作区
        action_frame = tk.Frame(self.current_frame, bg=COLORS['bg_dark'])
        action_frame.pack(fill=tk.X, pady=40)
        
        tk.Label(action_frame, text="快速开始", 
                font=('Microsoft YaHei', 20, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_dark']).pack(anchor='w', padx=50)
        
        # 操作按钮
        btn_frame = tk.Frame(action_frame, bg=COLORS['bg_dark'])
        btn_frame.pack(fill=tk.X, padx=50, pady=20)
        
        ModernButton(btn_frame, "🎙️ 开始跟读训练", 
                    command=self.show_shadowing,
                    bg_color=COLORS['primary']).pack(side=tk.LEFT, padx=10)
        
        ModernButton(btn_frame, "🎬 YouTube学习", 
                    command=self.show_youtube,
                    bg_color=COLORS['accent']).pack(side=tk.LEFT, padx=10)
        
        if stats['due_today'] > 0:
            ModernButton(btn_frame, f"📚 复习单词 ({stats['due_today']})", 
                        command=self.show_review,
                        bg_color=COLORS['warning']).pack(side=tk.LEFT, padx=10)
    
    def create_stat_card(self, parent, icon, value, label, color):
        """创建统计卡片"""
        card = tk.Frame(parent, bg=COLORS['bg_card'], 
                       highlightbackground=COLORS['border'],
                       highlightthickness=1)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # 内边距
        inner = tk.Frame(card, bg=COLORS['bg_card'])
        inner.pack(padx=30, pady=30)
        
        # 图标
        tk.Label(inner, text=icon, font=('Segoe UI', 40),
                bg=COLORS['bg_card']).pack()
        
        # 数值
        tk.Label(inner, text=value, font=('Segoe UI', 36, 'bold'),
                fg=color, bg=COLORS['bg_card']).pack(pady=5)
        
        # 标签
        tk.Label(inner, text=label, font=('Microsoft YaHei', 12),
                fg=COLORS['text_secondary'], bg=COLORS['bg_card']).pack()
    
    def show_youtube(self):
        """显示YouTube学习界面"""
        self.clear_content()
        
        # 导入YouTube界面模块
        from gui_youtube import YouTubeFrame
        youtube_frame = YouTubeFrame(self.current_frame, self)
        youtube_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_shadowing(self):
        """显示跟读训练界面"""
        self.clear_content()
        
        tk.Label(self.current_frame, text="🎙️ 跟读训练", 
                font=('Microsoft YaHei', 28, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_dark']).pack(pady=30)
        
        tk.Label(self.current_frame, text="功能开发中...", 
                font=('Segoe UI', 14),
                fg=COLORS['text_secondary'], bg=COLORS['bg_dark']).pack()
    
    def show_review(self):
        """显示复习界面"""
        self.clear_content()
        
        tk.Label(self.current_frame, text="📚 每日复习", 
                font=('Microsoft YaHei', 28, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_dark']).pack(pady=30)
        
        # 获取待复习单词
        due_words = self.db.get_due_words()
        
        if not due_words:
            tk.Label(self.current_frame, text="🎉 太棒了！今天没有需要复习的单词", 
                    font=('Microsoft YaHei', 16),
                    fg=COLORS['success'], bg=COLORS['bg_dark']).pack(pady=50)
        else:
            tk.Label(self.current_frame, text=f"今天有 {len(due_words)} 个单词需要复习", 
                    font=('Segoe UI', 14),
                    fg=COLORS['text_secondary'], bg=COLORS['bg_dark']).pack()
    
    def show_settings(self):
        """显示设置界面"""
        self.clear_content()
        
        tk.Label(self.current_frame, text="⚙️ 设置", 
                font=('Microsoft YaHei', 28, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_dark']).pack(pady=30)
        
        # 语言设置
        settings_frame = tk.Frame(self.current_frame, bg=COLORS['bg_card'],
                                 highlightbackground=COLORS['border'],
                                 highlightthickness=1)
        settings_frame.pack(fill=tk.X, padx=100, pady=20)
        
        inner = tk.Frame(settings_frame, bg=COLORS['bg_card'])
        inner.pack(padx=30, pady=30)
        
        tk.Label(inner, text="界面语言", font=('Microsoft YaHei', 14, 'bold'),
                fg=COLORS['text_primary'], bg=COLORS['bg_card']).pack(anchor='w')
        
        tk.Label(inner, text="当前: 中文", font=('Segoe UI', 12),
                fg=COLORS['text_secondary'], bg=COLORS['bg_card']).pack(anchor='w', pady=10)


def main():
    """主函数"""
    root = tk.Tk()
    app = HindiTrainerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
