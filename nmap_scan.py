import threading
import subprocess
import os
import re
import platform
from tkinter import Button
import logging
from settings import settings_style
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


class nmap_scan:
    def __init__(self, tab1_input, log_text, tab1_label_failed, tab1_stop_nmap,
                 root, update_ui, menu_frame_found, found_enter_choosed_ip,
                 button_references, processes_in, ongoing_processes, active_processes,
                 shared_nmap_processes, settings_instance=None,
                 on_finish=None):
        self.tab1_input = tab1_input
        self.button_references = button_references
        self.update_ui = update_ui
        self.log_text = log_text
        self.tab1_label_failed = tab1_label_failed
        self.tab1_stop_nmap = tab1_stop_nmap
        self.root = root
        self.menu_frame_found = menu_frame_found
        self.found_enter_choosed_ip = found_enter_choosed_ip
        self.processes_in = processes_in
        self.ongoing_processes = ongoing_processes
        self.active_processes = active_processes
        self.shared_nmap_processes = shared_nmap_processes
        self.on_finish = on_finish
        self.settings_instance = settings_instance
        self.current_process = None
        self.stopla = False
        self.current_ip_has_adb = False
        self.is_process_running = False
        self.found_ips = []
        logging.debug(
            f"button_references type: {type(self.button_references)}")
        t = threading.Thread(target=self.try_find)
        t.start()

    def show_close_proccess(self, event):
        self.stop_nmap()

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

    def show_ui_things(self):
        self.ip = self.tab1_input.get()
        # WE ARE GETTING ENTRY COORDINATES TO THE FAILED_LABELS
        if not self.ip:
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
            return
        self.stopla = False
        self.root.after(0, lambda: self.log_text.config(state="normal"))
        self.root.after(
            0, lambda: self.log_text.insert(
                "1.0", f"[{self.ip}]Scanning all ports...")
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

    def try_find(self):
        default_path = os.path.dirname(os.path.abspath(__file__))
        main_path_py = os.path.join(default_path, "now_logs.txt")
        self.is_process_running = True
        self.show_ui_things()

        if not hasattr(self, "ip") or not self.ip:
            return
        self.root.after(0, self.show_processes)
        self.current_process = subprocess.Popen(
            ["nmap", self.ip], shell=False, stdout=subprocess.PIPE, text=True
        )

        full_output = ""
        while True:
            line = self.current_process.stdout.readline()
            if not line or self.stopla:
                break
            full_output += line
            self.root.after(0, lambda l=line: self.update_ui(l))
        self.current_process.stdout.close()
        self.current_process.wait()

        with open(fr"{main_path_py}", "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0)
            file.write(full_output)
            file.truncate()
        for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+)', full_output):
            ip = match.group(1)
            if ip not in self.found_ips:
                self.found_ips.append(ip)
                self.root.after(
                    0, lambda ip=ip: self.add_ips_in_menu(ip)
                )
        logging.debug("[try_find]-File has been saved at: %s",
                      os.path.abspath("now_logs.txt"))
        self.root.after(2000, lambda: self.write_found_ips())
        if not self.stopla:
            self.stopla = True
            self.root.after(0, lambda: self.update_ui("Scan completed"))
            self.active_processes.remove("nmap_process")
            self.root.after(0, lambda: self.my_process_btn.destroy())
            if self.my_process_btn in self.shared_nmap_processes:
                self.shared_nmap_processes.remove(self.my_process_btn)
            if len(self.active_processes) == 0:
                self.root.after(0,
                                lambda: self.ongoing_processes.grid_forget())
        if len(self.shared_nmap_processes) == 0:
            self.root.after(0, lambda: self.tab1_stop_nmap.grid_forget())
            logging.debug("[try_find]-stop button is being deleted")
        self.root.after(0, lambda: self.log_text.config(state="disabled"))
        if self.settings_instance:
            self.root.after(
                0,
                lambda: self.settings_instance.apply_button_style(self.root))
        return

    def add_ips_in_menu(self, ip):
        logging.debug("[add_ips_in_menu]-Clicked")
        new_button = Button(self.menu_frame_found, text=f"{ip}")
        new_button.pack(fill="x")
        new_button.bind(
            "<Button-1>",
            lambda event, ip=ip: self.found_enter_choosed_ip(event, ip)
        )
        self.button_references.append(new_button)
        logging.debug(f"[add_ips_in_menu]-found ips: {new_button}")

        # ips_length = len(found_ips)
        # for i in range(ips_length):
        #    texts = f"found_menu_frame_in{i}"
        #    texts = Button(menu_frame_found, text=f"{found_ips[{i}]}")

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
                                    lambda: self.tab1_stop_nmap.grid_forget())
                self.shared_nmap_processes.remove(self.my_process_btn)

                self.root.after(0, lambda: self.my_process_btn.destroy())
            except Exception as e:
                logging.debug(
                    f"[stop_nmap]-Nmap scan is can't terminated: {e}")
            if self.on_finish:
                self.on_finish(self)

    def scanning_animation(self, count=0):
        ip = self.tab1_input.get()
        if not self.stopla:
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

    def write_found_ips(self):
        logging.debug(f"[write_found_ips]-IPs ===  {self.found_ips}")
