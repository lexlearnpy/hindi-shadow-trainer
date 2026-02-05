"""
SM-2间隔重复算法模块
SM-2 Spaced Repetition Algorithm Module

SuperMemo-2算法简化版实现
Simplified implementation of SuperMemo-2 algorithm
"""
import sys
from datetime import datetime, timedelta, date
from typing import Dict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class SM2Algorithm:
    """
    SuperMemo-2 间隔重复算法
    
    算法原理:
    1. 根据用户的复习质量(quality)决定下一次复习时间
    2. 复习质量0-2: 表示忘记，重置到第一阶段，隔天复习
    3. 复习质量3-5: 表示记得，进入下一阶段，间隔逐渐拉长
    
    复习质量映射 / Quality mapping:
    - 完全忘了 / Forgot: 0-2
    - 模糊 / Hard: 3
    - 记得 / Good: 4
    - 秒杀 / Easy: 5
    """
    
    def __init__(self):
        # 初始间隔天数（按阶段）
        # Initial intervals by stage
        self.intervals = Config.SRS_INTERVALS
        self.easiness_factor = Config.SRS_EASINESS_FACTOR
    
    def calculate_next_review(self, 
                            current_stage: int,
                            quality: int,
                            last_interval: int = None) -> Dict:
        """
        计算下次复习时间和新阶段
        Calculate next review date and new stage
        
        详细逻辑说明:
        1. 如果quality < 3（忘记）:
           - 回到第0阶段
           - 间隔1天
           
        2. 如果quality >= 3（记得）:
           - 阶段+1（最高5）
           - 使用预设间隔或EF因子计算
        
        Args:
            current_stage: 当前复习阶段 (0-5)
            quality: 复习质量 (0-5)
            last_interval: 上次间隔天数（用于高级阶段）
            
        Returns:
            dict: {
                'next_date': 下次复习日期,
                'new_stage': 新阶段,
                'new_interval': 新间隔天数
            }
        """
        # 处理忘记的情况
        # Handle forgotten case
        if quality < 3:
            # 忘记了，重置到第一阶段，隔天复习
            # Forgotten, reset to stage 0, review tomorrow
            return {
                'next_date': date.today() + timedelta(days=1),
                'new_stage': 0,
                'new_interval': 1
            }
        
        # 记住的情况，进入下一阶段
        # Remembered, advance to next stage
        new_stage = min(current_stage + 1, 5)
        
        # 计算间隔天数
        # Calculate interval
        if new_stage < len(self.intervals):
            # 使用预设间隔
            # Use predefined intervals
            interval = self.intervals[new_stage]
        else:
            # 超过预设阶段，使用EF因子增长
            # Beyond predefined stages, use EF factor
            if last_interval:
                interval = int(last_interval * self.easiness_factor)
            else:
                interval = self.intervals[-1]
        
        return {
            'next_date': date.today() + timedelta(days=interval),
            'new_stage': new_stage,
            'new_interval': interval
        }
    
    def quality_to_text(self, quality: int, lang: str = None) -> str:
        """
        将数字质量转换为文本描述
        Convert quality number to text description
        """
        if lang is None:
            lang = Config.LANGUAGE
            
        quality_map = {
            0: 'quality_forgot',
            1: 'quality_forgot',
            2: 'quality_forgot',
            3: 'quality_hard',
            4: 'quality_good',
            5: 'quality_easy'
        }
        
        key = quality_map.get(quality, 'quality_hard')
        return Config.get_text(key)


if __name__ == "__main__":
    # 测试算法
    srs = SM2Algorithm()
    
    # 测试场景1: 新单词，记得很好
    result = srs.calculate_next_review(0, 5)
    print(f"Stage 0, Quality 5: {result}")
    
    # 测试场景2: 忘记了
    result = srs.calculate_next_review(3, 1)
    print(f"Stage 3, Quality 1 (forgot): {result}")
    
    # 测试场景3: 模糊记得
    result = srs.calculate_next_review(2, 3)
    print(f"Stage 2, Quality 3: {result}")
