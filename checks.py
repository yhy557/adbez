from datetime import datetime
import os
import json
class startup_check:
    def app_startup(self, connected_devicesips, current_lang, data):
        self.connected_devicesips = connected_devicesips
        print(f"{data[current_lang]['l1']}")
        default_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(default_path, "check.json")

        now = datetime.now()
        #if not os.path.exists(file_path):
        json_default_data = {
            "last_entered": f"{now}",
            "last_commands": {},
            "connected_ips": {}
        }
        #else:
        #    pass

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump(json_default_data, f, indent=4, ensure_ascii=False)
                pass
            check_data = json_default_data
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                check_data = json.load(f)
                #json.dump(json_default_data, f, indent=4, ensure_ascii=False)
                #pass
        json_ip = check_data["connected_ips"]
        connected_devicesips.configure(text="\n".join(json_ip.keys()))

        #CONTROLLING SOMETHINGS
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        print(f"{data[current_lang]["l2"]}")
