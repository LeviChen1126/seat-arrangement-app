# 宴會座位安排系統

[English Version](./README.md)

這是一個以 **Tkinter + ttkbootstrap** 製作的拖曳式排座工具。  
適用於**婚宴、聚會、會議**等需要圓桌座位安排的場合。

![](demo/demo.gif)

---
## 功能特色
1. 拖曳安排座位
2. **座位 ↔ 座位** 直接交換
3. 右鍵取消座位安排
4. **主桌座位數可自訂**（第 1 桌可不同於其他桌）
5. 匯入待排座位的人員名單（TXT/CSV，能忽略空行與 `#` 註解）
6. 儲存 / 載入狀態（JSON 格式）
7. 輸出入座名單（CSV / JSON）
8. 即時統計：總人數 / 已安排 / 未安排
9. 支援最多 15 桌

---

## 開發環境
- Python 3.9+
- Tkinter（Python 標準函式庫）
- ttkbootstrap 1.10+

---

## 下載

可直接從 **[Latest Release](https://github.com/LeviChen1126/seat-arrangement-app/releases/latest)** 頁面下載最新的 Windows 執行檔（`.exe`）。

---

## 安裝 / 使用範例 （原始碼）

1. **前置**
   - 安裝 **Python 3.9+**  
   - 確認有 Tkinter（隨 Python 內建）  
   - 安裝需求套件  
   ```bash
   pip install -r requirements.txt
   ```

2. **執行**
   ```bash
   python seat_app.py
   ```

3. **使用方式**
   - 輸入桌數 / 每桌座位數 / （主桌座位數）  
   - 匯入或新增人員 → 拖曳至座位  
   - 座位 ↔ 座位直接拖曳交換；右鍵可取消安排  
   - 可儲存 / 載入狀態（JSON）或匯出結果（CSV/JSON）

---

## 專案結構
```
─── seat-arrangement-app
   ├── README.md
   ├── README_zh-TW.md
   ├── LICENSE
   ├── .gitattributes
   ├── .gitignore
   ├── requirements.txt
   ├── sample_names.txt   # 範例名單
   ├── seat_app.py        # 主程式
   └── demo/
       └── demo.gif
```

---

## 版權與致謝
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap)  
- [Python Tkinter](https://docs.python.org/3/library/tkinter.html)  
- 其他相關套件版權歸原作者所有
