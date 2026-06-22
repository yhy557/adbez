from tkinter import (Label, Button, Frame, Canvas,
                     Scrollbar, Entry,
                     Text, Checkbutton, IntVar, Variable,
                     filedialog, Toplevel, )
from tkinter import ttk
import json
import logging
import os
import subprocess
import sys
import config.constants as const
import config.paths as paths
from typing import TYPE_CHECKING
from ui.windows.monitor_window import SystemMonitorGUI
from config.state import global_state
from utils.file_utils import open_file, write_file
from ui.widgets.tooltip import Tooltip

if TYPE_CHECKING:
    from adbez import MainApp



class SettingsStyle:
    def __init__(self, app: 'MainApp', check_data, data, update_func, auto_finder_func):
        from core.nmap_scan import NmapBrain

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
        self.min_btn, self.max_btn, self.close_btn = self.app.min_btn, self.app.max_btn, self.app.close_btn
        self.found_path = self.app.found_path
        self.scrollable_content = self.app.scrollable_content
        self.update_func = update_func
        self.auto_finder_func = auto_finder_func
        self.get_text = self.app.get_text


        self.var = IntVar()
        self.live_helper_var = IntVar()
        self.var.trace_add("write", self.check_dark_theme_btn)
        self.auto_nmap_var = IntVar()
        self.auto_nmap_var.trace_add("write", self.start_auto_nmap)

        self.tab_settings.config(bg=const.S_BG)
        self.canvas = Canvas(self.tab_settings, bg=const.S_BG, highlightthickness=0)
        self.scrollbar = Scrollbar(self.tab_settings, orient="vertical", command=self.canvas.yview)

        self.settings_container = Frame(self.canvas, bg=const.S_BG)

        self.settings_style_frame = Frame(self.settings_container, bg=const.S_BG)
        self.settings_main_frame = Frame(self.settings_container, bg=const.S_BG)
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

        row1 = Frame(self.style_body, bg=const.CARD)
        row1.pack(fill="x", pady=4)
        Label(row1, text="Dark Mode", font=const.FONT_BOLD,
              bg=const.CARD, fg=const.FG, width=20, anchor="w").pack(side="left")
        Label(
            row1, text=self.get_text("l322"),
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, name="l322").pack(side="left", padx=(0, 20))
        self.dark_theme_btn = Button(
            row1,
            text=self.get_text("l324") if self.var.get() == 1 else self.get_text("l323"),
            name="l324" if self.var.get() == 1 else "l323",
            font=const.FONT_BOLD,
            bg=const.ACCENT if self.var.get() == 1 else "#D1D5DB",
            fg="white" if self.var.get() == 1 else const.FG,
            activebackground=const.BTN_ACT,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=5,
            bd=0,
            width=10,
            command=lambda: [
                self.var.set(0 if self.var.get() == 1 else 1),
                self._toggle(self.dark_theme_btn, self.var)
            ]
        )
        self.dark_theme_btn.pack(side="right")
        self.dark_theme_btn.bind()

        # ── Card: ADB ─────────────────────────────────────────────────
        self.body = self.make_card(
            self.settings_main_frame,
            self.get_text("l320"), "l320"
        )
        self.auto_nmap_body = self.make_card(
            self.settings_main_frame,
            self.get_text("l333"), "l333"
        )
        self.languages_body = self.make_card(
            self.settings_main_frame,
            self.get_text("l337"), "l337"
        )

        self.row2 = Frame(self.body, bg=const.CARD)
        self.background_processF = Frame(self.body, bg=const.CARD)
        self.auto_nmapF = Frame(self.auto_nmap_body, bg=const.CARD)
        self.langF = Frame(self.languages_body, bg=const.CARD)

        self.row2.pack(fill="x", pady=4)
        self.background_processF.pack(fill="x", pady=4)
        self.auto_nmapF.pack(fill="x", pady=4)
        self.langF.pack(fill="x", pady=4)

        self.row_label1 = Label(
            self.row2, text=self.get_text("l325"), font=const.FONT_BOLD,
            bg=const.CARD, fg=const.FG, width=20, anchor="w", name="l325"
        )
        self.root.update_idletasks()
        self.row_label2 = Label(
            self.row2, text=f"{self.get_text('l326')} {str(self.found_path)}",
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, wraplength=300,
            name="l326"
        )
        self.background_processL_main = Label(
            self.background_processF, text=self.get_text("l335"), font=const.FONT_BOLD, 
            bg=const.CARD, fg=const.FG, width=20, anchor="w", name="l335"
        )
        self.background_processL_inner = Label(
            self.background_processF, text=(self.get_text("l336")),
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, wraplength=300,
            name="l336"
        )
        self.auto_nmapL_main = Label(
            self.auto_nmapF, text=self.get_text("l334"), font=const.FONT_BOLD,
            bg=const.CARD, fg=const.FG, width=20, anchor="w", name="l334"
        )
        self.auto_nmapL_inner = Label(
            self.auto_nmapF, text=(self.get_text("l332")),
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, wraplength=300,
            name="l332"
        )
        self.languages_main = Label(
            self.langF, text=self.get_text("7"), font=const.FONT_BOLD, 
            bg=const.CARD, fg=const.FG, width=20, anchor="w", name="l337"
        )
        self.languages_inner = Label(
            self.langF, text=(self.get_text("l338")),
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, wraplength=300,
            name="l338"
        )

        self.row_label1.pack(side="left")
        self.row_label2.pack(side="left", padx=(0, 20))
        self.background_processL_main.pack(side="left")
        self.background_processL_inner.pack(side="left", padx=(0, 20))
        self.auto_nmapL_main.pack(side="left")
        self.auto_nmapL_inner.pack(side="left", padx=(0,20))
        self.languages_main.pack(side="left")
        self.languages_inner.pack(side="left", padx=(0,20))

        choose_path_btn = Button(
            self.row2,
            text=self.get_text("l328"),
            name="l328",
            font=const.FONT,
            bg=const.BTN_BG,
            fg=const.BTN_FG,
            activebackground=const.BTN_ACT,
            activeforeground=const.BTN_FG,
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
            font=const.FONT,
            bg=const.BTN_BG,
            fg=const.BTN_FG,
            activebackground=const.BTN_ACT,
            activeforeground=const.BTN_FG,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            bd=0
        )
        self.open_process_monitor_btn = Button(
            self.background_processF,
            text=self.get_text("l339"),
            name="l339",
            font=const.FONT,
            bg=const.BTN_BG,
            fg=const.BTN_FG,
            activebackground=const.BTN_ACT,
            activeforeground=const.BTN_FG,
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
            font=const.FONT_BOLD,
            bg=const.ACCENT if self.auto_nmap_var.get() == 1 else "#D1D5DB",
            fg="white" if self.auto_nmap_var.get() == 1 else const.FG,
            activebackground=const.BTN_ACT,
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
        self.choose_auto_nmap_ip.config(bg="lightgray")
        self.choose_auto_nmap_ip.bind("<Return>", self.get_nmap_ip)
        self.check_data = open_file(paths.CONFIG_FILE_PATH)
        if not self.check_data["ui_flags"]["has_seen_entry_save_hint"]:
            self.hint_tooltip = Tooltip(
                widget=self.choose_auto_nmap_ip,
                text="Please press Enter key to save",
                enter_event="<FocusIn>",
                leave_events=("<Return>",)
            )
            def on_first_focus_out(event):
                self.check_data["ui_flags"]["has_seen_entry_save_hint"] = True
                write_file(paths.CONFIG_FILE_PATH, self.check_data)
                self.hint_tooltip.unregister()
                self.choose_auto_nmap_ip.unbind("<FocusOut>", first_focus_out_id)
            first_focus_out_id = self.choose_auto_nmap_ip.bind("<FocusOut>", on_first_focus_out, add="+")

        choose_path_btn.pack(side="right")
        choose_path_auto_finder.pack(side="right")
        self.open_process_monitor_btn.pack(side="right")
        self.choose_auto_nmap_btn.pack(side="right")
        choose_path_btn.bind("<Button-1>", self.choose_path)
        choose_path_auto_finder.bind("<Button-1>", self.auto_finder_adb)
        self.open_process_monitor_btn.bind("<Button-1>", self.launch_process_monitor)

        self.menu_frame_lang, _lang_inner = app.menu_manager.scrollable_menu(self.tab_settings, max_height=100)
        menu_frame_lang1 = Button(_lang_inner, text="English")
        menu_frame_lang2 = Button(_lang_inner, text="Turkce")
        menu_frame_lang3 = Button(_lang_inner, text="Português")
        self.lang_button = Button(
            self.langF, text="Languages", width=10, height="1", bg="lightblue"
        )
        app.all_menu.append(self.menu_frame_lang)
        self.lang_button.pack(side="right")
        self.lang_button.bind(
            "<Button-1>",
            lambda event: app.menu_manager.toggle_menu(
                event, self.menu_frame_lang, self.lang_button, self.tab_settings
            )
        )
        menu_frame_lang1.pack(fill="x")
        menu_frame_lang2.pack(fill="x")
        menu_frame_lang3.pack(fill="x")
        # lang menu events
        menu_frame_lang1.bind("<Button-1>", lambda event: app.update_all_widgets("en"))
        menu_frame_lang2.bind("<Button-1>", lambda event: app.update_all_widgets("tr"))
        menu_frame_lang3.bind("<Button-1>", lambda event: app.update_all_widgets("pt"))

        self.live_helper = self.make_card(
            self.settings_main_frame,
            self.get_text("l329"), "l329"
        )
        self.row3 = Frame(self.live_helper, bg=const.CARD)
        self.row3.pack(fill="x", pady=4)
        self.row_label3 = Label(
            self.row3, text="Live Helper",
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, wraplength=300,
            name="l329"
        )
        self.row_label3.pack(side="left")
        self.live_helper_button = Button(
            self.row3,
            text=self.get_text("l324") if self.live_helper_var.get() == 1 else self.get_text("l323"),
            name="l324" if self.live_helper_var.get() == 1 else "l323",
            font=const.FONT_BOLD,
            bg=const.ACCENT if self.live_helper_var.get() == 1 else "#CB2314",
            fg="white" if self.live_helper_var.get() == 1 else const.FG,
            activebackground=const.BTN_ACT,
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
        self.row4 = Frame(self.adb_configurations, bg=const.CARD)
        self.row4.pack(fill="x", pady=4)
        self.row_label4 = Label(
            self.row4, text="Change the default port for ADB Connect",
            font=const.FONT_SMALL, bg=const.CARD, fg=const.FG_MUTED, wraplength=300,
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

        if not check_data["is_auto_nmap_on"]:
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
        write_file(paths.CONFIG_FILE_PATH, self.check_data)

    def make_card(self, parent, title, name):
        outer = Frame(parent, bg=const.BORDER, padx=1, pady=1)
        outer.pack(fill="x", padx=16, pady=(0, 8))

        header = Frame(outer, bg="#1E1E2E", padx=14, pady=8)
        header.pack(fill="x")
        title_label = Label(
            header, text=title, font=const.FONT_BOLD,
            bg="#1E1E2E", fg=const.ACCENT, name=name
        )
        title_label.pack(side="left")

        body = Frame(outer, bg=const.CARD, padx=14, pady=12)
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
            self.row_label2.configure(text=f"{self.get_text('l326')} {choosen_path}")

    def get_nmap_ip(self, event):
        logging.debug(f"auto_nmap_ip: {self.choose_auto_nmap_ip.get()}")
        self.check_data["choosen_nmap_ip"].append(self.choose_auto_nmap_ip.get())
        try:
            write_file(paths.CONFIG_FILE_PATH, self.check_data)
        except Exception as e:
            logging.debug(f"LOOK MTF {e}")
        self.choose_auto_nmap_ip.delete(0, 'end')
        self.choose_auto_nmap_ip.insert(0, "Saved!")
        self.choose_auto_nmap_ip.configure(bg="lightgreen")
        self.root.after(1500, lambda: self.choose_auto_nmap_ip.configure(bg="white"))
        self.root.after(1500, lambda: self.choose_auto_nmap_ip.delete(0, 'end'))

    def launch_process_monitor(self, event):
        monitor_window = Toplevel(self.root)
        SystemMonitorGUI(monitor_window)

    def auto_finder_adb(self, event):
        self.auto_finder_func()
        adb_path = self.check_data["choosen_path_for_adb"]
        self.root.after(
            1000, lambda: self.row_label2.configure(text=f"{self.get_text('l326')} ")
        )
        self.root.after(
            1000, lambda: self.row_label2.configure(text=f"{self.get_text('l326')} {adb_path}")
        )

    def check_dark_theme_btn(self, *args):
        if self.var.get() == 1:
            logging.debug("[check_Dark_theme_btn]-Choosen")
            self.check_data["theme"] = "dark"
            self.choose_theme("#292423", "white")
            self.choose_theme_special()
        else:
            self.check_data["theme"] = "white"
            self.choose_theme("SystemButtonFace", "black")
            self.choose_themeW("SystemButtonFace")
            logging.debug("the election was canceled")
        write_file(paths.CONFIG_FILE_PATH, self.check_data)

    def check_live_helper_is_on(self, *args):
        if self.live_helper_var.get() == 1:
            logging.debug("[check_live_helper_is_on] - Choosen")
            self.check["is_live_helper_on"] = True
        else:
            self.check["is_live_helper_on"] = False
        write_file(paths.CONFIG_FILE_PATH, self.check_data)  #check.json

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
        write_file(paths.CONFIG_FILE_PATH, self.check_data)

    def _toggle(self, btn, var):
        if var.get() == 1:
            btn.config(text=self.get_text("l324"), bg=const.ACCENT, fg="white", relief="flat")
        else:
            btn.config(text=self.get_text("l323"), bg="#D1D5DB", fg=const.FG, relief="flat")
    def _toggle_live_helper(self, btn, var):
        if var.get() == 1:
            btn.config(text=self.get_text("l324"), bg="#31AD12", fg="white", relief="flat")
        else:
            btn.config(text=self.get_text("l323"), bg="#CB2314", fg=const.FG, relief="flat")

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
            if isinstance(widget, ttk.Button):
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
            self.style_body.configure(bg=const.CARD)
            self.body.configure(bg=const.CARD)

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
