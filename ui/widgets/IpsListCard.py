import config.constants as const
from config.state import global_state
from tkinter import (IntVar, Frame, Checkbutton, Label)


class MakeIpCard:
    def __init__(self, parent, ip_text: str):

        self.ip_text = ip_text
        self.var_state = IntVar()

        self.main_frame = Frame(parent, bg="#2A2C23")
        self.main_frame.pack(fill="x")

        self.check_box = Checkbutton(
            self.main_frame,
            variable=self.var_state,
            command=self._on_toggle,
            bg=const.ROUNDED_PANELS_COLOR
        )
        self.check_box.pack(side="left", anchor="w")

        self.ip_label = Label(self.main_frame, text=self.ip_text, bg=const.ROUNDED_PANELS_COLOR, fg="white")
        self.ip_label.pack(side="left", expand=True, fill="x", anchor="center")

        self.is_connected_label = Label(self.main_frame, text="Not connected", bg=const.ROUNDED_PANELS_COLOR, fg="red")
        self.is_connected_label.pack(side="right",anchor="e")

        global_state.created_card_ips.append(ip_text)
        global_state.ip_card_map[self.ip_text] = self

    def _on_toggle(self):
        if self.var_state.get() == 1:
            print(f"Choosen: {self.ip_text}")
            global_state.adb_connect_choosen_ips.append(self.ip_text)
        else:
            if self.ip_text in global_state.adb_connect_choosen_ips:
                global_state.adb_connect_choosen_ips.remove(self.ip_text)
    
    def set_connected(self, succes: bool):
        if succes:
            self.is_connected_label.config(text="connected", fg="green")
        else:
            self.var_state.set(0)
            if self.is_connected_label.cget("text") == "connected":
                self.is_connected_label.config(text="disconnected", fg="red")
            else:
                pass