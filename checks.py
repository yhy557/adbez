from datetime import datetime
import os
import json
import logging
import platform
import shutil
from settings import settings_style

from adb_connect import adb_connect
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


class startup_check:
    def app_startup(
        self, connected_devicesips, current_lang, data, check_data,
        check_btn_ip, app,
        style: settings_style, update_lang_func
    ):
        
        choose_theme = style.choose_theme
        choose_themeW = style.choose_themeW
        self.update_lang_func = update_lang_func
        self.check_btn_ip = check_btn_ip
        choose_theme_special = style.choose_theme_special
        logging.debug("%s", data[current_lang]['l1']["text"])
        default_path = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(default_path, "check.json")

        self.check_vars = {}

        now = datetime.now()
        json_default_data = {
            "last_entered": f"{now}",
            "last_commands": {},
            "connected_ips": {},
            "theme": {},
            "choosen_ips": [],
            "choosen_port": "5555",
            "choosen_path_for_adb": {},
            "did_adb_work": False,
            "choosen_language": "en",
            "is_live_helper_on": False
        }
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump(json_default_data, f, indent=4, ensure_ascii=False)
                pass
            check_data = json_default_data
        else:
            logging.debug("LAST_ENTERED UPDATING")
            with open(self.file_path, "r", encoding="utf-8") as d:
                check_data=json.load(d)
            check_data["last_entered"] = f"{now}"
            with open(self.file_path, "w") as d:
                json.dump(check_data, d, indent=4, ensure_ascii=False)
            logging.debug("---LAST_ENTERED UPDATED---")
            logging.debug("Yazan dosya: %s", self.file_path)
        self.check_data = check_data
        self.update_lang_func(self.check_data["choosen_language"])

        if check_data["theme"] == "dark":
            choose_theme("#292423", "white")
            choose_theme_special()
        else:
            choose_theme("SystemButtonFace", "black")
            choose_themeW("SystemButtonFace")

        json_ip = check_data["connected_ips"]
        connected_devicesips.configure(text="\n".join(json_ip.keys()))
        logging.debug("%s", data[current_lang]["l2"]["text"])

        if check_data["did_adb_work"] is not True:
            self.try_find_adb()
            
        if len(check_data["choosen_ips"]) > 0:
            for writing in check_data["choosen_ips"]:
                adb_connect.create_checkbutton(
                    writing, app.root, app.check_btn_ip,
                    app.checkbutton_map, app.check_vars,
                    check_data, app.check_event
                )

    # -----------------------------------------
    def try_find_adb(self):
        if platform.system() == "Windows":
            path_for_now = "/AppData/Local/Android/Sdk/platform-tools/adb.exe"
            tries = [
                "C:/platform-tools/adb.exe",
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

