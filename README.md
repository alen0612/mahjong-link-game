# 麻將連連看 (Mahjong Link Game)

一個使用 Python 和 Pygame 開發的經典麻將連連看遊戲。

## 🎮 遊戲特色

- **經典玩法**：點擊相同的麻將牌進行配對消除
- **動態背景**：滾動的麻將牌背景效果
- **音效體驗**：背景音樂營造遊戲氛圍
- **視覺效果**：粒子特效和半透明效果
- **響應式設計**：支援視窗大小調整

## 🚀 快速開始

### 安裝需求

```bash
pip install -r requirements.txt
```

### 執行遊戲

```bash
python src/main.py
```

## 🎯 遊戲規則

1. 點擊兩張相同的麻將牌進行配對
2. 配對成功的牌會自動消除
3. 消除所有牌即可完成遊戲
4. 遊戲確保每次都有解，不會出現無解情況

## 🎨 素材來源

- **麻將牌圖示**：[riichi-mahjong-tiles](https://github.com/FluffyStuff/riichi-mahjong-tiles) - 由 FluffyStuff 提供，採用 Public Domain 授權
- **背景音樂**：[Artlist.io](https://artlist.io/) - 提供遊戲背景音樂

## 📁 專案結構

```
mahjong-link-game/
├── assets/
│   ├── audio/          # 音效檔案
│   └── tiles/          # 麻將牌圖示
├── src/
│   ├── main.py         # 遊戲主程式
│   ├── board.py        # 遊戲板邏輯
│   ├── tile.py         # 麻將牌類別
│   ├── particle.py     # 粒子效果
│   └── scrolling_background.py  # 滾動背景
└── requirements.txt    # Python 依賴套件
```

## 🛠️ 技術規格

- **語言**：Python 3.11+
- **遊戲引擎**：Pygame 2.5.2
- **視窗大小**：1600x1000 像素（可調整）
- **遊戲板**：16x8 格
- **麻將牌尺寸**：60x80 像素

## 📄 授權

本專案採用 MIT 授權，詳見 [LICENSE](LICENSE) 檔案。 
