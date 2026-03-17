from datetime import datetime
import os
import json
import logging
from settings import settings_style
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


class startup_check:
    def app_startup(
        self, connected_devicesips, current_lang, data, check_data,
        style: settings_style, update_lang_func
    ):
        choose_theme = style.choose_theme
        choose_themeW = style.choose_themeW
        self.update_lang_func = update_lang_func
        self.check_data = check_data
        self.update_lang_func(self.check_data["choosen_language"])
        choose_theme_special = style.choose_theme_special
        logging.debug("%s", data[current_lang]['l1'])
        default_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(default_path, "check.json")

        with open("check.json", "r", encoding="utf-8") as f:
            check_data = json.load(f)

        now = datetime.now()
        json_default_data = {
            "last_entered": f"{now}",
            "last_commands": {},
            "connected_ips": {},
            "theme": {},
            "choosen_ips": [],
            "choosen_path_for_adb": {},
            "did_adb_work": False,
            "choosen_language": "en"
        }

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump(json_default_data, f, indent=4, ensure_ascii=False)
                pass
            check_data = json_default_data
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                check_data = json.load(f)

        if check_data["theme"] == "dark":
            choose_theme("#292423", "white")
            choose_theme_special()
        else:
            choose_theme("SystemButtonFace", "black")
            choose_themeW("SystemButtonFace")

        json_ip = check_data["connected_ips"]
        connected_devicesips.configure(text="\n".join(json_ip.keys()))
        logging.debug("%s", data[current_lang]["l2"])

        
