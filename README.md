# Seat Arrangement App (圓桌座位安排系統)

以 Tkinter + ttkbootstrap 製作的 **拖曳式** 圓桌排座工具，適用婚宴、聚會、活動等場合。  
Features:
- 拖曳安排座位、座位↔座位交換
- 匯入名單（支援 # 註解與空行忽略）
- 儲存/載入狀態（JSON）
- 匯出 CSV/JSON
- 主桌座位數（第 1 桌可自訂）
- 統計總人數 / 已安排 / 未安排

## 安裝與執行
```bash
pip install -r requirements.txt
python seat_app.py
```