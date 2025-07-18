# Building Mahjong Link Game for Windows

## Quick Build (Recommended)

Simply double-click `build_windows_simple.bat` and it will:
1. Create a virtual environment
2. Install required packages
3. Build the executable
4. The game will be in `dist/mahjong-link-game.exe`

## Manual Build

If you prefer to build manually, run these commands:

```cmd
python -m venv venv
venv\Scripts\activate
pip install pygame==2.5.2 pyinstaller
pyinstaller --onefile --noconsole --add-data "assets;assets" --name mahjong-link-game src/main.py
```

## Requirements

- Python 3.7 or higher
- Windows 7 or higher

## Troubleshooting

If the game doesn't run properly:
1. Make sure all files in the `assets` folder are included
2. Try running from command line to see error messages
3. Ensure pygame is properly installed

## File Structure

After building, you should have:
```
dist/
  mahjong-link-game.exe  # The game executable
```

The exe file includes all necessary assets and can be distributed as a single file.