"""
发音评分模块
Pronunciation Scoring Module

使用Levenshtein距离计算文本相似度
Calculate text similarity using Levenshtein distance
"""
import sys
import string
from pathlib import Path

from Levenshtein import ratio

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class PronunciationScorer:
    """发音评分器"""
    
    def calculate_score(self, standard: str, transcribed: str) -> float:
        """
        计算发音相似度得分 (0-100)
        Calculate pronunciation similarity score
        
        Args:
            standard: 标准文本 / Standard text
            transcribed: 用户转写的文本 / User transcribed text
            
        Returns:
            得分 (0-100) / Score from 0-100
        """
        # 预处理文本
        # Preprocess text
        s1 = self._normalize(standard)
        s2 = self._normalize(transcribed)
        
        # 如果都为空，认为是完全匹配
        if not s1 and not s2:
            return 100.0
        
        # 如果标准为空但转写不为空，或反之，得分为0
        if not s1 or not s2:
            return 0.0
        
        # 计算Levenshtein相似度
        # Calculate Levenshtein similarity
        similarity = ratio(s1, s2)
        return round(similarity * 100, 1)
    
    def get_word_accuracy(self, standard: str, transcribed: str) -> tuple:
        """
        获取词级别的匹配情况
        Get word-level accuracy
        
        Returns:
            (正确词数, 总词数, 正确率) / (correct_count, total_count, accuracy)
        """
        words1 = standard.split()
        words2 = transcribed.split()
        
        # 标准化后比较
        w1 = [self._normalize_word(w) for w in words1]
        w2 = [self._normalize_word(w) for w in words2]
        
        # 计算匹配的单词数
        # Count matching words
        correct = sum(1 for w in w2 if w in w1)
        total = len(w1)
        
        accuracy = (correct / total * 100) if total > 0 else 0
        return correct, total, round(accuracy, 1)
    
    def _normalize(self, text: str) -> str:
        """
        文本标准化（参考项目逻辑）
        Text normalization (from reference project)
        
        步骤:
        1. 转小写
        2. 移除标点符号
        3. 统一空格
        """
        # 转小写
        text = text.lower().strip()
        
        # 移除标点符号
        # Remove punctuation
        text = ''.join(ch for ch in text if ch not in string.punctuation)
        
        # 统一空格
        # Normalize whitespace
        return ' '.join(text.split())
    
    def _normalize_word(self, word: str) -> str:
        """标准化单个单词"""
        return word.lower().strip(string.punctuation)
    
    def get_score_level(self, score: float) -> str:
        """
        根据分数返回评级
        Return rating based on score
        """
        if score >= Config.SCORE_EXCELLENT:
            return "🌟 Excellent"
        elif score >= Config.SCORE_GOOD:
            return "👍 Good"
        elif score >= Config.SCORE_POOR:
            return "😐 Needs Practice"
        else:
            return "💪 Keep Trying"


if __name__ == "__main__":
    # 测试
    scorer = PronunciationScorer()
    
    standard = "नमस्ते, आप कैसे हैं?"
    transcribed = "नमस्ते आप कैसे हैं"
    
    score = scorer.calculate_score(standard, transcribed)
    print(f"Score: {score}")
    print(f"Level: {scorer.get_score_level(score)}")
    
    correct, total, accuracy = scorer.get_word_accuracy(standard, transcribed)
    print(f"Word accuracy: {correct}/{total} ({accuracy}%)")
