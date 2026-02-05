"""
YouTube处理模块
YouTube Handler Module

功能：
1. 下载YouTube音频
2. 提取视频信息
3. 音频切片
"""
import sys
import uuid
import subprocess
from pathlib import Path
from pydub import AudioSegment

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config

# 尝试导入yt_dlp
try:
    import yt_dlp
except ImportError:
    print("Error: yt_dlp not installed. Run: pip install yt-dlp")
    raise


def check_ffmpeg():
    """检查是否安装了FFmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


class YouTubeHandler:
    """YouTube处理器"""
    
    def __init__(self):
        self.temp_dir = Path(Config.TTS_TEMP_DIR) / "youtube"
        self.segments_dir = Path(Config.TTS_TEMP_DIR) / "segments"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.segments_dir.mkdir(parents=True, exist_ok=True)
        self.has_ffmpeg = check_ffmpeg()
    
    def download_audio(self, url: str) -> dict:
        """
        下载YouTube音频
        Download YouTube audio
        
        Args:
            url: YouTube视频链接
            
        Returns:
            dict: {
                'video_id': 'xxx',
                'title': '视频标题',
                'duration': 754,
                'audio_path': 'path/to/audio.mp3'
            }
        """
        print(f"📥 Downloading audio from: {url}")
        
        if self.has_ffmpeg:
            # 使用FFmpeg转码为MP3
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True
            }
            extension = 'mp3'
        else:
            # 没有FFmpeg，直接下载M4A格式
            print("⚠️  FFmpeg not found, downloading M4A format instead")
            print("   To install FFmpeg, run: install_ffmpeg.bat")
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True
            }
            extension = 'm4a'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                video_id = info['id']
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                audio_path = self.temp_dir / f"{video_id}.{extension}"
                
                print(f"✅ Downloaded: {title}")
                print(f"⏱️  Duration: {duration}s")
                print(f"🎵 Audio: {audio_path}")
                
                return {
                    'video_id': video_id,
                    'title': title,
                    'duration': duration,
                    'audio_path': str(audio_path)
                }
        except Exception as e:
            print(f"❌ Download failed: {e}")
            if "ffprobe and ffmpeg not found" in str(e):
                print("\n💡 To fix this:")
                print("   1. Run: install_ffmpeg.bat")
                print("   2. Or download FFmpeg manually from: https://www.gyan.dev/ffmpeg/builds/")
                print("   3. Add FFmpeg bin folder to your PATH")
            raise
    
    def extract_segment(self, audio_path: str, start: float, end: float) -> str:
        """
        切分音频片段
        Extract audio segment
        
        Args:
            audio_path: 完整音频路径
            start: 开始时间（秒）
            end: 结束时间（秒）
            
        Returns:
            str: 片段文件路径
        """
        # 根据文件格式选择加载方法
        if audio_path.endswith('.m4a'):
            audio = AudioSegment.from_file(audio_path, format="m4a")
        else:
            audio = AudioSegment.from_mp3(audio_path)
        
        segment = audio[int(start*1000):int(end*1000)]
        
        segment_id = str(uuid.uuid4())[:8]
        segment_path = self.segments_dir / f"segment_{segment_id}.mp3"
        
        segment.export(str(segment_path), format="mp3")
        print(f"✂️  Segment saved: {segment_path}")
        
        return str(segment_path)


if __name__ == "__main__":
    # 测试
    handler = YouTubeHandler()
    # result = handler.download_audio("https://youtu.be/rRyb3Cm0eT0")
    # print(result)
