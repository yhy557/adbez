import threading
import subprocess
import os
import re
import platform
from tkinter import Button


class nmap_scan:
    def __init__(self, tab1_input, log_text, tab1_label_failed, tab1_stop_nmap,
                 root, update_ui, menu_frame_found, found_enter_choosed_ip,
                 button_references, processes_in):
        self.tab1_input = tab1_input
        self.button_references = button_references
        self.update_ui = update_ui
        self.log_text = log_text
        self.tab1_label_failed = tab1_label_failed
        self.tab1_stop_nmap = tab1_stop_nmap
        self.root = root
        self.current_process = None
        self.stopla = False
        self.menu_frame_found = menu_frame_found
        self.found_enter_choosed_ip = found_enter_choosed_ip
        self.processes_in = processes_in
        self.found_ips = []
        self.current_ip_has_adb = False
        self.is_process_running = False
        print(f"DEBUG: button_references type: {type(self.button_references)}")
        t = threading.Thread(target=self.try_find)
        t.start()

    def show_processes(self):
        self.processes_in.grid(row=1, column=0)
        self.root.after(1, lambda: self.processes_in.configure(text="Nmap scanning"))

    def try_find(self):
        ip = self.tab1_input.get()
        default_path = os.path.dirname(os.path.abspath(__file__))
        main_path_py = os.path.join(default_path, "now_logs.txt")
        self.is_process_running = True
        self.show_processes()

        if not ip:
            # WE ARE GETTING ENTRY COORDINATES TO THE FAILED_LABELS
            self.root.update_idletasks()
            x = self.tab1_input.winfo_rootx()
            y = self.tab1_input.winfo_rooty()
            print(f"x degeri: {x}, y degeri:{y}")
            self.tab1_label_failed.place(x=x-250, y=y-70)
            print("Nothing has writed")
            self.tab1_label_failed.config(
                text="Failed.Please write an IP address"
            )
            self.is_process_running = False
            self.root.after(0, lambda: self.processes_in.configure(text=""))
            self.root.after(0, lambda: self.processes_in.grid_forget())
            self.root.after(
                5000, lambda: self.tab1_label_failed.place_forget()
            )
            return
        self.stopla = False

        self.log_text.config(state="normal")
        self.log_text.insert("1.0", f"[{ip}]Scanning all ports...")
        self.root.after(0, self.scanning_animation)
        self.root.after(
            100, lambda: self.tab1_stop_nmap.grid(
                row=0, column=1, sticky="w", padx=(5, 0)
            )
        )

        self.current_process = subprocess.Popen(
            ["nmap", ip], shell=False, stdout=subprocess.PIPE, text=True
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
        for lines in content.splitlines():
            check_ips = re.search(r'(\d+\.\d+\.\d+\.\d+)', lines)
            if check_ips:
                checked_ips = check_ips.group(1)
                if checked_ips not in self.found_ips:
                    self.found_ips.append(checked_ips)
                    self.root.after(
                        0, lambda ip=checked_ips: self.add_ips_in_menu(ip)
                    )
        print("Dosya buraya kaydedildi:", os.path.abspath("now_logs.txt"))
        self.root.after(2000, lambda: self.write_found_ips())
        if not self.stopla:
            self.stopla = True
            self.root.after(0, lambda: self.update_ui("Scan completed"))
        try:
            self.root.after(0, lambda: self.tab1_stop_nmap.grid_forget())
            self.is_process_running = False
            self.root.after(0, lambda: self.processes_in.configure(text=""))
            self.root.after(0, lambda: self.processes_in.grid_forget())
            print("stop button is being deleted")
        except Exception as e:
            print(f"Can't deleting stop button: {e}")
        self.log_text.config(state="disabled")
        return

    def add_ips_in_menu(self, ip):
        print("Hello i am add_ips_menu")
        new_button = Button(self.menu_frame_found, text=f"{ip}")
        new_button.pack(fill="x")
        new_button.bind(
            "<Button-1>",
            lambda event, ip=ip: self.found_enter_choosed_ip(event, ip)
        )
        self.button_references.append(new_button)
        print(f"found ipsss: {new_button}")

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
                        print("The process is resisting, so it will be killed directly...")
                        os.kill(self.current_process.pid, signal.SIGKILL)

                self.stopla = True
                print("Nmap stopped")
                self.root.after(
                    20, lambda: self.update_ui("\n[!] NMAP scan is terminated")
                )
                self.root.after(0, lambda: self.tab1_stop_nmap.grid_forget())
            except Exception as e:
                print(f"Nmap scan is can't terminated: {e}")

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
        print(f"IPs ===  {self.found_ips}")
