import subprocess
import threading
import platform
import os
import json
import logging


from tkinter import Checkbutton, Label, IntVar


class adb_connect:
    def __init__(self, app, on_finish=None):
        self.tab1_input2 = app.tab1_input2
        self.root = app.root
        self.tab1_label_failed2 = app.tab1_label_failed2
        self.found_path = app.found_path
        self.tab1_stop_adb = app.tab1_stop_adb
        self.connected_devices_ips = app.connected_devices_ips
        self.update_ui = app.update_ui
        self.test_counter = app.test_counter
        self.processes_in = app.processes_in
        self.check_btn_ip = app.check_btn_ip
        self.ongoing_processes = app.ongoing_processes
        self.shared_adb_processes = app.shared_adb_processes
        self.on_finish = on_finish
        self.check_data = app.check_data
        self.tab_keyevents = app.tab_keyevents
        self.upper_frame = app.upper_frame

        self.test_counter_check = []
        self.check_ips = []
        self.ongoing_processes_list = []
        self.ongoing_processes_adb_list = []
        self.checkbutton_ips = []
        self.check_vars = {}
        self.checkbutton_map = {}
        self.current_process_adb = None
        self.stopla2 = False
        self.is_process_running = False
        self.process_counter = 0
        print("Clicked ADB")
        t = threading.Thread(target=self.try_connect)
        t.start()

    def _get_var_for_ip(self, ip):
        if ip not in self.check_vars:
            self.check_vars[ip] = IntVar()
        return self.check_vars[ip]

    def test_ip_keyevent(self, ip):
        print(f"[test_ip_keyevent]-Clicked {ip}")

    @staticmethod
    def disconnect_ip(tab1_input2, found_path, check_data, connected_devices_ips, upper_frame, root,
                      check_btn_ip, checkbutton_map):
        root.update_idletasks()
        label_text = tab1_input2.get().strip()
        if label_text in checkbutton_map:
            checkbutton_map[label_text].destroy()
            del checkbutton_map[label_text]
        logging.debug(f"current ip address:  {label_text}")
        logging.info("Clicked disconnect")
        connected_ips_text = connected_devices_ips.cget("text")
        logging.info(f"list is: \n {connected_ips_text}")
        connected_ips_list = connected_ips_text.split()

        background_color = upper_frame.cget("background")
        try:
            if found_path and isinstance(found_path, str):
                subprocess.Popen(
                    [found_path, "disconnect", label_text],
                    stdout=subprocess.PIPE,
                    text=True
                )
                logging.debug(f"Disconnected to {label_text}")
                check_btn_ip.grid_forget()
                with open("check.json", "r", encoding="utf-8") as f:
                    check_data = json.load(f)
                ip_to_remove = label_text.strip()
                logging.debug(f"Deleting ip: {ip_to_remove}")
                if ip_to_remove in check_data["connected_ips"]:
                    del check_data["connected_ips"][ip_to_remove]
                with open("check.json", "w", encoding="utf-8") as fi:
                    json.dump(check_data, fi, indent=4)
                for i in connected_ips_list:
                    if i == label_text:
                        connected_ips_list.remove(i)
                        new_text = "\n".join(connected_ips_list)
                        root.update_idletasks()
                        connected_devices_ips.configure(text=new_text)
                        logging.debug("Deleted ip")
                if connected_devices_ips.cget("text") == "":
                    connected_devices_ips.configure(background=background_color)
        except Exception as e:
            logging.error("Error: %s", e)

    def show_adb_failed(self):
        self.root.update_idletasks()
        self.root.after(
            0, lambda: self.tab1_label_failed2.place(
                in_=self.tab1_input2, relx=-0.69, rely=0, anchor="nw"
            )
        )
        logging.debug("[show_ui_things]-Nothing has writed")
        self.root.after(0, lambda: self.tab1_label_failed2.config(
            text="Failed. Please write an IP address"
        ))
        self.is_process_running = False
        self.root.after(5000, lambda: self.tab1_label_failed2.place_forget())
        if self.on_finish:
            self.on_finish(self)
        logging.debug("[show_ui_things]-Nothing has writed")
        self.root.after(0, lambda: self.tab1_label_failed2.config(
            text="Failed.Please write an IP address"
        ))

    def check_event(self, text):
        var = self._get_var_for_ip(text)
        if var.get() == 1:
            print(f"Choosen {text}")
            if text not in self.check_data["choosen_ips"]:
                self.check_data["choosen_ips"].append(text)
            with open("check.json", "w", encoding="utf-8") as f:
                json.dump(self.check_data, f, indent=4, ensure_ascii=False)
        else:
            for ip in self.check_data["choosen_ips"]:
                if text == ip:
                    self.check_data["choosen_ips"].remove(ip)
            with open("check.json", "w", encoding="utf-8") as f:
                json.dump(self.check_data, f, indent=4, ensure_ascii=False)
            print("Not choosen")

    def test_show_status(self):
        self.processes_list = []
        self.new_frame = self.processes_in.master
        self.new_label = Label(self.ongoing_processes, text="test")
        self.shared_adb_processes.append(self.new_label)
        self.root.after(0, lambda: self.ongoing_processes.grid(
            row=8, column=0, sticky="sw")
        )
        self.root.after(
            0, lambda: self.tab1_stop_adb.grid(row=0, column=1, padx=(5, 0))
        )
        self.root.after(0, lambda: self.new_label.pack())
        self.ongoing_processes_list.append(self.new_label)
        self.new_label.bind("<Button-3>", self.stop_adb)
        self.processes_list.append(self.new_label)
        self.root.after(0, lambda: self.new_label.configure(text="ADBprocess"))
        """
        now_text = self.processes_in.cget("text")
        self.processes_in.grid(row=1, column=0)
        if now_text == "":
            print("[test_show_status]-Test1", now_text)
            self.processes_in.configure(text="Adb process")
        else:
            print("[test_show_status]-Test2")
            self.processes_in.configure(
                text=f"{now_text}" + "\n" + "Adb process"
            )
        """
        full_output = ""
        while True:
            line = self.current_process_adb.stdout.readline()
            if not line or self.stopla2:
                break
            full_output += line
            self.root.after(0, lambda l=line: self.update_ui(l))
        self.current_process_adb.stdout.close()
        self.current_process_adb.wait()
        connected_label_text = self.connected_devices_ips.cget("text")
        connected_label_list = connected_label_text.split()
        new_writing = self.writing
        for word in full_output.lower().split():  # I can change this method to re.finditer
            if word == "connected" and "failed" not in full_output.lower():
                self.stopla2 = True
                self.is_process_running = False
                self._finish_process()

                self.root.after(0, lambda: self.update_ui("Connected"))
                with open("check.json", "r", encoding="utf-8") as f:
                    check_data = json.load(f)
                check_data["connected_ips"][self.writing] = "connected"
                self.check_data["connected_ips"][self.writing] = "connected"
                with open("check.json", "w", encoding="utf-8") as fi:
                    json.dump(check_data, fi, indent=4)
                self.test_counter += 1
                self.current_text = self.writing
                self.var = self._get_var_for_ip(self.writing)
                self.check_ips.append(self.check_btn_ip)
                self.master_frame = self.check_btn_ip.master
                already_exists = any(
                    isinstance(widget, Checkbutton) and widget.cget("text") == self.current_text
                    for widget in self.master_frame.winfo_children()
                )
                self.new_btn = Checkbutton(self.master_frame,
                                           text=self.current_text,
                                           variable=self.var,
                                           command=lambda e=self.current_text: self.check_event(e)
                                           )
                btn = self.new_btn
                row = len(self.master_frame.winfo_children())
                self.checkbutton_map[self.writing] = self.new_btn

                if not already_exists:
                    self.root.after(
                        0, lambda b=btn, r=row: btn.grid(
                            row=r, column=0
                        )
                    )
                    self.root.after(
                        0, lambda b=btn: b.configure(text=new_writing)
                    )
                """
                self.root.after(
                    0, lambda b=btn: b.configure(
                        command=lambda: self.test_ip_keyevent(new_writing)
                    )
                )
                """
                print(
                    "[test_show_status]-List of check ips",
                    self.test_counter_check
                )
                if connected_label_text == "":
                    self.root.after(
                        0, lambda: self.connected_devices_ips.configure(
                            background="lightblue"
                        )
                    )
                    self.root.after(
                        0, lambda: self.connected_devices_ips.config(
                            text=new_writing
                        )
                    )
                elif new_writing not in connected_label_list:
                    new_writing = f"{connected_label_text}\n{self.writing}"
                    self.root.after(
                        0, lambda: self.connected_devices_ips.configure(
                            background="lightblue"
                        )
                    )
                    self.root.after(
                        0, lambda: self.connected_devices_ips.config(
                            text=new_writing
                        )
                    )
                else:
                    print(
                        f"[test_show_status]-Already connected {new_writing}"
                    )
                    pass
                break
            elif word == "failed":
                print("[test_show_status]-Stop button is deleted")
                self.is_process_running = False
                self._finish_process()
                break
        try:
            self.is_process_running = False
            self._finish_process()
            print("[test_show_status]-stop button is being deleted")
        except Exception as e:
            self._finish_process()
            print(f"[test_show_status]-Can't deleting stop button: {e}")

    def try_connect(self):
        self.writing = self.tab1_input2.get().strip()
        print("[try_connect-]", self.writing)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if not self.writing:
            self.root.after(0, self.show_adb_failed)
            return
        self.stopla2 = False
        self.is_process_running = False
        try:
            self.current_process_adb = subprocess.Popen(
                [self.found_path, "connect", self.writing],
                stdout=subprocess.PIPE,
                text=True,
                startupinfo=si
            )
            self.test_show_status()
        except Exception as e:
            print(f"[try_connect]-Can't start adb connect: {e}")

    def stop_adb(self, event=None):
        system_os = platform.system()
        if self.current_process_adb and self.current_process_adb.poll() is None:
            try:
                if system_os == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.call(
                        [
                            'taskkill', '/F', '/T', '/PID', str(
                                self.current_process_adb.pid
                            )
                        ],
                        startupinfo=startupinfo
                    )
                else:
                    import signal
                    try:
                        os.kill(
                            self.current_process_adb.pid, signal.SIGTERM
                        )
                        self.current_process_adb.wait(1)
                    except subprocess.TimeoutExpired:
                        print("[stop_adb]-The process is resisting, so it will be killed directly...")
                        os.kill(
                            self.current_process_adb.pid, signal.SIGKILL
                        )
                print("[stop_adb]-Adb being stopped")
                self.root.after(
                    20, lambda: self.update_ui(
                        "\n[!] ADB connect is terminated"
                    )
                )
                self.stopla2 = True
                self._finish_process()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[stop_adb]-ADB connection couldn't terminate: {e}")
        else:
            if len(self.shared_adb_processes) == 0:
                self.tab1_stop_adb.grid_forget()

    def _finish_process(self):
        try:
            self.shared_adb_processes.remove(self.new_label)
            logging.debug("IT WORKED")
        except ValueError:
            pass
        try:
            self.ongoing_processes_list.remove(self.new_label)
            logging.debug("IT WORKED")
        except ValueError:
            pass
        self.root.after(100, lambda: self.new_label.pack_forget())
        if len(self.shared_adb_processes) == 0:
            self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
        if self.on_finish:
            self.on_finish(self)
