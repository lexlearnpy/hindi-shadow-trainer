"""
配置模块 - 支持国际化(i18n)
Configuration module with internationalization support
"""
import os
from pathlib import Path
from typing import Dict, Any

# 项目根目录 / Project root directory
BASE_DIR = Path(__file__).parent.resolve()

# 国际化配置 / Internationalization configuration
I18N_STRINGS = {
    'zh': {
        'app_title': '🇮🇳 印地语影子跟读训练器',
        'app_subtitle': 'Hindi Shadow Trainer with SRS',
        'menu_shadowing': '🎙️  开始跟读训练 (Shadowing)',
        'menu_review': '📚 生词本复习 (Daily Review)',
        'menu_add_vocab': '➕ 添加新单词 (Add Vocabulary)',
        'menu_statistics': '📊 查看学习统计 (Statistics)',
        'menu_settings': '⚙️  设置 (Settings)',
        'menu_exit': '👋 退出 (Exit)',
        'recording_ready': '🎙️ 准备录音...',
        'recording_countdown': '倒计时: {}',
        'recording_start': '🔴 开始录音!',
        'recording_stop': '⏹️  录音结束',
        'transcribing': '🔍 正在识别语音...',
        'score_result': '发音得分: {}',
        'standard_text': '标准文本',
        'your_pronunciation': '你的发音',
        'add_to_vocab': '是否加入生词本?',
        'quality_forgot': '完全忘了 (Forgot)',
        'quality_hard': '模糊 (Hard)',
        'quality_good': '记得 (Good)',
        'quality_easy': '秒杀 (Easy)',
        'next_review': '下次复习: {}',
        'exit_message': '再见！Namaste! 🙏',
        'error_microphone': '无法访问麦克风，请检查权限',
        'error_whisper': 'Whisper模型加载失败',
        'enter_hindi_text': '请输入印地语文本',
        'enter_meaning': '请输入中文含义',
        'save_success': '保存成功!',
        'no_words_due': '今天没有需要复习的单词',
        'words_due_count': '今天有 {} 个单词需要复习',
    },
    'en': {
        'app_title': '🇮🇳 Hindi Shadow Trainer',
        'app_subtitle': 'With Spaced Repetition System',
        'menu_shadowing': '🎙️  Start Shadowing Practice',
        'menu_review': '📚 Daily Vocabulary Review',
        'menu_add_vocab': '➕ Add New Word',
        'menu_statistics': '📊 Learning Statistics',
        'menu_settings': '⚙️  Settings',
        'menu_exit': '👋 Exit',
        'recording_ready': '🎙️ Preparing to record...',
        'recording_countdown': 'Countdown: {}',
        'recording_start': '🔴 Recording started!',
        'recording_stop': '⏹️  Recording stopped',
        'transcribing': '🔍 Transcribing speech...',
        'score_result': 'Pronunciation score: {}',
        'standard_text': 'Standard Text',
        'your_pronunciation': 'Your Pronunciation',
        'add_to_vocab': 'Add to vocabulary?',
        'quality_forgot': 'Forgot (Again)',
        'quality_hard': 'Hard',
        'quality_good': 'Good',
        'quality_easy': 'Easy',
        'next_review': 'Next review: {}',
        'exit_message': 'Goodbye! Namaste! 🙏',
        'error_microphone': 'Cannot access microphone. Please check permissions',
        'error_whisper': 'Failed to load Whisper model',
        'enter_hindi_text': 'Enter Hindi text',
        'enter_meaning': 'Enter Chinese meaning',
        'save_success': 'Saved successfully!',
        'no_words_due': 'No words due for review today',
        'words_due_count': '{} words due for review today',
    }
}


class Config:
    """全局配置类 / Global configuration class"""
    
    # 语言设置 (从环境变量读取，默认中文)
    # Language setting (read from environment, default Chinese)
    LANGUAGE = os.getenv('HINDI_TRAINER_LANG', 'zh')
    
    @classmethod
    def get_text(cls, key: str, *args) -> str:
        """获取国际化文本 / Get internationalized text"""
        text = I18N_STRINGS.get(cls.LANGUAGE, I18N_STRINGS['zh']).get(key, key)
        if args:
            return text.format(*args)
        return text
    
    @classmethod
    def set_language(cls, lang: str):
        """切换语言 / Switch language"""
        if lang in I18N_STRINGS:
            cls.LANGUAGE = lang
    
    # Whisper模型配置 / Whisper model configuration
    WHISPER_MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'medium')
    WHISPER_MODEL_DIR = Path(os.getenv('HF_HOME', BASE_DIR / 'models'))
    
    # TTS配置 / TTS configuration
    TTS_VOICE = "hi-IN-MadhurNeural"
    TTS_TEMP_DIR = BASE_DIR / 'temp'
    
    # 音频配置 / Audio configuration
    # 参考项目使用的标准参数 / Standard parameters from reference project
    AUDIO_SAMPLE_RATE = 16000      # Whisper要求的采样率
    AUDIO_CHANNELS = 1             # 单声道
    AUDIO_DURATION_DEFAULT = 30    # 默认录音时长（秒）
    AUDIO_DURATION_PER_CHAR = 0.3  # 每个字符预留的时间（秒）
    
    # 数据库配置 / Database configuration
    DB_PATH = BASE_DIR / 'data' / 'vocab.db'
    
    # 评分阈值 / Score thresholds
    SCORE_EXCELLENT = 90
    SCORE_GOOD = 70
    SCORE_POOR = 50
    
    # SM-2算法配置 / SM-2 algorithm configuration
    SRS_INTERVALS = [1, 3, 7, 14, 30, 90]  # 第0-5阶段的间隔（天）
    SRS_EASINESS_FACTOR = 1.3             # 高级阶段的增长因子


# 创建必要的目录 / Create necessary directories
Config.TTS_TEMP_DIR.mkdir(parents=True, exist_ok=True)
Config.WHISPER_MODEL_DIR.mkdir(parents=True, exist_ok=True)
Path(Config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
