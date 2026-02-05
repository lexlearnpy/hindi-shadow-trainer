"""
印地语翻译模块
Hindi Translator Module

功能：
1. 印地语 → 简化拉丁转写
2. 印地语 → 英语（deep-translator）
3. 印地语 → 中文（deep-translator）
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# 印地语到拉丁字母的简化映射表
# Hindi to Latin simplified transliteration mapping
HINDI_TO_LATIN = {
    # 元音 Vowels
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ii',
    'उ': 'u', 'ऊ': 'uu', 'ए': 'e', 'ऐ': 'ai',
    'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
    
    # 辅音 Consonants
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'व': 'w',
    'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy',
    'ड़': 'r', 'ढ़': 'rh',
    
    # 变音符号 Diacritics
    'ं': 'n', 'ः': 'h',
    'ा': 'aa', 'ि': 'i', 'ी': 'ii',
    'ु': 'u', 'ू': 'uu',
    'े': 'e', 'ै': 'ai',
    'ो': 'o', 'ौ': 'au',
    '्': '',  # 静音符号
    
    # 数字 Numbers
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
}


def transliterate_hindi(hindi_text: str) -> str:
    """
    印地语天城文 → 简化拉丁转写
    Hindi Devanagari → Simplified Latin transliteration
    
    Examples:
        नमस्ते → namaste
        भाई → bhai
        मेरा नाम → mera naam
    """
    result = []
    i = 0
    text = hindi_text.strip()
    
    while i < len(text):
        char = text[i]
        
        # 跳过空格
        if char == ' ':
            result.append(' ')
            i += 1
            continue
        
        # 尝试匹配双字符（如 क्ष, त्र, ज्ञ）
        if i + 1 < len(text):
            two_chars = text[i:i+2]
            if two_chars in HINDI_TO_LATIN:
                result.append(HINDI_TO_LATIN[two_chars])
                i += 2
                continue
        
        # 单字符匹配
        if char in HINDI_TO_LATIN:
            result.append(HINDI_TO_LATIN[char])
        else:
            # 保留未知字符（标点、数字等）
            result.append(char)
        
        i += 1
    
    # 清理连续空格
    transliterated = ''.join(result)
    transliterated = re.sub(r'\s+', ' ', transliterated).strip()
    
    return transliterated


try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("Warning: deep_translator not installed. Translation features disabled.")


class HindiTranslator:
    """印地语翻译器"""
    
    def __init__(self):
        self.en_translator = None
        self.zh_translator = None
        
        if TRANSLATOR_AVAILABLE:
            try:
                self.en_translator = GoogleTranslator(source='hi', target='en')
                self.zh_translator = GoogleTranslator(source='hi', target='zh-CN')
            except Exception as e:
                print(f"Warning: Failed to initialize translators: {e}")
    
    def translate_full(self, hindi_text: str) -> dict:
        """
        完整翻译处理
        Full translation processing
        
        Returns四行格式:
        {
            'hindi': 'नमस्ते',
            'transliteration': 'namaste',
            'english': 'Hello',
            'chinese': '你好'
        }
        """
        result = {
            'hindi': hindi_text,
            'transliteration': transliterate_hindi(hindi_text),
            'english': '',
            'chinese': ''
        }
        
        # 机器翻译
        if self.en_translator and self.zh_translator:
            try:
                result['english'] = self.en_translator.translate(hindi_text)
            except Exception as e:
                print(f"English translation failed: {e}")
                result['english'] = '[Translation failed]'
            
            try:
                result['chinese'] = self.zh_translator.translate(hindi_text)
            except Exception as e:
                print(f"Chinese translation failed: {e}")
                result['chinese'] = '[翻译失败]'
        else:
            result['english'] = '[Translator not available]'
            result['chinese'] = '[翻译器不可用]'
        
        return result
    
    def format_four_lines(self, data: dict) -> str:
        """
        格式化为四行显示
        Format as four-line display
        """
        return f"""
{data['hindi']}
{data['transliteration']}
{data['english']}
{data['chinese']}
        """.strip()


if __name__ == "__main__":
    # 测试
    test_texts = [
        "नमस्ते",
        "मेरा नाम राहुल है",
        "आप कैसे हैं",
        "भाई",
    ]
    
    translator = HindiTranslator()
    
    for text in test_texts:
        print(f"\n测试: {text}")
        result = translator.translate_full(text)
        print(translator.format_four_lines(result))
