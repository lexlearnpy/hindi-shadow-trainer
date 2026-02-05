"""
字体管理模块
Font Manager Module

自动加载Noto Sans Devanagari字体
"""
import os
import sys
import ctypes
from pathlib import Path
from tkinter import font


class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.font_dir = self.base_dir / "font"
        self.hindi_font = None
        self.hindi_font_bold = None
        
    def load_fonts(self):
        """加载印地语字体"""
        try:
            # Windows字体加载
            if sys.platform == 'win32':
                self._load_windows_font()
            
            # 创建字体对象
            self.hindi_font = font.Font(family="Noto Sans Devanagari", size=20)
            self.hindi_font_bold = font.Font(family="Noto Sans Devanagari", size=24, weight="bold")
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to load custom font: {e}")
            # 使用备用字体
            self.hindi_font = font.Font(family="Arial", size=20)
            self.hindi_font_bold = font.Font(family="Arial", size=24, weight="bold")
            return False
    
    def _load_windows_font(self):
        """Windows系统加载字体"""
        try:
            # 加载字体文件
            regular_ttf = self.font_dir / "static" / "NotoSansDevanagari-Regular.ttf"
            bold_ttf = self.font_dir / "static" / "NotoSansDevanagari-Bold.ttf"
            
            if regular_ttf.exists():
                # 使用Windows API加载字体
                gdi32 = ctypes.WinDLL('gdi32')
                AddFontResourceEx = gdi32.AddFontResourceExW
                AddFontResourceEx.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
                AddFontResourceEx.restype = ctypes.c_int
                
                # FR_PRIVATE = 0x10 (只给当前应用使用)
                AddFontResourceEx(str(regular_ttf), 0x10, None)
                
            if bold_ttf.exists():
                gdi32 = ctypes.WinDLL('gdi32')
                AddFontResourceEx = gdi32.AddFontResourceExW
                AddFontResourceEx.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
                AddFontResourceEx.restype = ctypes.c_int
                AddFontResourceEx(str(bold_ttf), 0x10, None)
                
        except Exception as e:
            print(f"Warning: Windows font loading failed: {e}")
    
    def get_hindi_font(self, size=20, bold=False):
        """获取印地语字体"""
        if bold:
            return font.Font(family="Noto Sans Devanagari", size=size, weight="bold")
        return font.Font(family="Noto Sans Devanagari", size=size)


# 全局字体管理器实例
font_manager = FontManager()
