from tkinter import Toplevel, Label



class Tooltip:
    def __init__(self, widget, text, enter_event="<Enter>", leave_events=("<Leave>",)):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.enter_event = enter_event

        self.anim_id = None

        self.enter_id = self.widget.bind(self.enter_event, self.show_tooltip, add="+")


        self.leave_ids = []
        for event in leave_events:
            lid = self.widget.bind(event, self.hide_tooltip, add="+")
            self.leave_ids.append((event, lid))

    def stop_animation(self):
        if self.anim_id:
            self.widget.after_cancel(self.anim_id)
            self.anim_id = None

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")

        self.current_alpha = 0.0
        self.tw.attributes("-alpha", self.current_alpha)

        self.stop_animation()
        self.open_tooltip()

        label = Label(self.tw, text=self.text, background="#5085a2",
                      relief="solid", borderwidth=1,
                      font=("tahoma", 8, "normal"))
        label.pack()

    def open_tooltip(self):
        if self.current_alpha < 1.0:
            self.current_alpha += 0.1
            self.tw.attributes("-alpha", self.current_alpha)
            self.anim_id = self.widget.after(30, self.open_tooltip)

    def hide_tooltip(self, event=None):
        self.stop_animation()
        self.close_tooltip()
    
    def close_tooltip(self, count: int = 0):
        if not self.tooltip_window:
            return

        self.tooltip_window.destroy()
        self.tooltip_window = None
        return
    
    def unregister(self):
        self.hide_tooltip()
        if hasattr(self, "enter_id"):
            self.widget.unbind(self.enter_event, self.enter_id)
        for event, lid in self.leave_ids:
            self.widget.unbind(event, lid)
