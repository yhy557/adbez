import tkinter as tk

class SmoothScrollbar(tk.Canvas):
    def __init__(self, parent, command, orient="vertical", **kwargs):
        self.orient = orient
        self.command = command
        self.drag_start = 0

        if self.orient == "vertical":
            super().__init__(parent, width=8, bg="#1a1a2e", highlightthickness=0, **kwargs)
        else:
            super().__init__(parent, height=8, bg="#1a1a2e", highlightthickness=0, **kwargs)
            
        self.thumb = self.create_rounded_thumb()
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_thumb(self):
        if self.orient == "vertical":
            return self.create_rectangle(2, 0, 6, 30, fill="#4a4a6a", tags="thumb", width=0)
        else:
            return self.create_rectangle(0, 2, 30, 6, fill="#4a4a6a", tags="thumb", width=0)

    def set(self, lo, hi):
        h = self.winfo_height()
        w = self.winfo_width()
        y0 = float(lo) * h
        y1 = float(hi) * h
        x0 = float(lo) * w
        x1 = float(hi) * w

        if self.orient == "vertical":
            self.coords(self.thumb, 2, y0, 6, y1)
        else:
            self.coords(self.thumb, x0, 2, x1, 6)

    def on_click(self, event):
        if self.orient == "vertical":
            self.drag_start = event.y
        else:
            self.drag_start = event.x

    def on_drag(self, event):
        if self.orient == "vertical":
            total = self.winfo_height()
            delta = (event.y - self.drag_start) / total
            self.drag_start = event.y
            coords = self.coords(self.thumb)
            current_pos = coords[1] / total if total > 0 else 0
        else:
            total = self.winfo_width()
            delta = (event.x - self.drag_start) / total
            self.drag_start = event.x
            coords = self.coords(self.thumb)
            current_pos = coords[0] / total if total > 0 else 0

        self.command("moveto", current_pos + delta)

    def on_enter(self, event):
        if self.orient == "vertical":
            self.itemconfig(self.thumb, fill="#6a6a9a")
        else:
            self.itemconfig(self.thumb, fill="#6a6a9a")

    def on_leave(self, event):
        self.itemconfig(self.thumb, fill="#4a4a6a")