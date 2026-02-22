import subprocess
import threading
import platform
import os
import json

class adb_connect:
    def __init__(self, tab1_input2, root,tab1_label_failed2,found_path,tab1_stop_adb,connected_devicesips, update_ui, connected_devicesips2, test_counter):
        self.tab1_input2 = tab1_input2
        self.root = root
        self.tab1_label_failed2 = tab1_label_failed2
        self.found_path = found_path
        self.tab1_stop_adb = tab1_stop_adb
        self.connected_devicesips = connected_devicesips
        self.connected_devicesips2 = connected_devicesips2
        self.update_ui = update_ui
        self.test_counter = test_counter
        self.test_counter_check = []
        self.current_process_adb = None
        self.stopla2 = False
        print("Clicked ADB")
        t = threading.Thread(target=self.try_connect)
        t.start()
    def try_connect(self):
        writing = self.tab1_input2.get().strip()
        print(writing)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if not writing:
            #WE ARE GETTING ENTRY COORDINATES TO THE FAILED_LABELS
            self.root.update_idletasks()
            x = self.tab1_input2.winfo_rootx()
            y = self.tab1_input2.winfo_rooty()
            print(f"x value: {x}, y value:{y}")
            self.tab1_label_failed2.place(x=x-250,y=y-70)
            self.tab1_label_failed2.config(text="Failed.Please write an IP address")
            self.root.after(5000, lambda: self.tab1_label_failed2.place_forget())
            return
        self.stopla2 = False
        try:
            self.current_process_adb = subprocess.Popen(
                [self.found_path, "connect", writing],
                    stdout=subprocess.PIPE,
                    text=True,
                    startupinfo=si
            )
            self.tab1_stop_adb.grid(row=0, column=1, padx=(5,0))
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
            new_writing = f"{writing}"
            for i in full_output.lower().split():
                if i == "connected":
                    self.stopla2 = True
                    self.root.after(0, lambda: self.update_ui("Connected"))
                    with open("check.json", "r", encoding="utf-8") as f:
                        check_data = json.load(f)
                    check_data["connected_ips"][new_writing] = "connected"
                    with open("check.json", "w", encoding="utf-8") as fi:
                        json.dump(check_data, fi, indent=4)
                    self.test_counter += 1
                    self.connected_devicesips2.grid(row=1, column=0 , sticky="nsew")
                    self.test_counter_check[0].configure(text=new_writing)
                    self.test_counter_check.append(self.connected_devicesips2)
                    print("List of check ips",self.test_counter_check)
                    if connected_label_text == "":
                        self.connected_devicesips.configure(background="lightblue")
                        self.connected_devicesips.config(text=new_writing)
                    for i in connected_label_list:
                        if i == new_writing:
                            print(f"Already connected {new_writing}")
                            pass
                        else:
                            new_writing = f"{connected_label_text}\n{writing}"
                            self.connected_devicesips.configure(background="lightblue")
                            self.connected_devicesips.config(text=new_writing)
                if i == "failed":
                    print("Stop button is deleted")
                    self.tab1_stop_adb.grid_forget()
            try:
                self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
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
                self.root.after(20, lambda: self.update_ui("\n[!] ADB connect is terminated"))
                self.root.after(0, lambda: self.tab1_stop_adb.grid_forget())
            except Exception as e:
                print(f"Nmap scan is can't terminated: {e}")
        else:
            self.tab1_stop_adb.grid_forget()
