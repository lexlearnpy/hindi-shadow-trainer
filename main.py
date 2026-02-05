#!/usr/bin/env python3
"""
印地语影子跟读训练器 - 主程序
Hindi Shadow Trainer - Main Application

功能:
1. 跟读训练 (Shadowing)
2. 每日复习 (Daily Review)
3. 添加单词 (Add Vocabulary)
4. 学习统计 (Statistics)
5. 设置 (Settings)
"""
import sys
import os
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from config import Config
from modules.shadowing import ShadowingSession
from modules.review import ReviewMode
from modules.database import VocabDatabase

console = Console()


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_header():
    """显示程序头部"""
    title = Text()
    title.append("🇮🇳 印地语影子跟读训练器\n", style="bold cyan")
    title.append("Hindi Shadow Trainer", style="dim")
    
    header = Panel(
        Align.center(title),
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(header)


def show_menu():
    """显示主菜单 - 简洁大方版本"""
    # 获取今日待复习数量
    db = VocabDatabase()
    stats = db.get_statistics()
    due_count = stats['due_today']
    
    # 创建选项卡片
    options = []
    
    # 选项1: 跟读训练
    shadowing_card = Panel(
        "[bold]🎙️  开始跟读[/bold]\n"
        "[dim]练习印地语发音[/dim]",
        border_style="green",
        padding=(1, 2),
        width=25
    )
    options.append(("1", shadowing_card))
    
    # 选项2: 每日复习（显示数量）
    review_text = f"[bold]📚 每日复习[/bold]\n[dim]"
    if due_count > 0:
        review_text += f"[red]今日 {due_count} 个[/red]"
    else:
        review_text += "今日无复习"
    review_text += "[/dim]"
    
    review_card = Panel(
        review_text,
        border_style="yellow" if due_count > 0 else "dim",
        padding=(1, 2),
        width=25
    )
    options.append(("2", review_card))
    
    # 选项3: 添加单词
    add_card = Panel(
        "[bold]➕ 添加单词[/bold]\n"
        "[dim]添加新词汇[/dim]",
        border_style="blue",
        padding=(1, 2),
        width=25
    )
    options.append(("3", add_card))
    
    # 选项4: 统计
    stats_card = Panel(
        f"[bold]📊 学习统计[/bold]\n"
        f"[dim]已掌握 {stats['total_words']} 词[/dim]",
        border_style="magenta",
        padding=(1, 2),
        width=25
    )
    options.append(("4", stats_card))
    
    # 选项5: 设置
    settings_card = Panel(
        "[bold]⚙️  设置[/bold]\n"
        "[dim]语言等选项[/dim]",
        border_style="white",
        padding=(1, 2),
        width=25
    )
    options.append(("5", settings_card))
    
    # 显示选项网格
    console.print()
    console.print(Columns([card for _, card in options], equal=True))
    
    # 显示退出选项
    console.print()
    console.print(Align.center("[dim]按 0 退出程序[/dim]"))
    console.print()


def show_welcome():
    """显示欢迎界面"""
    clear_screen()
    
    # ASCII艺术Logo
    logo = """
    ██╗  ██╗██╗███╗   ██╗██████╗ ██╗
    ██║  ██║██║████╗  ██║██╔══██╗██║
    ███████║██║██╔██╗ ██║██║  ██║██║
    ██╔══██║██║██║╚██╗██║██║  ██║██║
    ██║  ██║██║██║ ╚████║██████╔╝██║
    ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝
    """
    
    console.print(Align.center(Text(logo, style="cyan")))
    
    welcome_text = Text()
    welcome_text.append("欢迎来到印地语影子跟读训练器\n", style="bold green")
    welcome_text.append("Welcome to Hindi Shadow Trainer\n\n", style="dim")
    welcome_text.append("使用方向键或数字键选择功能\n", style="dim")
    welcome_text.append("Press number keys to select features", style="dim")
    
    console.print(Align.center(Panel(
        welcome_text,
        border_style="green",
        padding=(1, 4)
    )))
    
    console.print()
    input("按回车键开始...")
    clear_screen()


def add_vocabulary():
    """添加新单词 - 简洁版本"""
    console.print()
    console.print(Panel(
        "[bold]添加新单词[/bold]\n"
        "[dim]Add New Vocabulary[/dim]",
        border_style="green",
        padding=(1, 2)
    ))
    
    word = console.input("[cyan]印地语单词:[/cyan] ").strip()
    if not word:
        console.print("[red]❌ 单词不能为空[/red]")
        return
    
    meaning = console.input("[cyan]中文含义:[/cyan] ").strip()
    if not meaning:
        console.print("[red]❌ 含义不能为空[/red]")
        return
    
    context = console.input("[dim]例句 (可选): [/dim]").strip() or None
    
    db = VocabDatabase()
    word_id = db.add_word(word, meaning, context)
    
    console.print()
    console.print(Panel(
        f"[green]✓ 已保存[/green]\n"
        f"[dim]ID: {word_id}[/dim]",
        border_style="green"
    ))
    console.input("\n按回车继续...")


def show_statistics():
    """显示学习统计 - 图表版本"""
    console.print()
    
    db = VocabDatabase()
    stats = db.get_statistics()
    
    # 主统计面板
    main_stats = Table(show_header=False, box=box.SIMPLE)
    main_stats.add_column(style="cyan", justify="right")
    main_stats.add_column(style="white")
    
    main_stats.add_row("📚 总词汇量", str(stats['total_words']))
    main_stats.add_row("📅 今日待复习", f"[red]{stats['due_today']}[/red]" if stats['due_today'] > 0 else "0")
    
    # 阶段分布
    stage_data = stats['stage_distribution']
    if stage_data:
        stages_text = ""
        for stage, count in sorted(stage_data.items()):
            bar = "█" * count
            stages_text += f"[dim]阶段 {stage}:[/dim] {bar} {count}\n"
    else:
        stages_text = "[dim]暂无数据[/dim]"
    
    console.print(Panel(
        main_stats,
        title="[bold]学习统计[/bold]",
        border_style="magenta",
        padding=(1, 2)
    ))
    
    if stage_data:
        console.print()
        console.print(Panel(
            stages_text.strip(),
            title="[bold]掌握程度分布[/bold]",
            border_style="blue",
            padding=(1, 2)
        ))
    
    console.input("\n按回车继续...")


def show_settings():
    """显示设置菜单 - 简洁版本"""
    console.print()
    
    # 当前设置
    current_lang = "中文" if Config.LANGUAGE == 'zh' else "English"
    
    settings_table = Table(show_header=False, box=box.SIMPLE)
    settings_table.add_column(style="cyan")
    settings_table.add_column(style="white")
    
    settings_table.add_row("🌐 语言", current_lang)
    settings_table.add_row("🤖 Whisper模型", Config.WHISPER_MODEL_SIZE)
    
    console.print(Panel(
        settings_table,
        title="[bold]当前设置[/bold]",
        border_style="yellow",
        padding=(1, 2)
    ))
    
    console.print()
    console.print("[dim]切换语言:[/dim]")
    console.print("  [cyan]1.[/cyan] 中文")
    console.print("  [cyan]2.[/cyan] English")
    console.print("  [cyan]0.[/cyan] 返回")
    
    choice = Prompt.ask("\n选择", choices=["0", "1", "2"], default="0")
    
    if choice == "1":
        Config.set_language('zh')
        console.print("[green]✓ 已切换到中文[/green]")
    elif choice == "2":
        Config.set_language('en')
        console.print("[green]✓ Switched to English[/green]")
    
    if choice in ["1", "2"]:
        console.input("\n按回车继续...")


def main():
    """主函数"""
    try:
        show_welcome()
        
        while True:
            clear_screen()
            show_header()
            show_menu()
            
            choice = Prompt.ask(
                "[cyan]请选择[/cyan]",
                choices=["0", "1", "2", "3", "4", "5"],
                default="1"
            )
            
            if choice == "1":
                clear_screen()
                session = ShadowingSession()
                session.run()
                console.input("\n按回车返回主菜单...")
                
            elif choice == "2":
                clear_screen()
                review = ReviewMode()
                review.run()
                console.input("\n按回车返回主菜单...")
                
            elif choice == "3":
                clear_screen()
                add_vocabulary()
                
            elif choice == "4":
                clear_screen()
                show_statistics()
                
            elif choice == "5":
                clear_screen()
                show_settings()
                
            elif choice == "0":
                clear_screen()
                goodbye = Text()
                goodbye.append("谢谢使用！\n", style="bold green")
                goodbye.append("Thanks for using!\n\n", style="dim")
                goodbye.append("🙏 Namaste!", style="cyan")
                
                console.print(Align.center(Panel(
                    goodbye,
                    border_style="green",
                    padding=(2, 4)
                )))
                break
                
    except KeyboardInterrupt:
        console.print(f"\n[green]再见！Namaste! 🙏[/green]")
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        import traceback
        traceback.print_exc()
        input("\n按回车退出...")


if __name__ == "__main__":
    main()
