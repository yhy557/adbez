import threading
import subprocess
import os
import re
import platform
import tkinter
from tkinter import Button
import logging
import json
from dataclasses import dataclass
from settings import settings_style
from utils.file_utils import open_file, write_file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


default_path = os.path.dirname(os.path.abspath(__file__))
main_path_py = os.path.join(default_path, "now_logs.txt")
check_path = os.path.join(default_path, "check.json")



class nmap_ui:
    def __init__(self, app,
                 on_finish=None):
        self.tab1_input             = app.tab1_input
        self.log_text               = app.log_text
        self.tab1_label_failed      = app.tab1_label_failed
        self.tab1_stop_nmap         = app.tab1_stop_nmap
        self.root                   = app.root
        self.menu_frame_found       = app.menu_frame_found
        self.processes_in           = app.processes_in
        self.settings_instance      = app.my_settings
        self.button_references      = app.button_references
        self.shared_nmap_processes  = app.shared_nmap_processes
        self.ongoing_processes      = app.ongoing_processes
        self.active_processes       = app.active_processes
        self.update_ui              = app.update_ui
        self.found_enter_choosed_ip = app.found_enter_choosen_ip
        self.on_finish = on_finish
        self.current_process = None
        self.current_ip_has_adb = False
        self.is_process_running = False


        logging.debug(
            f"button_references type: {type(self.button_references)}")

        self.brain = nmap_brain(
            on_line = lambda line: self.root.after(0, lambda: self.update_ui(line)),
            on_ip_found = lambda ip: self.root.after(0, lambda: self.add_ips_in_menu(ip)),
            on_finish =  lambda inst: self.root.after(0, lambda: self.finished_nmap(inst))
        )
        t = threading.Thread(target=self.brain.try_find, args=(self.tab1_input.get(),))
        t.start()
        self.check_data = open_file(check_path)
        self.show_ui_things(self.tab1_input.get())

    def show_ui_things(self, ip: str):
        logging.debug(f"ip of nmap {ip}")
        # WE ARE GETTING ENTRY COORDINATES TO THE FAILED_LABELS
        if not ip:
            self.root.update_idletasks()
            self.root.after(
                0, lambda: self.tab1_label_failed.place(
                    in_=self.tab1_input, relx=-0.722, rely=0, anchor="nw"
                )
            )
            logging.debug("[show_ui_things]-Nothing has writed")
            self.root.after(0, lambda: self.tab1_label_failed.config(
                text="Failed. Please write an IP address"
            ))
            self.is_process_running = False
            self.root.after(5000,
                            lambda: self.tab1_label_failed.place_forget())
            if self.on_finish:
                self.on_finish(self)
                self.founded_ips()
            return
        self.brain.stopla = False
        self.root.after(0, lambda: self.log_text.config(state="normal"))
        self.root.after(
            0, lambda: self.log_text.insert(
                "1.0", f"[{ip}]Scanning all ports...")
        )
        self.root.after(0, self.scanning_animation)
        self.root.after(
            0, lambda: self.tab1_stop_nmap.grid(
                row=0, column=1, padx=(5, 0)
            )
        )
        if self.settings_instance:
            self.root.after(0,
                            lambda: self.settings_instance.apply_button_style(
                                self.root))

        self.root.after(0, self.show_processes())


    def add_ips_in_menu(self, ip: str):
        logging.debug("[add_ips_in_menu]-Clicked")
        active_buttons = self.menu_frame_found.winfo_children()
        for widget in active_buttons:
            if isinstance(widget, Button) and widget.cget("text") == str(ip):
                return
        new_button = Button(self.menu_frame_found, text=f"{ip}")
        new_button.pack(fill="x")
        new_button.bind(
            "<Button-1>",
            lambda event, ip=ip: self.found_enter_choosed_ip(event, ip)
        )
        self.button_references.append(new_button)
        logging.debug(f"[add_ips_in_menu]-found ips: {new_button}")

    def finished_nmap(self, test):
        logging.debug(f"finished_nmap: {test}")
        check_data = open_file(check_path)
        check_data["founded_ips"] = self.brain.found_ips
        write_file(check_path, check_data)
        logging.debug("[try_find]-File has been saved at: %s",
                      os.path.abspath("now_logs.txt"))
        self.brain.stopla = True
        if not hasattr(self, "my_process_btn"):
            return
        self.root.after(0, lambda: self.update_ui("Scan completed"))
        if "nmap_process" in self.active_processes:
            self.active_processes.remove("nmap_process")
        self.root.after(0, lambda: self.my_process_btn.destroy())
        if self.my_process_btn in self.shared_nmap_processes:
            self.shared_nmap_processes.remove(self.my_process_btn)
        if len(self.active_processes) == 0:
            self.root.after(0,
                            lambda: self.ongoing_processes.grid_forget())
        if self.my_process_btn in self.shared_nmap_processes:
            self.shared_nmap_processes.remove(self.my_process_btn)
        if len(self.shared_nmap_processes) == 0:
            self.root.after(0, lambda: self.tab1_stop_nmap.grid_forget())

            logging.debug("[try_find]-stop button is being deleted")
        self.root.after(0, lambda: self.log_text.config(state="disabled"))
        if self.settings_instance:
            self.root.after(
                0,
                lambda: self.settings_instance.apply_button_style(self.root))
        return

    def scanning_animation(self, count: int = 0) -> None:
        ip = self.tab1_input.get()
        if not self.brain.stopla:
            dots = [".", "..", "..."]
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.insert(
                "1.0", "Status: Scanning" + dots[count % 3] + f"[{ip}]"
            )
            self.log_text.config(state="disabled")

            self.root.after(500, lambda: self.scanning_animation(count + 1))
        else:
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "1.end")
            self.log_text.insert("1.0", "Status: Scanning Completed")
            self.log_text.config(state="disabled")
            return
    
    def stop_nmap_ui(self):
        self.brain.stop_nmap()
        if len(self.active_processes) == 0:
            self.root.after(0, lambda: self.ongoing_processes.grid_forget())
            logging.debug("[stop_nmap]-Nmap stopped")
            self.root.after(
                20, lambda: self.update_ui("\n[!] NMAP scan is terminated")
            )
            if "nmap_process" in self.active_processes:
                self.active_processes.remove("nmap_process")

            if len(self.shared_nmap_processes) == 0:
                self.root.after(0,
                                lambda: self.tab1_stop_nmap.destroy())
            self.shared_nmap_processes.remove(self.my_process_btn)

            self.root.after(0, lambda: self.my_process_btn.destroy())
    
    def show_close_proccess(self, event):
        self.brain.stop_nmap()

    def show_processes(self):
        self.active_processes.append("nmap_process")
        self.my_process_btn = Button(self.ongoing_processes,
                                     text=f"Nmap: {self.tab1_input.get()}")
        self.shared_nmap_processes.append(self.my_process_btn)
        self.root.after(0, lambda: self.my_process_btn.pack(fill="x"))
        self.root.after(0, lambda: self.ongoing_processes.grid(
            row=8, column=0, sticky="sw")
        )
        self.root.after(0, lambda: self.my_process_btn.bind(
            "<Button-3>", self.show_close_proccess)
        )

class nmap_brain:
    def __init__(self, on_line, on_ip_found, on_finish):
        self.on_line = on_line
        self.on_ip_found = on_ip_found
        self.on_finish = on_finish

        self.stopla = False

        self.found_ips = []

    def try_find(self, ip: str):
        logging.debug(f"NMAP IP IS: {ip}")
        self.is_process_running = True
        self.current_process = subprocess.Popen(
            ["nmap", ip], shell=False, stdout=subprocess.PIPE, text=True
        )

        full_output = ""
        while True:
            line = self.current_process.stdout.readline()
            if not line or self.stopla:
                break
            full_output += line
            if self.on_line:
                self.on_line(line)
        self.current_process.stdout.close()
        self.current_process.wait()
        if full_output:
            self.find_ips(full_output)

    def find_ips(self, logs: str) -> str:
        if not os.path.exists(main_path_py):
            open(main_path_py,"w").close()
        logging.debug(f"LOGS==== \n {logs}")
        full_output = logs
        with open(fr"{main_path_py}", "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0)
            file.write(full_output)
            file.truncate()
        for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+)', full_output):
            ip2 = match.group(1)
            logging.debug(f"IP IS: {ip2}")
            if ip2 not in self.found_ips:
                self.found_ips.append(ip2)
                logging.debug(f"Founded ips: {self.found_ips}")
                self.on_ip_found(ip2)
        self.finished_nmap()
        if self.on_finish:
            self.on_finish(self)
        return self.found_ips
    
    def finished_nmap(self):
        logging.debug(f"[write_found_ips]-IPs ===  {self.found_ips}")
        self.stopla = True

    def stop_nmap(self):
        if self.current_process:
            system_os = platform.system()
            try:
                if system_os == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    subprocess.call(
                        [
                            'taskkill', '/F', '/T', '/PID',
                            str(self.current_process.pid)
                        ],
                        startupinfo=startupinfo
                    )
                else:
                    import signal
                    try:
                        os.kill(self.current_process.pid, signal.SIGTERM)
                        self.current_process.wait(1)
                    except subprocess.TimeoutExpired:
                        logging.debug("[stop_nmap]-The process is resisting, so it will be killed directly...")
                        os.kill(self.current_process.pid, signal.SIGKILL)

                self.stopla = True
            except Exception as e:
                logging.debug(
                    f"[stop_nmap]-Nmap scan is can't terminated: {e}")
            if self.on_finish:
                self.on_finish(self)

