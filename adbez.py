from tkinter import *
from tkinter import font
from tkinter import ttk
import tkinter as tk
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

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
#MY FILES
from adb_connect import *
from nmap_scan import *
from checks import *

with open("lang.json", "r", encoding="utf-8") as e:
    data = json.load(e)

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

#For IP menu
def open_ip_menu(event):
    print("tiklandi")
    root.update_idletasks()
    if menu_frame.winfo_viewable():
        menu_frame.place_forget()
        print("menu_frame is deleted")
        return
    buton_x,buton_y = tab1_choose_ip.winfo_rootx(),tab1_choose_ip.winfo_rooty()
    buton_xp,buton_yp = tab_connect.winfo_rootx(),tab_connect.winfo_rooty()

    print("Real screen:",buton_x, buton_y)
    print("This window:",buton_xp, buton_yp)
    try:
        menu_frame.place(x=(buton_x - buton_xp), y=(buton_y - buton_yp)-tab1_choose_ip.winfo_height(), width=tab1_choose_ip.winfo_width(), anchor="w")
        menu_frame_in1.pack(fill=X)
        menu_frame_in2.pack(fill=X)
        root.update_idletasks()
        now_x,now_y = menu_frame.winfo_rootx(),menu_frame.winfo_rooty()
        print(f"Created menu at: {now_x, now_y}")
    except Exception as e:
        print(f"[E]Menu cant be created: {e}")

def open_founded_ip_menu(event):
    print("tiklandi")
    root.update_idletasks()
    if menu_frame_founded.winfo_viewable():
        menu_frame_founded.place_forget()
        print("menu_frame_founded is deleted")
        return
    buton_x,buton_y = tab1_found_ip.winfo_rootx(),tab1_found_ip.winfo_rooty()
    buton_xp,buton_yp = tab_connect.winfo_rootx(),tab_connect.winfo_rooty()

    print("Real screen:",buton_x, buton_y)
    print("This window:",buton_xp, buton_yp)
    try:
        menu_frame_founded.place(x=(buton_x - buton_xp), y=(buton_y - buton_yp)+tab1_found_ip.winfo_height(), width=tab1_found_ip.winfo_width(), anchor="nw")
        root.update_idletasks()
        now_x,now_y = menu_frame_founded.winfo_rootx(),menu_frame_founded.winfo_rooty()
        print(f"Created founded menu at: {now_x, now_y}")
    except Exception as e:
        print(f"[E]Menu cant be created: {e}")

def open_lang_menu(event):
    print("clicked")
    root.update_idletasks()
    if menu_frame_lang.winfo_viewable():
        menu_frame_lang.place_forget()
        print("menu_frame_lang is deleted")
        return
    buton_x,buton_y = tab1_lang_button.winfo_rootx(),tab1_lang_button.winfo_rooty()
    buton_xp,buton_yp = tab_connect.winfo_rootx(),tab_connect.winfo_rooty()

    print("Real screen:",buton_x, buton_y)
    print("This window:",buton_xp, buton_yp)
    try:
        menu_frame_lang.place(x=(buton_x - buton_xp), y=(buton_y - buton_yp)+tab1_lang_button.winfo_height(), width=tab1_lang_button.winfo_width(), anchor="nw")
        menu_frame_lang1.pack(fill=X)
        menu_frame_lang2.pack(fill=X)
        menu_frame_lang3.pack(fill=X)
        root.update_idletasks()
        now_x,now_y = menu_frame_lang.winfo_rootx(),menu_frame_lang.winfo_rooty()
        print(f"Created founded menu at: {now_x, now_y}")
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
def founded_enter_choosed_ip(event, ip):
    print(f"Pressed {ip}")
    if menu_frame_founded.winfo_exists() and menu_frame_founded.winfo_viewable():
        tab1_input2.delete(0, "end")
        tab1_input2.insert(0, ip)
        
#FOR MESSAGE BALLON, GEMINI GIVED ME THIS CODE------------------
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

#CATCHING WINDOW SIZE FOR IP MENU
def catch_size(event):
    global paned_window, upper_frame
    if event.widget == root:
        if menu_frame.winfo_viewable() and menu_frame.winfo_exists():
            menu_frame.place_forget()
            print("menu_frame is deleted")
        else:
            print("menu_frame is null")
        if menu_frame_founded.winfo_viewable() and menu_frame_founded.winfo_exists():
            menu_frame_founded.place_forget()
            print("menu_frame_founded is deleted")
        if event.height > 600:
            print(event.height)
            paned_window.paneconfigure(upper_frame, minsize=350, height=550)
            print("Minsize ayarlandı")

#FOR CATCHING CURRENT TAB
def on_tab_selected(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    print(tab_text)

def update_all_widgets(lang_code):
    global current_lang
    current_lang = lang_code
    new_texts = data[lang_code]

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
    active_adb = adb_connect(tab1_input2,root, tab1_label_failed2,found_path, tab1_stop_adb, connected_devicesips, update_ui)
def stop_adb_event(event):
    if active_adb:
        active_adb.stop_adb()
active_nmap = None
def scan(event):
    global active_nmap
    active_nmap = nmap_scan(tab1_input, log_text, tab1_label_failed, tab1_stop_nmap, root, update_ui, menu_frame_founded, founded_enter_choosed_ip, button_references)
def stop_nmap_event(event):
    if active_nmap:
        active_nmap.stop_nmap()
def checks():
    checker = startup_check()
    checker.app_startup(connected_devicesips, current_lang, data)
    
#-----------------------------------------

tries = [
    "C:/platform-tools/adb.exe",
    os.path.expanduser("~") + "/AppData/Local/Android/Sdk/platform-tools/adb.exe"
]

found_path = None

for path in tries:
    if os.path.exists(path):
        found_path = path

if found_path:
    print(f"Found: {found_path}")
else:
    print("Not found")

def devices():
    print("a")
    return

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
    if menu_frame_founded.winfo_viewable() and menu_frame_founded.winfo_exists():
        menu_frame_founded.place_forget()
        print("menu_frame_founded is deleted")

def minimize_window():
    root.state('withdrawn')
    root.overrideredirect(False) 
    root.iconify()

def on_deiconify(event):
    if not root.overrideredirect():
        root.overrideredirect(True)
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

#MAIN PANEL
root = Tk()
root.minsize(500,300)
root.title("AdbEz")
root.config(background="gray")
root.bind("<Map>", on_deiconify)
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

def on_enter_max(event):
    max_btn.config(bg="lightblue")
def leave_enter_max(event):
    max_btn.config(bg="#2d2d2d")
def on_enter_min(event):
    min_btn.config(bg="lightblue")
def leave_enter_min(event):
    min_btn.config(bg="#2d2d2d")
def on_enter_close(event):
    close_btn.config(bg="red")
def leave_enter_close(event):
    close_btn.config(bg="#2d2d2d")
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
        with open("check.json", "r", encoding="utf-8") as f:
            check_data = json.load(f)
        ip_to_remove = label_text.strip()
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
min_btn.bind("<Enter>", on_enter_min)
min_btn.bind("<Leave>", leave_enter_min)

#FULL SCREEN(□)
max_btn = Button(title_bar, text="▢", bg="#2d2d2d", fg="white", bd=0, 
                 activebackground="#404040", activeforeground="white",
                 command=maximize_window, width=4, font=("Arial", 10))
max_btn.pack(side="right", fill="y")
max_btn.bind("<Enter>", on_enter_max)
max_btn.bind("<Leave>", leave_enter_max)

close_btn = Button(title_bar, text="✕", bg="#2d2d2d", fg="white", bd=0, 
                      activebackground="red", command=root.destroy, width=4)
close_btn.pack(side="right", fill="y")
style.configure("Redbg.TButton", background="red")
close_btn.bind("<Enter>", on_enter_close)
close_btn.bind("<Leave>", leave_enter_close)

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
paned_window2 = PanedWindow(tab_keyevents, orient=HORIZONTAL, bd=1, relief="sunken", sashwidth=4, sashrelief="sunken")
upper_frame2 = Frame(paned_window2)
paned_window2.add(upper_frame2, minsize=700)
paned_window2.pack(fill=BOTH,expand=True, anchor="w", side="left")
lower_frame2 = Frame(paned_window2)
paned_window2.add(lower_frame2,minsize=50)
lower_frame2_log_label = Frame(lower_frame2)
lower_frame2_log_label.grid(row=0, column=0)

upper_frame2.config(bg="red")
lower_frame2.config(bg="lightblue")
lower_frame2.rowconfigure(2, weight=1)
lower_frame2.grid_columnconfigure(0, weight=1)
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
lang_btn_conatiner = ttk.Frame(upper_frame)
lang_btn_conatiner.grid(row=0, column=0, sticky="nw")
#TAB_KEYEVENTS--------------------------------------
canvas2 = Canvas(upper_frame2, bg="red", highlightthickness=0)
canvas2.pack(side="left", fill="both", expand=True)
scrollable_bar = ttk.Scrollbar(upper_frame2, orient="vertical", command=canvas2.yview)
scrollable_bar.pack(fill=Y, side="right", anchor="e")
canvas2.configure(yscrollcommand=scrollable_bar.set)
scrollable_content = Frame(canvas2, bg="red")
canvas2.create_window((0, 0), window=scrollable_content, anchor="nw")
scrollable_content.bind("<Configure>", on_frame_configure)
#WINDOWS-----------------------
canvas2.bind_all("<MouseWheel>", _on_mousewheel)
#------------------------------
#LINUX-------------------------
canvas2.bind_all("<Button-4>", _on_scroll_up)
canvas2.bind_all("<Button-5>", _on_scroll_down)
#------------------------------
up_bar = Frame(scrollable_content)
up_bar.pack()
up_bar.columnconfigure(0, weight=1)
up_bar.columnconfigure(3, weight=1)
search = Entry(up_bar, text="Naber")
category_button = Button(up_bar, text="Categories")
search.grid(row=0, column=1)
category_button.grid(row=0, column=2)

keyevents_buttons = []
keyevents_labels = []
for i in range(288):
    row_frame = Frame(scrollable_content)
    row_frame.pack(fill=X, pady=2)
    test_label = Label(row_frame, text="Test", width=65)
    test_label.pack(side="right", expand=True)
    name = f"Input keyevent {i+1}"
    buton = Button(row_frame, text=name, bg="lightblue")
    buton.pack()
    keyevents_buttons.append(buton)
    keyevents_labels.append(test_label)
print(keyevents_labels)
keyevents_labels[0].configure(text="It simulates a press of the soft left key (KEYCODE_SOFT_LEFT) on your device")
keyevents_labels[1].configure(text="It simulates a press of the soft right key.")
keyevents_labels[2].configure(text="It simulates a press of the Home button")
keyevents_labels[3].configure(text="It simulates a press of the Back button")
keyevents_labels[4].configure(text="It simulates a press of the Call button")
keyevents_labels[5].configure(text="It simulates a press of the End Call button")
keyevents_labels[6].configure(text="It simulates a press of the '0' number key")
keyevents_labels[7].configure(text="It simulates a press of the '1' number key")
keyevents_labels[8].configure(text="It simulates a press of the '2' number key")
keyevents_labels[9].configure(text="It simulates a press of the '3' number key")
keyevents_labels[10].configure(text="It simulates a press of the '4' number key")
keyevents_labels[11].configure(text="It simulates a press of the '5' number key")
keyevents_labels[12].configure(text="It simulates a press of the '6' number key")
keyevents_labels[13].configure(text="It simulates a press of the '7' number key")
keyevents_labels[14].configure(text="It simulates a press of the '8' number key")
keyevents_labels[15].configure(text="It simulates a press of the '9' number key")
keyevents_labels[16].configure(text="It simulates a press of the Star (*) key")
keyevents_labels[17].configure(text="It simulates a press of the Pound (#) key")
keyevents_labels[18].configure(text="It simulates a press of the D-pad Up button")
keyevents_labels[19].configure(text="It simulates a press of the D-pad Down button")
keyevents_labels[20].configure(text="It simulates a press of the D-pad Left button")
keyevents_labels[21].configure(text="It simulates a press of the D-pad Right button")
keyevents_labels[22].configure(text="It simulates a press of the D-pad Center button")
keyevents_labels[23].configure(text="It simulates a press of the Volume Up button")
keyevents_labels[24].configure(text="It simulates a press of the Volume Down button")
keyevents_labels[25].configure(text="It simulates a press of the Power button")
keyevents_labels[26].configure(text="It simulates a press of the Camera button")
keyevents_labels[27].configure(text="It simulates a press of the Clear key")
keyevents_labels[28].configure(text="It simulates a press of the 'A' key")
keyevents_labels[29].configure(text="It simulates a press of the 'B' key")
keyevents_labels[30].configure(text="It simulates a press of the 'C' key")
keyevents_labels[31].configure(text="It simulates a press of the 'D' key")
keyevents_labels[32].configure(text="It simulates a press of the 'E' key")
keyevents_labels[33].configure(text="It simulates a press of the 'F' key")
keyevents_labels[34].configure(text="It simulates a press of the 'G' key")
keyevents_labels[35].configure(text="It simulates a press of the 'H' key")
keyevents_labels[36].configure(text="It simulates a press of the 'I' key")
keyevents_labels[37].configure(text="It simulates a press of the 'J' key")
keyevents_labels[38].configure(text="It simulates a press of the 'K' key")
keyevents_labels[39].configure(text="It simulates a press of the 'L' key")
keyevents_labels[40].configure(text="It simulates a press of the 'M' key")
keyevents_labels[41].configure(text="It simulates a press of the 'N' key")
keyevents_labels[42].configure(text="It simulates a press of the 'O' key")
keyevents_labels[43].configure(text="It simulates a press of the 'P' key")
keyevents_labels[44].configure(text="It simulates a press of the 'Q' key")
keyevents_labels[45].configure(text="It simulates a press of the 'R' key")
keyevents_labels[46].configure(text="It simulates a press of the 'S' key")
keyevents_labels[47].configure(text="It simulates a press of the 'T' key")
keyevents_labels[48].configure(text="It simulates a press of the 'U' key")
keyevents_labels[49].configure(text="It simulates a press of the 'V' key")
keyevents_labels[50].configure(text="It simulates a press of the 'W' key")
keyevents_labels[51].configure(text="It simulates a press of the 'X' key")
keyevents_labels[52].configure(text="It simulates a press of the 'Y' key")
keyevents_labels[53].configure(text="It simulates a press of the 'Z' key")
keyevents_labels[54].configure(text="It simulates a press of the Comma (,) key")
keyevents_labels[55].configure(text="It simulates a press of the Period (.) key")
keyevents_labels[56].configure(text="It simulates a press of the Left Alt key")
keyevents_labels[57].configure(text="It simulates a press of the Right Alt key")
keyevents_labels[58].configure(text="It simulates a press of the Left Shift key")
keyevents_labels[59].configure(text="It simulates a press of the Right Shift key")
keyevents_labels[60].configure(text="It simulates a press of the Tab key")
keyevents_labels[61].configure(text="It simulates a press of the Space key")
keyevents_labels[62].configure(text="It simulates a press of the Symbol key")
keyevents_labels[63].configure(text="It simulates a press of the Explorer (Browser) key")
keyevents_labels[64].configure(text="It simulates a press of the Envelope (Mail) key")
keyevents_labels[65].configure(text="It simulates a press of the Enter key")
keyevents_labels[66].configure(text="It simulates a press of the Delete (Backspace) key")
keyevents_labels[67].configure(text="It simulates a press of the Grave (`) key")
keyevents_labels[68].configure(text="It simulates a press of the Minus (-) key")
keyevents_labels[69].configure(text="It simulates a press of the Equals (=) key")
keyevents_labels[70].configure(text="It simulates a press of the Left Bracket ([) key")
keyevents_labels[71].configure(text="It simulates a press of the Right Bracket (]) key")
keyevents_labels[72].configure(text="It simulates a press of the Backslash (\) key")
keyevents_labels[73].configure(text="It simulates a press of the Semicolon (;) key")
keyevents_labels[74].configure(text="It simulates a press of the Apostrophe (') key")
keyevents_labels[75].configure(text="It simulates a press of the Slash (/) key")
keyevents_labels[76].configure(text="It simulates a press of the At (@) key")
keyevents_labels[77].configure(text="It simulates a press of the Num Lock key")
keyevents_labels[78].configure(text="It simulates a press of the Headset Hook key")
keyevents_labels[79].configure(text="It simulates a press of the Camera Focus key")
keyevents_labels[80].configure(text="It simulates a press of the Plus (+) key")
keyevents_labels[81].configure(text="It simulates a press of the Menu key")
keyevents_labels[82].configure(text="It simulates a press of the Notification key")
keyevents_labels[83].configure(text="It simulates a press of the Search key")
keyevents_labels[84].configure(text="It simulates a press of the Media Play/Pause key")
keyevents_labels[85].configure(text="It simulates a press of the Media Stop key")
keyevents_labels[86].configure(text="It simulates a press of the Media Next key")
keyevents_labels[87].configure(text="It simulates a press of the Media Previous key")
keyevents_labels[88].configure(text="It simulates a press of the Media Rewind key")
keyevents_labels[89].configure(text="It simulates a press of the Media Fast Forward key")
keyevents_labels[90].configure(text="It simulates a press of the Mute key")
keyevents_labels[91].configure(text="It simulates a press of the Page Up key")
keyevents_labels[92].configure(text="It simulates a press of the Page Down key")
keyevents_labels[93].configure(text="It simulates a press of the Picture Symbols key")
keyevents_labels[94].configure(text="It simulates a press of the Switch Charset key")
keyevents_labels[95].configure(text="It simulates a press of the Gamepad A button")
keyevents_labels[96].configure(text="It simulates a press of the Gamepad B button")
keyevents_labels[97].configure(text="It simulates a press of the Gamepad C button")
keyevents_labels[98].configure(text="It simulates a press of the Gamepad X button")
keyevents_labels[99].configure(text="It simulates a press of the Gamepad Y button")
keyevents_labels[100].configure(text="It simulates a press of the Gamepad Z button")
keyevents_labels[101].configure(text="It simulates a press of the Gamepad L1 button")
keyevents_labels[102].configure(text="It simulates a press of the Gamepad R1 button")
keyevents_labels[103].configure(text="It simulates a press of the Gamepad L2 button")
keyevents_labels[104].configure(text="It simulates a press of the Gamepad R2 button")
keyevents_labels[105].configure(text="It simulates a press of the Gamepad Left Thumb button")
keyevents_labels[106].configure(text="It simulates a press of the Gamepad Right Thumb button")
keyevents_labels[107].configure(text="It simulates a press of the Gamepad Start button")
keyevents_labels[108].configure(text="It simulates a press of the Gamepad Select button")
keyevents_labels[109].configure(text="It simulates a press of the Gamepad Mode button")
keyevents_labels[110].configure(text="It simulates a press of the Escape key")
keyevents_labels[111].configure(text="It simulates a press of the Forward Delete key")
keyevents_labels[112].configure(text="It simulates a press of the Left Control key")
keyevents_labels[113].configure(text="It simulates a press of the Right Control key")
keyevents_labels[114].configure(text="It simulates a press of the Caps Lock key")
keyevents_labels[115].configure(text="It simulates a press of the Scroll Lock key")
keyevents_labels[116].configure(text="It simulates a press of the Left Meta (Windows/Command) key")
keyevents_labels[117].configure(text="It simulates a press of the Right Meta (Windows/Command) key")
keyevents_labels[118].configure(text="It simulates a press of the Function (Fn) key")
keyevents_labels[119].configure(text="It simulates a press of the System Request / Print Screen key")
keyevents_labels[120].configure(text="It simulates a press of the Break / Pause key")
keyevents_labels[121].configure(text="It simulates a press of the Home (Move to start) key")
keyevents_labels[122].configure(text="It simulates a press of the End (Move to end) key")
keyevents_labels[123].configure(text="It simulates a press of the Insert key")
keyevents_labels[124].configure(text="It simulates a press of the Forward key")
keyevents_labels[125].configure(text="It simulates a press of the Media Play key")
keyevents_labels[126].configure(text="It simulates a press of the Media Pause key")
keyevents_labels[127].configure(text="It simulates a press of the Media Close key")
keyevents_labels[128].configure(text="It simulates a press of the Media Eject key")
keyevents_labels[129].configure(text="It simulates a press of the Media Record key")
keyevents_labels[130].configure(text="It simulates a press of the F1 key")
keyevents_labels[131].configure(text="It simulates a press of the F2 key")
keyevents_labels[132].configure(text="It simulates a press of the F3 key")
keyevents_labels[133].configure(text="It simulates a press of the F4 key")
keyevents_labels[134].configure(text="It simulates a press of the F5 key")
keyevents_labels[135].configure(text="It simulates a press of the F6 key")
keyevents_labels[136].configure(text="It simulates a press of the F7 key")
keyevents_labels[137].configure(text="It simulates a press of the F8 key")
keyevents_labels[138].configure(text="It simulates a press of the F9 key")
keyevents_labels[139].configure(text="It simulates a press of the F10 key")
keyevents_labels[140].configure(text="It simulates a press of the F11 key")
keyevents_labels[141].configure(text="It simulates a press of the F12 key")
keyevents_labels[142].configure(text="It simulates a press of the Num Lock key")
keyevents_labels[143].configure(text="It simulates a press of the Numpad 0 key")
keyevents_labels[144].configure(text="It simulates a press of the Numpad 1 key")
keyevents_labels[145].configure(text="It simulates a press of the Numpad 2 key")
keyevents_labels[146].configure(text="It simulates a press of the Numpad 3 key")
keyevents_labels[147].configure(text="It simulates a press of the Numpad 4 key")
keyevents_labels[148].configure(text="It simulates a press of the Numpad 5 key")
keyevents_labels[149].configure(text="It simulates a press of the Numpad 6 key")
keyevents_labels[150].configure(text="It simulates a press of the Numpad 7 key")
keyevents_labels[151].configure(text="It simulates a press of the Numpad 8 key")
keyevents_labels[152].configure(text="It simulates a press of the Numpad 9 key")
keyevents_labels[153].configure(text="It simulates a press of the Numpad Divide (/) key")
keyevents_labels[154].configure(text="It simulates a press of the Numpad Multiply (*) key")
keyevents_labels[155].configure(text="It simulates a press of the Numpad Subtract (-) key")
keyevents_labels[156].configure(text="It simulates a press of the Numpad Add (+) key")
keyevents_labels[157].configure(text="It simulates a press of the Numpad Dot (.) key")
keyevents_labels[158].configure(text="It simulates a press of the Numpad Comma (,) key")
keyevents_labels[159].configure(text="It simulates a press of the Numpad Enter key")
keyevents_labels[160].configure(text="It simulates a press of the Numpad Equals (=) key")
keyevents_labels[161].configure(text="It simulates a press of the Numpad Left Parenthesis key")
keyevents_labels[162].configure(text="It simulates a press of the Numpad Right Parenthesis key")
keyevents_labels[163].configure(text="It simulates a press of the Volume Mute key")
keyevents_labels[164].configure(text="It simulates a press of the Info key")
keyevents_labels[165].configure(text="It simulates a press of the Channel Up key")
keyevents_labels[166].configure(text="It simulates a press of the Channel Down key")
keyevents_labels[167].configure(text="It simulates a press of the Zoom In key")
keyevents_labels[168].configure(text="It simulates a press of the Zoom Out key")
keyevents_labels[169].configure(text="It simulates a press of the TV key")
keyevents_labels[170].configure(text="It simulates a press of the Window key")
keyevents_labels[171].configure(text="It simulates a press of the Guide key")
keyevents_labels[172].configure(text="It simulates a press of the DVR key")
keyevents_labels[173].configure(text="It simulates a press of the Bookmark key")
keyevents_labels[174].configure(text="It simulates a press of the Captions key")
keyevents_labels[175].configure(text="It simulates a press of the Settings key")
keyevents_labels[176].configure(text="It simulates a press of the TV Power key")
keyevents_labels[177].configure(text="It simulates a press of the TV Input key")
keyevents_labels[178].configure(text="It simulates a press of the Set-top Box Power key")
keyevents_labels[179].configure(text="It simulates a press of the Set-top Box Input key")
keyevents_labels[180].configure(text="It simulates a press of the A/V Receiver Power key")
keyevents_labels[181].configure(text="It simulates a press of the A/V Receiver Input key")
keyevents_labels[182].configure(text="It simulates a press of the Program Red key")
keyevents_labels[183].configure(text="It simulates a press of the Program Green key")
keyevents_labels[184].configure(text="It simulates a press of the Program Yellow key")
keyevents_labels[185].configure(text="It simulates a press of the Program Blue key")
keyevents_labels[186].configure(text="It simulates a press of the App Switch key")
keyevents_labels[187].configure(text="It simulates a press of the Generic Button 1 key")
keyevents_labels[188].configure(text="It simulates a press of the Generic Button 2 key")
keyevents_labels[189].configure(text="It simulates a press of the Generic Button 3 key")
keyevents_labels[190].configure(text="It simulates a press of the Generic Button 4 key")
keyevents_labels[191].configure(text="It simulates a press of the Generic Button 5 key")
keyevents_labels[192].configure(text="It simulates a press of the Generic Button 6 key")
keyevents_labels[193].configure(text="It simulates a press of the Generic Button 7 key")
keyevents_labels[194].configure(text="It simulates a press of the Generic Button 8 key")
keyevents_labels[195].configure(text="It simulates a press of the Generic Button 9 key")
keyevents_labels[196].configure(text="It simulates a press of the Generic Button 10 key")
keyevents_labels[197].configure(text="It simulates a press of the Generic Button 11 key")
keyevents_labels[198].configure(text="It simulates a press of the Generic Button 12 key")
keyevents_labels[199].configure(text="It simulates a press of the Generic Button 13 key")
keyevents_labels[200].configure(text="It simulates a press of the Generic Button 14 key")
keyevents_labels[201].configure(text="It simulates a press of the Generic Button 15 key")
keyevents_labels[202].configure(text="It simulates a press of the Generic Button 16 key")
keyevents_labels[203].configure(text="It simulates a press of the Language Switch key")
keyevents_labels[204].configure(text="It simulates a press of the Manner Mode key")
keyevents_labels[205].configure(text="It simulates a press of the 3D Mode key")
keyevents_labels[206].configure(text="It simulates a press of the Contacts key")
keyevents_labels[207].configure(text="It simulates a press of the Calendar key")
keyevents_labels[208].configure(text="It simulates a press of the Music key")
keyevents_labels[209].configure(text="It simulates a press of the Calculator key")
keyevents_labels[210].configure(text="It simulates a press of the Zenkaku/Hankaku (Japanese) key")
keyevents_labels[211].configure(text="It simulates a press of the Eisu (Japanese) key")
keyevents_labels[212].configure(text="It simulates a press of the Muhenkan (Japanese) key")
keyevents_labels[213].configure(text="It simulates a press of the Henkan (Japanese) key")
keyevents_labels[214].configure(text="It simulates a press of the Katakana/Hiragana (Japanese) key")
keyevents_labels[215].configure(text="It simulates a press of the Yen (Japanese) key")
keyevents_labels[216].configure(text="It simulates a press of the Ro (Japanese) key")
keyevents_labels[217].configure(text="It simulates a press of the Kana (Japanese) key")
keyevents_labels[218].configure(text="It simulates a press of the Assist key")
keyevents_labels[219].configure(text="It simulates a press of the Brightness Down key")
keyevents_labels[220].configure(text="It simulates a press of the Brightness Up key")
keyevents_labels[221].configure(text="It simulates a press of the Media Audio Track key")
keyevents_labels[222].configure(text="It simulates a press of the Sleep key")
keyevents_labels[223].configure(text="It simulates a press of the Wakeup key")
keyevents_labels[224].configure(text="It simulates a press of the Pairing key")
keyevents_labels[225].configure(text="It simulates a press of the Media Top Menu key")
keyevents_labels[226].configure(text="It simulates a press of the '11' number key")
keyevents_labels[227].configure(text="It simulates a press of the '12' number key")
keyevents_labels[228].configure(text="It simulates a press of the Last Channel key")
keyevents_labels[229].configure(text="It simulates a press of the TV Data Service key")
keyevents_labels[230].configure(text="It simulates a press of the Voice Assist key")
keyevents_labels[231].configure(text="It simulates a press of the TV Radio Service key")
keyevents_labels[232].configure(text="It simulates a press of the TV Teletext key")
keyevents_labels[233].configure(text="It simulates a press of the TV Number Entry key")
keyevents_labels[234].configure(text="It simulates a press of the TV Terrestrial Analog key")
keyevents_labels[235].configure(text="It simulates a press of the TV Terrestrial Digital key")
keyevents_labels[236].configure(text="It simulates a press of the TV Satellite key")
keyevents_labels[237].configure(text="It simulates a press of the TV Satellite BS key")
keyevents_labels[238].configure(text="It simulates a press of the TV Satellite CS key")
keyevents_labels[239].configure(text="It simulates a press of the TV Satellite Service key")
keyevents_labels[240].configure(text="It simulates a press of the TV Network key")
keyevents_labels[241].configure(text="It simulates a press of the TV Antenna Cable key")
keyevents_labels[242].configure(text="It simulates a press of the TV Input HDMI 1 key")
keyevents_labels[243].configure(text="It simulates a press of the TV Input HDMI 2 key")
keyevents_labels[244].configure(text="It simulates a press of the TV Input HDMI 3 key")
keyevents_labels[245].configure(text="It simulates a press of the TV Input HDMI 4 key")
keyevents_labels[246].configure(text="It simulates a press of the TV Input Composite 1 key")
keyevents_labels[247].configure(text="It simulates a press of the TV Input Composite 2 key")
keyevents_labels[248].configure(text="It simulates a press of the TV Input Component 1 key")
keyevents_labels[249].configure(text="It simulates a press of the TV Input Component 2 key")
keyevents_labels[250].configure(text="It simulates a press of the TV Input VGA 1 key")
keyevents_labels[251].configure(text="It simulates a press of the TV Audio Description key")
keyevents_labels[252].configure(text="It simulates a press of the TV Audio Description Mix Up key")
keyevents_labels[253].configure(text="It simulates a press of the TV Audio Description Mix Down key")
keyevents_labels[254].configure(text="It simulates a press of the TV Zoom Mode key")
keyevents_labels[255].configure(text="It simulates a press of the TV Contents Menu key")
keyevents_labels[256].configure(text="It simulates a press of the TV Media Context Menu key")
keyevents_labels[257].configure(text="It simulates a press of the TV Timer Programming key")
keyevents_labels[258].configure(text="It simulates a press of the Help key")
keyevents_labels[259].configure(text="It simulates a press of the Navigate Previous key")
keyevents_labels[260].configure(text="It simulates a press of the Navigate Next key")
keyevents_labels[261].configure(text="It simulates a press of the Navigate In key")
keyevents_labels[262].configure(text="It simulates a press of the Navigate Out key")
keyevents_labels[263].configure(text="It simulates a press of the Stem Primary key")
keyevents_labels[264].configure(text="It simulates a press of the Stem 1 key")
keyevents_labels[265].configure(text="It simulates a press of the Stem 2 key")
keyevents_labels[266].configure(text="It simulates a press of the Stem 3 key")
keyevents_labels[267].configure(text="It simulates a press of the D-pad Up-Left button")
keyevents_labels[268].configure(text="It simulates a press of the D-pad Down-Left button")
keyevents_labels[269].configure(text="It simulates a press of the D-pad Up-Right button")
keyevents_labels[270].configure(text="It simulates a press of the D-pad Down-Right button")
keyevents_labels[271].configure(text="It simulates a press of the Media Skip Forward key")
keyevents_labels[272].configure(text="It simulates a press of the Media Skip Backward key")
keyevents_labels[273].configure(text="It simulates a press of the Media Step Forward key")
keyevents_labels[274].configure(text="It simulates a press of the Media Step Backward key")
keyevents_labels[275].configure(text="It simulates a press of the Soft Sleep key")
keyevents_labels[276].configure(text="It simulates a press of the Cut key")
keyevents_labels[277].configure(text="It simulates a press of the Copy key")
keyevents_labels[278].configure(text="It simulates a press of the Paste key")
keyevents_labels[279].configure(text="It simulates a press of the System Navigation Up key")
keyevents_labels[280].configure(text="It simulates a press of the System Navigation Down key")
keyevents_labels[281].configure(text="It simulates a press of the System Navigation Left key")
keyevents_labels[282].configure(text="It simulates a press of the System Navigation Right key")
keyevents_labels[283].configure(text="It simulates a press of the All Apps key")
keyevents_labels[284].configure(text="It simulates a press of the Refresh key")
keyevents_labels[285].configure(text="It simulates a press of the Thumbs Up key")
keyevents_labels[286].configure(text="It simulates a press of the Thumbs Down key")
keyevents_labels[287].configure(text="It simulates a press of the Profile Switch key")
#for widget in  scrollable_content.winfo_children():
#    widget.pack_configure(pady=1)
#---------------------------------------------------
#-----------------------------------------------------
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
tab1_nmap_buton = Button(nmap_btn_container, text=data[current_lang]["l4"], name="l4")
tab1_label2 = ttk.Label(upper_frame, text=data[current_lang]["l5"], name="l5")
tab1_input2 = ttk.Entry(adb_input_row)
tab1_connect_buton = Button(adb_btn_container, text=data[current_lang]["l6"], name="l6")
tab1_label_failed = Label(upper_frame, text="", foreground="red",width=26)
tab1_label_failed2 = Label(upper_frame, text="", foreground="red",width=26)
tab1_lang_button = Button(lang_btn_conatiner, text="Languages", width=10, height="1", bg="lightblue")
tab1_disconnect_button = Button(adb_btn_container, text=data[current_lang]["l19"], name="l19")
tab1_disconnect_button.grid(row=1, column=0)
tab1_disconnect_button.bind("<Button-1>", disconnect_ip)

tab2_log_label = Label(lower_frame2_log_label, text="Logs", background="lightblue")
tab2_log_label.grid(row=0, column=0)
tab2_log_box = Text(lower_frame2)
tab2_log_box.grid(row=1, column=0, rowspan=2,sticky="w", padx=(5,5))

connected_container = ttk.Frame(upper_frame)
connected_container.grid(row=0, column=2, sticky="ne")

connected_devices = Label(connected_container, text=data[current_lang]["l20"], name="l20")
connected_devicesips = Label(connected_container)
is_text_empty = connected_devicesips.cget("text")
connected_devices.grid(row=0, column=0, sticky="ne")
connected_devicesips.grid(row=1, column=0 , sticky="nsew")

#I WANT TO USE MENUBUTTON BUT IT CAN'T DO THE FEATURES I WANT,SO WE WILL CREATE OUR OWN MENU
#tab1_choose_ip = ttk.Menubutton(nmap_input_row, text="Choose")
tab1_choose_ip = Button(nmap_input_row, text=data[current_lang]["l13"], name="l13", takefocus=False, width=10)
tab1_found_ip = ttk.Button(adb_input_row, text=data[current_lang]["l14"], name="l14", takefocus=False)
#STOP NMAP-ADB BUTTON
tab1_stop_nmap = ttk.Button(nmap_btn_container,text=data[current_lang]["l15"], name="l15",takefocus=False, style="Redbg.TButton")
tab1_stop_adb = ttk.Button(adb_btn_container, text=data[current_lang]["l15"], name="l15", takefocus=False, style="Redbg.TButton")
# NMAP IP MENU
menu_frame = Frame(upper_frame,background="red")
print(tab1_choose_ip.winfo_width())
menu_frame_in1 = Button(menu_frame,text="192.168.1.0/24", font=custom_font)
menu_frame_in2 = Button(menu_frame,text="127.0.0.0/24")
#ADB IP MENU
menu_frame_founded = Frame(upper_frame, background="red")
log_text = Text(lower_frame, height=1)
#LANGUAGES MENU
menu_frame_lang = Frame(upper_frame, background="red")
menu_frame_lang1 = Button(menu_frame_lang, text="English")
menu_frame_lang2 = Button(menu_frame_lang, text="Turkce")
menu_frame_lang3 = Button(menu_frame_lang, text="Português")

#PLACEMENT
tab1_lang_button.grid(row=0, column=0, sticky="nsew")

tab1_label.grid(row=1, column=1, sticky="n", pady=(0, 5), padx=(0, 285))
tab1_input.grid(row=0, column=1, sticky="ew", pady=(0, 10))
tab1_choose_ip.grid(row=0, column=2, sticky="we", padx=(15,0), pady=(0,10))
tab1_nmap_buton.grid(row=0, column=0, sticky="ew")
nmap_btn_container.columnconfigure(0, minsize=100)

tab1_label2.grid(row=4, column=1, sticky="n", padx=(0, 295))
tab1_input2.grid(row=0, column=1, sticky="ew")
tab1_found_ip.grid(row=0, column=2, sticky="ew", padx=(15,0))
tab1_connect_buton.grid(row=0, column=0, sticky="ew",padx=(5,0))
log_text.pack(fill=BOTH, expand=True)

#BUTTON EVENTS-----------------------------------------------
tab1_lang_button.bind("<Button-1>", open_lang_menu)
tab1_choose_ip.bind("<Button-1>", open_ip_menu)
#tab1_nmap_buton.bind("<Button-1>", find)
tab1_nmap_buton.bind("<Button-1>", scan)
tab1_connect_buton.bind("<Button-1>", connect)
tab1_found_ip.bind("<Button-1>", open_founded_ip_menu)

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

checks()
show_in_taskbar(root)
root.mainloop()
