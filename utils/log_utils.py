from __future__ import annotations
import os
import json
from typing import Any

def auto_insert(widget, locate: str, text: Any):
    widget.config(state="normal")
    widget.insert(locate, f"\n{text}")
    widget.see("end")
    widget.config(state="disabled")