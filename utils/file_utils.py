from __future__ import annotations
import os
import json
from typing import Any

#We are opening files with secure method
def open_file(file_path: Any):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def write_file(file_path: Any, data: dict | str | int | None):
    temp_file = file_path + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, file_path)

def append_file(file_path: Any, data: dict | str | int | None):
    temp_file = file_path + ".tmp"
    with open(temp_file, "a", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, file_path)