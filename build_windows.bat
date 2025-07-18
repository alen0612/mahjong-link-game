@echo off
echo Building Mahjong Link Game for Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install pygame==2.5.2
pip install pyinstaller

REM Build the executable
echo Building executable...
pyinstaller ^
    --name "MahjongLinkGame" ^
    --onefile ^
    --windowed ^
    --add-data "assets;assets" ^
    --noconsole ^
    --clean ^
    --noconfirm ^
    src\main.py

echo.
echo Build complete! 
echo The executable file is located in: dist\MahjongLinkGame.exe
pause