"""
音频管理模块
Audio management module - recording and playback
"""
import sys
import wave
import threading
import time
from pathlib import Path
from typing import Optional

import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config

console = Console()


class AudioManager:
    """音频管理类 - 负责录音和播放"""
    
    def __init__(self):
        self.sample_rate = Config.AUDIO_SAMPLE_RATE
        self.channels = Config.AUDIO_CHANNELS
        self.dtype = 'int16'
        self.stop_recording = threading.Event()
        self.recording_data = []
        
    def calculate_duration(self, text: str) -> int:
        """
        根据文本长度智能计算录音时长
        Calculate recording duration based on text length
        
        Args:
            text: 印地语文本 / Hindi text
            
        Returns:
            建议的录音时长（秒）/ Recommended duration in seconds
        """
        # 基本时长 + 每个字符的预留时间
        base_duration = Config.AUDIO_DURATION_DEFAULT
        char_duration = len(text) * Config.AUDIO_DURATION_PER_CHAR
        return max(base_duration, int(char_duration))
    
    def _audio_callback(self, indata, frames, time_info, status):
        """音频回调函数，实时收集录音数据"""
        if status:
            print(f"音频状态: {status}")
        self.recording_data.append(indata.copy())
    
    def _create_ui(self, duration, elapsed_time, volume_level):
        """创建录音UI界面"""
        layout = Layout()
        
        # 顶部提示
        header = Panel(
            f"[bold red]🔴 正在录音...[/bold red]\n"
            f"[dim]按 [bold]空格键[/bold] 或 [bold]Enter[/bold] 结束录音[/dim]",
            border_style="red"
        )
        
        # 进度条
        progress = min(elapsed_time / duration, 1.0)
        progress_bar = "█" * int(progress * 30) + "░" * (30 - int(progress * 30))
        
        # 音量可视化
        volume_bar = "▓" * int(volume_level * 20) + "░" * (20 - int(volume_level * 20))
        
        content = f"""
[bold]时间:[/bold] {elapsed_time:.1f}s / {duration}s
[bold]进度:[/bold] [{progress_bar}] {progress*100:.0f}%

[bold]音量:[/bold] [{volume_bar}] {volume_level*100:.0f}%

[cyan]💡 提示: 朗读时保持音量在绿色区域最佳[/cyan]
        """
        
        panel = Panel(
            content,
            title="🎙️ 录音中",
            border_style="cyan"
        )
        
        return panel
    
    def _monitor_keyboard(self):
        """监控键盘输入（在新线程中运行）"""
        try:
            import msvcrt  # Windows only
            while not self.stop_recording.is_set():
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    # 空格键(32) 或 Enter键(13)
                    if key in [b' ', b'\r']:
                        self.stop_recording.set()
                        break
                time.sleep(0.1)
        except ImportError:
            # Linux/Mac 使用其他方式
            pass
    
    def record(self, duration: int, output_path: str) -> bool:
        """
        录制音频 - 带UI界面和按键结束功能
        Record audio with UI and keyboard control
        
        Args:
            duration: 录音时长（秒）
            output_path: 输出文件路径
            
        Returns:
            是否成功 / Success status
        """
        try:
            console.print(f"\n🎙️  {Config.get_text('recording_ready')}")
            console.print("[dim]准备开始，请按任意键...[/dim]")
            input()  # 等待用户准备就绪
            
            # 重置状态
            self.stop_recording.clear()
            self.recording_data = []
            start_time = time.time()
            
            # 启动键盘监听线程
            keyboard_thread = threading.Thread(target=self._monitor_keyboard)
            keyboard_thread.daemon = True
            keyboard_thread.start()
            
            # 开始录音
            stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._audio_callback
            )
            
            with stream:
                with Live(refresh_per_second=10) as live:
                    while not self.stop_recording.is_set():
                        elapsed = time.time() - start_time
                        
                        # 检查是否超时
                        if elapsed >= duration:
                            break
                        
                        # 计算音量
                        volume = 0.0
                        if self.recording_data:
                            recent_data = np.concatenate(self.recording_data[-5:]) if len(self.recording_data) >= 5 else np.concatenate(self.recording_data)
                            volume = min(np.abs(recent_data).mean() / 32768.0 * 5, 1.0)  # 放大音量显示
                        
                        # 更新UI
                        ui = self._create_ui(duration, elapsed, volume)
                        live.update(ui)
                        
                        time.sleep(0.1)
            
            # 合并录音数据
            if self.recording_data:
                recording = np.concatenate(self.recording_data, axis=0)
                
                # 保存为WAV文件
                with wave.open(output_path, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # int16 = 2 bytes
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(recording.tobytes())
                
                actual_duration = len(recording) / self.sample_rate
                console.print(f"[green]✅ 录音完成！时长: {actual_duration:.1f}秒[/green]\n")
                return True
            else:
                console.print("[red]❌ 没有录音数据[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ {Config.get_text('error_microphone')}: {e}[/red]")
            return False
    
    def play(self, audio_path: str) -> bool:
        """
        播放音频文件（支持MP3/WAV）
        Play audio file (supports MP3/WAV)
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            是否成功 / Success status
        """
        try:
            # 使用pydub加载和播放
            # Load and play using pydub
            audio = AudioSegment.from_file(audio_path)
            play(audio)
            return True
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            return False
    
    def play_with_delay(self, audio_path: str, delay_ms: int = 500) -> bool:
        """
        播放音频并在结束后延迟
        Play audio with delay after
        
        Args:
            audio_path: 音频文件路径
            delay_ms: 结束后的延迟（毫秒）
            
        Returns:
            是否成功 / Success status
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            # 添加静音延迟
            # Add silence delay
            audio_with_delay = audio + AudioSegment.silent(duration=delay_ms)
            play(audio_with_delay)
            return True
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    # Test code
    audio_mgr = AudioManager()
    
    # 测试录音
    test_path = "test_recording.wav"
    print("Testing recording...")
    if audio_mgr.record(3, test_path):
        print("Recording successful!")
        print("Playing back...")
        audio_mgr.play(test_path)
    else:
        print("Recording failed!")
