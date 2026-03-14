from tkinter import (Toplevel, Label, Button, Tk, PanedWindow,
                     Frame, Canvas, Scrollbar, Y, Entry,
                     Text, Checkbutton, IntVar, Variable)
from tkinter import font
from tkinter import ttk
import json
import platform
import logging


FONT = ("Segoe UI", 10)


class settings_style:
    def __init__(self, check_data, tab_connect, tab_settings,
                 paned_window, upper_frame, nmap_input_row, adb_input_row,
                 adb_btn_container, tab1_label, tab1_label2, log_text, tab1_input, tab1_input2,
                 tab1_nmap_button, tab1_connect_button, root, nmap_btn_container):
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

        self.var = IntVar()
        if check_data["theme"] == "dark":
            self.var.set(1)
        else:
            self.var.set(0)
        self.var.trace_add("write", self.check_dark_theme_btn)
        self.tab_settings.columnconfigure(0, weight=1)

        self.settings_frame = Frame(self.tab_settings, padx=10, pady=10)
        self.settings_frame.pack(fill="both")

        dark_theme_btn = Checkbutton(
            self.settings_frame,
            text="Dark Mode",
            variable=self.var,
            font=FONT,
            relief="flat",
            cursor="hand2",
        )
        dark_theme_btn.grid(row=0, column=2, sticky="nsew")
        dark_theme_btn.bind()


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

    def apply_button_style(self, container):
        for widget in container.winfo_children():
            if isinstance(widget, Button) and self.check_data["theme"] == "dark":
                widget.configure(bg="#2D2D2D", fg="#E0E0E0", activebackground="#3D3D3D")
            elif isinstance(widget, Button) and self.check_data["theme"] == "white":
                widget.configure(bg="SystemButtonFace", fg="black", activebackground="#3D3D3D")
            if widget.winfo_children():
                self.apply_button_style(widget)
            elif isinstance(widget, ttk.Button):
                style_name = str(widget) + ".TButton"
                s = ttk.Style()
                if self.check_data["theme"] == "dark":
                    s.configure(style_name, background="#2D2D2D", foreground="black")
                else:
                    s.configure(style_name, background="SystemButtonFace", foreground="black")
                widget.configure(style=style_name)
            


    def choose_theme(self, color, fg_color):
        self.tab_connect.config(bg=color)
        self.tab_settings.config(bg=color)
        self.settings_frame.config(bg=color)
        self.paned_window.config(bg="white")
        self.upper_frame.config(bg=color)
        self.nmap_input_row.config(bg=color)
        self.adb_input_row.config(bg=color)
        self.adb_btn_container.config(bg=color)
        self.nmap_btn_container.configure(bg=color)
        self.tab1_label.config(bg=color, fg=fg_color)
        self.tab1_label2.config(bg=color, fg=fg_color)
        self.log_text.configure(bg=color, fg=fg_color)
        self.apply_button_style(self.root)
            


    def choose_themeW(self, color):
        self.paned_window.config(bg="black")
        self.tab1_label.config(bg=color, fg="black")
        self.tab1_label2.config(bg=color, fg="black")
        self.tab1_input.config(bg=color)
        self.tab1_input2.config(bg=color)

    def choose_theme_special(self):
        self.tab1_input.config(bg="gray")
        self.tab1_input2.config(bg="gray")
