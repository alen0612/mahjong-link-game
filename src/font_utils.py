import os
import sys
import pygame

def get_chinese_font(size):
    """Get a font that supports Chinese characters"""
    # Try different font paths for different systems
    font_paths = [
        # Windows fonts
        "C:/Windows/Fonts/mingliu.ttc",  # 細明體
        "C:/Windows/Fonts/msjh.ttc",     # 微軟正黑體
        "C:/Windows/Fonts/msyh.ttc",     # 微軟雅黑
        "C:/Windows/Fonts/simsun.ttc",   # 宋體
        # macOS fonts
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        # Linux fonts
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]
    
    # Try to load each font
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    # If no Chinese font found, return default font
    # This will show boxes for Chinese characters
    return pygame.font.Font(None, size)