import tkinter as tk
from tkinter import ttk, messagebox
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Giả định rằng các file GA.py, GWO.py và data_loader.py 
# nằm cùng thư mục
from GA_algorithm import genetic_algorithm
from GWO_algorithm import gwo_algorithm
from data_loader import load_all_data

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧬 GA vs 🐺 GWO - So sánh lập lịch thời khóa biểu")
        self.root.geometry("1350x850")
        self.root.minsize(1100, 700)

        # Khởi tạo các biến trạng thái (thay thế cho biến toàn cục)
        self.ga_result = None
        self.gwo_result = None
        self.ga_fit = 0.0
        self.gwo_fit = 0.0
        self.ga_time = 0.0
        self.gwo_time = 0.0
        self.ga_history = []
        self.gwo_history = []
        self.teacher_names = {}
        self.class_names = {}
        self.subject_names = {}

        # Dựng giao diện
        self._create_controls_frame()
        self._create_main_frames()
        self._create_summary_frame()

    def _create_controls_frame(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        # chọn bộ dữ liệu
        tk.Label(frame_top, text="Dữ liệu:").grid(row=0, column=0)
        self.dataset_var = tk.StringVar(value="data_TH1")
        dataset_options = ["data_TH1", "data_TH2", "data_TH3"]
        dataset_menu = ttk.Combobox(
            frame_top, textvariable=self.dataset_var, values=dataset_options,
            width=10, state="readonly"
        )
        dataset_menu.grid(row=0, column=1, padx=5)


        tk.Label(frame_top, text="Quần thể:").grid(row=0, column=2)
        self.entry_pop = tk.Entry(frame_top, width=5)
        self.entry_pop.insert(0, "80")
        self.entry_pop.grid(row=0, column=3)

        tk.Label(frame_top, text="Thế hệ:").grid(row=0, column=4)
        self.entry_gen = tk.Entry(frame_top, width=5)
        self.entry_gen.insert(0, "100")
        self.entry_gen.grid(row=0, column=5)

        tk.Label(frame_top, text="Đột biến:").grid(row=0, column=6)
        self.entry_mut = tk.Entry(frame_top, width=5)
        self.entry_mut.insert(0, "0.2")
        self.entry_mut.grid(row=0, column=7)

        tk.Button(frame_top, text="⚙️ Chạy GA & GWO", bg="#27ae60", fg="white",
                command=self.run_algorithms).grid(row=0, column=8, padx=10)

    def _create_main_frames(self):
        """Tạo 2 khung chính cho GA và GWO."""
        frame_main = tk.Frame(self.root)
        frame_main.pack(fill="both", expand=True, padx=10)
        frame_main.columnconfigure(0, weight=1)
        frame_main.columnconfigure(1, weight=1)
        frame_main.rowconfigure(0, weight=1)

        self._create_ga_frame(frame_main)
        self._create_gwo_frame(frame_main)

    def _create_ga_frame(self, parent):
        """Tạo khung giao diện cho GA."""
        frame_ga = tk.Frame(parent)
        frame_ga.grid(row=0, column=0, sticky="nsew", padx=5)

        tk.Label(frame_ga, text="🧬 Genetic Algorithm (GA)", font=("Segoe UI", 13, "bold")).pack(pady=5)
        self.log_ga = tk.Text(frame_ga, height=8, bg="#f4f4f4")
        self.log_ga.pack(fill="x", padx=5)
        
        cols = ("Lớp", "Môn", "GV", "Phòng", "Slot")
        self.tree_ga = ttk.Treeview(frame_ga, columns=cols, show="headings")
        for c in cols:
            self.tree_ga.heading(c, text=c)
            self.tree_ga.column(c, width=110, anchor=tk.CENTER)
        self.tree_ga.pack(fill="both", expand=True, pady=(5, 0))

        btn_frame_ga = tk.Frame(frame_ga)
        btn_frame_ga.pack(fill="x", pady=5)
        tk.Button(btn_frame_ga, text="🧬 GV", command=lambda: self.show_timetable("Giáo viên", "GA")).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame_ga, text="🧬 Lớp", command=lambda: self.show_timetable("Lớp", "GA")).pack(side="left", padx=5)
        tk.Button(btn_frame_ga, text="🧬 Phòng", command=lambda: self.show_timetable("Phòng", "GA")).pack(side="left", padx=5)

    def _create_gwo_frame(self, parent):
        """Tạo khung giao diện cho GWO."""
        frame_gwo = tk.Frame(parent)
        frame_gwo.grid(row=0, column=1, sticky="nsew", padx=5)
        
        tk.Label(frame_gwo, text="🐺 Grey Wolf Optimizer (GWO)", font=("Segoe UI", 13, "bold")).pack(pady=5)
        self.log_gwo = tk.Text(frame_gwo, height=8, bg="#f4f4f4")
        self.log_gwo.pack(fill="x", padx=5)
        
        cols = ("Lớp", "Môn", "GV", "Phòng", "Slot")
        self.tree_gwo = ttk.Treeview(frame_gwo, columns=cols, show="headings")
        for c in cols:
            self.tree_gwo.heading(c, text=c)
            self.tree_gwo.column(c, width=110, anchor=tk.CENTER)
        self.tree_gwo.pack(fill="both", expand=True, pady=(5, 0))

        btn_frame_gwo = tk.Frame(frame_gwo)
        btn_frame_gwo.pack(fill="x", pady=5)
        tk.Button(btn_frame_gwo, text="🐺 GV", command=lambda: self.show_timetable("Giáo viên", "GWO")).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame_gwo, text="🐺 Lớp", command=lambda: self.show_timetable("Lớp", "GWO")).pack(side="left", padx=5)
        tk.Button(btn_frame_gwo, text="🐺 Phòng", command=lambda: self.show_timetable("Phòng", "GWO")).pack(side="left", padx=5)

    def _create_summary_frame(self):
        """Tạo khung tóm tắt so sánh và nút biểu đồ."""
        frame_summary = tk.LabelFrame(self.root, text="📈 So sánh tổng hợp")
        frame_summary.pack(padx=20, pady=10, fill="x")
        
        cols = ("Thuật toán", "Fitness", "Thời gian")
        self.summary_table = ttk.Treeview(frame_summary, columns=cols, show="headings", height=2)
        for c in cols:
            self.summary_table.heading(c, text=c)
            self.summary_table.column(c, width=150, anchor=tk.CENTER)
        self.summary_table.pack(side="left", padx=20, fill="x", expand=True)
        
        tk.Button(frame_summary, text="📊 Hiển thị biểu đồ", bg="#2980b9", fg="white",
                  command=self.draw_chart_summary).pack(side="left", padx=20, pady=10)

    # ==================== CÁC HÀM XỬ LÝ LOGIC ====================

    def run_algorithms(self):
        """Chạy cả hai thuật toán và cập nhật giao diện."""
        selected_folder = self.dataset_var.get().strip()

        # Map tự động để tránh lỗi do đổi tên thư mục
        folder_map = {
            "data_TH1": "data_TH1(small)",
            "data_TH2": "data_TH2(normal)",
            "data_TH3": "data_TH3(stress)"
        }

        folder = folder_map.get(selected_folder, selected_folder)
        data = load_all_data(folder)

        if not data:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu từ: {folder}")
            return

        # Lưu dữ liệu vào self
        (teachers, classes, subjects, rooms, timeslots,
        self.teacher_names, self.class_names, self.subject_names) = data

        try:
            pop = int(self.entry_pop.get())
            gen = int(self.entry_gen.get())
            mut = float(self.entry_mut.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Tham số không hợp lệ. Vui lòng nhập số.")
            return

        # Xóa log cũ
        self.log_ga.delete(1.0, tk.END)
        self.log_gwo.delete(1.0, tk.END)

        # =============== GA ===============
        self.log_ga.insert(tk.END, "🚀 Đang chạy Genetic Algorithm...\n")
        self.log_ga.update()
        start_ga = time.time()
        self.ga_result, self.ga_fit, self.ga_history = genetic_algorithm(
            teachers, classes, subjects, rooms, timeslots, self.log_ga, pop, gen, mut)
        self.ga_time = time.time() - start_ga
        self.log_ga.insert(tk.END, f"\n✅ GA hoàn tất\nThời gian: {self.ga_time:.2f}s\nBest: {self.ga_fit:.4f}\n")

        # =============== GWO ===============
        self.log_gwo.insert(tk.END, "🐺 Đang chạy Grey Wolf Optimizer...\n")
        self.log_gwo.update()
        start_gwo = time.time()
        self.gwo_result, self.gwo_fit, self.gwo_history = gwo_algorithm(
            teachers, classes, subjects, rooms, timeslots, self.log_gwo, pop, gen)
        self.gwo_time = time.time() - start_gwo
        self.log_gwo.insert(tk.END, f"\n✅ GWO hoàn tất\nThời gian: {self.gwo_time:.2f}s\nBest: {self.gwo_fit:.4f}\n")

        # Cập nhật bảng
        self._fill_table(self.tree_ga, self.ga_result)
        self._fill_table(self.tree_gwo, self.gwo_result)
        self._update_summary_table()

    def _fill_table(self, tree, data):
        """Điền dữ liệu kết quả vào Treeview."""
        if not data:
            return
        for row in tree.get_children():
            tree.delete(row)
        for (cls, sub, teacher, room, slot) in sorted(data, key=lambda x: x[-1]):
            tree.insert("", tk.END, values=(
                self.class_names.get(cls, cls),
                self.subject_names.get(sub, sub),
                self.teacher_names.get(teacher, teacher),
                room,
                slot
            ))

    def _update_summary_table(self):
        """Cập nhật bảng tóm tắt so sánh."""
        for i in self.summary_table.get_children():
            self.summary_table.delete(i)
        self.summary_table.insert("", "end", values=("GA", f"{self.ga_fit:.4f}", f"{self.ga_time:.2f}s"))
        self.summary_table.insert("", "end", values=("GWO", f"{self.gwo_fit:.4f}", f"{self.gwo_time:.2f}s"))

    # ==================== CÁC CỬA SỔ PHỤ ====================

    def show_timetable(self, mode, algo_name):
        """Hiển thị TKB chi tiết theo (GV, Lớp, Phòng)."""
        
        if algo_name == "GA":
            data = self.ga_result
        else:
            data = self.gwo_result

        if not data:
            messagebox.showwarning("Không có dữ liệu", f"Chưa có lịch {algo_name}.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"📅 {algo_name} - Thời khóa biểu theo {mode}")
        win.geometry("1100x650")
        win.configure(bg="#f8f8f8")
        win.minsize(900, 500)

        win.rowconfigure(0, weight=0)
        win.rowconfigure(1, weight=0)
        win.rowconfigure(2, weight=1)
        win.columnconfigure(0, weight=1)

        days = ["T2", "T3", "T4", "T5", "T6", "T7"]
        periods = ["S", "C"] # Sáng, Chiều

        tk.Label(win, text=f"{algo_name} - Thời khóa biểu theo {mode}",
                 font=("Segoe UI", 15, "bold"), bg="#f8f8f8").grid(row=0, column=0, pady=10)

        frame_select = tk.Frame(win, bg="#f8f8f8")
        frame_select.grid(row=1, column=0, pady=5)
        tk.Label(frame_select, text=f"Chọn {mode.lower()}:", font=("Segoe UI", 11),
                 bg="#f8f8f8").pack(side=tk.LEFT, padx=5)

        # Lấy danh sách tùy chọn (options) dựa trên chế độ xem
        if mode == "Giáo viên":
            options = sorted({self.teacher_names.get(t, t) for (_, _, t, _, _) in data})
            key_map = {self.teacher_names.get(t, t): t for (_, _, t, _, _) in data}
        elif mode == "Lớp":
            options = sorted({self.class_names.get(c, c) for (c, _, _, _, _) in data})
            key_map = {self.class_names.get(c, c): c for (c, _, _, _, _) in data}
        else: # Phòng
            options = sorted({r for (_, _, _, r, _) in data})
            key_map = {r: r for r in options}

        combo = ttk.Combobox(frame_select, values=options, state="readonly",
                             font=("Segoe UI", 11), width=30)
        combo.pack(side=tk.LEFT, padx=10)

        frame_table = tk.Frame(win, bg="#000", bd=1, relief="solid")
        frame_table.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)

        total_rows = len(periods) + 1
        total_cols = len(days) + 1
        for i in range(total_rows):
            frame_table.rowconfigure(i, weight=1, uniform="row")
        for j in range(total_cols):
            frame_table.columnconfigure(j, weight=1, uniform="col")

        headers = ["Buổi/Thứ"] + days
        for j, h in enumerate(headers):
            tk.Label(frame_table, text=h, bg="#e0e0e0", font=("Segoe UI", 10, "bold"),
                     relief="solid", borderwidth=1, padx=4, pady=4).grid(
                row=0, column=j, sticky="nsew")

        # Tạo bản đồ lịch (schedule map) để tra cứu nhanh
        schedule_map = {}
        for (cls, sub, teacher, room, slot) in data:
            key = None
            if mode == "Giáo viên":
                key = teacher
            elif mode == "Lớp":
                key = cls
            else: # Phòng
                key = room
            
            schedule_map.setdefault(key, {})[slot] = (
                f"Môn: {self.subject_names.get(sub, sub)}\n"
                f"GV: {self.teacher_names.get(teacher, teacher)}\n"
                f"Lớp: {self.class_names.get(cls, cls)}\n"
                f"Phòng: {room}"
            )

        def render(selected_name):
            """Vẽ lại bảng TKB khi combobox thay đổi."""
            # Lấy key (mã) thực sự từ tên đã chọn
            selected_key = key_map.get(selected_name)
            
            # Xóa các ô cũ
            for widget in frame_table.grid_slaves():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()

            # Vẽ lại các hàng và ô
            for i, ses in enumerate(periods, start=1):
                tk.Label(frame_table, text="Sáng" if ses == "S" else "Chiều",
                         bg="#f5f5f5", font=("Segoe UI", 10, "bold"),
                         relief="solid", borderwidth=1, padx=3, pady=3).grid(
                    row=i, column=0, sticky="nsew")

                for j, d in enumerate(days, start=1):
                    slot = f"{d}-{ses}"
                    content = schedule_map.get(selected_key, {}).get(slot, "")
                    label = tk.Label(frame_table, text=content, bg="white",
                                     font=("Segoe UI", 10), justify="center",
                                     wraplength=150, relief="solid", borderwidth=1)
                    label.grid(row=i, column=j, sticky="nsew")

        combo.bind("<<ComboboxSelected>>", lambda e: render(combo.get()))
        if options:
            combo.current(0)
            render(options[0])

    def draw_chart_summary(self):
        """Hiển thị biểu đồ đường so sánh fitness theo thế hệ (Matplotlib)."""
        if not self.ga_history and not self.gwo_history:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng chạy thuật toán trước khi xem biểu đồ.")
            return

        win = tk.Toplevel(self.root)
        win.title("📈 So sánh tiến hóa Fitness: GA vs GWO")
        win.geometry("900x650")

        fig, ax = plt.subplots(figsize=(8.5, 5.5))
        if self.ga_history:
            ax.plot(range(len(self.ga_history)), self.ga_history, label="GA (Genetic Algorithm)", linewidth=2)
        if self.gwo_history:
            ax.plot(range(len(self.gwo_history)), self.gwo_history, label="GWO (Grey Wolf Optimizer)", linewidth=2, linestyle="--")

        ax.set_title("So sánh tiến hóa Fitness giữa GA và GWO", fontsize=14, fontweight="bold")
        ax.set_xlabel("Thế hệ (Generation)", fontsize=12)
        ax.set_ylabel("Fitness tốt nhất", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
        fig.tight_layout()

        # Nhúng biểu đồ vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Thêm phần kết luận
        conclusion = ""
        if self.ga_fit == 0 and self.gwo_fit == 0:
            conclusion = "Chưa chạy thuật toán."
        else:
            fit_comp = "GWO tốt hơn" if self.gwo_fit > self.ga_fit else "GA tốt hơn" if self.ga_fit > self.gwo_fit else "Fitness bằng nhau"
            time_comp = "GWO nhanh hơn" if self.gwo_time < self.ga_time else "GA nhanh hơn" if self.ga_time < self.gwo_time else "Tốc độ bằng nhau"
            conclusion = f"➡️ Kết luận: {fit_comp} và {time_comp}."

        tk.Label(win, text=conclusion, font=("Segoe UI", 11, "italic"), fg="black").pack(pady=8)

