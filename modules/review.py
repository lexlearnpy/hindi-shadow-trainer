"""
复习模式模块
Review Mode Module

实现每日生词复习功能，基于SM-2算法
Implement daily vocabulary review based on SM-2 algorithm
"""
import sys
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from modules.database import VocabDatabase
from modules.tts import HindiTTS
from modules.srs import SM2Algorithm

console = Console()


class ReviewMode:
    """复习模式类"""
    
    # 质量选项映射
    QUALITY_OPTIONS = {
        '1': ('forgot', 0),
        '2': ('hard', 3),
        '3': ('good', 4),
        '4': ('easy', 5)
    }
    
    def __init__(self):
        self.db = VocabDatabase()
        self.tts = HindiTTS()
        self.srs = SM2Algorithm()
    
    def run(self):
        """运行复习模式"""
        # 获取今天需要复习的单词
        due_words = self.db.get_due_words()
        
        if not due_words:
            console.print(f"[yellow]{Config.get_text('no_words_due')}[/yellow]")
            return
        
        console.print(Panel(
            f"[bold]{Config.get_text('words_due_count', len(due_words))}[/bold]",
            border_style="green"
        ))
        
        # 开始复习
        for word_data in due_words:
            self._review_word(word_data)
        
        console.print("[green]✅ 复习完成！[/green]")
    
    def _review_word(self, word_data: Dict):
        """复习单个单词"""
        word = word_data['word']
        meaning = word_data['meaning']
        context = word_data.get('context_sentence', '')
        current_stage = word_data['review_stage']
        
        # 显示单词
        console.print()
        console.print(Panel(
            f"[bold cyan]{word}[/bold cyan]\n"
            f"[dim]{context}[/dim]" if context else word,
            title=f"阶段 {current_stage}",
            border_style="blue"
        ))
        
        # 播放发音（使用TTS）
        # Play pronunciation using TTS
        try:
            audio_path = self.tts.synthesize_sync(word)
            from modules.audio import AudioManager
            audio_mgr = AudioManager()
            audio_mgr.play(str(audio_path))
        except Exception as e:
            console.print(f"[dim]音频播放失败: {e}[/dim]")
        
        # 等待用户查看含义
        input("\n按回车查看含义...")
        
        # 显示含义
        console.print(f"[bold green]含义: {meaning}[/bold green]\n")
        
        # 询问记忆程度
        quality = self._ask_quality()
        
        # 计算下次复习时间
        result = self.srs.calculate_next_review(
            current_stage,
            quality,
            word_data.get('last_interval')
        )
        
        # 更新数据库
        self.db.update_review(
            word_data['id'],
            quality,
            result['next_date'],
            result['new_stage']
        )
        
        # 显示结果
        console.print(
            f"[dim]{Config.get_text('next_review', result['next_date'])} "
            f"(阶段 {result['new_stage']})[/dim]"
        )
    
    def _ask_quality(self) -> int:
        """询问用户记忆程度"""
        console.print("[bold]记忆程度?[/bold]")
        console.print("1. " + Config.get_text('quality_forgot'))
        console.print("2. " + Config.get_text('quality_hard'))
        console.print("3. " + Config.get_text('quality_good'))
        console.print("4. " + Config.get_text('quality_easy'))
        
        while True:
            choice = Prompt.ask(
                "选择",
                choices=["1", "2", "3", "4"],
                default="3"
            )
            
            if choice in self.QUALITY_OPTIONS:
                return self.QUALITY_OPTIONS[choice][1]
    
    def show_statistics(self):
        """显示学习统计"""
        stats = self.db.get_statistics()
        
        table = Table(title="学习统计")
        table.add_column("项目", style="cyan")
        table.add_column("数值", style="green")
        
        table.add_row("总单词数", str(stats['total_words']))
        table.add_row("今日需复习", str(stats['due_today']))
        
        # 各阶段分布
        for stage, count in sorted(stats['stage_distribution'].items()):
            table.add_row(f"阶段 {stage}", str(count))
        
        console.print(table)


if __name__ == "__main__":
    # 测试
    review = ReviewMode()
    review.run()
