#!/usr/bin/env python3
"""
YouTube学习命令行工具
YouTube Learning CLI Tool

Usage:
    python youtube_cli.py --url "https://youtu.be/xxx" --start 30 --end 45
    python youtube_cli.py --url "https://youtu.be/xxx" --full
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.youtube_handler import YouTubeHandler
from modules.translator import HindiTranslator
from modules.whisper_engine import WhisperEngine
from modules.database import VocabDatabase


def format_four_lines(data: dict) -> str:
    """格式化为四行显示"""
    return f"""
╔════════════════════════════════════════════════════════╗
║  🇮🇳 {data['hindi']:<48} ║
╠════════════════════════════════════════════════════════╣
║  🔤 {data['transliteration']:<48} ║
╠════════════════════════════════════════════════════════╣
║  🇬🇧 {data['english']:<48} ║
╠════════════════════════════════════════════════════════╣
║  🇨🇳 {data['chinese']:<48} ║
╚════════════════════════════════════════════════════════╝
    """.strip()


def process_segment(url: str, start: float, end: float, db: VocabDatabase = None):
    """
    处理单个时间段
    Process a single time segment
    """
    print("\n" + "="*60)
    print("🎬 YouTube Learning Mode")
    print("="*60)
    
    # 初始化组件
    youtube = YouTubeHandler()
    translator = HindiTranslator()
    
    # 1. 下载音频（如果还没有）
    print("\n📥 Step 1: Downloading audio...")
    try:
        video_info = youtube.download_audio(url)
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return
    
    # 2. 切分音频
    print(f"\n✂️  Step 2: Extracting segment ({start}s - {end}s)...")
    try:
        segment_path = youtube.extract_segment(
            video_info['audio_path'], start, end
        )
    except Exception as e:
        print(f"❌ Segment extraction failed: {e}")
        return
    
    # 3. Whisper转录
    print("\n🎯 Step 3: Transcribing with Whisper...")
    try:
        whisper = WhisperEngine()
        hindi_text = whisper.transcribe(segment_path)
        print(f"📝 Recognized: {hindi_text}")
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return
    
    # 4. 翻译
    print("\n🌍 Step 4: Translating...")
    try:
        result = translator.translate_full(hindi_text)
        print("\n" + format_four_lines(result))
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return
    
    # 5. 保存到数据库（如果提供了db）
    if db:
        print("\n💾 Step 5: Saving to database...")
        try:
            lesson_id = db.add_youtube_lesson(
                video_url=url,
                video_title=video_info['title'],
                segment_path=segment_path,
                start_time=start,
                end_time=end,
                hindi_text=result['hindi'],
                transliteration=result['transliteration'],
                english_text=result['english'],
                chinese_text=result['chinese']
            )
            print(f"✅ Saved! Lesson ID: {lesson_id}")
        except Exception as e:
            print(f"❌ Database save failed: {e}")
    
    print("\n" + "="*60)
    print("✨ Done!")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='YouTube Hindi Learning Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process specific time segment
  python youtube_cli.py --url "https://youtu.be/rRyb3Cm0eT0" --start 30 --end 45
  
  # Process with database save
  python youtube_cli.py --url "https://youtu.be/rRyb3Cm0eT0" --start 60 --end 75 --save
  
  # Interactive mode (full video segmentation)
  python youtube_cli.py --url "https://youtu.be/rRyb3Cm0eT0" --full
        """
    )
    
    parser.add_argument('--url', '-u', required=True,
                       help='YouTube video URL')
    parser.add_argument('--start', '-s', type=float,
                       help='Start time in seconds')
    parser.add_argument('--end', '-e', type=float,
                       help='End time in seconds')
    parser.add_argument('--save', action='store_true',
                       help='Save to database')
    parser.add_argument('--full', '-f', action='store_true',
                       help='Process full video with auto-segmentation')
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.full and (args.start is None or args.end is None):
        parser.error("--start and --end are required unless using --full")
    
    # 初始化数据库（如果需要保存）
    db = VocabDatabase() if args.save else None
    
    if args.full:
        print("\n🚧 Full video mode not yet implemented.")
        print("Use --start and --end for specific segments.\n")
    else:
        process_segment(args.url, args.start, args.end, db)


if __name__ == "__main__":
    main()
