import os

# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE_PATH = os.path.join(BASE_DIR, "check.json")
LOG_FILE_PATH = os.path.join(BASE_DIR, "now_logs.txt")
LANG_FILE_PATH = os.path.join(BASE_DIR, "lang.json")
PROCESS_MONITOR_FILE_PATH = os.path.join(BASE_DIR, "ui", "windows", "monitor_window.py")

