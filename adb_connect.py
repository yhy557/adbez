import subprocess
import threading
import platform
import os
import json

from tkinter import Checkbutton, Label


class adb_connect:
    def __init__(self, tab1_input2, root, tab1_label_failed2, found_path,
                 tab1_stop_adb, connected_devicesips, update_ui,
                 test_counter, processes_in, check_btn_ip):
        self.tab1_input2 = tab1_input2
        self.root = root
        self.tab1_label_failed2 = tab1_label_failed2
        self.found_path = found_path
        self.tab1_stop_adb = tab1_stop_adb
        self.connected_devicesips = connected_devicesips
        self.update_ui = update_ui
        self.test_counter = test_counter
        self.processes_in = processes_in
        self.check_btn_ip = check_btn_ip
        self.test_counter_check = []
        self.check_ips = []
        self.current_process_adb = None
        self.stopla2 = False
        self.is_process_running = False
        self.process_counter = 0
        print("Clicked ADB")
        t = threading.Thread(target=self.try_connect)
        t.start()

    def test_ip_keyevent(self, ip):
        print(f"[test_ip_keyevent]-Clicked {ip}")

    def show_adb_failed(self):
        self.root.update_idletasks()
        x = self.tab1_input2.winfo_rootx()
        y = self.tab1_input2.winfo_rooty()
        print(f"[show_adb_failed]-x value: {x}, y value:{y}")
        self.tab1_label_failed2.place(x=x-250, y=y-70)
        self.tab1_label_failed2.config(
            text="Failed.Please write an IP address"
        )
        self.root.after(5000, lambda: self.tab1_label_failed2.place_forget())
        self.root.after(0, lambda: self.new_label.grid_forget())

    def test_show_status(self):
        self.processes_list = []
        self.new_frame = self.processes_in.master
        self.new_label = Label(self.new_frame, text="test")
        self.root.after(
            0, lambda: self.tab1_stop_adb.grid(row=0, column=1, padx=(5, 0))
        )
        self.root.after(0, lambda: self.new_label.grid())
        self.root.after(0, lambda: self.processes_list.append(self.new_label))
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
        connected_label_text = self.connected_devicesips.cget("text")
        connected_label_list = connected_label_text.split()
        new_writing = self.writing
        for word in full_output.lower().split():
            if word == "connected" and "failed" not in full_output.lower():
                self.stopla2 = True
                self.is_process_running = False
                self.root.after(100, lambda: self.new_label.grid_forget())
                self.root.after(0, lambda: self.update_ui("Connected"))
                with open("check.json", "r", encoding="utf-8") as f:
                    check_data = json.load(f)
                check_data["connected_ips"][self.writing] = "connected"
                with open("check.json", "w", encoding="utf-8") as fi:
                    json.dump(check_data, fi, indent=4)
                self.test_counter += 1
                self.check_ips.append(self.check_btn_ip)
                self.master_frame = self.check_btn_ip.master
                self.new_btn = Checkbutton(self.master_frame)
                btn = self.new_btn
                row = len(self.master_frame.winfo_children())
                self.root.after(
                    0, lambda b=btn, r=row: btn.grid(
                        row=r, column=0
                    )
                )
                self.root.after(
                    0, lambda b=btn: b.configure(text=new_writing)
                )
                self.root.after(
                    0, lambda b=btn: b.configure(
                        command=lambda: self.test_ip_keyevent(new_writing)
                    )
                )
                print("[test_show_status]-List of check ips", self.test_counter_check)
                if connected_label_text == "":
                    self.root.after(
                        0, lambda: self.connected_devicesips.configure(
                            background="lightblue"
                        )
                    )
                    self.root.after(
                        0, lambda: self.connected_devicesips.config(
                            text=new_writing
                        )
                    )
                elif new_writing not in connected_label_list:
                    new_writing = f"{connected_label_text}\n{self.writing}"
                    self.root.after(
                        0, lambda: self.connected_devicesips.configure(
                            background="lightblue"
                        )
                    )
                    self.root.after(
                        0, lambda: self.connected_devicesips.config(
                            text=new_writing
                        )
                    )
                else:
                    print(f"[test_show_status]-Already connected {new_writing}")
                    pass
                break
            elif word == "failed":
                print("[test_show_status]-Stop button is deleted")
                self.is_process_running = False
                self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
                break
        try:
            self.is_process_running = False
            self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
            self.root.after(100, lambda: self.new_label.grid_forget())
            print("[test_show_status]-stop button is being deleted")
        except Exception as e:
            self.root.after(100, lambda: self.new_label.grid_forget())
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

    def stop_adb(self):
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
                self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
            except Exception as e:
                print(f"[stop_adb]-ADB connection couldn't terminate: {e}")
        else:
            self.tab1_stop_adb.grid_forget()
