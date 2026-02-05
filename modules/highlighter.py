"""
文本高亮模块
Text Highlighting Module

使用Rich库在终端中显示带颜色的差异对比
Use Rich library to display colored differences in terminal
"""
import sys
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.text import Text
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from modules.scoring import PronunciationScorer


console = Console()


class TextHighlighter:
    """文本高亮器 - 显示标准文本和发音对比"""
    
    def __init__(self):
        self.scorer = PronunciationScorer()
    
    def highlight_diff(self, standard: str, transcribed: str, score: float):
        """
        高亮显示标准文本和转写文本的差异
        Highlight differences between standard and transcribed text
        
        显示逻辑:
        - 绿色: 匹配的单词
        - 红色: 标准中有但转写中缺失的单词
        - 灰色: 转写中有但标准中没有的单词（多余发音）
        
        Args:
            standard: 标准印地语文本
            transcribed: Whisper转写的文本
            score: 得分
        """
        # 标准化用于比较
        s_words = standard.split()
        t_words = transcribed.split()
        
        # 构建标准文本的高亮显示
        # Build highlighted standard text
        standard_text = Text()
        matched_indices = set()
        
        # 找到匹配的单词位置
        # Find matching word positions
        for i, s_word in enumerate(s_words):
            normalized_s = self.scorer._normalize_word(s_word)
            found = False
            
            for j, t_word in enumerate(t_words):
                if j in matched_indices:
                    continue
                normalized_t = self.scorer._normalize_word(t_word)
                
                if normalized_s == normalized_t:
                    standard_text.append(f"{s_word} ", style="bold green")
                    matched_indices.add(j)
                    found = True
                    break
            
            if not found:
                # 未匹配到，显示红色
                # Not matched, show in red
                standard_text.append(f"{s_word} ", style="bold red")
        
        # 构建转写文本的显示
        # Build transcribed text display
        transcribed_text = Text()
        for j, t_word in enumerate(t_words):
            if j in matched_indices:
                # 已匹配，显示绿色
                # Matched, show in green
                transcribed_text.append(f"{t_word} ", style="green")
            else:
                # 多余的单词，显示灰色
                # Extra words, show in gray
                transcribed_text.append(f"{t_word} ", style="dim")
        
        # 显示结果
        # Display results
        console.print()
        console.print(Panel(
            standard_text,
            title=f"[bold cyan]{Config.get_text('standard_text')}[/bold cyan]",
            border_style="cyan"
        ))
        
        console.print(Panel(
            transcribed_text,
            title=f"[bold cyan]{Config.get_text('your_pronunciation')}[/bold cyan]",
            border_style="blue"
        ))
        
        # 显示得分
        # Show score
        score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
        console.print(f"\n[bold]{Config.get_text('score_result')}:[/bold] [{score_color}]{score}%[/{score_color}]")
        
        # 显示评级
        # Show rating
        level = self.scorer.get_score_level(score)
        console.print(f"[bold]评级:[/bold] {level}\n")
    
    def show_comparison_table(self, standard: str, transcribed: str):
        """
        显示详细的对比表格
        Show detailed comparison table
        """
        from rich.table import Table
        
        table = Table(title="发音对比分析")
        table.add_column("标准单词", style="cyan")
        table.add_column("你的发音", style="blue")
        table.add_column("状态", style="green")
        
        s_words = standard.split()
        t_words = transcribed.split()
        
        max_len = max(len(s_words), len(t_words))
        
        for i in range(max_len):
            s_word = s_words[i] if i < len(s_words) else "-"
            t_word = t_words[i] if i < len(t_words) else "-"
            
            if s_word == t_word:
                status = "✓ 匹配"
                style = "green"
            elif s_word == "-":
                status = "✗ 多余"
                style = "yellow"
            elif t_word == "-":
                status = "✗ 遗漏"
                style = "red"
            else:
                status = "~ 近似"
                style = "blue"
            
            table.add_row(s_word, t_word, f"[{style}]{status}[/{style}]")
        
        console.print(table)


if __name__ == "__main__":
    # 测试
    highlighter = TextHighlighter()
    
    standard = "नमस्ते, आप कैसे हैं?"
    transcribed = "नमस्ते आप कैसे है"
    score = 85.5
    
    highlighter.highlight_diff(standard, transcribed, score)
