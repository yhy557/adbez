import tkinter as tk
import logging
from core.process import registry

# SOME CONFIGURE FOR LOGGING
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S',
    force=True
)

class ProcessCard(tk.Frame):
    def __init__(self, parent, pid, cpu, memory):
        super().__init__(parent, bg="#ffffff", highlightbackground="#e9ecef", highlightthickness=1)
        self.is_expanded = False
        self.target_height = 100
        self.current_height = 0
        
        self.main_row = tk.Frame(self, bg="#ffffff", height=50)
        self.main_row.pack(fill="x", side="top")
        self.main_row.pack_propagate(False)
        
        for i in range(7):
            self.main_row.columnconfigure(i, weight=1, uniform="col")
            
        """self.lbl_name = tk.Label(self.main_row, text=name, font=("Segoe UI", 10, "bold"), fg="#212529", bg="#ffffff", anchor="w")
        self.lbl_name.grid(row=0, column=0, sticky="ew", padx=15, pady=13)"""
        
        self.lbl_pid = tk.Label(self.main_row, text=str(pid), font=("Segoe UI", 10), fg="#495057", bg="#ffffff", anchor="w")
        self.lbl_pid.grid(row=0, column=1, sticky="ew", padx=15, pady=13)

        
        self.lbl_cpu = tk.Label(self.main_row, text=str(cpu), font=("Segoe UI", 10, "bold"), fg="#fd7e14", bg="#ffffff", anchor="w")
        self.lbl_cpu.grid(row=0, column=3, sticky="ew", padx=15, pady=13)
        
        self.lbl_mem = tk.Label(self.main_row, text=memory, font=("Segoe UI", 10), fg="#495057", bg="#ffffff", anchor="w")
        self.lbl_mem.grid(row=0, column=4, sticky="ew", padx=15, pady=13)
        
        """self.lbl_disk = tk.Label(self.main_row, text=disk, font=("Segoe UI", 10), fg="#495057", bg="#ffffff", anchor="w")
        self.lbl_disk.grid(row=0, column=5, sticky="ew", padx=15, pady=13)"""
        
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
            self.animate_collapse()
        else:
            self.animate_expand()
            
    def animate_expand(self):
        if self.current_height < self.target_height:
            self.current_height += 10
            self.detail_frame.configure(height=self.current_height)
            self.after(15, self.animate_expand)
        else:
            self.is_expanded = True
            
    def animate_collapse(self):
        if self.current_height > 0:
            self.current_height -= 10
            self.detail_frame.configure(height=self.current_height)
            self.after(15, self.animate_collapse)
        else:
            self.is_expanded = False

    def update(self, cpu, memory):
        self.lbl_cpu.config(text=str(cpu))
        self.lbl_mem.config(text=str(memory))


class SystemMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")
        self.root.geometry("650x450")
        self.root.configure(bg="#f8f9fa")

        self.cards = {}
        
        self.top_bar = tk.Frame(self.root, bg="#f8f9fa", height=30)
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
        
        self.search_bar = tk.Frame(self.root, bg="#f8f9fa", height=30)
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
        
        self.cpu_icon = tk.Label(self.stats_frame, text="⚙ CPU: 100.0%", font=("Segoe UI", 10, "bold"), fg="#212529", bg="#f8f9fa")
        self.cpu_icon.pack(side="left", padx=15)
        
        self.mem_icon = tk.Label(self.stats_frame, text="💾 Mem: 6.8 GB", font=("Segoe UI", 10, "bold"), fg="#212529", bg="#f8f9fa")
        self.mem_icon.pack(side="left", padx=15)
        
        self.table_header = tk.Frame(self.root, bg="#f8f9fa", height=30)
        self.table_header.pack(fill="x", side="top", padx=20, pady=(15, 5))
        
        """headers = ["PROCESS NAME", "PID", "USER", "% CPU ↓", "MEMORY", "DISK", "NETWORK"]"""
        headers = ["PID", "% CPU ↓", "MEMORY"]
        for i, name in enumerate(headers):
            self.table_header.columnconfigure(i, weight=1, uniform="col")
            lbl = tk.Label(self.table_header, text=name, font=("Segoe UI", 9, "bold"), fg="#6c757d", bg="#f8f9fa", anchor="w")
            lbl.grid(row=0, column=i, sticky="ew", padx=15)
            
        self.container = tk.Frame(self.root, bg="#f8f9fa")
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
        
        self.bottom_bar = tk.Frame(self.root, bg="#f1f3f5", height=35)
        self.bottom_bar.pack(fill="x", side="bottom")
        
        """self.lbl_proc_count = tk.Label(self.bottom_bar, text="11 Processes", font=("Segoe UI", 9), fg="#495057", bg="#f1f3f5")
        self.lbl_proc_count.pack(side="left", padx=20, pady=8)
        
        IT WILL NEEDS TO CHANGE self.lbl_threads = tk.Label(self.bottom_bar, text="", font=("Segoe UI", 9), fg="#495057", bg="#f1f3f5")
        self.lbl_threads.pack(side="right", padx=20, pady=8)
        
        self.lbl_uptime = tk.Label(self.bottom_bar, text="Uptime: 4 days, 12:45:00", font=("Segoe UI", 9), fg="#495057", bg="#f1f3f5")
        self.lbl_uptime.pack(side="right", padx=20, pady=8)"""
        
        self.root.after(1000, self.insert_data)

    def maintain_canvas_width(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=self.canvas.winfo_width())

    def create_process_card(self, pid, cpu, memory):
        card = ProcessCard(self.scrollable_frame, pid, cpu, memory)
        self.cards[pid] = card
        card.pack(fill="x", pady=4, padx=2)
        self.root.update_idletasks()
        return card
    
    def update_process_card(self, pid, cpu, memory):
        self.cards[pid].update(cpu, memory)

    def insert_data(self):
        stats = registry.get_stats()

        for pid, data in stats.items():
            cpu = data["cpu"]
            memory = data["ram"]
            if pid in self.cards:
                self.update_process_card(pid, cpu, memory)
            else:
                self.create_process_card(pid, cpu, memory)
        for pid  in list(self.cards.keys()):
            if pid not in stats:
                self.cards[pid].destroy()
                del self.cards[pid]

        self.root.after(1000, self.insert_data)


if __name__ == "__main__":
    main_window = tk.Tk()
    app = SystemMonitorGUI(main_window)
    main_window.mainloop()