@echo off
echo Building Mahjong Link Game for Windows...
echo.

REM 建立虛擬環境
echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

REM 啟動虛擬環境
echo Step 2: Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM 安裝依賴
echo Step 3: Installing dependencies...
pip install pygame==2.5.2 pyinstaller
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM 建立執行檔
echo Step 4: Building executable...
pyinstaller --onefile --noconsole --add-data "assets;assets" --name mahjong-link-game src\main.py
if errorlevel 1 (
    echo Error: Failed to build executable
    pause
    exit /b 1
)

echo.
echo Build complete!
echo The executable is located at: dist\mahjong-link-game.exe
echo.
echo You can now run the game by double-clicking: dist\mahjong-link-game.exe
pause