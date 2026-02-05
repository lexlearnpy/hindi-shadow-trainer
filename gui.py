"""
印地语影子跟读训练器 - 现代GUI版本
Hindi Shadow Trainer - Modern GUI Version (Flet)
"""
import sys
import os
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime, date

import flet as ft

sys.path.insert(0, str(Path(__file__).parent))
from config import Config
from modules.database import VocabDatabase
from modules.srs import SM2Algorithm
from modules.scoring import PronunciationScorer
from modules.whisper_engine import WhisperEngine
from modules.tts import HindiTTS
from modules.audio import AudioManager


class HindiTrainerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "印地语影子跟读训练器"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        
        # 初始化组件
        self.db = VocabDatabase()
        self.tts = HindiTTS()
        self.scorer = PronunciationScorer()
        self.srs = SM2Algorithm()
        self.audio_mgr = AudioManager()
        self.whisper_engine = None
        
        # 当前视图
        self.current_view = "home"
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 顶部导航栏
        self.app_bar = ft.AppBar(
            title=ft.Text("🇮🇳 印地语影子跟读训练器", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.colors.DEEP_PURPLE,
            color=ft.colors.WHITE,
            actions=[
                ft.IconButton(ft.icons.HOME, tooltip="首页", on_click=lambda _: self.show_home()),
                ft.IconButton(ft.icons.MIC, tooltip="跟读", on_click=lambda _: self.show_shadowing()),
                ft.IconButton(ft.icons.BOOK, tooltip="复习", on_click=lambda _: self.show_review()),
                ft.IconButton(ft.icons.ADD_CIRCLE, tooltip="添加", on_click=lambda _: self.show_add_vocab()),
                ft.IconButton(ft.icons.ANALYTICS, tooltip="统计", on_click=lambda _: self.show_stats()),
            ]
        )
        
        # 主要内容区域
        self.main_content = ft.Container(
            content=self.build_home_view(),
            expand=True,
            padding=20
        )
        
        self.page.appbar = self.app_bar
        self.page.add(self.main_content)
    
    def build_home_view(self):
        """构建首页视图"""
        stats = self.db.get_statistics()
        
        return ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("欢迎回来!", size=32, weight=ft.FontWeight.BOLD),
                            ft.Text("继续你的印地语学习之旅", size=16, color=ft.colors.GREY_600),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=40,
                    alignment=ft.alignment.center
                ),
                
                # 统计卡片行
                ft.Row(
                    [
                        self._stat_card("📚", str(stats['total_words']), "总词汇"),
                        self._stat_card("📅", str(stats['due_today']), "待复习", 
                                       color=ft.colors.RED if stats['due_today'] > 0 else ft.colors.GREEN),
                        self._stat_card("🏆", str(stats['stage_distribution'].get(5, 0)), "已掌握"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                ),
                
                ft.Divider(height=40),
                
                # 快速操作
                ft.Text("快速开始", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        self._action_button("🎙️ 开始跟读", ft.colors.BLUE, self.show_shadowing),
                        self._action_button("📚 每日复习", ft.colors.ORANGE, self.show_review),
                        self._action_button("➕ 添加单词", ft.colors.GREEN, self.show_add_vocab),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _stat_card(self, icon, value, label, color=ft.colors.DEEP_PURPLE):
        """统计卡片"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(icon, size=40),
                        ft.Text(value, size=36, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(label, size=14, color=ft.colors.GREY_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                padding=30,
                width=200,
                height=180
            ),
            elevation=5
        )
    
    def _action_button(self, text, color, on_click):
        """操作按钮"""
        return ft.ElevatedButton(
            text,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=color,
                padding=ft.padding.symmetric(horizontal=40, vertical=20),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
            ),
            on_click=lambda _: on_click()
        )
    
    def show_shadowing(self):
        """显示跟读页面"""
        self.current_view = "shadowing"
        
        input_text = ft.TextField(
            label="输入印地语文本",
            hint_text="例如: नमस्ते, आप कैसे हैं?",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=10
        )
        
        result_text = ft.Text(size=18, selectable=True)
        score_text = ft.Text(size=48, weight=ft.FontWeight.BOLD)
        
        async def on_transcribe(e):
            if not input_text.value:
                return
            
            # 显示加载
            self.page.dialog = ft.AlertDialog(
                content=ft.Column(
                    [ft.ProgressRing(), ft.Text("识别中...")],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            self.page.dialog.open = True
            self.page.update()
            
            try:
                # 录音（简化版，实际应该使用音频录制）
                recording_path = tempfile.mktemp(suffix='.wav')
                self.audio_mgr.record(5, recording_path)  # 录制5秒示例
                
                # 加载Whisper（如果未加载）
                if self.whisper_engine is None:
                    self.whisper_engine = WhisperEngine()
                
                # 识别
                transcribed = self.whisper_engine.transcribe(recording_path)
                
                # 评分
                score = self.scorer.calculate_score(input_text.value, transcribed)
                
                # 更新结果
                result_text.value = f"识别结果: {transcribed}"
                score_text.value = f"{score}%"
                score_text.color = ft.colors.GREEN if score >= 70 else ft.colors.ORANGE if score >= 50 else ft.colors.RED
                
                self.page.dialog.open = False
                
            except Exception as ex:
                result_text.value = f"错误: {str(ex)}"
                self.page.dialog.open = False
            
            self.page.update()
        
        async def on_play(e):
            if input_text.value:
                try:
                    audio_path = await self.tts.synthesize(input_text.value)
                    self.audio_mgr.play(str(audio_path))
                except Exception as ex:
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"播放失败: {str(ex)}")))
        
        view = ft.Column(
            [
                ft.Text("🎙️ 跟读训练", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                input_text,
                ft.Row(
                    [
                        ft.ElevatedButton("🔊 播放标准发音", on_click=on_play),
                        ft.ElevatedButton("🎤 录制并识别", bgcolor=ft.colors.RED, color=ft.colors.WHITE, on_click=on_transcribe),
                    ],
                    spacing=20
                ),
                ft.Divider(),
                ft.Text("识别结果", size=20, weight=ft.FontWeight.BOLD),
                result_text,
                ft.Text("发音评分", size=20, weight=ft.FontWeight.BOLD),
                score_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        self.main_content.content = view
        self.page.update()
    
    def show_review(self):
        """显示复习页面"""
        self.current_view = "review"
        
        due_words = self.db.get_due_words()
        
        if not due_words:
            view = ft.Column(
                [
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=100, color=ft.colors.GREEN),
                    ft.Text("太棒了!", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("今天没有需要复习的单词", size=18, color=ft.colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
            self.main_content.content = view
            self.page.update()
            return
        
        current_index = [0]
        show_answer = [False]
        
        def build_card():
            word = due_words[current_index[0]]
            
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"{current_index[0] + 1} / {len(due_words)}", 
                                   size=14, color=ft.colors.GREY_600),
                            ft.Text(word['word'], size=48, weight=ft.FontWeight.BOLD),
                            ft.Text(f"阶段 {word['review_stage']}", 
                                   size=14, color=ft.colors.GREY_600),
                            
                            ft.Divider(),
                            
                            if show_answer[0]:
                                ft.Column([
                                    ft.Text(word['meaning'], size=32, color=ft.colors.GREEN),
                                    if word.get('context_sentence'):
                                        ft.Text(f"例句: {word['context_sentence']}", 
                                               size=16, color=ft.colors.GREY_600, italic=True),
                                    
                                    ft.Divider(),
                                    ft.Text("记忆程度?", size=18),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton("😵 忘了", 
                                                            on_click=lambda _: rate_word(0)),
                                            ft.ElevatedButton("😰 模糊", 
                                                            on_click=lambda _: rate_word(3)),
                                            ft.ElevatedButton("🙂 记得", 
                                                            on_click=lambda _: rate_word(4)),
                                            ft.ElevatedButton("😎 秒杀", 
                                                            on_click=lambda _: rate_word(5)),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                    )
                                ])
                            else:
                                ft.ElevatedButton("👀 显示答案", 
                                                on_click=lambda _: show_answer_btn())
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    padding=40,
                    width=600
                ),
                elevation=10
            )
        
        def show_answer_btn():
            show_answer[0] = True
            refresh_view()
        
        def rate_word(quality):
            word = due_words[current_index[0]]
            result = self.srs.calculate_next_review(
                word['review_stage'],
                quality
            )
            self.db.update_review(word['id'], quality, 
                                result['next_date'], result['new_stage'])
            
            current_index[0] += 1
            show_answer[0] = False
            
            if current_index[0] >= len(due_words):
                self.page.dialog = ft.AlertDialog(
                    title=ft.Text("🎉 复习完成!"),
                    content=ft.Text(f"完成了 {len(due_words)} 个单词的复习"),
                    actions=[ft.TextButton("确定", on_click=lambda _: close_dialog())]
                )
                self.page.dialog.open = True
            
            refresh_view()
        
        def close_dialog():
            self.page.dialog.open = False
            self.show_home()
        
        def refresh_view():
            if current_index[0] < len(due_words):
                view_content.controls[1] = build_card()
                self.page.update()
        
        view_content = ft.Column(
            [
                ft.Text("📚 每日复习", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                build_card(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        
        self.main_content.content = view_content
        self.page.update()
    
    def show_add_vocab(self):
        """显示添加单词页面"""
        self.current_view = "add"
        
        word_input = ft.TextField(label="印地语单词", border_radius=10)
        meaning_input = ft.TextField(label="中文含义", border_radius=10)
        context_input = ft.TextField(
            label="例句 (可选)", 
            multiline=True,
            min_lines=2,
            border_radius=10
        )
        
        def on_save(e):
            if word_input.value and meaning_input.value:
                word_id = self.db.add_word(
                    word_input.value,
                    meaning_input.value,
                    context_input.value if context_input.value else None
                )
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"✅ 已保存! ID: {word_id}"))
                )
                word_input.value = ""
                meaning_input.value = ""
                context_input.value = ""
                self.page.update()
        
        view = ft.Column(
            [
                ft.Text("➕ 添加新单词", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                word_input,
                meaning_input,
                context_input,
                ft.ElevatedButton(
                    "💾 保存单词",
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(horizontal=50, vertical=20)
                    ),
                    on_click=on_save
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )
        
        self.main_content.content = view
        self.page.update()
    
    def show_stats(self):
        """显示统计页面"""
        self.current_view = "stats"
        
        stats = self.db.get_statistics()
        
        # 创建图表数据
        stage_data = stats['stage_distribution']
        chart_bars = []
        
        for stage in range(6):
            count = stage_data.get(stage, 0)
            max_count = max(stage_data.values()) if stage_data else 1
            percentage = (count / max_count * 100) if max_count > 0 else 0
            
            chart_bars.append(
                ft.Row(
                    [
                        ft.Text(f"阶段 {stage}", width=80),
                        ft.ProgressBar(
                            value=count / max(stats['total_words'], 1),
                            width=400,
                            color=ft.colors.DEEP_PURPLE
                        ),
                        ft.Text(str(count), width=50),
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            )
        
        view = ft.Column(
            [
                ft.Text("📊 学习统计", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("总词汇", size=16, color=ft.colors.GREY_600),
                            ft.Text(str(stats['total_words']), size=36, weight=ft.FontWeight.BOLD),
                        ], alignment=ft.CrossAxisAlignment.CENTER),
                        ft.VerticalDivider(width=50),
                        ft.Column([
                            ft.Text("待复习", size=16, color=ft.colors.GREY_600),
                            ft.Text(str(stats['due_today']), size=36, weight=ft.FontWeight.BOLD,
                                   color=ft.colors.RED if stats['due_today'] > 0 else ft.colors.GREEN),
                        ], alignment=ft.CrossAxisAlignment.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                
                ft.Divider(),
                ft.Text("掌握程度分布", size=20, weight=ft.FontWeight.BOLD),
                ft.Column(chart_bars, spacing=10),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        self.main_content.content = view
        self.page.update()
    
    def show_home(self):
        """显示首页"""
        self.current_view = "home"
        self.main_content.content = self.build_home_view()
        self.page.update()


def main(page: ft.Page):
    HindiTrainerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
