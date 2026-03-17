from tkinter import (Toplevel, Label, Button, Tk, PanedWindow,
                     Frame, Canvas, Scrollbar, Y, Entry,
                     Text, Checkbutton, IntVar, Variable,
                     filedialog, )
from tkinter import font
from tkinter import ttk
import json
import platform
import logging

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
    def __init__(self, check_data, tab_connect, tab_settings,
                 paned_window, upper_frame, nmap_input_row, adb_input_row,
                 adb_btn_container, tab1_label, tab1_label2, log_text,
                 tab1_input, tab1_input2, tab1_nmap_button,
                 tab1_connect_button, root, nmap_btn_container, data,
                 current_lang, min_btn, max_btn, close_btn, found_path,
                 scrollable_content,
                 update_func, auto_finder_func):
        self.tab_connect = tab_connect
        self.tab_settings = tab_settings
        self.paned_window = paned_window
        self.upper_frame = upper_frame
        self.nmap_input_row = nmap_input_row
        self.adb_input_row = adb_input_row
        self.adb_btn_container = adb_btn_container
        self.tab1_label = tab1_label
        self.tab1_label2 = tab1_label2
        self.check_data = check_data
        self.log_text = log_text
        self.tab1_input = tab1_input
        self.tab1_input2 = tab1_input2
        self.tab1_nmap_button = tab1_nmap_button
        self.tab1_connect_button = tab1_connect_button
        self.root = root
        self.nmap_btn_container = nmap_btn_container
        self.data = data
        self.current_lang = current_lang
        self.min_btn, self.max_btn, self.close_btn = min_btn, max_btn, close_btn
        self.found_path = found_path
        self.scrollable_content = scrollable_content
        self.update_func = update_func
        self.auto_finder_func = auto_finder_func

        self.var = IntVar()
        if check_data["theme"] == "dark":
            self.var.set(1)
        else:
            self.var.set(0)
        self.var.trace_add("write", self.check_dark_theme_btn)

        self.tab_settings.config(bg=S_BG)
        self.settings_style_frame = Frame(self.tab_settings, bg=S_BG)
        self.settings_main_frame = Frame(self.tab_settings, bg=S_BG)
        self.settings_style_frame.pack(fill="both")
        self.settings_main_frame.pack(fill="both", pady=(0, 0))

        # ── Card: body ───────────────────────────────────────────
        self.style_body = self.make_card(
            self.settings_style_frame,
            self.data[self.current_lang]["l319"], "l319"
        )

        row1 = Frame(self.style_body, bg=CARD)
        row1.pack(fill="x", pady=4)
        Label(row1, text="Dark Mode", font=FONT_BOLD,
              bg=CARD, fg=FG, width=20, anchor="w").pack(side="left")
        Label(
            row1, text=self.data[self.current_lang]["l322"],
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, name="l322").pack(side="left", padx=(0, 20))
        dark_theme_btn = Button(
            row1,
            text=self.data[self.current_lang]["l324"] if self.var.get() == 1 else self.data[self.current_lang]["l323"],
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
            self.data[self.current_lang]["l320"], "l320"
        )

        self.row2 = Frame(self.body, bg=CARD)
        self.row2.pack(fill="x", pady=4)
        self.row_label1 = Label(
            self.row2, text=self.data[self.current_lang]["l325"], font=FONT_BOLD,
            bg=CARD, fg=FG, width=20, anchor="w", name="l325"
        )
        self.row_label2 = Label(
            self.row2, text=f"{self.data[self.current_lang]['l326']} {self.found_path}",
            font=FONT_SMALL, bg=CARD, fg=FG_MUTED, wraplength=300,
            name="l326"
        )
        self.row_label1.pack(side="left")
        self.row_label2.pack(side="left", padx=(0, 20))
        choose_path_btn = Button(
            self.row2,
            text=self.data[self.current_lang]["l328"],
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
            text=self.data[self.current_lang]["l327"],
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
        choose_path_btn.pack(side="right")
        choose_path_auto_finder.pack(side="right")
        choose_path_btn.bind("<Button-1>", self.choose_path)
        choose_path_auto_finder.bind("<Button-1>", self.auto_finder_adb)

    @property
    def is_dark(self):
        return self.check_data["theme"] == "dark"

    @property
    def is_white(self):
        return self.check_data["theme"] == "white"

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

    def choose_path(self, event):
        self.root.update_idletasks()
        logging.info("[choose_path]-clicked")
        choosen_path = filedialog.askopenfilename()
        if choosen_path:
            self.update_func(choosen_path)
            self.row_label2.configure(text=f"{self.data[self.current_lang]["l326"]} {choosen_path}")

    def auto_finder_adb(self, event):
        self.auto_finder_func()
        adb_path = self.check_data["choosen_path_for_adb"]
        self.root.after(
            1000, lambda: self.row_label2.configure(text=f"{self.data[self.current_lang]["l326"]} {adb_path}")
        )

    def check_dark_theme_btn(self, *args):
        if self.var.get() == 1:
            print("Choosen")
            self.check_data["theme"] = "dark"
            with open("check.json", "w", encoding="utf-8") as fi:
                json.dump(self.check_data, fi, indent=4)
            self.choose_theme("#292423", "white")
            self.choose_theme_special()
        else:
            self.check_data["theme"] = "white"
            with open("check.json", "w", encoding="utf-8") as fi:
                json.dump(self.check_data, fi, indent=4)
            self.choose_theme("SystemButtonFace", "black")
            self.choose_themeW("SystemButtonFace")
            print("the election was canceled")

    def _toggle(self, btn, var):
        if var.get() == 1:
            btn.config(text=self.data[self.current_lang]["l324"], bg=ACCENT, fg="white", relief="flat")
        else:
            btn.config(text=self.data[self.current_lang]["l323"], bg="#D1D5DB", fg=FG, relief="flat")

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
