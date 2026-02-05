"""
音频管理模块
Audio management module - recording and playback
"""
import sys
import wave
from pathlib import Path
from typing import Optional

import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from pydub.playback import play

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class AudioManager:
    """音频管理类 - 负责录音和播放"""
    
    def __init__(self):
        self.sample_rate = Config.AUDIO_SAMPLE_RATE
        self.channels = Config.AUDIO_CHANNELS
        self.dtype = 'int16'
        
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
    
    def record(self, duration: int, output_path: str) -> bool:
        """
        录制音频
        Record audio from microphone
        
        Args:
            duration: 录音时长（秒）
            output_path: 输出文件路径
            
        Returns:
            是否成功 / Success status
        """
        try:
            print(f"🎙️  {Config.get_text('recording_ready')}")
            
            # 录制音频数据
            # Record audio data
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype
            )
            
            # 等待录音完成
            # Wait for recording to complete
            sd.wait()
            
            # 保存为WAV文件
            # Save as WAV file
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # int16 = 2 bytes
                wf.setframerate(self.sample_rate)
                wf.writeframes(recording.tobytes())
            
            return True
            
        except Exception as e:
            print(f"❌ {Config.get_text('error_microphone')}: {e}")
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
