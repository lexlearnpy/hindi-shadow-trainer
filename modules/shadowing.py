"""
跟读模式模块
Shadowing Mode Module

实现完整的跟读训练流程:
1. 播放标准音频
2. 倒计时
3. 录制用户发音
4. Whisper识别
5. 评分和高亮显示
"""
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from modules.audio import AudioManager
from modules.tts import HindiTTS
from modules.whisper_engine import WhisperEngine
from modules.scoring import PronunciationScorer
from modules.highlighter import TextHighlighter
from modules.database import VocabDatabase

console = Console()


class ShadowingSession:
    """跟读训练会话"""
    
    def __init__(self):
        self.audio_mgr = AudioManager()
        self.tts = HindiTTS()
        self.whisper = WhisperEngine()
        self.scorer = PronunciationScorer()
        self.highlighter = TextHighlighter()
        self.db = VocabDatabase()
    
    def run(self, text: str = None, audio_file: str = None):
        """
        运行跟读训练
        Run shadowing practice session
        
        Args:
            text: 印地语文本（如不提供则使用音频文件）
            audio_file: 预录音频文件路径（可选）
        """
        # 获取文本
        if not text:
            text = input(f"{Config.get_text('enter_hindi_text')}: ").strip()
        
        if not text:
            console.print("[red]❌ 请输入文本 / Please enter text[/red]")
            return
        
        # 步骤1: 播放标准音频
        # Step 1: Play standard audio
        self._play_standard_audio(text, audio_file)
        
        # 步骤2: 倒计时
        # Step 2: Countdown
        self._countdown()
        
        # 步骤3: 录音
        # Step 3: Record
        recording_path = self._record_audio(text)
        if not recording_path:
            return
        
        # 步骤4: 语音识别
        # Step 4: Speech recognition
        transcribed = self._transcribe(recording_path)
        if not transcribed:
            return
        
        # 步骤5: 评分和显示
        # Step 5: Scoring and display
        score = self._score_and_display(text, transcribed)
        
        # 步骤6: 询问是否加入生词本
        # Step 6: Ask to add to vocabulary
        self._ask_add_to_vocab(text, score)
    
    def _play_standard_audio(self, text: str, audio_file: str = None):
        """播放标准音频"""
        console.print(Panel(
            f"[bold]{Config.get_text('standard_text')}:[/bold]\n{text}",
            border_style="cyan"
        ))
        
        if audio_file and Path(audio_file).exists():
            # 播放本地音频文件
            # Play local audio file
            console.print("🔊 播放标准音频...")
            self.audio_mgr.play(audio_file)
        else:
            # 使用TTS生成音频
            # Use TTS to generate audio
            console.print("🔊 正在生成标准发音...")
            try:
                audio_path = self.tts.synthesize_sync(text)
                self.audio_mgr.play(str(audio_path))
            except Exception as e:
                console.print(f"[yellow]⚠️ TTS生成失败: {e}[/yellow]")
    
    def _countdown(self):
        """倒计时 3-2-1"""
        console.print()
        for i in range(3, 0, -1):
            console.print(f"[bold yellow]{Config.get_text('recording_countdown', i)}...[/bold yellow]")
            time.sleep(1)
        console.print(f"[bold green]{Config.get_text('recording_start')}[/bold green]")
    
    def _record_audio(self, text: str) -> str:
        """录制用户发音"""
        # 计算录音时长
        # Calculate recording duration
        duration = self.audio_mgr.calculate_duration(text)
        
        console.print(f"⏱️  录音时长: {duration}秒")
        
        # 录音文件路径
        recording_path = Config.TTS_TEMP_DIR / "user_recording.wav"
        
        # 开始录音
        if not self.audio_mgr.record(duration, str(recording_path)):
            return None
        
        console.print(f"[bold]{Config.get_text('recording_stop')}[/bold]")
        return str(recording_path)
    
    def _transcribe(self, audio_path: str) -> str:
        """语音识别"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 正在识别...", total=None)
            
            try:
                transcribed = self.whisper.transcribe(audio_path)
                progress.update(task, completed=True)
                return transcribed
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]识别失败: {e}[/red]")
                return ""
    
    def _score_and_display(self, standard: str, transcribed: str) -> float:
        """评分和显示结果"""
        # 计算得分
        score = self.scorer.calculate_score(standard, transcribed)
        
        # 显示高亮对比
        self.highlighter.highlight_diff(standard, transcribed, score)
        
        return score
    
    def _ask_add_to_vocab(self, text: str, score: float):
        """询问是否加入生词本"""
        if score >= Config.SCORE_GOOD:
            console.print("[green]✅ 发音很好，不需要加入生词本[/green]")
            return
        
        response = input(f"\n{Config.get_text('add_to_vocab')} (y/n): ").lower()
        
        if response == 'y':
            meaning = input(f"{Config.get_text('enter_meaning')}: ")
            if meaning:
                word_id = self.db.add_word(text, meaning)
                console.print(f"[green]{Config.get_text('save_success')} ID: {word_id}[/green]")


if __name__ == "__main__":
    # 测试
    session = ShadowingSession()
    session.run("नमस्ते, आप कैसे हैं?")
