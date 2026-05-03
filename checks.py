from datetime import datetime
import os
import json
import logging
import platform
import shutil
import threading
from nmap_scan import nmap_brain,nmap_ui
from settings import settings_style
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bcopy import MainApp

from adb_connect import adb_connect
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


class startup_check:
    def app_startup(
        self, connected_devicesips, current_lang, data, check_data,
        check_btn_ip, app:'MainApp',
        style: settings_style, update_lang_func
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

        self.default_path = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(self.default_path, "check.json")

        self.now = datetime.now()
        self.json_default_data = {
            "last_entered": f"{self.now}",
            "last_commands": {},
            "connected_ips": {},
            "theme": {},
            "choosen_ips": [],
            "choosen_nmap_ip": [],
            "founded_ips": [],
            "choosen_port": "5555",
            "choosen_path_for_adb": {},
            "did_adb_work": False,
            "did_nmap_work": False,
            "choosen_language": "en",
            "is_live_helper_on": False,
            "is_auto_nmap_on": False
        }
        self.check_vars = {}
        if self.check_data["did_adb_work"] is not True:
            self.try_find_adb()
        self._init_data_file()
        self._init_language()
        self._init_auto_nmap()
        self._load_connected_ips()
        self._apply_theme()

    def _init_data_file(self):
        """In here,we are updating last_entered time"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump(self.json_default_data, f, indent=4, ensure_ascii=False)
                pass
            self.check_data = self.json_default_data
        else:
            logging.debug("LAST_ENTERED UPDATING")
            with open(self.file_path, "r", encoding="utf-8") as d:
                loaded = json.load(d)
                logging.debug(f"TRY IT {self.check_data}")
            self.check_data.update(loaded)
            self.check_data["last_entered"] = f"{self.now}"
            with open(self.file_path, "w") as d:
                json.dump(self.check_data, d, indent=4, ensure_ascii=False)
            logging.debug("---LAST_ENTERED UPDATED---")
            logging.debug("Written file: %s", self.file_path)

    def _init_language(self):
        logging.debug("%s", self.data[self.current_lang]['l1']["text"])
        """In here, we are updating the language"""
        self.update_lang_func(self.check_data["choosen_language"]) 
        logging.debug("%s", self.data[self.current_lang]["l2"]["text"])


    def _init_auto_nmap(self):
        """In here,we are checking auto nmap.The nmap_scan is starts If auto nmap is on"""
        if self.check_data["is_auto_nmap_on"] == True:
            # self.nmap_scan_instance = nmap_ui(app=app)
            self.nmap_brain = nmap_brain(
                on_line=None,
                on_ip_found= lambda ip: self.app.root.after(0, lambda i=ip: self._add_ip_to_menu(i, self.app)),
                on_finish=None
            )
            t = threading.Thread(target=self.nmap_brain.try_find, args=(self.check_data["choosen_nmap_ip"],), daemon=True)
            t.start()
            self.choose_auto_nmap_btn.config(text=self.get_text("l324"), bg="#2563EB", fg="white", relief="flat")
        else:
            self.choose_auto_nmap_btn.config(text=self.get_text("l323"), bg="#2D2D2D", fg="white", relief="flat")

    def _load_connected_ips(self):
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
        app.button_references.append(new_button)

    # -----------------------------------------
    def try_find_adb(self):
        if platform.system() == "Windows":
            path_for_now = "/AppData/Local/Android/Sdk/platform-tools/adb.exe"
            tries = [
                "C:/platform-tools/adb.exe",
                "C:/adb.exe",
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
            self.check_data["did_adb_work"] = True
            self.check_data["choosen_path_for_adb"] = self.found_path
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.check_data, f, indent=4, ensure_ascii=False)
        else:
            logging.warning("Not found")

        print("Found path = ", self.found_path)

