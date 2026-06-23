import ctypes
import logging
import os
import platform
import re
from datetime import datetime
from pathlib import Path
from tkinter import (Toplevel, Label, Button, Tk, PanedWindow,
                     Frame, Canvas, Scrollbar, Y, Entry,
                     Text, Checkbutton)
from tkinter import font
from tkinter import ttk
import tkinter as tk
# MY FILES
import core.adb_connect as adbc
import core.checks as appchecks
import core.nmap_scan as nmaps
import config.constants as const
import config.paths as paths
from config.state import global_state
from core.process import registry
from concurrent.futures import ThreadPoolExecutor
from ui.widgets.scroll_buttons import Buttons
from ui.settings import SettingsStyle
from ui.tab_control import TabControl
from utils.file_utils import open_file, write_file
from ui.widgets.rounded_panel import draw_rounded, resize_inner
from ui.widgets.dropdown_menu import MenuManager


# SOME CONFIGURE FOR LOGGING
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S',
    force=True
)


if platform.system() == "Windows":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

data = open_file(paths.LANG_FILE_PATH)

now = datetime.now()
json_default_data = {
    "last_entered": f"{now}",
    "connected_ips": {},
    "theme": {},
    "choosen_nmap_ip": [],
    "choosen_port": "5555",
    "choosen_path_for_adb": "",
    "choosen_language": "en",
    "is_live_helper_on": False,
    "is_auto_nmap_on": False,
    "ui_flags": {
        "has_seen_entry_save_hint": False
    }
}    


if not os.path.exists(paths.CONFIG_FILE_PATH):
    write_file(paths.CONFIG_FILE_PATH, json_default_data)
    check_data = json_default_data
else:
    check_data = open_file(paths.CONFIG_FILE_PATH)


if platform.system() == "Windows":
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



class MainApp:
    def __init__(self):
        self.nmap_router = NmapRouter(self)
        self.adb_router = AdbRouter(self)
        self.found_path = check_data["choosen_path_for_adb"]
        self.check_data = check_data

        self.checkbutton_map = {}
        self.check_vars = {}
        self.category_btn = []
        self.my_settings = None
        self._tab_canvas = None
        self._content_frame = None

        self._tabs = {}   # key -> {frame, text_id, bg_tag, lang_key}
        self.load_clicked = 0
        self.test_counter = 0

        self._last_width = 1000
        self._last_height = 700

        # MAIN PANEL
        self.root = Tk()
        self.root.title("AdbEz")
        self.root.geometry("1000x700")
        self.root.minsize(800, 350)

        self.menu_manager = MenuManager(root=self.root)

        self.root.config(background="gray")
        self.root.bind("<Map>", self.on_deiconify)
        self.root.bind("<Button-1>", self.close_menus)
        self.root.overrideredirect(True)
        self.root.config(bg='#1e1e1e')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        style = ttk.Style()
        style.configure("Siyah.TFrame", background="black")
        style.configure(
            "Redbg.TButton", background="red", borderwidth=0, relief="flat"
        )
        # CATCHING SIZE OF THE WINDOW FOR IP MENU
        self.root.bind("<Configure>", self.catch_size)
        # CATCHING ROOT BECAUSE OF THE ENTRY FOCUS SHITS
        self.root.bind("<Button-1>", self._clear_focus, add="+")

        self._build_main_window()
        self.root.update_idletasks()
        grip_canvas_up = Canvas(self.root, width=self.root.winfo_width(), height=2, bg="#ffffff",
                     highlightthickness=0, cursor="size_ns")
        grip_canvas_left = Canvas(self.root, width=2, height=self.root.winfo_height(), bg="#ffffff",
                     highlightthickness=0, cursor="size_we")
        grip_canvas_up.place(relx=0.0, rely=0.01, anchor="sw", x=1, y=-1)
        grip_canvas_left.place(relx=0.0, rely=0.01, anchor="w", x=1, y=(self.root.winfo_height()/2))
        grip_canvas_up.propagate(False)
        grip_canvas_left.propagate(False)

        def start_resize(event, direction):
            direction.start_x = self.root.winfo_x()
            direction.start_y = self.root.winfo_y()
            direction.start_w = self.root.winfo_width()
            direction.start_h = self.root.winfo_height()
            direction.press_x = event.x_root
            direction.press_y = event.y_root

        def do_resize_up(event):
            # dx = event.x_root - grip_canvas_up.press_x
            dy = event.y_root - grip_canvas_up.press_y

            new_y = grip_canvas_up.start_y + dy
            new_h = grip_canvas_up.start_h - dy

            if new_h > 180:
                self.root.update_idletasks()
                self.root.geometry(f"{self.root.winfo_width()}x{new_h}+{self.root.winfo_x()}+{new_y}")
        def do_resize_down(event):
            dx = event.x_root - grip_canvas_left.press_x
            dy = event.y_root - grip_canvas_left.press_y

            new_x = grip_canvas_left.start_x + dx
            new_y = grip_canvas_left.start_y + dy
            new_w = grip_canvas_left.start_w - dx
            new_h = grip_canvas_left.start_h - dy

            if new_w > 250 and new_h > 180:
                self.root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
        def do_resize_left(event):
            dx = event.x_root - grip_canvas_left.press_x
            # dy = event.y_root - grip_canvas_left.press_y

            new_x = grip_canvas_left.start_x + dx
            new_w = grip_canvas_left.start_w - dx

            self.root.update_idletasks()
            if new_w > 250:
                self.root.geometry(f"{new_w}x{self.root.winfo_height()}+{new_x}+{self.root.winfo_y()}")
        def do_resize_right(event):
            dx = event.x_root - grip_canvas_left.press_x
            dy = event.y_root - grip_canvas_up.press_y

            new_x = grip_canvas_up.start_x + dx
            new_y = grip_canvas_up.start_y + dy
            new_w = grip_canvas_up.start_w - dx
            new_h = grip_canvas_up.start_h - dy

            if new_w > 250 and new_h > 180:
                self.root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")

        grip_canvas_up.bind("<Button-1>", lambda event: start_resize(event, grip_canvas_up))
        grip_canvas_left.bind("<Button-1>", lambda event: start_resize(event, grip_canvas_left))
        grip_canvas_up.bind("<B1-Motion>", do_resize_up)
        grip_canvas_left.bind("<B1-Motion>", do_resize_left)

        style = ttk.Style()
        style.configure("Grip.TLabel", font=("Arial", 22), foreground="#666666")
        # DEFINITION
        self.tab_connect = Frame(self._content_frame)
        self.tab_keyevents = Frame(self._content_frame)
        tab_usefull = ttk.Frame(self._content_frame)
        tab_danger = ttk.Frame(self._content_frame)
        tab_everything = ttk.Frame(self._content_frame)
        tab_learn = ttk.Frame(self._content_frame)
        tab_terminal = ttk.Frame(self._content_frame)
        self.tab_settings = Frame(self._content_frame)
        self.tab_connected = Frame(self._content_frame)

        self._tab_defs = [
            ("connect",    data[global_state.current_lang]["l7"],  self.tab_connect,    "l7"),
            ("keyevents",  data[global_state.current_lang]["l8"],  self.tab_keyevents,  "l8"),
            ("usefull",    data[global_state.current_lang]["l9"],  tab_usefull,    "l9"),
            ("danger",     data[global_state.current_lang]["l10"], tab_danger,     "l10"),
            ("everything", data[global_state.current_lang]["l11"], tab_everything, "l11"),
            ("learn",      data[global_state.current_lang]["l12"], tab_learn,      "l12"),
            ("terminal",   data[global_state.current_lang]["l16"], tab_terminal,   "l16"),
            ("settings",   data[global_state.current_lang]["l17"], self.tab_settings,   "l17"),
            ("connected",  data[global_state.current_lang]["l18"], self.tab_connected,  "l18"),
        ]
        self.background_color = const.BG_COLOR
        self._build_tab_connect()
        self._build_tab_keyevents()
        self._build_tab_connected()
        self._bind_events()

        # BLOCKS-----------------------------------------------
        self.root.update_idletasks()
        self.root.after(100, lambda: self.paned_window.sash_place(0, 0, 420))

        # WINDOWS-----------------------
        self.canvas2.bind_all("<MouseWheel>", self._on_mousewheel)
        # ------------------------------
        # LINUX-------------------------
        self.canvas2.bind_all("<Button-4>", self._on_scroll_up)
        self.canvas2.bind_all("<Button-5>", self._on_scroll_down)
        # ------------------------------
        # -----------------------------------------------------

        self.canvas2.bind("<Configure>", self.on_canvas_resize)
        # PLACEMENT CONFIGURATION
        self.upper_frame.rowconfigure(0, weight=0)
        self.upper_frame.rowconfigure(1, weight=1)
        self.upper_frame.rowconfigure(8, weight=0)
        self.upper_frame.columnconfigure(0, weight=1)
        self.upper_frame.columnconfigure(1, weight=0)
        self.upper_frame.columnconfigure(2, weight=1)
        
        self.checks()
        if platform.system() == "Windows":
            show_in_taskbar(self.root)

    def _clear_focus(self, event):
            if not isinstance(event.widget, (Entry, Text)):
                self.root.focus_set()

    def _build_main_window(self):
        # OUTER FRAME
        external_frame = tk.Frame(self.root, bg=const.BORDER_COLOR, bd=0)
        external_frame.pack(fill="both", expand=True)
        # INNER MAIN AREA
        main_area = tk.Frame(external_frame, bg=const.BG_COLOR, bd=0)
        main_area.pack(fill="both", expand=True, padx=1, pady=1)
        # TITLE BAR
        title_bar = tk.Frame(main_area, bg=const.HEADER_BAR_COLOR, height=30)
        title_bar.pack(fill="x")
        if platform.system() == "Windows":
            title_bar.bind("<Button-1>", self.on_move)
        else:
            title_bar.bind("<ButtonPress-1>", self.start_move)
            title_bar.bind("<ButtonRelease-1>", self.stop_move)
            title_bar.bind("<B1-Motion>", self.on_move)
       
        frm = ttk.Frame(main_area, style="Siyah.TFrame", padding=10)
        frm.pack(fill="both", expand=True) 
        # FOR SIZABLE
        sizegrip = ttk.Sizegrip(main_area)
        sizegrip.pack(side="right", anchor="se")

        title_label = Label(title_bar, text="ADBez",
                            bg=const.HEADER_BAR_COLOR, fg="white",
                            font=("Arial", 9))
        title_label.pack(side="left", padx=10)
        self.min_btn = Button(title_bar, text="—", bg=const.HEADER_BAR_COLOR, fg="white", bd=0,
                        activebackground="#404040", activeforeground="white",
                        command=self.minimize_window, width=4, font=("Arial", 9))
        self.min_btn.pack(side="right", fill="y")
        self.min_btn.bind("<Enter>", self.on_enter)
        self.min_btn.bind("<Leave>", self.leave_enter)

        # FULL SCREEN(□)
        self.max_btn = Button(title_bar, text="▢", bg=const.HEADER_BAR_COLOR, fg="white", bd=0,
                        activebackground="#404040", activeforeground="white",
                        command=self.maximize_window, width=4, font=("Arial", 10))
        self.max_btn.pack(side="right", fill="y")
        self.max_btn.bind("<Enter>", self.on_enter)
        self.max_btn.bind("<Leave>", self.leave_enter)

        self.close_btn = Button(title_bar, text="✕", bg=const.HEADER_BAR_COLOR, fg="white", bd=0,
                        activebackground="red", width=4)
        self.close_btn.pack(side="right", fill="y")
        self.close_btn.bind("<Button-1>", self.close_window)
        self.close_btn.bind("<Enter>", self.on_enter)
        self.close_btn.bind("<Leave>", self.leave_enter)
        _tab_bar = Frame(frm, bg="#1e1e1e")
        _tab_bar.pack(fill="x", pady=(0, 4))

        self._content_frame = Frame(frm, bg="#1e1e1e")
        self._content_frame.pack(fill="both", expand=True)

        self._tab_canvas = Canvas(
            _tab_bar, bg="#1e1e1e", height=const.TAB_H, highlightthickness=0)

        _scroll_left = Button(_tab_bar, text="◀", bg="#1e1e1e", fg="white", bd=0,
                            activebackground="#2a2a3a", width=2,
                            command=lambda: self._tab_canvas.xview_scroll(-2, "units"))
        _scroll_left.pack(side="left")

        self._tab_canvas.pack(side="left", fill="x", expand=True)
        self._tab_canvas.bind(
            "<MouseWheel>",
            lambda e: self._tab_canvas.xview_scroll(int(-1*(e.delta/120)), "units")
        )

        _scroll_right = Button(_tab_bar, text="▶", bg="#1e1e1e", fg="white", bd=0,
                            activebackground="#2a2a3a", width=2,
                            command=lambda: self._tab_canvas.xview_scroll(2, "units"))
        _scroll_right.pack(side="left")


    def _build_tab_connect(self):
        # -TAB_CONNECT LAYOUTS

        self.paned_window = PanedWindow(self.tab_connect, orient="vertical", bd=1,
                                relief="sunken", sashwidth=4,
                                sashrelief="sunken", background="black")
        self.paned_window.pack(fill="both", expand=True)
        self.upper_frame = Frame(self.paned_window)
        self.paned_window.add(self.upper_frame, minsize=300)
        lower_frame = Frame(self.paned_window, background="black")
        self.paned_window.add(lower_frame, minsize=50)

        self.canvas_rounded_window = Canvas(
            self.upper_frame,
            bg=self.upper_frame.cget("bg"),
            highlightthickness=0
        )
        self.canvas_rounded_window.grid(row=1, column=1, sticky="nsew", pady=10)
        self.inner_frame = Frame(self.canvas_rounded_window, bg=const.ROUNDED_PANELS_COLOR)
        self.canvas_rounded_window.create_window(
            20, 20,
            anchor="nw",
            window=self.inner_frame,
            tags="inner"
        )
        self.canvas_rounded_window.bind("<Configure>", lambda e: (draw_rounded(self.canvas_rounded_window, e), resize_inner(self.canvas_rounded_window, e)))


        self.connected_devices_ips_panel_borders = Canvas(
            self.upper_frame,
            bg=self.upper_frame.cget("bg"),
            highlightthickness=0
        )
        self.connected_devices_ips_panel_borders.grid(row=1, column=2, sticky="nsew", pady=10)
        self.ips_inner_frame = Frame(self.connected_devices_ips_panel_borders, bg=const.ROUNDED_PANELS_COLOR)
        self.connected_devices_ips_panel_borders.create_window(
            20, 20,
            anchor="nw",
            window=self.ips_inner_frame,
            tags="inner"
        )
        self.connected_devices_ips_panel_borders.bind("<Configure>", lambda e: (draw_rounded(self.connected_devices_ips_panel_borders, e), resize_inner(self.connected_devices_ips_panel_borders, e)))

        # -NMAP INPUT ROW
        self.nmap_input_row = Frame(self.inner_frame)
        self.nmap_input_row.grid(row=0, column=0, sticky="ew", padx=(10))
        self.nmap_input_row.columnconfigure(1, minsize=300)
        self.nmap_input_row.columnconfigure(0, weight=0)
        self.nmap_input_row.columnconfigure(1, weight=1)
        self.nmap_input_row.columnconfigure(2, weight=0)
        # -ADB INPUT ROW
        self.adb_input_row = Frame(self.inner_frame)
        self.adb_btn_container = Frame(self.inner_frame)
        self.adb_btn_container.grid(row=3, column=0, sticky="n")
        self.adb_input_row.grid(row=2, column=0, sticky="ew", padx=(10))

        self.adb_input_row.columnconfigure(0, weight=0)
        self.adb_input_row.columnconfigure(1, weight=1)
        self.adb_input_row.columnconfigure(2, weight=0)
        # -NMAP BUTTON ROW
        self.nmap_btn_container = Frame(self.inner_frame)
        self.nmap_btn_container.grid(row=1, column=0, sticky="n")
        self.nmap_btn_container.columnconfigure(0, weight=0)
        self.nmap_btn_container.columnconfigure(1, weight=0)

        self.ongoing_processes = ttk.Frame(self.upper_frame)
        connected_container = ttk.Frame(self.upper_frame)
        connected_container.grid(row=0, column=2, sticky="ne")

        # NMAP IP MENU
        self.menu_frame = Frame(self.upper_frame, background="red")
        self.menu_frame_in1 = Button(self.menu_frame, text="")
        menu_frame_in2 = Button(self.menu_frame, text="127.0.0.0/24")
        # ADB IP MENU
        self.menu_frame_found,self.menu_frame_found_inner = self.menu_manager.scrollable_menu(
            self.upper_frame, max_height=125)
        self.log_text = Text(lower_frame, height=1)

        # DEFINITION
        self.tab1_label = Label(self.inner_frame, text=self.get_text("l3"), name="l3")
        self.tab1_input = Entry(self.nmap_input_row, font="bold")
        self.tab1_nmap_button = Button(
            self.nmap_btn_container, text=self.get_text("l4"), name="l4"
        )
        self.tab1_label2 = Label(self.inner_frame, text=self.get_text("l5"), name="l5")
        self.tab1_input2 = Entry(self.adb_input_row, font="bold")
        self.tab1_connect_button = Button(
            self.adb_btn_container, text=self.get_text("l6"), name="l6"
        )
        self.tab1_label_failed = Label(self.upper_frame, text="", foreground="red", width=26)
        self.tab1_label_failed2 = Label(self.upper_frame, text="", foreground="red", width=26)
        tab1_disconnect_button = Button(
            self.adb_btn_container, text=self.get_text("l19"), name="l19"
        )
        tab1_disconnect_button.grid(row=1, column=0)
        tab1_disconnect_button.bind("<Button-1>", lambda e: adbc.adb_connect.disconnect_ip(
            self.tab1_input2, self.found_path, check_data, self.connected_devices_ips, self.upper_frame,
            self.root, self.check_btn_ip, self.checkbutton_map
        ))

        processes_lists_text = Label(
            self.ongoing_processes,
            text=self.get_text("l318"), name="l318"
        )
        self.processes_in = Button(self.ongoing_processes)
        processes_lists_text.pack(fill="x")
        connected_devices = Label(
            connected_container, text=self.get_text("l20"), name="l20",
            background="lightgray"
        )

        self.connected_devices_ips = Label(connected_container)
        # is_text_empty = self.connected_devices_ips.cget("text")
        connected_devices.grid(row=0, column=0, sticky="nsew")
        self.connected_devices_ips.grid(row=1, column=0, sticky="nsew")

        

        # I WANT TO USE MENUBUTTON BUT IT CAN'T DO THE FEATURES I WANT
        # SO WE WILL CREATE OUR OWN MENU
        # tab1_choose_ip = ttk.Menubutton(nmap_input_row, text="Choose")
        self.tab1_choose_ip = Button(
            self.nmap_input_row, text=self.get_text("l13"),
            name="l13", takefocus=False, width=10, cursor="hand2"
        )
        self.tab1_found_ip = Button(
            self.adb_input_row, text=self.get_text("l14"), name="l14", takefocus=False,
            cursor="hand2"
        )

        # self.tab1_label.grid(row=0, column=0, sticky="n", pady=(0, 72), padx=(0, 285))
        self.tab1_label.grid(row=0, column=0, sticky="n", pady=(0, 72))
        self.tab1_input.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        self.tab1_choose_ip.grid(row=0, column=2, sticky="we", padx=(15, 0), pady=(0, 10))
        self.tab1_nmap_button.grid(row=0, column=0, sticky="ew")

        # self.tab1_label2.grid(row=2, column=0, sticky="n", pady=(0,62), padx=(0, 295))
        self.tab1_label2.grid(row=2, column=0, sticky="n", pady=(0,62))
        self.tab1_input2.grid(row=0, column=1, sticky="ew")
        self.tab1_found_ip.grid(row=0, column=2, sticky="ew", padx=(15, 0))
        self.tab1_connect_button.grid(row=0, column=0, sticky="ew", padx=(5, 0))
        self.log_text.pack(fill="both", expand=True)

        # STOP NMAP-ADB BUTTON
        self.tab1_stop_nmap = ttk.Button(
            self.nmap_btn_container, text=self.get_text("l15"),
            name="l15", takefocus=False, style="Redbg.TButton"
        )
        self.tab1_stop_adb = ttk.Button(
            self.adb_btn_container, text=self.get_text("l15"),
            name="l15", takefocus=False, style="Redbg.TButton"
        )

        # BUTTON EVENTS-----------------------------------------------
        self.tab1_choose_ip.bind(
            "<Button-1>",
            lambda event: self.menu_manager.toggle_menu(
                event, self.menu_frame, self.tab1_choose_ip, self.tab_connect
            )
        )

        self.tab1_nmap_button.bind("<Button-1>", self.nmap_router.scan)
        self.tab1_connect_button.bind("<Button-1>", self.adb_router.connect)
        self.tab1_found_ip.bind(
            "<Button-1>",
            lambda event: self.menu_manager.toggle_menu(
                event, self.menu_frame_found, self.tab1_found_ip, self.tab_connect
            )
        )
        # nmap ip menu events
        self.menu_frame_in1.bind("<Button-1>", self.enter_choosed_ip)
        menu_frame_in2.bind("<Button-1>", self.enter_choosed_ip)

        # stop nmap button event
        self.tab1_stop_nmap.bind("<Button-1>", self.nmap_router.stop_nmap_event)
        self.tab1_stop_adb.bind("<Button-1>", self.adb_router.stop_adb_event)

        # CATCHING PANED WINDOW EVENT
        self.paned_window.bind("<B1-Motion>", self.changed_paned)

        self.canvas_rounded_window.after(50, resize_inner(self.canvas_rounded_window))


    def _build_tab_keyevents(self):
        # FONT STYLE DEFINITION
        custom_font = font.Font(size=8)
        keyevents_buttons = []
        keyevents_labels = []

        # -TAB_KEYEVENTS LAYOUTS
        self.paned_window2 = PanedWindow(self.tab_keyevents, orient="horizontal", bd=1,
                                    relief="sunken", sashwidth=4,
                                    sashrelief="sunken", bg="black")
        self.upper_frame2 = Frame(self.paned_window2)
        self.paned_window2.add(self.upper_frame2, minsize=500)
        self.paned_window2.pack(fill="both", expand=True, anchor="w", side="left")
        lower_frame2 = Frame(self.paned_window2)
        lower_frame2.grid_columnconfigure(0, weight=1)
        lower_frame2.grid_rowconfigure(0, weight=1)
        lower_frame2.grid_rowconfigure(1, weight=1)
        self.paned_window2.add(lower_frame2, minsize=50)

        lower_frame2_connected_devices = Frame(lower_frame2, bg="red")
        lower_frame2_connected_devices_f = Frame(lower_frame2_connected_devices, bg="blue")
        keyevents_checkframe = Frame(lower_frame2_connected_devices_f, bg="pink")
        lower_frame2_connected_ips = Frame(lower_frame2_connected_devices_f)

        lower_frame2_connected_devices.grid(row=0, column=0)
        lower_frame2_connected_devices_f.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        keyevents_checkframe.grid(row=0, column=0, sticky="ew")
        lower_frame2_connected_ips.grid(row=1, column=0, sticky="nsew")

        # lower_frame2_connected_devices.configure(0, weight=1)
        lower_frame2_connected_devices.rowconfigure(0,minsize=100)
        lower_frame2_connected_devices_f.rowconfigure(0, weight=1)
        lower_frame2_connected_devices_f.columnconfigure(0, weight=1)
        lower_frame2_connected_ips.configure(bg="yellow")
        lower_frame2.config(bg="lightblue")
        """lower_frame2.rowconfigure(2, weight=1)
        lower_frame2.grid_columnconfigure(0, weight=1)"""
        self.paned_window2.paneconfigure(lower_frame2, minsize=1)


        # TAB_KEYEVENTS--------------------------------------
        self.canvas2 = Canvas(self.upper_frame2, bg="gray", highlightthickness=0)
        self.canvas2.pack(side="left", fill="both", expand=True)
        scrollable_bar = Scrollbar(self.upper_frame2, orient="vertical",
                                command=self.canvas2.yview, background="yellow")
        scrollable_bar.pack(fill=Y, side="right", anchor="e")
        self.canvas2.configure(yscrollcommand=scrollable_bar.set)
        self.scrollable_content = Frame(self.canvas2)
        self.canvas_window = self.canvas2.create_window((0, 0), window=self.scrollable_content,
                                            anchor="nw")
        self.scrollable_content.bind("<Configure>", self.on_frame_configure)
        tab2_scroll_button_frame = Frame(self.scrollable_content)
        tab2_scroll_load_frame = Frame(self.scrollable_content, bg="gray")
        up_bar = Frame(self.scrollable_content)
        up_bar.pack(expand=True)
        tab2_scroll_button_frame.pack(fill="x", expand=True)
        tab2_scroll_load_frame.pack(expand=True, fill="x")
        up_bar.columnconfigure(0, weight=1)
        up_bar.columnconfigure(3, weight=1)

        self.connected_container2 = Frame(lower_frame2_connected_devices)
        self.connected_container2.grid(row=0, column=0, sticky="n")

        self.connected_devices2 = Label(
            self.connected_container2, text=self.get_text("l20"), name="l20"
        )
        self.check_btn_ip = Checkbutton(keyevents_checkframe, bg="black")
        self.connected_devices2.grid(row=0, column=0, sticky="nsew")

        # CATEGORY MENU
        menu_frame_category = Frame(self.upper_frame2, background="blue")
        for b in range(const.CATEGORY_COUNT):
            btn_key = f"l{b+310}"
            menu_frame_category_in1 = Button(
                menu_frame_category, text=self.get_text(btn_key),
                name=btn_key, font=custom_font
            )
            menu_frame_category_in1.bind(
                "<Button-1>", lambda event, k=btn_key: self.btn_instance.categorize(k)
            )
            self.category_btn.append(menu_frame_category_in1)

        search = Entry(up_bar)
        search.grid(row=0, column=1)
        self.tab2_category_button = Button(up_bar, text=self.get_text("l309"),
                                    name="l309")
        self.tab2_category_button.bind(
            "<Button-1>",
            lambda event: self.menu_manager.toggle_menu(
                event, menu_frame_category, self.tab2_category_button, self.tab_keyevents
            )
        )
        self.tab2_category_button.grid(row=0, column=2)

        tab2_log_label = Label(
            lower_frame2, text="Logs", background="lightblue"
        )
        tab2_log_label.grid(row=1, column=0)
        tab2_log_box = Text(lower_frame2)
        tab2_log_box.rowconfigure(2, weight=1)
        tab2_log_box.grid(row=2, column=0, rowspan=2, sticky="w", padx=(5, 5))
        tab2_load_more_btn = Button(tab2_scroll_load_frame, text="Load more...")
        tab2_load_more_btn.pack()
        tab2_load_more_btn.bind(
            "<Button-1>",
            lambda e: self.btn_instance.called_test_function()
        )


        self.btn_instance = Buttons(
            tab2_scroll_button_frame,
            self.root,
            tab2_load_more_btn,
            tab2_scroll_load_frame,
            keyevents_buttons,
            keyevents_labels,
            data,
            global_state.current_lang,
            self.background_color,
            self.canvas2,
            up_bar,
            self.get_text,
            search,
            check_data,
            tab2_log_box,
        )

        self.all_menu = [self.menu_frame, self.menu_frame_found, menu_frame_category]
        some_keywords = [self._tab_canvas, self._tabs, self.all_menu, self.btn_instance,
                         self.canvas2, tab2_scroll_button_frame, self._content_frame]

        self.tabcontrol = TabControl(*some_keywords)
        _x = 0
        for _key, _text, _frame, _lk in self._tab_defs:
            self.tabcontrol.make_tab(self._tab_canvas, _x, _key, _text, _frame, _lk)
            _x += const.TAB_W + const.TAB_GAP
        self._tab_canvas.config(scrollregion=(0, 0, _x, const.TAB_H))

    def _build_tab_connected(self):

        self.main_paned = PanedWindow(self.tab_connected, orient="horizontal", bd=1,
                                    relief="sunken", sashwidth=4,
                                    sashrelief="sunken", bg="black")  # OK
        self.main_paned.pack(fill="both", expand=True)
        self.left_paned = PanedWindow(self.main_paned, orient="vertical", bd=1,
                                    relief="sunken", sashwidth=4,
                                    sashrelief="sunken", bg="black")  # OK
        self.right_paned = PanedWindow(self.main_paned, orient="vertical", bd=1,
                                    relief="sunken", sashwidth=4,
                                    sashrelief="sunken", bg="black")  # OK
        self.phone_screen_pnd = PanedWindow(self.main_paned, orient="vertical", bd=1,
                                    relief="sunken", sashwidth=4,
                                    sashrelief="sunken", bg="black")  # OK

        self.files_frm = Frame(self.left_paned, bg="red")
        self.terminal_frm = Frame(self.left_paned, bg="green")

        self.shortcut_frm = Frame(self.main_paned, bg="lightgreen", )
        self.phone_screen_frm = Frame(self.main_paned, bg="black")

        self.device_infos_frm = Frame(self.right_paned, bg="lightgray")
        self.aichat_frm = Frame(self.right_paned, bg="gray")
        
        self.left_paned.add(self.files_frm, minsize=250)
        self.left_paned.add(self.terminal_frm, minsize=250)

        self.phone_screen_pnd.add(self.shortcut_frm, minsize=50)
        self.phone_screen_pnd.add(self.phone_screen_frm, minsize=500)

        
        self.main_paned.add(self.left_paned,minsize=250)
        self.main_paned.add(self.phone_screen_pnd, minsize=250)
        self.main_paned.add(self.right_paned,minsize=250)

        self.right_paned.add(self.device_infos_frm,minsize=150)
        self.right_paned.add(self.aichat_frm,minsize=150)


    def _bind_events(self):
        pass

    def get_text(self, key: str, default: str = ""):
        lang_data = data.get(global_state.current_lang, {})
        item = lang_data.get(key, default)
        if isinstance(item, dict):
            return item.get("text", default)
        return item


    def close_window(self, event):
        pids = list(registry.processes.keys())
        if pids:
            with ThreadPoolExecutor(max_workers=len(pids)) as executor:
                executor.map(registry.remove, pids)

        check_data = open_file(paths.CONFIG_FILE_PATH)
        logging.debug(check_data)
        write_file(paths.CONFIG_FILE_PATH, check_data)
        if hasattr(self.checker, "nmap_brain"):
            self.checker.nmap_brain.stop_nmap()
        self.root.after(100, lambda: self.root.destroy())


    def on_enter(self, event):
        event.widget.configure(bg="lightblue")

    def leave_enter(self, event):
        event.widget.configure(bg=const.HEADER_BAR_COLOR)

    def catch_size(self, event):
        if event.widget == self.root:
            if self.root.winfo_width() != self._last_width or self.root.winfo_height() != self._last_height:
                geo = self.root.winfo_geometry()
                match = re.search(r'(\d+)x(\d+)', geo)

                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    logging.debug(f"x: {x}, y: {y}")
                for m in self.all_menu:
                    if m.winfo_viewable() and m.winfo_exists():
                        m.place_forget()
                        logging.debug(f"{m} is deleted")
                    else:
                        logging.debug(f"{m} is null")
                if event.height > 600:
                    logging.info(event.height)
                    self.paned_window.paneconfigure(self.upper_frame, minsize=350, height=550)
                    logging.info("Minsize updated")
                if x > 1300:
                    self.paned_window2.paneconfigure(self.upper_frame2, minsize=900)
                else:
                    self.paned_window2.paneconfigure(self.upper_frame2, minsize=700)

    # FOR EXPAND WINDOW
    def on_canvas_resize(self, event):
        logging.debug("ON_CANVAS_RESİZE")
        self.canvas2.itemconfig(self.canvas_window, width=event.width)


    def update_all_widgets(self, lang_code: str):
        logging.debug("UPDATE_ALL_WIDGETS")
        global_state.current_lang = lang_code
        check_data = open_file(paths.CONFIG_FILE_PATH)

        check_data["choosen_language"] = lang_code
        write_file(paths.CONFIG_FILE_PATH, check_data)

        if self.my_settings is not None:
            self.my_settings.current_lang = lang_code
        new_texts = data[lang_code]
        self.btn_instance.current_lang = lang_code 
        self.btn_instance.load_again()

        for info in self._tabs.values():
            lk = info["lang_key"]
            if lk in new_texts:
                self._tab_canvas.itemconfig(info["text_id"], text=new_texts[lk]["text"])

        try:
            default_path = os.path.dirname(os.path.abspath(__file__))
            file_path2 = os.path.join(default_path, "lang.json")
            full_data = open_file(file_path2)

            logging.debug(f"LANG: {lang_code} {type(lang_code)} ")

            def recursive_update(container):
                for widget in container.winfo_children():
                    w_name = str(widget).split('.')[-1]
                    if w_name in full_data.get(lang_code, {}):
                        selected_texts = full_data[lang_code][w_name]["text"]
                        try:
                            widget.config(text=selected_texts)
                        except Exception as e:
                            logging.error("An error occurred while updating widget: %s", e)

                    if widget.winfo_children():
                        recursive_update(widget)

                    if widget == self.my_settings.row_label2:
                        widget.config(text=f"{self.get_text('l326')} {self.found_path}")


            recursive_update(self.root)
            self.root.update_idletasks()

            if self.my_settings is not None:
                self.my_settings._toggle(self.my_settings.dark_theme_btn, self.my_settings.var)
                self.my_settings._toggle(self.my_settings.choose_auto_nmap_btn, self.my_settings.auto_nmap_var)
                self.my_settings._toggle_live_helper(self.my_settings.live_helper_button, self.my_settings.live_helper_var)
            logging.info(f"Language changed to: {lang_code}")
        except Exception as e:
            logging.exception("Language update error: %s", e)


    def update_ui(self, output: str):
        logging.debug("UPDATE UI")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"\n {output}")
        self.log_text.see("end")
        self.log_text.config(state="disabled")


    def checks(self):
        self.checker = appchecks.StartupCheck()
        self.my_settings = SettingsStyle(
            app=self,
            check_data=self.check_data,
            data=data,
            update_func=self.update_path,
            auto_finder_func=self.checker.try_find_adb
        )
        self.checker.app_startup(
            self.connected_devices_ips, global_state.current_lang, data, check_data,
            self.check_btn_ip, self, self.my_settings,
            update_lang_func=self.update_all_widgets)

        self.root.after(2000, self._update_ip_label)

    def _update_ip_label(self):
        if hasattr(self.checker, "ip"):
            self.menu_frame_in1.config(text=self.checker.ip)
        else:
            self.root.after(2000, self._update_ip_label)


    def update_path(self, new_path: str):
        self.found_path = new_path
        logging.debug(f"[update_path]FOUND PATH ISSSSSSSSSSSSS= {self.found_path}")
        check_data["choosen_path_for_adb"] = self.found_path
        write_file(paths.CONFIG_FILE_PATH, check_data)


    def start_move(self, event):
        logging.debug("START_MOVE")
        self.root.x = event.x
        self.root.y = event.y


    def stop_move(self, event):
        logging.debug("STOP_MOVE")
        self.root.x = None
        self.root.y = None


    def on_move(self, event):
        if platform.system() == "Windows":
            self.root.unbind("<Configure>")
            ctypes.windll.user32.ReleaseCapture()
            id_of_window = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.PostMessageW(id_of_window, 0xA1, 2, 0)
            self.root.bind("<Configure>", self.catch_size)
            self.root.update()
        else:
            deltax = event.x - self.root.x
            deltay = event.y - self.root.y
            min_x = 0
            max_x = self.root.winfo_screenwidth() - self.root.winfo_width()
            # max_y = self.root.winfo_screenheight() - self.root.winfo_height()
            new_x = self.root.winfo_x() + deltax
            new_y = self.root.winfo_y() + deltay
            x = max(min_x, min(new_x, max_x))
            y = max(min_x, min(new_y, max_x))
            self.root.geometry(f"+{x}+{y}")


    def changed_paned(self, event):
        if self.menu_frame.winfo_viewable() and self.menu_frame.winfo_exists():
            self.menu_frame.place_forget()
            logging.debug("menu_frame is deleted")
        else:
            pass
        if self.menu_frame_found.winfo_viewable() and self.menu_frame_found.winfo_exists():
            self.menu_frame_found.place_forget()
            logging.debug("menu_frame_found is deleted")


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


    # FOR SCROLLING
    def on_frame_configure(self, event):
        logging.debug("ON_FRAME_CONFIGURE")
        self.canvas2.configure(scrollregion=self.canvas2.bbox("all"))


    def _on_mousewheel(self, event):
        # Windows and MacOS
        self.canvas2.yview_scroll(int(-1*(event.delta/120)), "units")


    # FOR LINUX
    def _on_scroll_up(self, event):
        self.canvas2.yview_scroll(-1, "units")


    def _on_scroll_down(self, event):
        self.canvas2.yview_scroll(1, "units")


    def close_menus(self, event):
        dont_close = [self.tab1_choose_ip, self.tab1_found_ip, self.tab2_category_button, self.my_settings.lang_button]
        if event.widget in dont_close or isinstance(event.widget, Scrollbar):
            return
        for menus in self.all_menu:
            if menus.winfo_viewable() and menus.winfo_exists():
                logging.debug("All menus are closing")
                menus.place_forget()


    # IP MENU EVENTS
    def enter_choosed_ip(self, event):
        clicked_button = event.widget
        clicked_button_label = clicked_button.cget("text")
        logging.info(f"Pressed {clicked_button_label}")
        if self.menu_frame.winfo_exists() and self.menu_frame.winfo_viewable():
            self.menu_frame.place_forget()
            self.tab1_input.delete(0, "end")
            self.tab1_input.insert(0, clicked_button_label)

    # ADB MENU EVENTS
    def found_enter_choosen_ip(self, event, ip: str):
        logging.info(f"Pressed {ip}")
        if self.menu_frame_found.winfo_exists() and self.menu_frame_found.winfo_viewable():
            self.tab1_input2.delete(0, "end")
            self.tab1_input2.insert(0, ip + ":" + check_data["choosen_port"])

    def check_event(self, text):
        var = self.check_vars.get(text)
        if var is None:
            return
        if var.get() == 1:
            logging.debug(f"Choosen {text}")
            if text not in global_state.choosen_ips:
                global_state.choosen_ips.append(text)

            write_file(paths.CONFIG_FILE_PATH, self.check_data)
        else:
            for ip in global_state.choosen_ips:
                if text == ip:
                    global_state.choosen_ips.remove(ip)

            write_file(paths.CONFIG_FILE_PATH, self.check_data)
            logging.debug("Not choosen")

        


class AdbRouter:
    def __init__(self, app):
        self.app = app
        # TO ACCESS THE FUNCTIONS WITHIN THE CLASS-
        self.active_adb = None


    def connect(self, event):
        instance = adbc.adb_connect(
            self.app,
            on_finish=lambda inst: global_state.active_adb_list.remove(inst) if inst in global_state.active_adb_list else None
        )
        global_state.active_adb_list.append(instance)

    def stop_adb_event(self, event):
        if global_state.active_adb_list:
            global_state.active_adb_list[0].stop_adb()


class NmapRouter:
    def __init__(self, app):
        self.app = app
        self.active_nmap = None

    def scan(self, event=None):
        instance = nmaps.NmapUi(
            self.app,
            on_finish=lambda inst: global_state.active_nmap_list.remove(inst)
                      if inst in global_state.active_nmap_list else None
        )
        global_state.active_nmap_list.append(instance)


    def stop_nmap_event(self, event):
        logging.debug(f"active_nmap_list= {global_state.active_nmap_list}")
        if global_state.active_nmap_list:
            global_state.active_nmap_list[-1].stop_nmap_ui()


if __name__ == "__main__":
    app = MainApp()
    app.root.mainloop()
