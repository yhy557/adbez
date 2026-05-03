from tkinter import (Toplevel, Label, Button, Tk, PanedWindow,
                     Frame, Canvas, Scrollbar, Y, Entry,
                     Text, Checkbutton, IntVar, Variable,
                     filedialog, )
from tkinter import font
from tkinter import ttk
import json
import platform
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bcopy import MainApp

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)

S_BG = "#F0F2F5"
CARD = "#FFFFFF"
BORDER = "#D1D5DB"
HEADER_BG = "#E8EAED"
FG = "#111827"
FG_MUTED = "#6B7280"
ACCENT = "#2563EB"
BTN_BG = "#2563EB"
BTN_FG = "#FFFFFF"
BTN_ACT = "#1D4ED8"


class settings_style:
    def __init__(self, app: 'MainApp', check_data, data, update_func, auto_finder_func):
        from nmap_scan import nmap_brain

        self.app = app
        self.check_data = check_data
        self.data = data

        self.tab_connect = self.app.tab_connect
        self.tab_settings = self.app.tab_settings
        self.paned_window = self.app.paned_window
        self.upper_frame = self.app.upper_frame
        self.nmap_input_row = self.app.nmap_input_row
        self.adb_input_row = self.app.adb_input_row
        self.adb_btn_container = self.app.adb_btn_container
        self.tab1_label = self.app.tab1_label
        self.tab1_label2 = self.app.tab1_label2
        self.log_text = self.app.log_text
        self.tab1_input = self.app.tab1_input
        self.tab1_input2 = self.app.tab1_input2
        self.tab1_nmap_button = self.app.tab1_nmap_button
        self.tab1_connect_button = self.app.tab1_connect_button
        self.root = self.app.root
        self.nmap_btn_container = self.app.nmap_btn_container
        self.current_lang = self.app.current_lang
        self.min_btn, self.max_btn, self.close_btn = self.app.min_btn, self.app.max_btn, self.app.close_btn
        self.found_path = self.app.found_path
        self.scrollable_content = self.app.scrollable_content
        self.update_func = update_func
        self.auto_finder_func = auto_finder_func
        self.get_text = self.app.get_text

        default_path = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(default_path, "check.json")

        self.var = IntVar()
        self.live_helper_var = IntVar()
        self.var.trace_add("write", self.check_dark_theme_btn)

        self.auto_nmap_var = IntVar()
        self.auto_nmap_var.trace_add("write", self.start_auto_nmap)

        self.tab_settings.config(bg=S_BG)
        self.canvas = Canvas(self.tab_settings, bg=S_BG, highlightthickness=0)
        self.scrollbar = Scrollbar(self.tab_settings, orient="vertical", command=self.canvas.yview)

        self.settings_container = Frame(self.canvas, bg=S_BG)

        self.settings_style_frame = Frame(self.settings_container, bg=S_BG)
        self.settings_main_frame = Frame(self.settings_container, bg=S_BG)

        self.settings_style_frame.pack(fill="both")
        self.settings_main_frame.pack(fill="both")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.settings_container, anchor="nw")

        self.settings_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.settings_container.bind("<MouseWheel>", self._on_mousewheel)

        # ── Card: body ───────────────────────────────────────────
        self.style_body = self.make_card(
            self.settings_style_frame,
            self.get_text("l319"), "l319"
        )

        row1 = Frame(self.style_body, bg=CARD)
        row1.pack(fill="x", pady=4)
        Label(row1, text="Dark Mode", font=FONT_BOLD,
              bg=CARD, fg=FG, width=20, anchor="w").pack(side="left")
        Label(
            row1, text=self.get_text("l322"),
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, name="l322").pack(side="left", padx=(0, 20))
        dark_theme_btn = Button(
            row1,
            text=self.get_text("l324") if self.var.get() == 1 else self.get_text("l323"),
            name="l324" if self.var.get() == 1 else "l323",
            font=FONT_BOLD,
            bg=ACCENT if self.var.get() == 1 else "#D1D5DB",
            fg="white" if self.var.get() == 1 else FG,
            activebackground=BTN_ACT,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=5,
            bd=0,
            width=10,
            command=lambda: [
                self.var.set(0 if self.var.get() == 1 else 1),
                self._toggle(dark_theme_btn, self.var)
            ]
        )
        dark_theme_btn.pack(side="right")
        dark_theme_btn.bind()

        # ── Card: ADB ─────────────────────────────────────────────────
        self.body = self.make_card(
            self.settings_main_frame,
            self.get_text("l320"), "l320"
        )
        self.auto_nmap_body = self.make_card(
            self.settings_main_frame,
            self.get_text("l333"), "l333"
        )

        self.row2 = Frame(self.body, bg=CARD)
        self.background_processF = Frame(self.body, bg=CARD)
        self.auto_nmapF = Frame(self.auto_nmap_body, bg=CARD)

        self.row2.pack(fill="x", pady=4)
        self.background_processF.pack(fill="x", pady=4)
        self.auto_nmapF.pack(fill="x", pady=4)

        self.row_label1 = Label(
            self.row2, text=self.get_text("l325"), font=FONT_BOLD,
            bg=CARD, fg=FG, width=20, anchor="w", name="l325"
        )
        self.root.update_idletasks()
        self.row_label2 = Label(
            self.row2, text=f"{self.get_text("l326")} {str(self.found_path)}",
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, wraplength=300,
            name="l326"
        )
        self.background_processL_main = Label(
            self.background_processF, text=self.get_text("l335"), font=FONT_BOLD, 
            bg=CARD, fg=FG, width=20, anchor="w", name="l335"
        )
        self.background_processL_inner = Label(
            self.background_processF, text=(self.get_text("l336")),
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, wraplength=300,
            name="l336"
        )
        self.auto_nmapL_main = Label(
            self.auto_nmapF, text=self.get_text("l334"), font=FONT_BOLD, 
            bg=CARD, fg=FG, width=20, anchor="w", name="l334"
        )
        self.auto_nmapL_inner = Label(
            self.auto_nmapF, text=(self.get_text("l332")),
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, wraplength=300,
            name="l332"
        )

        self.row_label1.pack(side="left")
        self.row_label2.pack(side="left", padx=(0, 20))
        self.background_processL_main.pack(side="left")
        self.background_processL_inner.pack(side="left", padx=(0, 20))
        self.auto_nmapL_main.pack(side="left")
        self.auto_nmapL_inner.pack(side="left", padx=(0,20))

        choose_path_btn = Button(
            self.row2,
            text=self.get_text("l328"),
            name="l328",
            font=FONT,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_ACT,
            activeforeground=BTN_FG,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            bd=0
        )
        choose_path_auto_finder = Button(
            self.row2,
            text=self.get_text("l327"),
            name="l327",
            font=FONT,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_ACT,
            activeforeground=BTN_FG,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            bd=0
        )
        self.choose_auto_nmap_btn = Button(
            self.auto_nmapF,
            text=self.get_text("l324") if self.auto_nmap_var.get() == 1 else self.get_text("l323"),
            name="l324" if self.auto_nmap_var.get() == 1 else "l323",
            font=FONT_BOLD,
            bg=ACCENT if self.auto_nmap_var.get() == 1 else "#D1D5DB",
            fg="white" if self.auto_nmap_var.get() == 1 else FG,
            activebackground=BTN_ACT,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=5,
            bd=0,
            width=10,
            command=lambda: [
                self.auto_nmap_var.set(0 if self.auto_nmap_var.get() == 1 else 1),
                self._toggle(self.choose_auto_nmap_btn, self.auto_nmap_var)
            ]
        )
        self.choose_auto_nmap_ip = Entry(
            self.auto_nmapF
        )
        self.choose_auto_nmap_ip.bind("<Return>", self.get_nmap_ip)
        choose_path_btn.pack(side="right")
        choose_path_auto_finder.pack(side="right")
        self.choose_auto_nmap_btn.pack(side="right")
        choose_path_btn.bind("<Button-1>", self.choose_path)
        choose_path_auto_finder.bind("<Button-1>", self.auto_finder_adb)

        self.live_helper = self.make_card(
            self.settings_main_frame,
            self.get_text("l329"), "l329"
        )
        self.row3 = Frame(self.live_helper, bg=CARD)
        self.row3.pack(fill="x", pady=4)
        self.row_label3 = Label(
            self.row3, text="Live Helper",
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, wraplength=300,
            name="l329"
        )
        self.row_label3.pack(side="left")
        self.live_helper_button = Button(
            self.row3,
            text=self.get_text("l324") if self.live_helper_var.get() == 1 else self.get_text("l323"),
            name="l324" if self.live_helper_var.get() == 1 else "l323",
            font=FONT_BOLD,
            bg=ACCENT if self.live_helper_var.get() == 1 else "#CB2314",
            fg="white" if self.live_helper_var.get() == 1 else FG,
            activebackground=BTN_ACT,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=5,
            bd=0,
            width=10,
            command=lambda: [
                self.live_helper_var.set(0 if self.live_helper_var.get() == 1 else 1),
                self._toggle_live_helper(self.live_helper_button, self.live_helper_var)
            ]
        )
        self.live_helper_button.pack(side="right")

        self.adb_configurations = self.make_card(
            self.settings_main_frame,
            self.get_text("l330"), "l330"
        )
        self.row4 = Frame(self.adb_configurations, bg=CARD)
        self.row4.pack(fill="x", pady=4)
        self.row_label4 = Label(
            self.row4, text="Change the default port for ADB Connect",
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, wraplength=300,
            name="l331"
        )
        self.row_label4.pack(side="left")
        self.change_port_input = Entry(
            self.row4,
        )
        self.change_port_input.pack(side="right")
        self.change_port_input.delete(0, "end")
        self.change_port_input.insert(0, str(check_data["choosen_port"]))
        self.change_port_input.bind('<Return>', self.change_port_func)

        if check_data["theme"] == "dark":
            self.var.set(1)
        else:
            self.var.set(0)

        if check_data["is_auto_nmap_on"] == False:
            self.auto_nmap_var.set(0)
            if self.choose_auto_nmap_ip.winfo_viewable():
                self.choose_auto_nmap_ip.pack_forget()
            else:
                pass
        else:
            self.auto_nmap_var.set(1)
            if self.choose_auto_nmap_ip.winfo_viewable():
                pass
            else:
                self.choose_auto_nmap_ip.pack(side="right")


    @property
    def is_dark(self):
        return self.check_data["theme"] == "dark"

    @property
    def is_white(self):
        return self.check_data["theme"] == "white"
    
    def change_port_func(self, event):
        self.check_data["choosen_port"] = self.change_port_input.get()
        with open(self.file_path, "w") as f:
            json.dump(self.check_data, f, indent=4, ensure_ascii=False)

    def make_card(self, parent, title, name):
        outer = Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="x", padx=16, pady=(0, 8))

        header = Frame(outer, bg="#1E1E2E", padx=14, pady=8)
        header.pack(fill="x")
        title_label = Label(
            header, text=title, font=FONT_BOLD,
            bg="#1E1E2E", fg=ACCENT, name=name
        )
        title_label.pack(side="left")

        body = Frame(outer, bg=CARD, padx=14, pady=12)
        body.pack(fill="x")
        return body
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def choose_path(self, event):
        self.root.update_idletasks()
        logging.info("[choose_path]-clicked")
        choosen_path = filedialog.askopenfilename()
        if choosen_path:
            self.update_func(choosen_path)
            self.row_label2.configure(text=f"{self.get_text("l326")} {choosen_path}")

    def get_nmap_ip(self, event):
        self.choose_auto_nmap_ip.configure(bg="lightgreen")
        self.root.after(1000, lambda: self.choose_auto_nmap_ip.configure(bg="white"))
        logging.debug(f"auto_nmap_ip: {self.choose_auto_nmap_ip.get()}")
        self.check_data["choosen_nmap_ip"] = self.choose_auto_nmap_ip.get()
        try:
            logging.debug("")
            with open(self.file_path, "w") as g:
                json.dump(self.check_data, g, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.debug(f"LOOK MTF {e}")


    def auto_finder_adb(self, event):
        self.auto_finder_func()
        adb_path = self.check_data["choosen_path_for_adb"]
        self.root.after(
            1000, lambda: self.row_label2.configure(text=f"{self.get_text("l326")} {adb_path}")
        )

    def check_dark_theme_btn(self, *args):
        if self.var.get() == 1:
            print("[check_Dark_theme_btn]-Choosen")
            self.check_data["theme"] = "dark"
            self.choose_theme("#292423", "white")
            self.choose_theme_special()
        else:
            self.check_data["theme"] = "white"
            self.choose_theme("SystemButtonFace", "black")
            self.choose_themeW("SystemButtonFace")
            print("the election was canceled")
        with open(self.file_path, "w", encoding="utf-8") as fi:
            json.dump(self.check_data, fi, indent=4, ensure_ascii=False)

    def check_live_helper_is_on(self, *args):
        if self.live_helper_var.get() == 1:
            print("[check_live_helper_is_on] - Choosen")
            self.check["is_live_helper_on"] = True
        else:
            self.check["is_live_helper_on"] = False
        with open("check.json", "w", encoding="utf-8") as le:
            json.dump(self.check_data, le, indent=4, ensure_ascii=False)

    def start_auto_nmap(self, *args):
        if self.auto_nmap_var.get() == 1:
            self.check_data["is_auto_nmap_on"] = True
            if self.choose_auto_nmap_ip.winfo_viewable():
                pass
            else:
                self.choose_auto_nmap_ip.pack(side="right")
            logging.debug("PRESSED AUTO NMAP BUTTON OPENED")
        else:
            self.check_data["is_auto_nmap_on"] = False
            if self.choose_auto_nmap_ip.winfo_viewable():
                self.choose_auto_nmap_ip.pack_forget()
            else:
                pass
            logging.debug("PRESSED AUTO NMAP BUTTON CLOSED")
        with open(self.file_path, "w") as v:
            json.dump(self.check_data, v, indent=4, ensure_ascii=False)

    def _toggle(self, btn, var):
        if var.get() == 1:
            btn.config(text=self.get_text("l324"), bg=ACCENT, fg="white", relief="flat")
        else:
            btn.config(text=self.get_text("l323"), bg="#D1D5DB", fg=FG, relief="flat")
    def _toggle_live_helper(self, btn, var):
        if var.get() == 1:
            btn.config(text=self.get_text("l324"), bg="#31AD12", fg="white", relief="flat")
        else:
            btn.config(text=self.get_text("l323"), bg="#CB2314", fg=FG, relief="flat")

    def apply_button_style(self, container):
        for widget in container.winfo_children():
            if isinstance(widget, Button) and self.is_dark:
                if widget in [self.max_btn, self.close_btn, self.min_btn]:
                    pass
                else:
                    widget.configure(
                        bg="#2D2D2D", fg="#E0E0E0", activebackground="#3D3D3D"
                    )
            elif isinstance(widget, Button) and self.is_white:
                if widget in [self.max_btn, self.close_btn, self.min_btn]:
                    pass
                else:
                    widget.configure(
                        bg="SystemButtonFace", fg="black",
                        activebackground="#3D3D3D"
                    )
            if widget.winfo_children():
                self.apply_button_style(widget)
            elif isinstance(widget, ttk.Button):
                style_name = str(widget) + ".TButton"
                s = ttk.Style()
                if self.check_data["theme"] == "dark":
                    s.configure(
                        style_name, background="#2D2D2D", foreground="black"
                    )
                else:
                    s.configure(
                        style_name,
                        background="SystemButtonFace", foreground="black"
                    )
                widget.configure(style=style_name)

    def apply_frame_style(self, container):
        frames = [self.settings_main_frame, self.settings_style_frame]
        for widget in container.winfo_children():
            if isinstance(widget, Frame) and self.is_dark:
                if widget in frames:
                    widget.configure(bg="#292423")
                else:
                    widget.configure(bg="gray")
            elif isinstance(widget, Frame) and self.is_white:
                widget.configure(bg="SystemButtonFace")
        if self.check_data["theme"] == "dark":
            self.style_body.configure(bg="gray")
            self.body.configure(bg="gray")
        else:
            self.style_body.configure(bg=CARD)
            self.body.configure(bg=CARD)

    def choose_theme(self, color, fg_color):
        self.tab_connect.config(bg=color)
        self.tab_settings.config(bg=color)
        self.settings_style_frame.config(bg=color)
        self.settings_main_frame.config(bg=color)
        self.paned_window.config(bg="white")
        self.upper_frame.config(bg=color)
        self.nmap_input_row.config(bg=color)
        self.adb_input_row.config(bg=color)
        self.adb_btn_container.config(bg=color)
        self.nmap_btn_container.configure(bg=color)
        self.tab1_label.config(bg=color, fg=fg_color)
        self.tab1_label2.config(bg=color, fg=fg_color)
        self.log_text.configure(bg=color, fg=fg_color)
        self.settings_main_frame.config(bg=color)
        self.settings_style_frame.config(bg=color)
        self.scrollable_content.config(bg=color)
        self.apply_button_style(self.root)
        self.apply_frame_style(self.tab_settings)

    def choose_themeW(self, color):
        self.paned_window.config(bg="black")
        self.tab1_label.config(bg=color, fg="black")
        self.tab1_label2.config(bg=color, fg="black")
        self.tab1_input.config(bg=color)
        self.tab1_input2.config(bg=color)

    def choose_theme_special(self):
        self.tab1_input.config(bg="gray")
        self.tab1_input2.config(bg="gray")
