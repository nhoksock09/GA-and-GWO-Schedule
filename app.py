import tkinter as tk
from tkinter import ttk, messagebox
from GA import genetic_algorithm
from data_loader import load_all_data



def show_timetable(mode, data):
    if not data:
        messagebox.showwarning("Không có dữ liệu", "Chưa có lịch.")
        return

    win = tk.Toplevel(root)
    win.title(f"📅 Thời khóa biểu - {mode}")
    win.geometry("1100x650")
    win.configure(bg="#f8f8f8")

    days = ["T2", "T3", "T4", "T5", "T6", "T7"]
    periods = ["S", "C"]

    tk.Label(win, text=f"Thời khóa biểu theo {mode}",
             font=("Segoe UI", 15, "bold"), bg="#f8f8f8").pack(pady=10)

    frame_select = tk.Frame(win, bg="#f8f8f8")
    frame_select.pack(pady=5)
    tk.Label(frame_select, text=f"Chọn {mode.lower()}:", font=("Segoe UI", 11),
             bg="#f8f8f8").pack(side=tk.LEFT, padx=5)

    # === Các lựa chọn (Lớp / Giáo viên / Phòng)
    if mode == "Giáo viên":
        options = sorted({t for (_, _, t, _, _) in data})
    elif mode == "Lớp":
        options = sorted({c for (c, _, _, _, _) in data})
    else:
        options = sorted({r for (_, _, _, r, _) in data})

    combo = ttk.Combobox(frame_select, values=options, state="readonly",
                         font=("Segoe UI", 11), width=20)
    combo.pack(side=tk.LEFT, padx=10)

    # === Khung bảng chính
    frame_table = tk.Frame(win, bg="#000", bd=1, relief="solid")
    frame_table.pack(fill="both", expand=True, padx=20, pady=15)

    # Cấu hình grid để chia đều cột & hàng
    total_rows = len(periods) + 1
    total_cols = len(days) + 1
    for i in range(total_rows):
        frame_table.rowconfigure(i, weight=1, uniform="row")
    for j in range(total_cols):
        frame_table.columnconfigure(j, weight=1, uniform="col")

    # === Header hàng đầu
    headers = ["Buổi/Thứ"] + days
    for j, h in enumerate(headers):
        tk.Label(frame_table, text=h, bg="#e0e0e0", font=("Segoe UI", 10, "bold"),
                 relief="solid", borderwidth=1, padx=4, pady=4).grid(
            row=0, column=j, sticky="nsew")

    # === Chuẩn bị map dữ liệu
    schedule_map = {}
    for (cls, sub, teacher, room, slot) in data:
        key = teacher if mode == "Giáo viên" else cls if mode == "Lớp" else room
        schedule_map.setdefault(key, {})[slot] = (
            f"Môn học: {subject_names.get(sub, sub)}\n"
            f"GV: {teacher_names.get(teacher, teacher)}\n"
            f"Lớp: {class_names.get(cls, cls)}\n"
            f"Phòng: {room}"
        )



    def render(selected):
        # Xóa nội dung cũ
        for widget in frame_table.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        # Vẽ lại bảng mới
        for i, ses in enumerate(periods, start=1):
            tk.Label(frame_table, text="Sáng" if ses == "S" else "Chiều",
                     bg="#f5f5f5", font=("Segoe UI", 10, "bold"),
                     relief="solid", borderwidth=1, padx=3, pady=3).grid(
                row=i, column=0, sticky="nsew")

            for j, d in enumerate(days, start=1):
                slot = f"{d}-{ses}"
                content = schedule_map.get(selected, {}).get(slot, "")
                label = tk.Label(frame_table, text=content, bg="white",
                                 font=("Segoe UI", 10), justify="center",
                                 wraplength=150, relief="solid", borderwidth=1)
                label.grid(row=i, column=j, sticky="nsew", padx=0, pady=0)

    combo.bind("<<ComboboxSelected>>", lambda e: render(combo.get()))
    if options:
        combo.current(0)
        render(options[0])





def run_ga():
    global best_schedule, teacher_names, class_names, subject_names
    data = load_all_data()
    if not data:
        return
    teachers, classes, subjects, rooms, timeslots, teacher_names, class_names, subject_names = data

    pop, gen, mut = int(entry_pop.get()), int(entry_gen.get()), float(entry_mut.get())
    log_text.delete(1.0, tk.END)
    best, fit = genetic_algorithm(teachers, classes, subjects, rooms, timeslots, log_text, pop, gen, mut)
    best_schedule = best

    for row in tree.get_children():
        tree.delete(row)

    for (cls, sub, teacher, room, slot) in sorted(best, key=lambda x: x[-1]):
        tree.insert("", tk.END, values=(
            class_names.get(cls, cls),
            subject_names.get(sub, sub),
            teacher_names.get(teacher, teacher),
            room, slot
        ))



root = tk.Tk()
root.title("🧬 GA - Thời khóa biểu (Adaptive + Repair + View)")
root.geometry("950x650")

frame_top = tk.Frame(root); frame_top.pack(pady=10)
tk.Label(frame_top, text="Quần thể:").grid(row=0, column=0)
entry_pop = tk.Entry(frame_top, width=5); entry_pop.insert(0, "80"); entry_pop.grid(row=0, column=1)
tk.Label(frame_top, text="Thế hệ:").grid(row=0, column=2)
entry_gen = tk.Entry(frame_top, width=5); entry_gen.insert(0, "300"); entry_gen.grid(row=0, column=3)
tk.Label(frame_top, text="Đột biến:").grid(row=0, column=4)
entry_mut = tk.Entry(frame_top, width=5); entry_mut.insert(0, "0.2"); entry_mut.grid(row=0, column=5)
tk.Button(frame_top, text="🚀 Chạy GA", bg="#2ecc71", fg="white", command=run_ga).grid(row=0, column=6, padx=10)

log_text = tk.Text(root, height=8, bg="#f4f4f4"); log_text.pack(fill="x", padx=10, pady=10)
cols = ("Lớp", "Môn", "Giảng viên", "Phòng", "Thời gian")
tree = ttk.Treeview(root, columns=cols, show="headings")
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=150, anchor=tk.CENTER)
tree.pack(fill="both", expand=True, padx=10, pady=10)

frame_bottom = tk.Frame(root); frame_bottom.pack(pady=10)
tk.Button(frame_bottom, text="🧑‍🏫 Theo giáo viên", command=lambda: show_timetable("Giáo viên", best_schedule)).grid(row=0, column=0, padx=10)
tk.Button(frame_bottom, text="🏫 Theo lớp", command=lambda: show_timetable("Lớp", best_schedule)).grid(row=0, column=1, padx=10)
tk.Button(frame_bottom, text="🏢 Theo phòng", command=lambda: show_timetable("Phòng", best_schedule)).grid(row=0, column=2, padx=10)

root.mainloop()
