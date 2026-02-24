from tkinter import *
from tkinter import font
from tkinter import ttk
import random
import time
import os
import json
import subprocess
import threading
from datetime import datetime
import platform
import re
from pathlib import Path
import shutil
#MY FILES
import adb_connect as adbc
import nmap_scan as nmaps
from checks import *
from scroll_buttons import buttons

import tkinter as tk
if platform.system() == "Windows":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()


with open("lang.json", "r", encoding="utf-8") as e:
    data = json.load(e)

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

button_references = []
current_lang = "en"

def open_menu(event, frame, choosen_button, selected_tab):
    print("Test")
    root.update_idletasks()
    if frame.winfo_viewable():
        frame.place_forget()
        print(f"{frame} is deleted")
        return
    button_x,button_y = choosen_button.winfo_rootx(),choosen_button.winfo_rooty()
    button_xp,button_yp = selected_tab.winfo_rootx(),selected_tab.winfo_rooty()

    print("Real screen:",button_x, button_y)
    print("This window:",button_xp, button_yp)
    try:
        frame.place(x=(button_x - button_xp) + choosen_button.winfo_width(), y=(button_y - button_yp) , anchor="nw")
        for child in frame.winfo_children():
            child.pack(fill=X)
        root.update_idletasks()
        now_x,now_y = frame.winfo_rootx(),frame.winfo_rooty()
        print(f"Created found menu at: {now_x, now_y}")
    except Exception as e:
        print(f"[E]Menu cant be created: {e}")

#IP MENU EVENTS
def enter_choosed_ip(event):
    clicked_button = event.widget
    clicked_button_label = clicked_button.cget("text")
    print(f"Pressed {clicked_button_label}")
    if menu_frame.winfo_exists() and menu_frame.winfo_viewable():
        menu_frame.place_forget()
        tab1_input.delete(0, "end")
        tab1_input.insert(0, clicked_button_label)
#ADB MENU EVENTS
def found_enter_choosed_ip(event, ip):
    print(f"Pressed {ip}")
    if menu_frame_found.winfo_exists() and menu_frame_found.winfo_viewable():
        tab1_input2.delete(0, "end")
        tab1_input2.insert(0, ip)
        
#FOR MESSAGE BALLON, GEMINI GAVE ME THIS CODE------------------
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def on_tab_selected(event):
    global load_clicked
    load_clicked = 0
    canvas2.yview_moveto(0)
    print(load_clicked)
    delete_widgets()
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    btn_instance.load_again()
    for m in all_menu:
        if m.winfo_exists():
            m.place_forget()
        else:
            print(f"{m} is null")
    print(tab_text)

def update_all_widgets(lang_code):
    global current_lang
    current_lang = lang_code
    new_texts = data[lang_code]
    btn_instance.current_lang = lang_code
    btn_instance.load_again()

    tabs = [
        (tab_connect, "l7"),
        (tab_keyevents, "l8"),
        (tab_usefull, "l9"),
        (tab_danger, "l10"),
        (tab_everything, "l11"),
        (tab_learn, "l12"),
        (tab_terminal, "l16"),
        (tab_settings, "l17"),
        (tab_connected, "l18")
    ]

    for tab_widget, json_key in tabs:
        if json_key in new_texts:
            main_sections.tab(tab_widget, text=new_texts[json_key])
    
    try:
        with open("lang.json", "r", encoding="utf-8") as f:
            full_data = json.load(f)
        selected_texts = full_data[lang_code]
        
        def recursive_update(container):
            for widget in container.winfo_children():
                w_name = str(widget).split('.')[-1]

                if w_name in selected_texts:
                    try:
                        widget.config(text=selected_texts[w_name])
                    except Exception as e:
                        print(f"An error occurred while updating and finding widgets: {e}")
                        pass
                if widget.winfo_children():
                    recursive_update(widget)

        recursive_update(root)
        root.update_idletasks()
        print(f"Language changed to: {lang_code}")
    except Exception as e:
        print(f"Language update error: {e}")

def update_ui(output):
    log_text.config(state="normal")
    log_text.insert("end", f"\n {output}")
    log_text.see("end")
    log_text.config(state="disabled")
#TO ACCESS THE FUNCTIONS WITHIN THE CLASS-
active_adb = None
def connect(event):
    global active_adb
    active_adb = adbc.adb_connect(tab1_input2,root, tab1_label_failed2,found_path, tab1_stop_adb, connected_devicesips, update_ui, connected_devicesips2, test_counter, processes_in)
def stop_adb_event(event):
    if active_adb:
        active_adb.stop_adb()
active_nmap = None
def scan(event):
    global active_nmap
    active_nmap = nmaps.nmap_scan(tab1_input, log_text, tab1_label_failed, tab1_stop_nmap, root, update_ui, menu_frame_found, found_enter_choosed_ip, button_references)
def stop_nmap_event(event):
    if active_nmap:
        active_nmap.stop_nmap()
def checks():
    checker = startup_check()
    checker.app_startup(connected_devicesips, current_lang, data)
    
#-----------------------------------------

if platform.system() == "Windows":
    tries = [
        "C:/platform-tools/adb.exe",
        os.path.expanduser("~") + "/AppData/Local/Android/Sdk/platform-tools/adb.exe"
    ]
else:
    tries = [
        shutil.which("adb"),
        "adb",
        os.path.expanduser("~") + "/Android/Sdk/platform-tools/adb",
        "/usr/bin/adb",
        "/usr/local/bin/adb",
    ]
    tries = [t for t in tries if t is not None]

found_path = None

for path in tries:
    if os.path.exists(path):
        found_path = path

if found_path:
    print(f"Found: {found_path}")
else:
    print("Not found")

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

def changed_paned(event):
    if menu_frame.winfo_viewable() and menu_frame.winfo_exists():
            menu_frame.place_forget()
            print("menu_frame is deleted")
    else:
        print("menu_frame is null")
    if menu_frame_found.winfo_viewable() and menu_frame_found.winfo_exists():
        menu_frame_found.place_forget()
        print("menu_frame_found is deleted")

def minimize_window():
    root.state('withdrawn')
    root.overrideredirect(False) 
    root.iconify()

def on_deiconify(event):
    if not root.overrideredirect():
        root.overrideredirect(True)
        if platform.system() == "Windows":
            root.after(10, lambda: show_in_taskbar(root))

def maximize_window():
    if root.state() == 'zoomed':
        root.state('normal')
    else:
        root.state('zoomed')

#FOR SCROLLING
def on_frame_configure(event):
    canvas2.configure(scrollregion=canvas2.bbox("all"))
def _on_mousewheel(event):
    # Windows and MacOS
    canvas2.yview_scroll(int(-1*(event.delta/120)), "units")

#FOR LINUX
def _on_scroll_up(event):
    canvas2.yview_scroll(-1, "units")

def _on_scroll_down(event):
    canvas2.yview_scroll(1, "units")

def close_menus(event):
    print("HIIIIIIIIIIIIIII")
    if isinstance(event.widget, Button):
        return
    for menus in all_menu:
        if menus.winfo_viewable() and menus.winfo_exists():
            menus.place_forget()

#MAIN PANEL
root = Tk()
root.minsize(800,350)
root.title("AdbEz")
root.config(background="gray")
root.bind("<Map>", on_deiconify)
root.bind("<Button-1>", close_menus)
root.geometry("1000x700")
root.overrideredirect(True)
root.config(bg='#1e1e1e')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
style = ttk.Style()
style.configure("TNotebook.Tab", padding=[20, 5])
style.configure("Siyah.TFrame", background="black")
style2 = ttk.Style()
style2.theme_use('default')
style2.map("TNotebook.Tab",
          background=[("selected", "#5a95d8"),("active", "#737171")],
          foreground=[("selected", "white")])

border_color = "#3d3d3d"
bg_color = "#1e1e1e"

#OUTER FRAME
external_frame = tk.Frame(root, bg=border_color, bd=0)
external_frame.pack(fill="both", expand=True)

#INNER MAIN AREA
main_area = tk.Frame(external_frame, bg=bg_color, bd=0)
main_area.pack(fill="both", expand=True, padx=1, pady=1)

#FOR SIZABLE
sizegrip = ttk.Sizegrip(main_area)
sizegrip.pack(side="right", anchor="se")
sizegrip2 = ttk.Sizegrip(main_area)
sizegrip2.pack(side="left", anchor="nw")

#TITLE BAR
title_bar = tk.Frame(main_area, bg="#2d2d2d", height=30)
title_bar.pack(fill="x")

title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", on_move)

title_label = Label(title_bar, text="ADBez", bg="#2d2d2d", fg="white", font=("Arial", 9))
title_label.pack(side="left", padx=10)

def on_enter(event):
    event.widget.configure(bg="lightblue")
def leave_enter(event):
    event.widget.configure(bg="#2d2d2d")
def disconnect_ip(event):
    root.update_idletasks()
    label_text = tab1_input2.get().strip()
    print("current ip address: ", label_text)
    print("Clicked disconnect")
    connected_ips_text = connected_devicesips.cget("text")
    print(f"list is: \n {connected_ips_text}")
    connected_ips_list = connected_ips_text.split()
    background_color = upper_frame.cget("background")
    try:
        subprocess.Popen(
            [found_path, "disconnect", label_text],
            stdout=subprocess.PIPE,
            text=True
        )
        print(f"Disconnected to {label_text}")
        connected_devicesips2.grid_forget()
        with open("check.json", "r", encoding="utf-8") as f:
            check_data = json.load(f)
        ip_to_remove = label_text.strip()
        print(f"Deleting ip: {ip_to_remove}")
        #now_data = list(check_data["connected_ips"].keys())
        #print("Testinggggg: ", now_data.split("\n"))
        if ip_to_remove in check_data["connected_ips"]:
            del check_data["connected_ips"][ip_to_remove]
        with open("check.json", "w", encoding="utf-8") as fi:
            json.dump(check_data, fi, indent=4)
        for i in connected_ips_list:
            if i == label_text:
                connected_ips_list.remove(i)
                new_text = "\n".join(connected_ips_list)
                root.update_idletasks()
                connected_devicesips.configure(text=new_text)
                print("Deleted ip")
        if connected_devicesips.cget("text") == "":
            connected_devicesips.configure(background=background_color)
    except Exception as e:
        print(f"Error: {e}")

min_btn = Button(title_bar, text="—", bg="#2d2d2d", fg="white", bd=0, 
                 activebackground="#404040", activeforeground="white",
                 command=minimize_window, width=4, font=("Arial", 9))
min_btn.pack(side="right", fill="y")
min_btn.bind("<Enter>", on_enter)
min_btn.bind("<Leave>", leave_enter)

def catch_size(event):
    global paned_window, upper_frame
    if event.widget == root:
        for m in all_menu:
            if m.winfo_viewable() and m.winfo_exists():
                m.place_forget()
                print(f"{m} is deleted")
            else:
                print(f"{m} is null")
        if event.height > 600:
            print(event.height)
            paned_window.paneconfigure(upper_frame, minsize=350, height=550)
            print("Minsize is set")

#FULL SCREEN(□)
max_btn = Button(title_bar, text="▢", bg="#2d2d2d", fg="white", bd=0, 
                 activebackground="#404040", activeforeground="white",
                 command=maximize_window, width=4, font=("Arial", 10))
max_btn.pack(side="right", fill="y")
max_btn.bind("<Enter>", on_enter)
max_btn.bind("<Leave>", leave_enter)

close_btn = Button(title_bar, text="✕", bg="#2d2d2d", fg="white", bd=0, 
                      activebackground="red", command=root.destroy, width=4)
close_btn.pack(side="right", fill="y")
style.configure("Redbg.TButton", background="red")
close_btn.bind("<Enter>", on_enter)
close_btn.bind("<Leave>", leave_enter)

#CATCHING SIZE OF THE WINDOW FOR IP MENU
root.bind("<Configure>", catch_size)
frm = ttk.Frame(main_area, style="Siyah.TFrame",padding=10)
frm.pack(fill=BOTH, expand=True)

main_sections = ttk.Notebook(frm)
main_sections.pack(fill=BOTH, expand=True)
main_sections.config()

#DEFINITION
tab_connect = ttk.Frame(main_sections)
tab_keyevents = ttk.Frame(main_sections)
tab_usefull = ttk.Frame(main_sections)
tab_danger = ttk.Frame(main_sections)
tab_everything = ttk.Frame(main_sections)
tab_learn = ttk.Frame(main_sections)
tab_terminal = ttk.Frame(main_sections)
tab_settings = ttk.Frame(main_sections)
tab_connected = ttk.Frame(main_sections)

#PLACEMENT
main_sections.add(tab_connect, text=data[current_lang]["l7"])
main_sections.add(tab_keyevents, text=data[current_lang]["l8"])
main_sections.add(tab_usefull, text=data[current_lang]["l9"])
main_sections.add(tab_danger, text=data[current_lang]["l10"])
main_sections.add(tab_everything, text=data[current_lang]["l11"])
main_sections.add(tab_learn, text=data[current_lang]["l12"])
main_sections.add(tab_terminal, text=data[current_lang]["l16"])
main_sections.add(tab_settings, text=data[current_lang]["l17"])
main_sections.add(tab_connected, text=data[current_lang]["l18"])

#BLOCKS-----------------------------------------------
#-TAB_CONNECT LAYOUTS
paned_window = PanedWindow(tab_connect, orient=VERTICAL, bd=1, relief="sunken", sashwidth=4, sashrelief="sunken", background="black")
paned_window.pack(fill=BOTH,expand=True)
upper_frame = Frame(paned_window)
paned_window.add(upper_frame, minsize=300)
lower_frame = Frame(paned_window, background="black")
paned_window.add(lower_frame,minsize=50)
root.update_idletasks()
root.after(100, lambda: paned_window.sash_place(0, 0, 420))
#-TAB_KEYEVENTS LAYOUTS
paned_window2 = PanedWindow(tab_keyevents, orient=HORIZONTAL, bd=1, relief="sunken", sashwidth=4, sashrelief="sunken", bg="black")
upper_frame2 = Frame(paned_window2)
paned_window2.add(upper_frame2, minsize=700)
paned_window2.pack(fill=BOTH,expand=True, anchor="w", side="left")
lower_frame2 = Frame(paned_window2)
paned_window2.add(lower_frame2,minsize=50)
lower_frame2_log_label = Frame(lower_frame2)
lower_frame2_connected_ips = Frame(lower_frame2)
lower_frame2_connected_ips.grid(row=0, column=1)
lower_frame2_log_label.grid(row=1, column=0)
lower_frame2_connected_ips.configure(bg="yellow")

upper_frame2.config()
lower_frame2.config(bg="lightblue")
lower_frame2.rowconfigure(2, weight=1)
lower_frame2.grid_columnconfigure(0, weight=1)
paned_window2.paneconfigure(lower_frame2, minsize=1)
#-NMAP INPUT ROW
nmap_input_row = Frame(upper_frame)
nmap_input_row.grid(row=2, column=1, sticky="ew",padx=(10))
nmap_input_row.columnconfigure(1, minsize=300)
nmap_input_row.columnconfigure(0,weight=0)
nmap_input_row.columnconfigure(1,weight=1)
nmap_input_row.columnconfigure(2,weight=0)
#-ADB INPUT ROW
adb_input_row = Frame(upper_frame)
adb_btn_container = Frame(upper_frame)
adb_btn_container.grid(row=7,column=1, sticky="n")
adb_input_row.grid(row=6, column=1, sticky="ew", padx=(10))

adb_input_row.columnconfigure(0,weight=0)
adb_input_row.columnconfigure(1,weight=1)
adb_input_row.columnconfigure(2,weight=0)
#-NMAP BUTTON ROW
nmap_btn_container = ttk.Frame(upper_frame)
nmap_btn_container.grid(row=3, column=1,sticky="n")
nmap_btn_container.columnconfigure(0, weight=0)
nmap_btn_container.columnconfigure(1, weight=0)
#-LANGUAGE BUTTON ROW
lang_btn_container = ttk.Frame(upper_frame)
lang_btn_container.grid(row=0, column=0, sticky="nw")
#TAB_KEYEVENTS--------------------------------------
canvas2 = Canvas(upper_frame2, bg="red", highlightthickness=0)
canvas2.pack(side="left", fill="both", expand=True)
scrollable_bar = Scrollbar(upper_frame2, orient="vertical", command=canvas2.yview, background="white")
scrollable_bar.pack(fill=Y, side="right", anchor="e")
canvas2.configure(yscrollcommand=scrollable_bar.set)
scrollable_content = Frame(canvas2)
canvas_window = canvas2.create_window((0, 0), window=scrollable_content, anchor="nw")
scrollable_content.bind("<Configure>", on_frame_configure)
tab2_seperate_scroll_BTN = Frame(scrollable_content)
tab2_seperate_scroll_LOAD = Frame(scrollable_content)
up_bar = Frame(scrollable_content)
up_bar.pack(expand=True)
tab2_seperate_scroll_BTN.pack(fill=X, expand=True)
tab2_seperate_scroll_LOAD.pack(expand=True, fill=X)
up_bar.columnconfigure(0, weight=1)
up_bar.columnconfigure(3, weight=1)
#WINDOWS-----------------------
canvas2.bind_all("<MouseWheel>", _on_mousewheel)
#------------------------------
#LINUX-------------------------
canvas2.bind_all("<Button-4>", _on_scroll_up)
canvas2.bind_all("<Button-5>", _on_scroll_down)
#------------------------------
search = Entry(up_bar, text="Hi")
search.grid(row=0, column=1)
tab2_category_button = Button(up_bar, text=data[current_lang]["l309"], name="l309")
tab2_category_button.bind("<Button-1>", lambda event: open_menu(event, menu_frame_category, tab2_category_button, tab_keyevents))
tab2_category_button.grid(row=0, column=2)
#---------------------------------------------------
#-----------------------------------------------------

#FOR EXPAND WINDOW
def on_canvas_resize(event):
    canvas2.itemconfig(canvas_window, width=event.width)
canvas2.bind("<Configure>", on_canvas_resize)
#PLACEMENT CONFIGURATION
upper_frame.rowconfigure(0, weight=1)
upper_frame.rowconfigure(8, weight=1)
upper_frame.columnconfigure(0, weight=1)
upper_frame.columnconfigure(1, weight=0)
upper_frame.columnconfigure(2, weight=1)

#FONT STYLE DEFINITION
custom_font = font.Font(size=8)
#DEFINITION
tab1_label = ttk.Label(upper_frame, text=data[current_lang]["l3"], name="l3")
tab1_input = ttk.Entry(nmap_input_row)
tab1_nmap_button = Button(nmap_btn_container, text=data[current_lang]["l4"], name="l4")
tab1_label2 = ttk.Label(upper_frame, text=data[current_lang]["l5"], name="l5")
tab1_input2 = ttk.Entry(adb_input_row)
tab1_connect_button = Button(adb_btn_container, text=data[current_lang]["l6"], name="l6")
tab1_label_failed = Label(upper_frame, text="", foreground="red",width=26)
tab1_label_failed2 = Label(upper_frame, text="", foreground="red",width=26)
tab1_lang_button = Button(lang_btn_container, text="Languages", width=10, height="1", bg="lightblue")
tab1_disconnect_button = Button(adb_btn_container, text=data[current_lang]["l19"], name="l19")
tab1_disconnect_button.grid(row=1, column=0)
tab1_disconnect_button.bind("<Button-1>", disconnect_ip)

tab2_log_label = Label(lower_frame2_log_label, text="Logs", background="lightblue")
tab2_log_label.grid(row=0, column=0)
tab2_log_box = Text(lower_frame2)
tab2_log_box.grid(row=1, column=0, rowspan=2,sticky="w", padx=(5,5))
tab2_load_more_btn = Button(tab2_seperate_scroll_LOAD, text="Load more...")
tab2_load_more_btn.pack()
tab2_load_more_btn.bind("<Button-1>", lambda e: btn_instance.called_test_function())

connected_container2 = ttk.Frame(lower_frame2)
connected_container2.grid(row=0, column=0, sticky="n")

test_counter = 0
connected_devices2 = Label(connected_container2, text=data[current_lang]["l20"], name="l20")
connected_devicesips2 = Checkbutton(connected_container2)
is_text_empty2 = connected_devicesips2.cget("text")
connected_devices2.grid(row=0, column=0, sticky="ne")

keyevents_buttons = []
keyevents_labels = []
background_color = upper_frame.cget("background")
btn_instance = buttons(
    tab2_seperate_scroll_BTN,
    root,
    tab2_load_more_btn,
    tab2_seperate_scroll_LOAD,
    keyevents_buttons,
    keyevents_labels,
    data,
    current_lang,
    background_color
)

connected_container = ttk.Frame(upper_frame)
ongoing_processes = ttk.Frame(upper_frame)
connected_container.grid(row=0, column=2, sticky="ne")
ongoing_processes.grid(row=8, column=0, sticky="sw")
processes_lists_text = Label(ongoing_processes, text="-Ongoing processes-")
processes_in = Label(ongoing_processes)
processes_lists_text.grid(row=0, column=0)
connected_devices = Label(connected_container, text=data[current_lang]["l20"], name="l20")
connected_devicesips = Label(connected_container)
is_text_empty = connected_devicesips.cget("text")
connected_devices.grid(row=0, column=0, sticky="ne")
connected_devicesips.grid(row=1, column=0 , sticky="nsew")

#I WANT TO USE MENUBUTTON BUT IT CAN'T DO THE FEATURES I WANT,SO WE WILL CREATE OUR OWN MENU
#tab1_choose_ip = ttk.Menubutton(nmap_input_row, text="Choose")
tab1_choose_ip = Button(nmap_input_row, text=data[current_lang]["l13"], name="l13", takefocus=False, width=10)
tab1_found_ip = Button(adb_input_row, text=data[current_lang]["l14"], name="l14", takefocus=False)
#STOP NMAP-ADB BUTTON
tab1_stop_nmap = ttk.Button(nmap_btn_container,text=data[current_lang]["l15"], name="l15",takefocus=False, style="Redbg.TButton")
tab1_stop_adb = ttk.Button(adb_btn_container, text=data[current_lang]["l15"], name="l15", takefocus=False, style="Redbg.TButton")
# NMAP IP MENU
menu_frame = Frame(upper_frame,background="red")
menu_frame_in1 = Button(menu_frame,text="192.168.1.0/24")
menu_frame_in2 = Button(menu_frame,text="127.0.0.0/24")
#ADB IP MENU
menu_frame_found = Frame(upper_frame, background="red")
log_text = Text(lower_frame, height=1)
#LANGUAGES MENU
menu_frame_lang = Frame(upper_frame, background="red")
menu_frame_lang1 = Button(menu_frame_lang, text="English")
menu_frame_lang2 = Button(menu_frame_lang, text="Turkce")
menu_frame_lang3 = Button(menu_frame_lang, text="Português")
#CATEGORY MENU
menu_frame_category = Frame(upper_frame2, background="blue")
menu_frame_category_in1 = Button(menu_frame_category,text=data[current_lang]["l310"], name="l310", font=custom_font)
menu_frame_category_in2 = Button(menu_frame_category,text=data[current_lang]["l311"], name="l311", font=custom_font)
menu_frame_category_in3 = Button(menu_frame_category,text=data[current_lang]["l312"], name="l312", font=custom_font)
menu_frame_category_in4 = Button(menu_frame_category,text=data[current_lang]["l313"], name="l313", font=custom_font)
menu_frame_category_in5 = Button(menu_frame_category,text=data[current_lang]["l314"], name="l314", font=custom_font)
menu_frame_category_in6 = Button(menu_frame_category,text=data[current_lang]["l315"], name="l315", font=custom_font)
menu_frame_category_in7 = Button(menu_frame_category,text=data[current_lang]["l316"], name="l316", font=custom_font)
menu_frame_category_in8 = Button(menu_frame_category,text=data[current_lang]["l317"], name="l317", font=custom_font)
menu_frame_category_in1.bind("<Button-1>", lambda self: buttons.categorize(self))

#PLACEMENT
tab1_lang_button.grid(row=0, column=0, sticky="nsew")

tab1_label.grid(row=1, column=1, sticky="n", pady=(0, 5), padx=(0, 285))
tab1_input.grid(row=0, column=1, sticky="ew", pady=(0, 10))
tab1_choose_ip.grid(row=0, column=2, sticky="we", padx=(15,0), pady=(0,10))
tab1_nmap_button.grid(row=0, column=0, sticky="ew")
nmap_btn_container.columnconfigure(0, minsize=100)

tab1_label2.grid(row=4, column=1, sticky="n", padx=(0, 295))
tab1_input2.grid(row=0, column=1, sticky="ew")
tab1_found_ip.grid(row=0, column=2, sticky="ew", padx=(15,0))
tab1_connect_button.grid(row=0, column=0, sticky="ew",padx=(5,0))
log_text.pack(fill=BOTH, expand=True)

#BUTTON EVENTS-----------------------------------------------
tab1_lang_button.bind("<Button-1>", lambda event: open_menu(event, menu_frame_lang, tab1_lang_button, tab_connect))
tab1_choose_ip.bind("<Button-1>", lambda event: open_menu(event, menu_frame, tab1_choose_ip, tab_connect))
#tab1_nmap_button.bind("<Button-1>", find)
tab1_nmap_button.bind("<Button-1>", scan)
tab1_connect_button.bind("<Button-1>", connect)
tab1_found_ip.bind("<Button-1>", lambda event: open_menu(event, menu_frame_found, tab1_found_ip, tab_connect))

main_sections.bind("<<NotebookTabChanged>>", on_tab_selected)

#nmap ip menu events
menu_frame_in1.bind("<Button-1>", enter_choosed_ip)
menu_frame_in2.bind("<Button-1>", enter_choosed_ip)
#lang menu events
menu_frame_lang1.bind("<Button-1>", lambda event: update_all_widgets("en"))
menu_frame_lang2.bind("<Button-1>", lambda event: update_all_widgets("tr"))
menu_frame_lang3.bind("<Button-1>", lambda event: update_all_widgets("pt"))

#stop nmap button event
tab1_stop_nmap.bind("<Button-1>", stop_nmap_event)
tab1_stop_adb.bind("<Button-1>", stop_adb_event)

#CATCHING PANED WINDOW EVENT
paned_window.bind("<B1-Motion>", changed_paned)

#FOR CATCHING CURRENT TAB
def delete_widgets():
    for widgets in tab2_seperate_scroll_BTN.winfo_children()[60:]:
        widgets.destroy()
        print("Widgets deleting")

#CATCHING WINDOW SIZE FOR IP MENU
all_menu = [menu_frame, menu_frame_found, menu_frame_lang, menu_frame_category]

checks()
if platform.system() == "Windows":
    show_in_taskbar(root)
root.mainloop()
