"""
数据库模块 - SQLite生词本管理
Database Module - SQLite Vocabulary Management
"""
import sqlite3
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class VocabDatabase:
    """生词本数据库类"""
    
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建生词表
            # Create vocabulary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vocab (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    context_sentence TEXT,
                    review_stage INTEGER DEFAULT 0,
                    next_review_date DATE,
                    last_quality INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_word(self, word: str, meaning: str, 
                 context_sentence: str = None) -> int:
        """
        添加新单词到生词本
        Add new word to vocabulary
        
        Args:
            word: 印地语单词
            meaning: 中文含义
            context_sentence: 上下文例句
            
        Returns:
            新单词的ID / New word ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 设置明天为首次复习时间
            # Set tomorrow as first review date
            tomorrow = date.today() + date.resolution
            
            cursor.execute('''
                INSERT INTO vocab (word, meaning, context_sentence, 
                                 next_review_date)
                VALUES (?, ?, ?, ?)
            ''', (word, meaning, context_sentence, tomorrow))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_due_words(self) -> List[Dict]:
        """
        获取今天需要复习的单词
        Get words due for review today
        
        Returns:
            单词列表 / List of words
        """
        today = date.today()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM vocab 
                WHERE next_review_date <= ?
                ORDER BY next_review_date ASC
            ''', (today,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_review(self, word_id: int, quality: int,
                      next_date: date, new_stage: int):
        """
        更新复习记录
        Update review record
        
        Args:
            word_id: 单词ID
            quality: 复习质量 (0-5)
            next_date: 下次复习日期
            new_stage: 新的复习阶段
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE vocab 
                SET review_stage = ?,
                    next_review_date = ?,
                    last_quality = ?
                WHERE id = ?
            ''', (new_stage, next_date, quality, word_id))
            
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """
        获取学习统计
        Get learning statistics
        
        Returns:
            统计信息字典 / Statistics dictionary
        """
        today = date.today()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 总单词数
            cursor.execute('SELECT COUNT(*) FROM vocab')
            total = cursor.fetchone()[0]
            
            # 今天需要复习的
            cursor.execute('''
                SELECT COUNT(*) FROM vocab 
                WHERE next_review_date <= ?
            ''', (today,))
            due_today = cursor.fetchone()[0]
            
            # 各阶段分布
            cursor.execute('''
                SELECT review_stage, COUNT(*) 
                FROM vocab 
                GROUP BY review_stage
            ''')
            stages = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_words': total,
                'due_today': due_today,
                'stage_distribution': stages
            }
    
    def delete_word(self, word_id: int):
        """删除单词"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM vocab WHERE id = ?', (word_id,))
            conn.commit()


if __name__ == "__main__":
    # 测试
    db = VocabDatabase()
    
    # 添加测试单词
    word_id = db.add_word("नमस्ते", "你好", "नमस्ते, आप कैसे हैं?")
    print(f"Added word with ID: {word_id}")
    
    # 获取统计
    stats = db.get_statistics()
    print(f"Statistics: {stats}")
