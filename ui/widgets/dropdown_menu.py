import logging
import config.constants as const
from tkinter import Frame, Scrollbar, Canvas



class MenuManager:
    def __init__(self, root):
        self.root = root

    def scrollable_menu(self, parent, max_height=150):
            max_width = 150
            outer = Frame(parent, bg=const.MENU_COLOR, bd=1, relief="solid")
            scrollable_menu_canvas = Canvas(outer, bg=const.MENU_COLOR, highlightthickness=0, height=1)
            scrollbar = Scrollbar(outer, orient="vertical", command=scrollable_menu_canvas.yview, width=10)
            inner = Frame(scrollable_menu_canvas, bg=const.MENU_COLOR)
            
            inner.bind("<Configure>", lambda e: (
                scrollable_menu_canvas.configure(scrollregion=scrollable_menu_canvas.bbox("all")),
                scrollable_menu_canvas.configure(
                    height=min(inner.winfo_reqheight(), max_height), 
                    width=min(inner.winfo_reqwidth(), max_width)
                )
            ) if e.widget == inner else None)
            scrollable_menu_canvas.create_window((0, 0), window=inner, anchor="nw")
            scrollable_menu_canvas.configure(yscrollcommand=scrollbar.set, width=inner.winfo_reqwidth())

            scrollable_menu_canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            scrollable_menu_canvas.bind("<MouseWheel>", lambda e: scrollable_menu_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            scrollable_menu_canvas.bind("<Button-4>", lambda e: scrollable_menu_canvas.yview_scroll(-1, "units"))
            scrollable_menu_canvas.bind("<Button-5>", lambda e: scrollable_menu_canvas.yview_scroll(1, "units"))
            
            return outer, inner

    def toggle_menu(self, event, frame, choosen_button, selected_tab):
        logging.debug(f"{choosen_button} is opening")
        self.root.update_idletasks()
        if frame.winfo_viewable():
            frame.place_forget()
            logging.debug(f"{frame} is deleted")
            return
        button_x = choosen_button.winfo_rootx()
        button_y = choosen_button.winfo_rooty()
        button_xp = selected_tab.winfo_rootx()
        button_yp = selected_tab.winfo_rooty()

        logging.debug(f"Real screen: {button_x}, {button_y}")
        logging.debug(f"This window: {button_xp}, {button_yp}")
        try:
            frame.place(x=(button_x - button_xp),
                        y=(button_y - button_yp) + choosen_button.winfo_height(), anchor="nw")
            children = frame.winfo_children()
            if children and not isinstance(children[0], Canvas):
                for child in children:
                    child.pack(fill="x")
            frame.lift()
            self.root.update_idletasks()
            now_x, now_y = frame.winfo_rootx(), frame.winfo_rooty()
            logging.debug(f"Created found menu at: {now_x, now_y}")
        except Exception as e:
            logging.error("[E]Menu can't be created: %s", e)
