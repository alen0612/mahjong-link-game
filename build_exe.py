import PyInstaller.__main__
import os

# 獲取當前腳本所在目錄
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'src/main.py',
    '--name=MahjongLinkGame',
    '--onefile',
    '--windowed',
    '--icon=NONE',  # 如果有圖標檔案，可以在這裡指定
    f'--add-data={os.path.join(current_dir, "assets")}:assets',
    '--noconsole',
    '--clean',
    '--noconfirm',
])