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
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from config import Config
from modules.shadowing import ShadowingSession
from modules.review import ReviewMode
from modules.database import VocabDatabase

console = Console()


def show_menu():
    """显示主菜单"""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]{Config.get_text('app_title')}[/bold cyan]\n"
        f"[dim]{Config.get_text('app_subtitle')}[/dim]",
        border_style="cyan"
    ))
    
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("选项", style="yellow")
    table.add_column("功能", style="white")
    
    table.add_row("1", Config.get_text('menu_shadowing'))
    table.add_row("2", Config.get_text('menu_review'))
    table.add_row("3", Config.get_text('menu_add_vocab'))
    table.add_row("4", Config.get_text('menu_statistics'))
    table.add_row("5", Config.get_text('menu_settings'))
    table.add_row("0", Config.get_text('menu_exit'))
    
    console.print(table)


def add_vocabulary():
    """添加新单词"""
    console.print(Panel(
        Config.get_text('menu_add_vocab'),
        border_style="green"
    ))
    
    word = input(f"{Config.get_text('enter_hindi_text')}: ").strip()
    if not word:
        console.print("[red]❌ 单词不能为空[/red]")
        return
    
    meaning = input(f"{Config.get_text('enter_meaning')}: ").strip()
    if not meaning:
        console.print("[red]❌ 含义不能为空[/red]")
        return
    
    context = input("上下文例句 (可选): ").strip() or None
    
    db = VocabDatabase()
    word_id = db.add_word(word, meaning, context)
    
    console.print(f"[green]{Config.get_text('save_success')} ID: {word_id}[/green]")


def show_statistics():
    """显示学习统计"""
    review = ReviewMode()
    review.show_statistics()


def show_settings():
    """显示设置菜单"""
    console.print(Panel("设置", border_style="yellow"))
    
    console.print(f"\n当前语言: {Config.LANGUAGE}")
    console.print("\n1. 中文 (Chinese)")
    console.print("2. English")
    console.print("0. 返回")
    
    choice = Prompt.ask("选择", choices=["0", "1", "2"], default="0")
    
    if choice == "1":
        Config.set_language('zh')
        console.print("[green]已切换到中文[/green]")
    elif choice == "2":
        Config.set_language('en')
        console.print("[green]Switched to English[/green]")


def main():
    """主函数"""
    try:
        while True:
            show_menu()
            
            choice = Prompt.ask(
                "请选择",
                choices=["0", "1", "2", "3", "4", "5"],
                default="1"
            )
            
            if choice == "1":
                # 跟读训练
                session = ShadowingSession()
                session.run()
                
            elif choice == "2":
                # 每日复习
                review = ReviewMode()
                review.run()
                
            elif choice == "3":
                # 添加单词
                add_vocabulary()
                
            elif choice == "4":
                # 学习统计
                show_statistics()
                
            elif choice == "5":
                # 设置
                show_settings()
                
            elif choice == "0":
                # 退出
                console.print(f"[green]{Config.get_text('exit_message')}[/green]")
                break
                
    except KeyboardInterrupt:
        console.print(f"\n[green]{Config.get_text('exit_message')}[/green]")
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
