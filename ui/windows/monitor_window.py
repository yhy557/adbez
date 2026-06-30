import tkinter as tk
import logging
import platform
import ctypes
from collections import deque
from core.process import registry
from config.state import global_state
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adbez import MainApp

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S',
    force=True
)

if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

    def show_in_taskbar(root):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, root.deiconify)

class ProcessCard(tk.Frame):
    def __init__(self, parent, name, pid, cpu, memory):
        super().__init__(parent, bg="#ffffff", highlightbackground="#e9ecef", highlightthickness=1)
        self.target_height = 250
        self.current_height = 0
        self.is_expanded = False
        self.canvas_widget = None
        self.canvas = None
        self.current_cpu = cpu
        self.current_memory = memory

        self.main_row = tk.Frame(self, bg="#ffffff", height=50)
        self.main_row.pack(fill="x", side="top")
        self.main_row.pack_propagate(False)

        for i in range(4):
            self.main_row.columnconfigure(i, weight=1, uniform="col")

        self.lbl_name = tk.Label(self.main_row, text=name, font=("Segoe UI", 10, "bold"), fg="#212529", bg="#ffffff", anchor="w")
        self.lbl_name.grid(row=0, column=0, sticky="ew", padx=15, pady=13)

        self.lbl_pid = tk.Label(self.main_row, text=str(pid), font=("Segoe UI", 10), fg="#495057", bg="#ffffff", anchor="w")
        self.lbl_pid.grid(row=0, column=1, sticky="ew", padx=15, pady=13)

        self.lbl_cpu = tk.Label(self.main_row, text=str(cpu), font=("Segoe UI", 10, "bold"), fg="#fd7e14", bg="#ffffff", anchor="w")
        self.lbl_cpu.grid(row=0, column=2, sticky="ew", padx=15, pady=13)

        self.lbl_mem = tk.Label(self.main_row, text=memory, font=("Segoe UI", 10), fg="#495057", bg="#ffffff", anchor="w")
        self.lbl_mem.grid(row=0, column=3, sticky="ew", padx=15, pady=13)

        self.detail_frame = tk.Frame(self, bg="#f8f9fa", height=0)
        self.detail_frame.pack(fill="x", side="top")
        self.detail_frame.pack_propagate(False)

        self.bind_click_events(self.main_row)

    def bind_click_events(self, widget):
        widget.bind("<Button-1>", self.toggle_panel)
        for child in widget.winfo_children():
            child.bind("<Button-1>", self.toggle_panel)

    def toggle_panel(self, event):
        if self.is_expanded:
            self.is_expanded = False
            self.animate_collapse()
            self.destroy_graph()
        else:
            self.is_expanded = True
            self.setup_graph()
            self.animate_expand()

    def setup_graph(self):
        self.max_pts = 40
        self.cpu_log = deque([0] * self.max_pts, maxlen=self.max_pts)
        self.ram_log = deque([0] * self.max_pts, maxlen=self.max_pts)
        self.x_axis = list(range(self.max_pts))

        self.fig = Figure(figsize=(7, 2.5), facecolor='#111116')
        self.gs = self.fig.add_gridspec(2, 2, width_ratios=[1.3, 1], wspace=0.25, hspace=0.35)

        self.ax_c = self.fig.add_subplot(self.gs[0, 0], facecolor='#16161f')
        self.ax_r = self.fig.add_subplot(self.gs[1, 0], facecolor='#16161f')
        self.ax_d = self.fig.add_subplot(self.gs[:, 1], facecolor='#111116')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.detail_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_graph(self.current_cpu, self.current_memory)

    def destroy_graph(self):
        if getattr(self, 'canvas_widget', None):
            self.canvas_widget.destroy()
            self.canvas_widget = None
            self.canvas = None
            self.fig = None

    def update_graph(self, cpu, memory):
        if not self.is_expanded or getattr(self, 'canvas', None) is None:
            return

        try:
            c_val = float(str(cpu).replace('%', '').strip())
            r_val = float(str(memory).replace(' MB', '').replace(' KB', '').strip())
        except ValueError:
            c_val = 0.0
            r_val = 0.0

        self.cpu_log.append(c_val)
        self.ram_log.append(r_val)

        self.ax_c.clear()
        self.ax_c.set_facecolor('#16161f')
        self.ax_c.plot(self.x_axis, list(self.cpu_log), color='#00e5ff', linewidth=1.5)
        self.ax_c.fill_between(self.x_axis, list(self.cpu_log), color='#00e5ff', alpha=0.1)
        self.ax_c.set_ylim(0, max(100, max(self.cpu_log) + 10))
        self.ax_c.axis('off')
        self.ax_c.text(0.02, 0.7, f"CPU   {c_val}%", color='white', transform=self.ax_c.transAxes, fontsize=10, weight='bold')

        self.ax_r.clear()
        self.ax_r.set_facecolor('#16161f')
        self.ax_r.plot(self.x_axis, list(self.ram_log), color='#b388ff', linewidth=1.5)
        self.ax_r.fill_between(self.x_axis, list(self.ram_log), color='#b388ff', alpha=0.1)
        self.ax_r.set_ylim(0, max(100, max(self.ram_log) + 10))
        self.ax_r.axis('off')
        self.ax_r.text(0.02, 0.7, f"RAM   {memory}", color='white', transform=self.ax_r.transAxes, fontsize=10, weight='bold')

        self.ax_d.clear()
        cpu_ratio = min(100.0, c_val)
        ram_ratio = min(100.0, r_val)

        self.ax_d.pie([cpu_ratio, max(0.0, 100.0 - cpu_ratio)], radius=1.0, colors=['#00e5ff', '#22222b'], startangle=90, wedgeprops=dict(width=0.12, edgecolor='none'))
        self.ax_d.pie([ram_ratio, max(0.0, 100.0 - ram_ratio)], radius=0.8, colors=['#b388ff', '#22222b'], startangle=90, wedgeprops=dict(width=0.12, edgecolor='none'))
        self.ax_d.axis('off')

        avg_load = int((c_val + ram_ratio) // 2)
        self.ax_d.text(0, -0.1, f"{avg_load}%", color='white', ha='center', va='center', fontsize=14, weight='bold')
        self.ax_d.text(0, 0.25, "LOAD", color='#7f8c8d', ha='center', va='center', fontsize=9, weight='bold')

        self.canvas.draw_idle()

    def animate_expand(self):
        if self.current_height < self.target_height:
            self.current_height += 25
            self.detail_frame.configure(height=self.current_height)
            self.after(15, self.animate_expand)

    def animate_collapse(self):
        if self.current_height > 0:
            self.current_height -= 25
            self.detail_frame.configure(height=self.current_height)
            self.after(15, self.animate_collapse)

    def update(self, cpu, memory):
        self.current_cpu = cpu
        self.current_memory = memory
        self.lbl_cpu.config(text=str(cpu))
        self.lbl_mem.config(text=str(memory))


class SystemMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")
        self.root.geometry("650x450")
        self.root.minsize(500, 350)
        self.root.configure(bg="#ced4da")

        self.root.overrideredirect(True)
        self.root.bind("<Map>", self.on_deiconify)

        self.external_frame = tk.Frame(self.root, bg="#ced4da", bd=0)
        self.external_frame.pack(fill="both", expand=True)

        self.main_area = tk.Frame(self.external_frame, bg="#f8f9fa", bd=0)
        self.main_area.pack(fill="both", expand=True, padx=2, pady=2)

        self.title_bar = tk.Frame(self.main_area, bg="#343a40", height=30)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)

        if platform.system() == "Windows":
            self.title_bar.bind("<Button-1>", self.on_move)
        else:
            self.title_bar.bind("<ButtonPress-1>", self.start_move)
            self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
            self.title_bar.bind("<B1-Motion>", self.on_move)

        self.app_title = tk.Label(self.title_bar, text="System Monitor", fg="white", bg="#343a40", font=("Segoe UI", 9))
        self.app_title.pack(side="left", padx=10)

        self.close_btn = tk.Button(self.title_bar, text="✕", bg="#343a40", fg="white", bd=0, width=4, activebackground="red", command=self.close_window)
        self.close_btn.pack(side="right", fill="y")
        self.close_btn.bind("<Enter>", lambda e: self.on_enter(e, "red"))
        self.close_btn.bind("<Leave>", self.leave_enter)

        self.max_btn = tk.Button(self.title_bar, text="▢", bg="#343a40", fg="white", bd=0, width=4, activebackground="#495057", command=self.maximize_window)
        self.max_btn.pack(side="right", fill="y")
        self.max_btn.bind("<Enter>", lambda e: self.on_enter(e, "#495057"))
        self.max_btn.bind("<Leave>", self.leave_enter)

        self.min_btn = tk.Button(self.title_bar, text="—", bg="#343a40", fg="white", bd=0, width=4, activebackground="#495057", command=self.minimize_window)
        self.min_btn.pack(side="right", fill="y")
        self.min_btn.bind("<Enter>", lambda e: self.on_enter(e, "#495057"))
        self.min_btn.bind("<Leave>", self.leave_enter)

        self.setup_resizing()

        self.cards = {}

        self.top_bar = tk.Frame(self.main_area, bg="#f8f9fa", height=30)
        self.top_bar.pack(fill="x", side="top", padx=20, pady=10)
        self.top_bar.pack_propagate(False)

        self.title_label = tk.Label(self.top_bar, text="~ System Monitor", font=("Segoe UI", 13, "bold"), fg="#212529", bg="#f8f9fa")
        self.title_label.pack(side="left")

        self.tab_frame = tk.Frame(self.top_bar, bg="#f8f9fa")
        self.tab_frame.pack(side="right")

        self.btn_processes = tk.Button(self.tab_frame, text="Processes", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#212529", relief="flat", bd=1, padx=15, pady=5)
        self.btn_processes.pack(side="left", padx=2)

        self.btn_performance = tk.Button(self.tab_frame, text="Performance", font=("Segoe UI", 10), bg="#f8f9fa", fg="#495057", relief="flat", bd=0, padx=15, pady=5)
        self.btn_performance.pack(side="left", padx=2)

        self.search_bar = tk.Frame(self.main_area, bg="#f8f9fa", height=30)
        self.search_bar.pack(fill="x", side="top", padx=20, pady=5)
        self.search_bar.pack_propagate(False)

        self.search_wrapper = tk.Frame(self.search_bar, bg="#ffffff", highlightbackground="#e9ecef", highlightthickness=1, width=240)
        self.search_wrapper.pack_propagate(False)
        self.search_wrapper.pack(side="left", fill="y")

        self.search_entry = tk.Entry(self.search_wrapper, font=("Segoe UI", 10), bg="#ffffff", fg="#212529", bd=0)
        self.search_entry.insert(0, "Search processes...")
        self.search_entry.pack(fill="both", expand=True, padx=10, pady=8)

        self.stats_frame = tk.Frame(self.search_bar, bg="#f8f9fa")
        self.stats_frame.pack(side="right", fill="y")

        self.cpu_icon = tk.Label(self.stats_frame, text="CPU: 0.0%", font=("Segoe UI", 10, "bold"), fg="#212529", bg="#f8f9fa")
        self.cpu_icon.pack(side="left", padx=15)

        self.mem_icon = tk.Label(self.stats_frame, text="Mem: 0.0 MB", font=("Segoe UI", 10, "bold"), fg="#212529", bg="#f8f9fa")
        self.mem_icon.pack(side="left", padx=15)

        self.table_header = tk.Frame(self.main_area, bg="#f8f9fa", height=30)
        self.table_header.pack(fill="x", side="top", padx=20, pady=(15, 5))

        headers = ["PROCESS NAME", "PID", "% CPU ↓", "MEMORY"]
        for i, name in enumerate(headers):
            self.table_header.columnconfigure(i, weight=1, uniform="col")
            lbl = tk.Label(self.table_header, text=name, font=("Segoe UI", 9, "bold"), fg="#6c757d", bg="#f8f9fa", anchor="w")
            lbl.grid(row=0, column=i, sticky="ew", padx=15)

        self.container = tk.Frame(self.main_area, bg="#f8f9fa")
        self.container.pack(fill="both", expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(self.container, bg="#f8f9fa", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.root.bind("<Configure>", self.maintain_canvas_width)

        self.bottom_bar = tk.Frame(self.main_area, bg="#f1f3f5", height=35)
        self.bottom_bar.pack(fill="x", side="bottom")

        if platform.system() == "Windows":
            show_in_taskbar(self.root)

        self.root.after(1000, self.insert_data)

    def setup_resizing(self):
        grip_top = tk.Frame(self.root, cursor="size_ns", height=4, bg="#ced4da")
        grip_bottom = tk.Frame(self.root, cursor="size_ns", height=4, bg="#ced4da")
        grip_left = tk.Frame(self.root, cursor="size_we", width=4, bg="#ced4da")
        grip_right = tk.Frame(self.root, cursor="size_we", width=4, bg="#ced4da")

        grip_nw = tk.Frame(self.root, cursor="sizing", width=8, height=8, bg="#ced4da")
        grip_ne = tk.Frame(self.root, cursor="sizing", width=8, height=8, bg="#ced4da")
        grip_sw = tk.Frame(self.root, cursor="sizing", width=8, height=8, bg="#ced4da")
        grip_se = tk.Frame(self.root, cursor="sizing", width=8, height=8, bg="#ced4da")

        grip_top.place(relx=0, rely=0, relwidth=1, anchor="nw")
        grip_bottom.place(relx=0, rely=1, relwidth=1, anchor="sw")
        grip_left.place(relx=0, rely=0, relheight=1, anchor="nw")
        grip_right.place(relx=1, rely=0, relheight=1, anchor="ne")

        grip_nw.place(relx=0, rely=0, anchor="nw")
        grip_ne.place(relx=1, rely=0, anchor="ne")
        grip_sw.place(relx=0, rely=1, anchor="sw")
        grip_se.place(relx=1, rely=1, anchor="se")

        def start_resize(event, direction):
            direction.start_x = self.root.winfo_x()
            direction.start_y = self.root.winfo_y()
            direction.start_w = self.root.winfo_width()
            direction.start_h = self.root.winfo_height()
            direction.press_x = event.x_root
            direction.press_y = event.y_root

        def do_resize_top(event):
            dy = event.y_root - grip_top.press_y
            new_y = grip_top.start_y + dy
            new_h = grip_top.start_h - dy
            if new_h > 350:
                self.root.geometry(f"{self.root.winfo_width()}x{new_h}+{self.root.winfo_x()}+{new_y}")

        def do_resize_bottom(event):
            dy = event.y_root - grip_bottom.press_y
            new_h = grip_bottom.start_h + dy
            if new_h > 350:
                self.root.geometry(f"{self.root.winfo_width()}x{new_h}+{self.root.winfo_x()}+{self.root.winfo_y()}")

        def do_resize_left(event):
            dx = event.x_root - grip_left.press_x
            new_x = grip_left.start_x + dx
            new_w = grip_left.start_w - dx
            if new_w > 500:
                self.root.geometry(f"{new_w}x{self.root.winfo_height()}+{new_x}+{self.root.winfo_y()}")

        def do_resize_right(event):
            dx = event.x_root - grip_right.press_x
            new_w = grip_right.start_w + dx
            if new_w > 500:
                self.root.geometry(f"{new_w}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}")

        def do_resize_nw(event):
            dx = event.x_root - grip_nw.press_x
            dy = event.y_root - grip_nw.press_y
            new_x = grip_nw.start_x + dx
            new_y = grip_nw.start_y + dy
            new_w = grip_nw.start_w - dx
            new_h = grip_nw.start_h - dy
            if new_w > 500 and new_h > 350:
                self.root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")

        def do_resize_ne(event):
            dx = event.x_root - grip_ne.press_x
            dy = event.y_root - grip_ne.press_y
            new_y = grip_ne.start_y + dy
            new_w = grip_ne.start_w + dx
            new_h = grip_ne.start_h - dy
            if new_w > 500 and new_h > 350:
                self.root.geometry(f"{new_w}x{new_h}+{self.root.winfo_x()}+{new_y}")

        def do_resize_sw(event):
            dx = event.x_root - grip_sw.press_x
            dy = event.y_root - grip_sw.press_y
            new_x = grip_sw.start_x + dx
            new_w = grip_sw.start_w - dx
            new_h = grip_sw.start_h + dy
            if new_w > 500 and new_h > 350:
                self.root.geometry(f"{new_w}x{new_h}+{new_x}+{self.root.winfo_y()}")

        def do_resize_se(event):
            dx = event.x_root - grip_se.press_x
            dy = event.y_root - grip_se.press_y
            new_w = grip_se.start_w + dx
            new_h = grip_se.start_h + dy
            if new_w > 500 and new_h > 350:
                self.root.geometry(f"{new_w}x{new_h}+{self.root.winfo_x()}+{self.root.winfo_y()}")

        for grip, func in [(grip_top, do_resize_top), (grip_bottom, do_resize_bottom),
                           (grip_left, do_resize_left), (grip_right, do_resize_right),
                           (grip_nw, do_resize_nw), (grip_ne, do_resize_ne),
                           (grip_sw, do_resize_sw), (grip_se, do_resize_se)]:
            grip.bind("<Button-1>", lambda e, g=grip: start_resize(e, g))
            grip.bind("<B1-Motion>", func)

    def start_move(self, event):
        self.root.x = event.x
        self.root.y = event.y

    def stop_move(self, event):
        self.root.x = None
        self.root.y = None

    def on_move(self, event):
        if platform.system() == "Windows":
            ctypes.windll.user32.ReleaseCapture()
            id_of_window = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.PostMessageW(id_of_window, 0xA1, 2, 0)
        else:
            deltax = event.x - self.root.x
            deltay = event.y - self.root.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.root.state('withdrawn')
        self.root.overrideredirect(False)
        self.root.iconify()

    def on_deiconify(self, event):
        if not self.root.overrideredirect():
            self.root.overrideredirect(True)
            if platform.system() == "Windows":
                self.root.after(10, lambda: show_in_taskbar(self.root))

    def maximize_window(self):
        if self.root.state() == 'zoomed':
            self.root.state('normal')
        else:
            self.root.state('zoomed')

    def close_window(self):
        self.root.destroy()

    def on_enter(self, event, color):
        event.widget.configure(bg=color)

    def leave_enter(self, event):
        event.widget.configure(bg="#343a40")

    def maintain_canvas_width(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=self.canvas.winfo_width())

    def create_process_card(self, name, pid, cpu, memory):
        card = ProcessCard(self.scrollable_frame, name, pid, cpu, memory)
        self.cards[pid] = card
        card.pack(fill="x", pady=4, padx=2)
        self.root.update_idletasks()
        return card

    def update_process_card(self, pid, cpu, memory):
        self.cards[pid].update(cpu, memory)
        self.cards[pid].update_graph(cpu, memory)

    def insert_data(self):
        stats = registry.get_stats()

        total_ram = sum(data["ram"] for data in stats.values())
        total_cpu = sum(data["cpu"] for data in stats.values())
        self.mem_icon.config(text=f"Mem: {total_ram:.1f} MB")
        self.cpu_icon.config(text=f"CPU: {total_cpu:.1f}%")

        for pid, data in stats.items():
            name = data["name"]
            cpu = data["cpu"]
            memory = data["ram"]
            if pid in self.cards:
                self.update_process_card(pid, cpu, memory)
            else:
                self.create_process_card(name, pid, cpu, memory)

        for pid in list(self.cards.keys()):
            if pid not in stats:
                self.cards[pid].destroy()
                del self.cards[pid]

        self.root.after(1000, self.insert_data)

if __name__ == "__main__":
    main_window = tk.Tk()
    app = SystemMonitorGUI(main_window)
    main_window.mainloop()