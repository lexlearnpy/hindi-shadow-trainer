"""
Whisper语音识别模块
Whisper Speech Recognition Module

参考项目逻辑 Reference project logic:
- 必须使用 language='hi' 指定印地语
- fp16=False 确保CPU兼容性
"""
import os
import sys
from pathlib import Path

import whisper

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class WhisperEngine:
    """Whisper语音识别引擎"""
    
    def __init__(self):
        self.model = None
        self.model_size = Config.WHISPER_MODEL_SIZE
        self.model_dir = Config.WHISPER_MODEL_DIR
        self._load_model()
    
    def _load_model(self):
        """
        加载Whisper模型
        Load Whisper model with custom download directory
        """
        try:
            print(f"📥 正在加载Whisper模型: {self.model_size}...")
            print(f"📁 模型存储位置: {self.model_dir}")
            
            # 设置模型下载目录
            # Set model download directory
            os.environ["WHISPER_CACHE_DIR"] = str(self.model_dir)
            
            # 加载模型
            # Load model
            self.model = whisper.load_model(
                self.model_size,
                download_root=str(self.model_dir)
            )
            
            print(f"✅ Whisper模型加载完成!")
            
        except Exception as e:
            print(f"❌ {Config.get_text('error_whisper')}: {e}")
            raise
    
    def transcribe(self, audio_path: str) -> str:
        """
        将音频转写为印地语文本
        Transcribe audio to Hindi text
        
        关键参数说明 Key parameters (from reference project):
        - language='hi': 强制使用印地语识别，提高准确率
        - fp16=False: 禁用半精度浮点，确保CPU兼容性
        
        Args:
            audio_path: 音频文件路径 / Path to audio file
            
        Returns:
            转写的印地语文本 / Transcribed Hindi text
        """
        try:
            print(f"🔍 {Config.get_text('transcribing')}")
            
            # 使用参考项目的关键参数
            # Use key parameters from reference project
            result = self.model.transcribe(
                audio_path,
                language='hi',      # 必须指定印地语
                fp16=False          # CPU模式更安全
            )
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""


if __name__ == "__main__":
    # 测试
    engine = WhisperEngine()
    # 这里需要有一个测试音频文件
    # test_audio = "test_hindi.wav"
    # if Path(test_audio).exists():
    #     result = engine.transcribe(test_audio)
    #     print(f"转写结果: {result}")
