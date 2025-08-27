import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from ttkbootstrap import Style
import math
import csv
import json
import os

class SeatingApp:
    def __init__(self, root):
        self.root = root
        self.style = Style("morph")
        self.root.title("圓桌座位安排系統")
        self.root.geometry("1200x700")

        self.max_tables = 15
        self.table_data = []
        self.assigned = {}
        self.people = []

        self.color_pool = [
            "#FFB3BA",  # Light Red
            "#FFDFBA",  # Light Orange
            "#FFFFBA",  # Light Yellow
            "#BAFFC9",  # Light Green
            "#BAE1FF",  # Light Blue
            "#D5BAFF",  # Light Indigo
            "#FFBAED",  # Light Violet
            "#FFE5B4",  # Peach
            "#C9F0FF",  # Pale Cyan
            "#E6E6FA",  # Lavender
            "#F0E68C",  # Khaki
            "#D3FFCE",  # Mint
            "#ADD8E6",  # Light Sky Blue
            "#E0BBE4",  # Orchid
            "#FFDAB9"   # Peach Puff
        ][:self.max_tables]

        self.drag_data = {"widget": None, "text": "", "floating": None, "source_tag": None}

        self.stats_label = tk.Label(self.root, text="總人數: 0｜已安排: 0｜未安排: 0", font=("Arial", 10), anchor="w")
        self.stats_label.pack(fill="x", padx=10, pady=(0, 5))

        self.create_top_controls()
        self.create_main_frames()
        self.root.bind("<Configure>", self.on_resize)

    def update_stats(self):
        total = len(self.people) + len(set(self.assigned.values()))
        assigned = len(set(self.assigned.values()))
        unassigned = len(self.people)
        self.stats_label.config(text=f"總人數: {total}｜已安排: {assigned}｜未安排: {unassigned}")

    def create_top_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", pady=10)

        tk.Label(control_frame, text="桌數:").pack(side="left")
        self.entry_tables = tk.Entry(control_frame, width=5)
        self.entry_tables.insert(0, "5")
        self.entry_tables.pack(side="left", padx=5)

        tk.Label(control_frame, text="每桌座位數:").pack(side="left")
        self.entry_seats = tk.Entry(control_frame, width=5)
        self.entry_seats.insert(0, "8")
        self.entry_seats.pack(side="left", padx=5)

        tk.Button(control_frame, text="建立座位圖", command=self.generate_tables).pack(side="left", padx=10)
        tk.Button(control_frame, text="匯入名單", command=self.import_names).pack(side="left", padx=10)
        tk.Button(control_frame, text="儲存狀態", command=self.save_state).pack(side="left", padx=10)
        tk.Button(control_frame, text="載入狀態", command=self.load_state).pack(side="left", padx=10)
        tk.Button(control_frame, text="匯出資料", command=self.export_data).pack(side="left", padx=10)

    def create_main_frames(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-3>", self.cancel_seat)
        self.canvas.bind("<ButtonRelease-1>", self.drop_on_canvas)
        self.canvas.bind("<Motion>", self.drag_motion)
        self.canvas.tag_bind("seat", "<Button-1>", self.drag_start_from_seat)

        self.sidebar = tk.Frame(self.main_frame, width=250)
        self.sidebar.pack(side="right", fill="y")

        tk.Label(self.sidebar, text="人員清單", font=("Arial", 14)).pack(pady=10)

        # 包裹 frame 加入 Canvas 與 Scrollbar
        scroll_canvas = tk.Canvas(self.sidebar)
        scrollbar = tk.Scrollbar(self.sidebar, orient="vertical", command=scroll_canvas.yview)
        self.people_container = tk.Frame(scroll_canvas)

        self.people_container.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        scroll_canvas.create_window((0, 0), window=self.people_container, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        # 支援滑鼠滾輪
        def _on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows & Linux
        scroll_canvas.bind_all("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))  # Linux
        scroll_canvas.bind_all("<Button-5>", lambda e: scroll_canvas.yview_scroll(1, "units"))   # Linux

        scroll_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.people_frame = self.people_container  # 讓其他程式繼續使用 self.people_frame

        tk.Button(self.sidebar, text="新增人員", command=self.add_person).pack(pady=10)

    def add_person(self):
        name = simpledialog.askstring("新增人員", "請輸入人員名稱：")
        if name and name not in self.people and name not in self.assigned.values():
            self.people.append(name)
            self.create_person_label(name)

    def create_person_label(self, name):
        lbl = tk.Label(self.people_frame, text=name, bg="#f0f0f0", relief="raised", padx=5, pady=2)
        lbl.pack(pady=2, fill="x")
        lbl.bind("<Button-1>", self.drag_start)
        lbl.bind("<B1-Motion>", self.drag_motion)
        lbl.bind("<ButtonRelease-1>", self.drop_on_canvas)
        lbl.bind("<Button-3>", lambda e, n=name, w=lbl: self.remove_person(n, w))
        self.update_stats()

    def remove_person(self, name, widget):
        if messagebox.askyesno("確認刪除", f"確定要刪除 {name} 嗎？"):
            self.people.remove(name)
            widget.destroy()
            self.update_stats()

    def cancel_seat(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for tag, (sx, sy) in self.seat_positions.items():
            if abs(sx - x) < 25 and abs(sy - y) < 25:
                if tag in self.assigned:
                    name = self.assigned.pop(tag)
                    if name not in self.people:
                        self.people.append(name)
                        self.create_person_label(name)
                    self.draw_tables()
                break
        self.update_stats()

    def import_names(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text/CSV", "*.txt *.csv")])
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if not name or name.startswith("#"):
                    continue
                if name not in self.people and name not in self.assigned.values():
                    self.people.append(name)
                    self.create_person_label(name)
        self.update_stats()

    def save_state(self):
        state = {
            "tables": int(self.entry_tables.get()),
            "seats": int(self.entry_seats.get()),
            "assigned": self.assigned,
            "unassigned": self.people
        }
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "狀態已儲存")

    def load_state(self):
        path = filedialog.askopenfilename(filetypes=[("JSON 檔案", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.entry_tables.delete(0, tk.END)
        self.entry_tables.insert(0, str(state["tables"]))
        self.entry_seats.delete(0, tk.END)
        self.entry_seats.insert(0, str(state["seats"]))
        self.assigned = state["assigned"]
        self.people = state["unassigned"]
        for widget in self.people_frame.winfo_children():
            widget.destroy()
        for name in self.people:
            self.create_person_label(name)
        self.generate_tables()
        self.update_stats()

    def generate_tables(self):
        try:
            table_count = int(self.entry_tables.get())
            seats_per_table = int(self.entry_seats.get())
        except ValueError:
            messagebox.showerror("錯誤", "請輸入數字")
            return

        if table_count > self.max_tables:
            messagebox.showerror("錯誤", f"最多只能建立 {self.max_tables} 桌")
            return

        self.table_data = [(seats_per_table, self.color_pool[i % len(self.color_pool)]) for i in range(table_count)]
        self.draw_tables()

    def draw_tables(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        cols = max(1, width // 300)
        rows = math.ceil(len(self.table_data) / cols)

        spacing_x = width // (cols + 1)
        spacing_y = height // (rows + 1)

        self.seat_positions = {}

        for idx, (seats, color) in enumerate(self.table_data):
            col = idx % cols
            row = idx // cols
            cx = spacing_x * (col + 1)
            cy = spacing_y * (row + 1)
            radius = 50

            self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                    fill=color, outline="black", width=2)
            self.canvas.create_text(cx, cy, text=f"第 {idx + 1} 桌", font=("Arial", 10, "bold"))

            for s in range(seats):
                angle = 2 * math.pi * s / seats
                seat_x = cx + math.cos(angle) * 100
                seat_y = cy + math.sin(angle) * 100
                tag = f"seat_{idx}_{s}"
                fill_color = "white" if tag not in self.assigned else "#dfffdc"
                self.canvas.create_oval(seat_x - 20, seat_y - 20, seat_x + 20, seat_y + 20,
                                        fill=fill_color, outline="gray", tags=("seat", tag))
                if tag in self.assigned:
                    name = self.assigned[tag].replace("_", "\n")
                    self.canvas.create_text(seat_x, seat_y, text=name, tags=("seat", tag))
                self.seat_positions[tag] = (seat_x, seat_y)
        self.update_stats()

    def drag_start(self, event):
        widget = event.widget
        self.drag_data["widget"] = widget
        self.drag_data["text"] = widget["text"]
        self.drag_data["source_tag"] = None
        if not self.drag_data["floating"]:
            self.drag_data["floating"] = tk.Label(self.root, text=self.drag_data["text"], bg="lightyellow", relief="solid")
        self.drag_data["floating"].place(x=event.x_root, y=event.y_root)

    def drag_start_from_seat(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for tag, (sx, sy) in self.seat_positions.items():
            if abs(sx - x) < 25 and abs(sy - y) < 25 and tag in self.assigned:
                self.drag_data["widget"] = None
                self.drag_data["text"] = self.assigned[tag]
                self.drag_data["source_tag"] = tag
                if not self.drag_data["floating"]:
                    self.drag_data["floating"] = tk.Label(self.root, text=self.drag_data["text"], bg="lightyellow", relief="solid")
                self.drag_data["floating"].place(x=event.x_root, y=event.y_root)
                break

    def drag_motion(self, event):
        if self.drag_data["floating"]:
            self.drag_data["floating"].place(x=event.x_root + 10, y=event.y_root + 10)

    def drop_on_canvas(self, event):
        if not self.drag_data["text"]:
            return

        x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx())
        y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty())
        dropped = False

        for tag, (sx, sy) in self.seat_positions.items():
            if abs(sx - x) < 25 and abs(sy - y) < 25:
                for k, v in list(self.assigned.items()):
                    if v == self.drag_data["text"]:
                        del self.assigned[k]
                self.assigned[tag] = self.drag_data["text"]
                dropped = True
                break

        if dropped:
            if self.drag_data["widget"] and self.drag_data["widget"].winfo_exists():
                self.drag_data["widget"].destroy()
            if self.drag_data["text"] in self.people:
                self.people.remove(self.drag_data["text"])
        elif self.drag_data["source_tag"]:
            self.assigned[self.drag_data["source_tag"]] = self.drag_data["text"]

        self.draw_tables()

        if self.drag_data["floating"]:
            self.drag_data["floating"].destroy()
            self.drag_data["floating"] = None
        self.drag_data["widget"] = None
        self.drag_data["text"] = ""
        self.drag_data["source_tag"] = None

    def export_data(self):
        if not self.assigned:
            messagebox.showinfo("提醒", "尚未有任何安排")
            return
        filetypes = [("CSV 檔案", "*.csv"), ("JSON 檔案", "*.json")]
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes)
        if not file_path:
            return

        sorted_items = sorted(self.assigned.items(), key=lambda x: (int(x[0].split("_")[1]), int(x[0].split("_")[2])))

        if file_path.endswith(".csv"):
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["桌號", "座位", "人名"])
                for tag, name in sorted_items:
                    t_idx, s_idx = map(int, tag.split("_")[1:])
                    writer.writerow([f"第 {t_idx + 1} 桌", f"第 {s_idx + 1} 位", name])
        elif file_path.endswith(".json"):
            data = []
            for tag, name in sorted_items:
                t_idx, s_idx = map(int, tag.split("_")[1:])
                data.append({"table": t_idx + 1, "seat": s_idx + 1, "name": name})
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("成功", f"已匯出至 {file_path}")

    def on_resize(self, event):
        self.draw_tables()

if __name__ == "__main__":
    root = tk.Tk()
    app = SeatingApp(root)
    root.mainloop()
