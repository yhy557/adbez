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

def app_startup():
    print(f"{data[current_lang]["l1"]}")
    default_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(default_path, "check.json")

    now = datetime.now()
    json_default_data = {
        "last_entered": f"{now}",
        "last_commands": {},
        "finded_ips": {}
    }

    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(json_default_data, f, indent=4, ensure_ascii=False)
            pass
    else:
        with open(file_path, "w") as f:
            json.dump(json_default_data, f, indent=4, ensure_ascii=False)
            pass

    #CONTROLLING SOMETHINGS
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    print(f"{data[current_lang]["l2"]}")

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
    buton_x,buton_y = tab1_finded_ip.winfo_rootx(),tab1_finded_ip.winfo_rooty()
    buton_xp,buton_yp = tab_connect.winfo_rootx(),tab_connect.winfo_rooty()

    print("Real screen:",buton_x, buton_y)
    print("This window:",buton_xp, buton_yp)
    try:
        menu_frame_founded.place(x=(buton_x - buton_xp), y=(buton_y - buton_yp)+tab1_finded_ip.winfo_height(), width=tab1_finded_ip.winfo_width(), anchor="nw")
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

def add_ips_in_menu(ip):
    print("Hello i am add_ips_menu")
    new_button = Button(menu_frame_founded, text=f"{ip}")
    new_button.pack(fill="x")
    new_button.bind("<Button-1>", lambda event, ip=ip: founded_enter_choosed_ip(event, ip))
    button_references.append(new_button)
    print(f"Founded ipsss: {new_button}")

    #ips_length = len(founded_ips)
    #for i in range(ips_length):
    #    texts = f"founded_menu_frame_in{i}"
    #    texts = Button(menu_frame_founded, text=f"{founded_ips[{i}]}")

class nmap_scan:
    def __init__(self):
        self.current_process = None
        self.stopla = False
        self.founded_ips = []
        self.current_ip_has_adb = False
        t = threading.Thread(target=self.try_find)
        t.start()
    def try_find(self):
        ip = tab1_input.get()
        default_path = os.path.dirname(os.path.abspath(__file__))
        main_path_py = os.path.join(default_path, "now_logs.txt")

        if not ip:
            #WE ARE GETTING ENTRY COORDINATES TO THE FAILED_LABELS
            root.update_idletasks()
            x = tab1_input.winfo_rootx()
            y = tab1_input.winfo_rooty()
            print(f"x degeri: {x}, y degeri:{y}")
            tab1_label_failed.place(x=x-250,y=y-70)
            print("Nothing has writed")
            tab1_label_failed.config(text="Failed.Please write an IP address")
            root.after(5000, lambda: tab1_label_failed.place_forget())
            return
        self.stopla = False
        
        log_text.config(state="normal")
        log_text.insert("1.0", f"[{ip}]Scanning all ports...")
        root.after(0, self.scanning_animation)
        root.after(100, lambda: tab1_stop_nmap.grid(row=0, column=1, sticky="w",padx=(5,0)))

        self.current_process = subprocess.Popen(f"nmap {ip}", shell=True, stdout=subprocess.PIPE, text=True)

        full_output = ""
        while True:
            line = self.current_process.stdout.readline()
            if not line or self.stopla:
                break
            full_output += line
            root.after(0, lambda l=line: update_ui(l))
        self.current_process.stdout.close()
        self.current_process.wait()

        with open(fr"{main_path_py}", "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0)
            file.write(full_output)
            file.truncate()
        for lines in content.splitlines():
            check_ips = re.search(r'(\d+\.\d+\.\d+\.\d+)', lines)
            if check_ips:
                checked_ips = check_ips.group(1)
                if checked_ips not in self.founded_ips:
                    self.founded_ips.append(checked_ips)
                    root.after(0, lambda ip=checked_ips: add_ips_in_menu(ip))
        print("Dosya buraya kaydedildi:", os.path.abspath("now_logs.txt"))
        root.after(2000, lambda: self.write_founded_ips())
        if not self.stopla:
            self.stopla = True
            root.after(0, lambda: update_ui("Scan completed"))
        try:
            root.after(0, lambda:tab1_stop_nmap.grid_forget())
            print("stop button is being deleted")
        except Exception as e:
            print(f"Can't deleting stop button: {e}")
        log_text.config(state="disabled")
        return
    def stop_nmap(self):
        if self.current_process:
            system_os = platform.system()
            try:
                if system_os == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.current_process.pid)], 
                                    startupinfo=startupinfo)
                else:
                    import signal
                    try:
                        os.kill(self.current_process.pid, signal.SIGTERM)
                        self.current_process.wait(1)
                    except subprocess.TimeoutExpired:
                        print("The process is resisting, so it will be killed directly...")
                        os.kill(self.current_process.pid, signal.SIGKILL)

                self.stopla = True
                print("Nmap stopped")
                root.after(20, lambda: update_ui("\n[!] NMAP scan is terminated"))
                root.after(0, lambda: tab1_stop_nmap.grid_forget())
            except Exception as e:
                print(f"Nmap scan is can't terminated: {e}")

    def scanning_animation(self, count=0):
        ip = tab1_input.get()
        if not self.stopla:
            dots = [".", "..", "..."]
            log_text.config(state="normal")
            log_text.delete("1.0", "end")
            log_text.insert("1.0", "Status: Scanning" + dots[count % 3] + f"[{ip}]")
            log_text.config(state="disabled")

            root.after(500,lambda: self.scanning_animation(count + 1))
        else:
            log_text.config(state="normal")
            log_text.delete("1.0", "1.end")
            log_text.insert("1.0", "Status: Scanning Completed")
            log_text.config(state="disabled")
            return
    def write_founded_ips(self):
        print(f"IPs ===  {self.founded_ips}")
class adb_connect:
    def __init__(self):
        self.current_process_adb = None
        self.stopla2 = False
        print("Clicked ADB")
        t = threading.Thread(target=self.try_connect)
        t.start()
    def try_connect(self):
        writing = tab1_input2.get().strip()
        print(writing)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if not writing:
            #WE ARE GETTING ENTRY COORDINATES TO THE FAILED_LABELS
            root.update_idletasks()
            x = tab1_input2.winfo_rootx()
            y = tab1_input2.winfo_rooty()
            print(f"x value: {x}, y value:{y}")
            tab1_label_failed2.place(x=x-250,y=y-70)
            tab1_label_failed2.config(text="Failed.Please write an IP address")
            root.after(5000, lambda: tab1_label_failed2.place_forget())
            return
        self.stopla2 = False
        try:
            self.current_process_adb = subprocess.Popen(
                [finded_path, "connect", writing],
                    stdout=subprocess.PIPE,
                    text=True,
                    startupinfo=si
            )
            tab1_stop_adb.grid(row=0, column=1, padx=(5,0))
            full_output = ""
            while True:
                line = self.current_process_adb.stdout.readline()
                if not line or self.stopla2:
                    break
                full_output += line
                root.after(0, lambda l=line: update_ui(l))
            self.current_process_adb.stdout.close()
            self.current_process_adb.wait()
            connected_label_text = connected_devicesips.cget("text")
            connected_label_list = connected_label_text.split()
            new_writing = f"{writing}"
            for i in full_output.lower().split():
                if i == "connected":
                    self.stopla2 = True
                    root.after(0, lambda: update_ui("Connected"))
                    if connected_label_text == "":
                        connected_devicesips.configure(background="lightblue")
                        connected_devicesips.config(text=new_writing)
                    for i in connected_label_list:
                        if i == new_writing:
                            print(f"Already connected {new_writing}")
                            pass
                        else:
                            new_writing = f"{connected_label_text}\n{writing}"
                            connected_devicesips.configure(background="lightblue")
                            connected_devicesips.config(text=new_writing)
            try:
                root.after(0, lambda: tab1_stop_adb.grid_forget())
                print("stop button is being deleted")
            except Exception as e:
                print(f"Can't deleting stop button: {e}")
        except Exception as e:
            print(f"Can't start adb connect: {e}")
    def stop_adb(self):
        system_os = platform.system()
        if self.current_process_adb and self.current_process_adb.poll() is None:
            try:
                if system_os == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.current_process_adb.pid)], 
                                    startupinfo=startupinfo)
                else:
                    import signal
                    try:
                        os.kill(self.current_process_adb.pid, signal.SIGTERM)
                        self.current_process_adb.wait(1)
                    except subprocess.TimeoutExpired:
                        print(f"The process is resisting, so it will be killed directly...")
                        os.kill(self.current_process_adb.pid, signal.SIGKILL)
                print("Adb being stopped")
                root.after(20, lambda: update_ui("\n[!] ADB connect is terminated"))
                root.after(0, lambda: tab1_stop_adb.grid_forget())
            except Exception as e:
                print(f"Nmap scan is can't terminated: {e}")
        else:
            tab1_stop_adb.grid_forget()


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
    active_adb = adb_connect()
def stop_adb_event(event):
    if active_adb:
        active_adb.stop_adb()
active_nmap = None
def scan(event):
    global active_nmap
    active_nmap = nmap_scan()
def stop_nmap_event(event):
    if active_nmap:
        active_nmap.stop_nmap()
#-----------------------------------------
tries = [
    "C:/platform-tools/adb.exe",
    os.path.expanduser("~") + "/AppData/Local/Android/Sdk/platform-tools/adb.exe"
]

finded_path = None

for path in tries:
    if os.path.exists(path):
        finded_path = path

if finded_path:
    print(f"Found: {finded_path}")
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
            [finded_path, "disconnect", label_text],
            stdout=subprocess.PIPE,
            text=True
        )
        print(f"Disconnected to {label_text}")
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
upper_frame2.config(bg="red")
lower_frame2.config(bg="blue")
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
search = Entry(scrollable_content, textvariable="Naber")
search.pack()
for i in range(20):
    name = f"Input keyevent {i}"
    buton = Button(scrollable_content, text=name)
    buton.pack()

for widget in  scrollable_content.winfo_children():
    widget.pack_configure(pady=1)
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
tab1_disconnect_button = Button(adb_btn_container, text="disconnect")
tab1_disconnect_button.grid(row=1, column=0)
tab1_disconnect_button.bind("<Button-1>", disconnect_ip)

connected_container = ttk.Frame(upper_frame)
connected_container.grid(row=0, column=2, sticky="ne")

connected_devices = Label(connected_container, text="Connected IPs")
connected_devicesips = Label(connected_container)
is_text_empty = connected_devicesips.cget("text")
connected_devices.grid(row=0, column=0, sticky="ne")
connected_devicesips.grid(row=1, column=0 , sticky="nsew")

#I WANT TO USE MENUBUTTON BUT IT CAN'T DO THE FEATURES I WANT,SO WE WILL CREATE OUR OWN MENU
#tab1_choose_ip = ttk.Menubutton(nmap_input_row, text="Choose")
tab1_choose_ip = Button(nmap_input_row, text=data[current_lang]["l13"], name="l13", takefocus=False, width=10)
tab1_finded_ip = ttk.Button(adb_input_row, text=data[current_lang]["l14"], name="l14", takefocus=False)
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
tab1_finded_ip.grid(row=0, column=2, sticky="ew", padx=(15,0))
tab1_connect_buton.grid(row=0, column=0, sticky="ew",padx=(5,0))
log_text.pack(fill=BOTH, expand=True)

#BUTTON EVENTS-----------------------------------------------
tab1_lang_button.bind("<Button-1>", open_lang_menu)
tab1_choose_ip.bind("<Button-1>", open_ip_menu)
#tab1_nmap_buton.bind("<Button-1>", find)
tab1_nmap_buton.bind("<Button-1>", scan)
tab1_connect_buton.bind("<Button-1>", connect)
tab1_finded_ip.bind("<Button-1>", open_founded_ip_menu)

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

app_startup()
show_in_taskbar(root)
root.mainloop()
