import logging
import os
import platform
import subprocess
import threading
import config.paths as paths
from config.state import global_state
from core.process import registry
from tkinter import Checkbutton, Label, IntVar
from utils.file_utils import open_file, write_file
from ui.widgets.IpsListCard import MakeIpCard

class AdbConnectBrain:
    def __init__(self, adb_path, on_line=None, on_connected=None, on_failed=None, on_finish=None):
        self.adb_path = adb_path
        self.on_line = on_line
        self.on_connected = on_connected
        self.on_failed = on_failed
        self.on_finish = on_finish
        self.processes = {}
        self.stopla = False

    def try_connect(self, ip: str):
        if not self.adb_path:
            logging.debug(f"[AdbConnectBrain]-adb_path is none, ip={ip}")
            if self.on_failed:
                self.on_failed(ip)
            if self.on_finish:
                self.on_finish(ip)
            return

        try:
            process = registry.start([self.adb_path, "connect", ip])
        except Exception as e:
            logging.debug(f"[try_connect]-Can't start adb connect: {e}")
            if self.on_failed:
                self.on_failed(ip)
            if self.on_finish:
                self.on_finish(ip)
            return

        self.processes[ip] = process
        full_output = ""
        while True:
            line = process.stdout.readline()
            if not line or self.stopla:
                break
            full_output += line
            if self.on_line:
                self.on_line(line)
        process.stdout.close()
        process.wait()

        output_lower = full_output.lower()
        if "connected" in output_lower and "failed" not in output_lower:
            if self.on_connected:
                self.on_connected(ip)
        else:
            if self.on_failed:
                self.on_failed(ip)

        self.processes.pop(ip, None)
        if self.on_finish:
            self.on_finish(ip)

    def disconnect_ip(self, ip: str):
        if not self.adb_path:
            logging.debug(f"[disconnect_ip]-adb_path is none, ip={ip}")
            return
        try:
            registry.start([self.adb_path, "disconnect", ip])
            logging.debug(f"[disconnect_ip]-Disconnected {ip}")
        except Exception as e:
            logging.error(f"[disconnect_ip]-Error: {e}")

    def stop_connect(self, ip=None):
        self.stopla = True
        if ip:
            process = self.processes.get(ip)
            if process and process.poll() is None:
                self._kill_process(process)
        else:
            for process in list(self.processes.values()):
                if process.poll() is None:
                    self._kill_process(process)

    def _kill_process(self, process):
        system_os = platform.system()
        try:
            if system_os == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.call(
                    ['taskkill', '/F', '/T', '/PID', str(process.pid)],
                    startupinfo=startupinfo
                )
            else:
                import signal
                try:
                    os.kill(process.pid, signal.SIGTERM)
                    process.wait(1)
                except subprocess.TimeoutExpired:
                    os.kill(process.pid, signal.SIGKILL)
        except Exception as e:
            logging.debug(f"[_kill_process]-Couldn't terminate: {e}")


class AdbUi:
    def __init__(self, app, on_finish=None):
        self.app = app
        self.tab1_input2 = app.tab1_input2
        self.root = app.root
        self.tab1_label_failed2 = app.tab1_label_failed2
        self.found_path = app.found_path
        self.tab1_stop_adb = app.tab1_stop_adb
        self.connected_devices_ips = app.connected_devices_ips
        self.update_ui = app.update_ui
        self.processes_in = app.processes_in
        self.check_btn_ip = app.check_btn_ip
        self.ongoing_processes = app.ongoing_processes
        self.check_data = app.check_data
        self.upper_frame = app.upper_frame
        self.checkbutton_map = app.checkbutton_map
        self.check_event = app.check_event
        self.check_vars = app.check_vars
        self.on_finish = on_finish

        self.labels = {}

        self.brain = AdbConnectBrain(
            adb_path=self.found_path,
            on_line=lambda line: self.root.after(0, lambda: self.update_ui(line)),
            on_connected=lambda ip: self.root.after(0, lambda: self.handle_connected(ip)),
            on_failed=lambda ip: self.root.after(0, lambda: self.handle_failed(ip)),
            on_finish=lambda ip: self.root.after(0, lambda: self.handle_finish(ip))
        )

        ip_list = self.collect_target_ips()
        self.start_connections(ip_list)

    def collect_target_ips(self) -> list:
        targets = set()
        written = self.tab1_input2.get().strip()
        if written:
            if ":" in written:
                cleaned = written
            else:
                cleaned = written.partition(":")[0]
            targets.add(cleaned)

        for ip in global_state.adb_connect_choosen_ips:
            targets.add(ip)

        return list(targets)

    def start_connections(self, ip_list):
        if not ip_list:
            self.show_adb_failed()
            return
        global_state.is_process_running = True
        for ip in ip_list:
            self.show_processes(ip)
            t = threading.Thread(target=self.brain.try_connect, args=(ip,))
            t.start()

    def show_adb_failed(self):
        self.root.update_idletasks()
        self.root.after(
            0, lambda: self.tab1_label_failed2.place(
                in_=self.tab1_input2, relx=-0.69, rely=0, anchor="nw"
            )
        )
        self.root.after(0, lambda: self.tab1_label_failed2.config(
            text="Failed. Please write an IP address"
        ))
        global_state.is_process_running = False
        self.root.after(5000, lambda: self.tab1_label_failed2.place_forget())
        if self.on_finish:
            self.on_finish(self)

    def show_processes(self, ip):
        global_state.shared_adb_processes.append(ip)
        global_state.ongoing_processes_list.append(ip)
        label = Label(self.ongoing_processes, text=f"ADB: {ip}")
        self.labels[ip] = label
        self.root.after(0, lambda: self.ongoing_processes.grid(row=8, column=0, sticky="sw"))
        self.root.after(0, lambda: self.tab1_stop_adb.grid(row=0, column=2, padx=(5, 0)))
        self.root.after(0, lambda: label.pack())
        label.bind("<Button-3>", lambda e: self.stop_adb_ui(ip))

    def handle_connected(self, ip):
        check_data = open_file(paths.CONFIG_FILE_PATH)
        check_data["connected_ips"][ip] = "connected"
        self.check_data["connected_ips"][ip] = "connected"
        write_file(paths.CONFIG_FILE_PATH, check_data)

        AdbUi.create_checkbutton(
            ip, self.root, self.check_btn_ip,
            self.checkbutton_map, self.check_vars, self.check_event
        )

        connected_label_text = self.connected_devices_ips.cget("text")
        connected_label_list = connected_label_text.split()

        if connected_label_text == "":
            self.connected_devices_ips.configure(background="lightblue")
            self.connected_devices_ips.config(text=ip)
        elif ip not in connected_label_list:
            new_writing = f"{connected_label_text}\n{ip}"
            self.connected_devices_ips.configure(background="lightblue")
            self.connected_devices_ips.config(text=new_writing)
        else:
            logging.debug(f"[handle_connected]-Already connected {ip}")

        self.update_ui(f"Connected: {ip}")
        card = global_state.ip_card_map.get(ip)
        if card:
            card.set_connected(True)

    def handle_failed(self, ip):
        logging.debug(f"[handle_failed]-Failed to connect: {ip}")
        self.update_ui(f"Failed: {ip}")

    def handle_finish(self, ip):
        try:
            global_state.shared_adb_processes.remove(ip)
        except ValueError:
            pass
        try:
            global_state.ongoing_processes_list.remove(ip)
        except ValueError:
            pass

        label = self.labels.pop(ip, None)
        if label:
            self.root.after(100, lambda: label.pack_forget())

        if len(global_state.shared_adb_processes) == 0:
            self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
            global_state.is_process_running = False

        if self.on_finish:
            self.on_finish(self)

    @staticmethod
    def create_checkbutton(ip, root, check_btn_ip, checkbutton_map, check_vars, check_event):
        var = check_vars.setdefault(ip, IntVar())
        master_frame = check_btn_ip.master
        already_exists = any(
            isinstance(w, Checkbutton) and w.cget("text") == ip
            for w in master_frame.winfo_children()
        )
        if not already_exists:
            btn = Checkbutton(
                master_frame, text=ip, variable=var,
                command=lambda: check_event(ip)
            )
            checkbutton_map[ip] = btn
            row = len(master_frame.winfo_children())
            root.after(0, lambda: btn.grid(row=row, column=0, sticky="ew"))

    def stop_adb_ui(self, ip):
        self.brain.stop_connect(ip)
        self.root.after(20, lambda: self.update_ui(f"\n[!] ADB connect terminated: {ip}"))