import logging
from scroll_buttons import buttons

class TabControl:
    def __init__(self, _tab_canvas, _tabs, all_menu, btn_instance, canvas2, tab2_seperate_scroll_BTN, _content_frame):

        self._tab_canvas = _tab_canvas
        self._tabs = _tabs
        self.all_menu = all_menu
        self.btn_instance = btn_instance
        self.canvas2 = canvas2
        self.tab2_seperate_scroll_BTN = tab2_seperate_scroll_BTN
        self._content_frame = _content_frame

        self.TAB_W = 110
        self.TAB_H = 32
        self.TAB_R = 8
        self.TAB_GAP = 2
        self.TAB_BG = "#2a2a3a"
        self.TAB_ACTIVE = "#6ec9a4"
        self.TAB_HOVER = "#3a3a4a"
        self.TAB_FG = "#ffffff"
        self.TAB_FONT = ("Segoe UI", 9)

        self._active_tab = None

        
    
    def make_tab(self, canvas, x, key, text, frame, lang_key):
        r, w, h = self.TAB_R, self.TAB_W, self.TAB_H
        bg_tag = f"bg_{key}"
        txt_tag = f"txt_{key}"
        line_tag = f"line_{key}"
        color = self.TAB_BG

        canvas.create_arc(x, 0, x+2*r, 2*r, start=90, extent=90, fill=color,
                        outline="", tags=bg_tag)
        canvas.create_arc(x+w-2*r, 0, x+w, 2*r, start=0, extent=90, fill=color,
                        outline="", tags=bg_tag)
        canvas.create_rectangle(x+r, 0, x+w-r, h, fill=color,
                                outline="", tags=bg_tag)
        canvas.create_rectangle(x, r, x+w, h, fill=color, outline="", tags=bg_tag)

        txt_id = canvas.create_text(x + w//2, h//2, text=text,
                                    fill=self.TAB_FG, font=self.TAB_FONT, tags=txt_tag)

        canvas.create_rectangle(x+2, h-3, x+w-2, h,
                                fill=self.TAB_BG, outline="", tags=line_tag)

        self._tabs[key] = {"frame": frame, "text_id": txt_id,
                    "bg_tag": bg_tag, "line_tag": line_tag, "lang_key": lang_key}

        for tag in (bg_tag, txt_tag):
            canvas.tag_bind(tag, "<Button-1>", lambda e, k=key: self.switch_tab(k))
            canvas.tag_bind(tag, "<Enter>",
                            lambda e, k=key: self._tab_hover(k, True))
            canvas.tag_bind(tag, "<Leave>",
                            lambda e, k=key: self._tab_hover(k, False))
        self.switch_tab("connect")

    def _tab_hover(self, key, entering):
        if key == self._active_tab:
            return
        color = self.TAB_HOVER if entering else self.TAB_BG
        self._tab_canvas.itemconfig(self._tabs[key]["bg_tag"], fill=color)

    def switch_tab(self, key):
        if key == self._active_tab:
            return
        for k, v in self._tabs.items():
            v["frame"].place_forget()
            if k != key:
                self._tab_canvas.itemconfig(v["bg_tag"], fill=self.TAB_BG)
                self._tab_canvas.itemconfig(v["line_tag"], fill=self.TAB_BG)
        self._tabs[key]["frame"].place(in_=self._content_frame, x=0, y=0,
                                relwidth=1, relheight=1)
        self._tab_canvas.itemconfig(self._tabs[key]["line_tag"], fill=self.TAB_ACTIVE)
        self._active_tab = key
        self._on_tab_change(key)

    # FOR CATCHING CURRENT TAB
    def delete_widgets(self):
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[60:]:
            widgets.destroy()
        logging.debug("Widgets are deleting")
    
    def _on_tab_change(self, key):
        for m in self.all_menu:
            if m.winfo_exists():
                m.place_forget()
            else:
                logging.warning(f"{m} is null")
        if key == "keyevents":
            self.btn_instance.restart_number()
            self.canvas2.yview_moveto(0)
            self.delete_widgets()
            self.btn_instance.load_again()
        if hasattr(self.btn_instance, "new_back_btn"):
            logging.debug("BACK BUTON IS DELETING")
            if self.btn_instance.new_back_btn is not None:
                logging.debug(f"NEW_BACK_BTN IS NOT NONE {type(self.btn_instance.new_back_btn)}")
                if self.btn_instance.new_back_btn.winfo_exists():
                    logging.debug("NEW_BACK_BTN IS HERE")
                    self.btn_instance.root.update_idletasks()
                    self.btn_instance.new_back_btn.destroy()
        logging.debug(key)
