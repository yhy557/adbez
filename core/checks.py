from datetime import datetime
import os
import json
import logging
import platform
import shutil
import socket
import threading
import config.paths as paths
from core.nmap_scan import NmapBrain,NmapUi
from ui.settings import SettingsStyle
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from adbez import MainApp
from utils.log_utils import auto_insert
from utils.file_utils import write_file

from core.adb_connect import adb_connect
from config.state import global_state
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)



class StartupCheck:
    def app_startup(
        self, connected_devicesips, current_lang, data, check_data,
        check_btn_ip, app:'MainApp',
        style: SettingsStyle, update_lang_func
    ):

        self.app = app
        self.connected_devicesips = connected_devicesips
        self.current_lang = current_lang
        self.data = data
        self.check_data = check_data
        self.choose_theme = style.choose_theme
        self.choose_themeW = style.choose_themeW
        self.choose_auto_nmap_btn = style.choose_auto_nmap_btn
        self.get_text = style.get_text
        self.update_lang_func = update_lang_func
        self.check_btn_ip = check_btn_ip
        self.choose_theme_special = style.choose_theme_special

        self.now = datetime.now()
        self.json_default_data = {
            "last_entered": f"{self.now}",
            "connected_ips": {},
            "theme": {},
            "choosen_nmap_ip": [],
            "choosen_port": "5555",
            "choosen_path_for_adb": {},
            "choosen_language": "en",
            "is_live_helper_on": False,
            "is_auto_nmap_on": False,
            "ui_flags": {
                "has_seen_entry_save_hint": False
            }
        }
        self.check_vars = {}
        if global_state.did_adb_work is not True:
            self.try_find_adb()
        self._init_data_file()
        self._init_language()
        self._init_auto_nmap()
        self._load_connected_ips()
        self._apply_theme()

        get_ip_thread = threading.Thread(target=self._get_local_ip, daemon=True)
        get_ip_thread.start()

    def _get_local_ip(self):
        port = 80

        try:
            hostname = socket.gethostname()
            all_ips = socket.getaddrinfo(hostname, None, socket.AF_INET)

            for item in all_ips:
                ip = item[4][0]
                if ip.startswith("192.168."):
                    ip1 = list(ip.split("."))
                    ip2 = ip1[:3]
                    self.ip = ".".join(ip2) + ".0/24"
                    logging.debug(f"Local ip successfully found: {self.ip}")
                    return
                
            for item in all_ips:
                ip = item[4][0]
                if ip.startswith("10."):
                    self.ip = ip
                    logging.debug(f"Local ip successfully found: {self.ip}")
                    return
            
            port = 80
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", port))
            self.ip = s.getsockname()[0]
            s.close()

        except Exception as e:
            self.ip = "192.168.1.0/24"
            logging.debug(f"Local ip found failed: {e}")

    def _init_data_file(self):
        """In here,we are updating last_entered time"""
        if not os.path.exists(paths.CONFIG_FILE_PATH):
            with open(paths.CONFIG_FILE_PATH, "w") as f:
                json.dump(self.json_default_data, f, indent=4, ensure_ascii=False)
                pass
            self.check_data = self.json_default_data
        else:
            logging.debug("LAST_ENTERED UPDATING")
            with open(paths.CONFIG_FILE_PATH, "r", encoding="utf-8") as d:
                loaded = json.load(d)
                logging.debug(f"TRY IT {self.check_data}")
            self.check_data.update(loaded)
            self.check_data["last_entered"] = f"{self.now}"
            with open(paths.CONFIG_FILE_PATH, "w") as d:
                json.dump(self.check_data, d, indent=4, ensure_ascii=False)
            logging.debug("---LAST_ENTERED UPDATED---")
            logging.debug("Written file: %s", paths.CONFIG_FILE_PATH)

    def _init_language(self):
        logging.debug("%s", self.data[self.current_lang]['l1']["text"])
        """In here, we are updating the language"""
        self.update_lang_func(self.check_data["choosen_language"]) 
        logging.debug("%s", self.data[self.current_lang]["l2"]["text"])


    def _init_auto_nmap(self):
        """In here,we are checking auto nmap.The nmap_scan is starts If auto nmap is on"""
        target_ips = self.check_data.get("choosen_nmap_ip", [])

        if self.check_data["is_auto_nmap_on"]:
            if not target_ips:
                self.app.root.after(0, lambda: auto_insert(self.app.log_text, "end", "[Auto Nmap is terminated]- Choosen IPs are none"))
                self.choose_auto_nmap_btn.config(text=self.get_text("l323"), bg="#2D2D2D", fg="white", relief="flat")
                self.check_data["is_auto_nmap_on"] = False
                write_file(paths.CONFIG_FILE_PATH, self.check_data)
                
                return
            # self.nmap_scan_instance = nmap_ui(app=app)
            self.nmap_brain = NmapBrain(
                on_line=None,
                on_ip_found= lambda ip: self.app.root.after(0, lambda i=ip: self._add_ip_to_menu(i, self.app)),
                on_finish= lambda inst: self._update_log_label()
            )
            t = threading.Thread(target=self.nmap_brain.try_find, args=(target_ips,), daemon=True)
            logging.debug("[auto_nmap]-Threading is successfully created")
            self.app.root.after(0, lambda: auto_insert(self.app.log_text, "end", "[Auto Nmap is started]"))
            t.start()
            self.choose_auto_nmap_btn.config(text=self.get_text("l324"), bg="#2563EB", fg="white", relief="flat")
        else:
            self.choose_auto_nmap_btn.config(text=self.get_text("l323"), bg="#2D2D2D", fg="white", relief="flat")
    
    def _update_log_label(self):
        self.app.root.after(0, lambda: auto_insert(self.app.log_text, "end", "[Auto Nmap is finished]"))

    def _load_connected_ips(self):
        """In here, we are loading last saved connected_ips"""
        json_ip = self.check_data["connected_ips"]
        self.connected_devicesips.configure(text="\n".join(json_ip.keys()))
        if len(self.check_data["connected_ips"]) > 0:
            for writing in self.check_data["connected_ips"]:
                adb_connect.create_checkbutton(
                    writing, self.app.root, self.app.check_btn_ip,
                    self.app.checkbutton_map, self.app.check_vars,
                    self.check_data, self.app.check_event
                )

    def _apply_theme(self):
        """In here,we are setting the theme"""
        if self.check_data["theme"] == "dark":
            self.choose_theme("#292423", "white")
            self.choose_theme_special()
        else:
            self.choose_theme("SystemButtonFace", "black")
            self.choose_themeW("SystemButtonFace")

    def _add_ip_to_menu(self, ip: str, app):
        from tkinter import Button
        """self.app.log_text.config(state="normal")
        self.app.log_text.insert("end", f"Nmap scan is started in background: {ip}")
        self.app.log_text.config(state="disabled")"""
        new_button = Button(app.menu_frame_found, text=ip)
        new_button.pack(fill="x")
        new_button.bind(
            "<Button-1>",
            lambda event, i=ip: app.found_enter_choosen_ip(event, i)
        )
        global_state.button_references.append(new_button)

    # -----------------------------------------
    def try_find_adb(self):
        if platform.system() == "Windows":
            path_for_now = "/AppData/Local/Android/Sdk/platform-tools/adb.exe"
            tries = [
                "C:/platform-tools/adb.exe",
                "C:/adb.exe",
                "D:/adb.exe",
                "E:/adb.exe",
                os.path.expanduser("~") + path_for_now
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

        self.found_path = None
        system_adb = shutil.which("adb")
        if system_adb:
            tries.append(system_adb)

        for path in tries:
            if os.path.exists(path):
                self.found_path = path

        if self.found_path:
            logging.debug("Found: %s", self.found_path)
            global_state.did_adb_work = True
            self.check_data["choosen_path_for_adb"] = self.found_path
            with open(paths.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.check_data, f, indent=4, ensure_ascii=False)
        else:
            logging.warning("Not found")

        logging.debug(f"Found path = \n {self.found_path}")

