"""
TTS模块 - 使用Edge TTS生成印地语音频
TTS Module - Using Edge TTS to generate Hindi audio
"""
import asyncio
import sys
from pathlib import Path

import edge_tts

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class HindiTTS:
    """印地语TTS类"""
    
    def __init__(self):
        self.voice = Config.TTS_VOICE
        self.temp_dir = Config.TTS_TEMP_DIR
        
    async def synthesize(self, text: str, output_path: str = None) -> Path:
        """
        生成印地语语音
        Generate Hindi speech
        
        Args:
            text: 要合成的文本 / Text to synthesize
            output_path: 输出路径（可选）/ Output path (optional)
            
        Returns:
            生成的音频文件路径 / Path to generated audio file
        """
        if not output_path:
            # 生成临时文件名
            output_path = self.temp_dir / f"tts_{hash(text)}.mp3"
        else:
            output_path = Path(output_path)
        
        # 使用edge-tts生成音频
        # Use edge-tts to generate audio
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output_path))
        
        return output_path
    
    def synthesize_sync(self, text: str, output_path: str = None) -> Path:
        """
        同步版本的合成（方便调用）
        Synchronous version for easier calling
        """
        return asyncio.run(self.synthesize(text, output_path))


if __name__ == "__main__":
    # 测试
    tts = HindiTTS()
    text = "नमस्ते, आप कैसे हैं?"  # 你好，你好吗？
    print(f"Generating TTS for: {text}")
    audio_path = tts.synthesize_sync(text)
    print(f"Saved to: {audio_path}")
