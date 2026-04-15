from tkinter import Button, Frame, Label
import logging
import subprocess
import json
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
 
class buttons:
    def __init__(self, tab2_seperate_scroll_BTN, root, tab2_load_more_btn,
                 tab2_seperate_scroll_LOAD, keyevents_buttons,
                 keyevents_labels, data, current_lang, background_color,
                 canvas2, up_bar, get_text, search, check_data):
        self.tab2_seperate_scroll_BTN = tab2_seperate_scroll_BTN
        self.root = root
        self.tab2_load_more_btn = tab2_load_more_btn
        self.tab2_seperate_scroll_LOAD = tab2_seperate_scroll_LOAD
        self.data = data
        self.current_lang = current_lang
        self.background_color = background_color
        self.canvas2 = canvas2
        self.up_bar = up_bar
        self.get_text = get_text
        self.search = search
        self.check_data = check_data
 
        self.keyevents_buttons = []
        self.keyevents_labels = []
        self.keyevents_labels_2 = []
        self.keyevents_labels_3 = []
        self.keyevents_labels_4 = []
        self.back_btn_list = []

        self.now_btn = []
        self.search_widgets = {}
 
        self.load_clicked = 0

        self._timer = None
        self.searc_only_keys = set()
        self.load_first()

        self.root.after(200, lambda: self.search.bind("<KeyRelease>", self.timer_func))

    def back_all(self):
        logging.debug("Clicked back button")
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[:60]:
            widgets.destroy()
        self.keyevents_labels.clear()
        if hasattr(self, "new_back_btn") and self.new_back_btn.winfo_exists():
            for b in self.back_btn_list:
                self.root.after(0, lambda b=b: b.grid_forget())
        self.restart_number()
        self.root.after(101, lambda: self.tab2_load_more_btn.pack())
        self.load_again()
 
    def categorize(self, text):
        if hasattr(self, "new_back_btn") and self.new_back_btn.winfo_exists():
            self.new_back_btn.destroy()
        self.back_btn_list.clear()
        self.new_back_btn = Button(
            self.up_bar, text="Back", command=self.back_all
        )
        self.back_btn_list.append(self.new_back_btn)
        if self.new_back_btn.winfo_exists():
            self.root.after(0, lambda: self.new_back_btn.grid_forget())
            for b in self.back_btn_list:
                self.root.after(0, lambda b=b: b.grid_forget())
        self.root.after(
            0,
            lambda: self.new_back_btn.grid(
                row=0, column=3, sticky="ne"
            )
        )
        logging.debug(f"[categorize]-Clicked {text}")
        self.canvas2.yview_moveto(0)
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[:288]:
            widgets.destroy()
        self.keyevents_labels.clear()
        self.tab2_load_more_btn.pack_forget()
        logging.debug("[categorize]-Widgets are deleting")
 
        category_sizes = {
            "l310": 25,  # Navigation
            "l311": 22,  # Media & Audio
            "l312": 98,  # Keyboard
            "l313": 10,  # Editing
            "l314": 13,  # System & Power
            "l315": 51,  # TV & Remote Control
            "l316": 15,  # App Shortcuts
            "l317": 53,  # Other
        }
 
        if text not in category_sizes:
            return
 
        self.now_btn = []
        count = category_sizes[text]
 
        for z in range(0, count):
            json_key=f"l{z+21}"
            row_frame = Frame(self.tab2_seperate_scroll_BTN, bg="#292423")
            row_frame.grid(sticky="ew")
            row_frame.columnconfigure(1, weight=1)
            test_label = Label(
                row_frame,
                text="> STATUS: ONLINE",
                fg="#aaaaaa", bg="#1a1a1a",
                justify="left", wraplength=350
            )
            test_label.grid(row=0, column=1, sticky="ew")
            name = f"Input keyevent {z+1}"
            button = Button(
                row_frame,
                text=name,
                font=("Consolas", 10),
                fg="white",
                bg="#2d2d2d",
                activeforeground="white",
                activebackground="#3d3d3d",
                bd=0,
                relief="flat",
                padx=15,
                pady=4,
                cursor="hand2"
            )
            self.now_btn.append(test_label)
            button.grid(row=0, column=0, sticky="w")
            button.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
            button.bind(
                "<Leave>",
                lambda event: self.change_bg_leave(
                    event, "#2d2d2d"
                )
            )
            button.bind(
                "<Button-1>",
                lambda event, key=json_key: self.test_buton_event(
                    event, key
                )
            )
            self.keyevents_buttons.append(button)
            self.keyevents_labels.append(test_label)
 
        if text == "l310":
            self.now_btn[0].configure(text=self.get_text("l23"))
            self.now_btn[1].configure(text=self.get_text("l24"))
            self.now_btn[2].configure(text=self.get_text("l39"))
            self.now_btn[3].configure(text=self.get_text("l40"))
            self.now_btn[4].configure(text=self.get_text("l41"))
            self.now_btn[5].configure(text=self.get_text("l42"))
            self.now_btn[6].configure(text=self.get_text("l43"))
            self.now_btn[7].configure(text=self.get_text("l24"))
            self.now_btn[8].configure(text=self.get_text("l112"))
            self.now_btn[9].configure(text=self.get_text("l113"))
            self.now_btn[10].configure(text=self.get_text("l142"))
            self.now_btn[11].configure(text=self.get_text("l143"))
            self.now_btn[12].configure(text=self.get_text("l145"))
            self.now_btn[13].configure(text=self.get_text("l280"))
            self.now_btn[14].configure(text=self.get_text("l281"))
            self.now_btn[15].configure(text=self.get_text("l282"))
            self.now_btn[16].configure(text=self.get_text("l283"))
            self.now_btn[17].configure(text=self.get_text("l288"))
            self.now_btn[18].configure(text=self.get_text("l289"))
            self.now_btn[19].configure(text=self.get_text("l290"))
            self.now_btn[20].configure(text=self.get_text("l291"))
            self.now_btn[21].configure(text=self.get_text("l300"))
            self.now_btn[22].configure(text=self.get_text("l301"))
            self.now_btn[23].configure(text=self.get_text("l302"))
            self.now_btn[24].configure(text=self.get_text("l303"))
 
        elif text == "l311":
            self.now_btn[0].configure(text=self.get_text("l44"))
            self.now_btn[1].configure(text=self.get_text("l45"))
            self.now_btn[2].configure(text=self.get_text("l105"))
            self.now_btn[3].configure(text=self.get_text("l106"))
            self.now_btn[4].configure(text=self.get_text("l107"))
            self.now_btn[5].configure(text=self.get_text("l108"))
            self.now_btn[6].configure(text=self.get_text("l109"))
            self.now_btn[7].configure(text=self.get_text("l110"))
            self.now_btn[8].configure(text=self.get_text("l111"))
            self.now_btn[9].configure(text=self.get_text("l146"))
            self.now_btn[10].configure(text=self.get_text("l147"))
            self.now_btn[11].configure(text=self.get_text("l148"))
            self.now_btn[12].configure(text=self.get_text("l149"))
            self.now_btn[13].configure(text=self.get_text("l150"))
            self.now_btn[14].configure(text=self.get_text("l184"))
            self.now_btn[15].configure(text=self.get_text("l240"))
            self.now_btn[16].configure(text=self.get_text("l241"))
            self.now_btn[17].configure(text=self.get_text("l242"))
            self.now_btn[18].configure(text=self.get_text("l292"))
            self.now_btn[19].configure(text=self.get_text("l293"))
            self.now_btn[20].configure(text=self.get_text("l294"))
            self.now_btn[21].configure(text=self.get_text("l295"))
 
        elif text == "l312":
            for i in range(0, 10):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+27}")
                )
 
            self.now_btn[10].configure(text=self.get_text("l37"))
            self.now_btn[11].configure(text=self.get_text("l38"))
 
            for i in range(12, 38):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+37}")
                )
            for i in range(38, 44):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+37}")
                )
 
            self.now_btn[44].configure(text=self.get_text("l82"))
            self.now_btn[45].configure(text=self.get_text("l83"))
 
            for i in range(46, 57):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+42}")
                )
 
            self.now_btn[57].configure(text=self.get_text("l101"))
 
            for i in range(58, 65):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+75}")
                )
 
            for i in range(65, 98):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+86}")
                )
 
        elif text == "l313":
            self.now_btn[0].configure(text=self.get_text("l48"))
            self.now_btn[1].configure(text=self.get_text("l81"))
            self.now_btn[2].configure(text=self.get_text("l86"))
            self.now_btn[3].configure(text=self.get_text("l87"))
            self.now_btn[4].configure(text=self.get_text("l131"))
            self.now_btn[5].configure(text=self.get_text("l132"))
            self.now_btn[6].configure(text=self.get_text("l144"))
            self.now_btn[7].configure(text=self.get_text("l297"))
            self.now_btn[8].configure(text=self.get_text("l298"))
            self.now_btn[9].configure(text=self.get_text("l299"))
 
        elif text == "l314":
            self.now_btn[0].configure(text=self.get_text("l46"))
            self.now_btn[1].configure(text=self.get_text("l102"))
            self.now_btn[2].configure(text=self.get_text("l140"))
            self.now_btn[3].configure(text=self.get_text("l141"))
            self.now_btn[4].configure(text=self.get_text("l207"))
            self.now_btn[5].configure(text=self.get_text("l224"))
            self.now_btn[6].configure(text=self.get_text("l243"))
            self.now_btn[7].configure(text=self.get_text("l244"))
            self.now_btn[8].configure(text=self.get_text("l245"))
            self.now_btn[9].configure(text=self.get_text("l296"))
            self.now_btn[10].configure(text=self.get_text("l304"))
            self.now_btn[11].configure(text=self.get_text("l305"))
            self.now_btn[12].configure(text=self.get_text("l308"))
 
        elif text == "l315":
            for i in range(0, 10):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+186}")
                )
 
            self.now_btn[10].configure(text=self.get_text("l197"))
            for i in range(11, 20):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+187}")
                )
 
            self.now_btn[20].configure(text=self.get_text("l247"))
            self.now_btn[21].configure(text=self.get_text("l248"))
            self.now_btn[22].configure(text=self.get_text("l249"))
            self.now_btn[23].configure(text=self.get_text("l250"))
            self.now_btn[24].configure(text=self.get_text("l252"))
 
            for i in range(25, 51):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+228}")
                )
 
        elif text == "l316":
            self.now_btn[0].configure(text=self.get_text("l25"))
            self.now_btn[1].configure(text=self.get_text("l26"))
            self.now_btn[2].configure(text=self.get_text("l47"))
            self.now_btn[3].configure(text=self.get_text("l84"))
            self.now_btn[4].configure(text=self.get_text("l85"))
            self.now_btn[5].configure(text=self.get_text("l100"))
            self.now_btn[6].configure(text=self.get_text("l103"))
            self.now_btn[7].configure(text=self.get_text("l104"))
            self.now_btn[8].configure(text=self.get_text("l185"))
            self.now_btn[9].configure(text=self.get_text("l196"))
            self.now_btn[10].configure(text=self.get_text("l227"))
            self.now_btn[11].configure(text=self.get_text("l228"))
            self.now_btn[12].configure(text=self.get_text("l229"))
            self.now_btn[13].configure(text=self.get_text("l230"))
            self.now_btn[14].configure(text=self.get_text("l251"))
 
        elif text == "l317":
 
            self.now_btn[0].configure(text=self.get_text("l21"))
            self.now_btn[1].configure(text=self.get_text("l22"))
            self.now_btn[2].configure(text=self.get_text("l99"))
            self.now_btn[3].configure(text=self.get_text("l114"))
            self.now_btn[4].configure(text=self.get_text("l115"))
 
            for i in range(5, 20):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+111}")
                )
 
            for i in range(20, 36):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+188}")
                )
 
            self.now_btn[36].configure(text=self.get_text("l225"))
            self.now_btn[37].configure(text=self.get_text("l226"))
 
            for i in range(38, 46):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+193}")
                )
 
            self.now_btn[46].configure(text=self.get_text("l279"))
 
            for i in range(47, 51):
                self.now_btn[i].configure(
                    text=self.get_text(f"l{i+237}")
                )
 
            self.now_btn[51].configure(text=self.get_text("l306"))
            self.now_btn[52].configure(text=self.get_text("l307"))
 
    def change_bg(self, event, color):
        event.widget.configure(background=color)
 
    def change_bg_leave(self, event, color):
        event.widget.configure(background=color)

    def timer_func(self, event):
        if self._timer:
            self.root.after_cancel(self._timer)
        self._timer = self.root.after(800, self.search_categorize)

    def search_categorize(self):
        self.keyevents_labels.clear()
        self.keyevents_buttons.clear()
        self.tab2_load_more_btn.pack_forget()
        search_term = self.search.get().lower()

        if not search_term:
            for key, (row_frame, button, label) in self.search_widgets.items():
                if key in self.searc_only_keys:
                    row_frame.grid_remove()
                else:
                    row_frame.grid()
                    if not self.tab2_load_more_btn.winfo_viewable():
                        self.tab2_load_more_btn.pack()
            return

        for key, (row_frame, button, label) in self.search_widgets.items():
            row_frame.grid_remove()

        for key, content in self.data[self.current_lang].items():
            key_number = int(key[1:]) if key[1:].isdigit() else 0
            if not (21 <= key_number <= 308):
                continue
            if not any(search_term.lower() in str(v).lower() for v in content.values()):
                continue
            if key in self.search_widgets:
                self.search_widgets[key][0].grid()
            else:
                row_frame = Frame(self.tab2_seperate_scroll_BTN, bg="#292423")
                row_frame.grid(sticky="ew")
                row_frame.columnconfigure(1, weight=1)
                test_label = Label(
                    row_frame,
                    text=self.get_text(key),
                    fg="#aaaaaa", bg="#1a1a1a",
                    justify="left", wraplength=350
                )
                test_label.grid(row=0, column=1, sticky="ew")
                button = Button(
                    row_frame,
                    text=f"Input Keyevent {key}",
                    font=("Consolas", 10),
                    fg="white",
                    bg="#2d2d2d",
                    activeforeground="white",
                    activebackground="#3d3d3d",
                    bd=0,
                    relief="flat",
                    padx=15,
                    pady=4,
                    cursor="hand2"
                )
                self.now_btn.append(test_label)
                button.grid(row=0, column=0, sticky="w")
                button.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
                button.bind(
                    "<Leave>",
                    lambda event: self.change_bg_leave(
                        event, "#2d2d2d"
                    )
                )
                button.bind(
                    "<Button-1>",
                    lambda event, k=key: self.test_buton_event(
                        event, k
                    )
                )
                self.keyevents_buttons.append(button)
                self.keyevents_labels.append(test_label)

                self.search_widgets[key] = (row_frame, button, test_label)
                self.searc_only_keys.add(key)
                


    def load_first(self):
        self.tab2_seperate_scroll_BTN.columnconfigure(0, weight=1)
        for i in range(60):
            json_key=f"l{i+21}"
            row_frame = Frame(self.tab2_seperate_scroll_BTN, bg="#292423")
            row_frame.grid(sticky="ew")
            row_frame.columnconfigure(1, weight=1)
            self.test_label = Label(
                row_frame,
                text="> STATUS: ONLINE",
                fg="#aaaaaa", bg="#1a1a1a",
                justify="left", wraplength=350
            )
 
            """
            THIS FEATURE WAS PUTTING A 0.4% - 0.5% LOAD ON THE CPU,
            SO I DISABLED IT FOR THAT REASON
            test_label.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
            test_label.bind("<Leave>", lambda event: self.change_bg_leave(event, "#121212"))
            """
            self.test_label.grid(row=0, column=1, sticky="ew")
            name = f"Input keyevent {i+1}"
            self.button = Button(
                row_frame,
                text=name,
                font=("Consolas", 10),
                fg="white",
                bg="#2d2d2d",
                activeforeground="white",
                activebackground="#3d3d3d",
                bd=0,
                relief="flat",
                padx=15,
                pady=4,
                cursor="hand2"
            )
            self.button.grid(row=0, column=0, sticky="w")
            self.button.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
            self.button.bind(
                "<Leave>", lambda event: self.change_bg_leave(event, "#2d2d2d")
            )
            self.button.bind(
                "<Button-1>",
                lambda event, key=json_key: self.test_buton_event(
                    event, key
                )
            )
            self.keyevents_buttons.append(self.button)
            self.keyevents_labels.append(self.test_label)
 
            key = f"l{i+21}"
            self.search_widgets[key] = (row_frame, self.button, self.test_label)
            self.searc_only_keys.discard(key)
            self.keyevents_labels[i].configure(
                text=self.get_text(key))
            if not self.tab2_load_more_btn.winfo_viewable():
                self.root.after(101, lambda: self.tab2_load_more_btn.pack())
 
    def restart_number(self):
        self.load_clicked = 0
 
    def called_test_function(self):
        self.load_clicked += 1
        logging.debug(
            "[called_test_function]-clicked test: %s", self.load_clicked)
        if self.load_clicked == 1:
            self.load_all(60, 120)
        elif self.load_clicked == 2:
            self.load_all(120, 180)
        elif self.load_clicked == 3:
            self.load_all(180, 240)
        elif self.load_clicked == 4:
            self.load_all(240, 288, is_last=True)
        else:
            logging.debug("[called_test_function]-All keyevents loaded")
 
    # IF LANGUAGES CHANGED, LOAD AGAIN
    def load_again(self):
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[:60]:
            widgets.destroy()
            self.keyevents_labels.clear()
            logging.debug("[load_again]-Widgets are deleting")
        self.keyevents_buttons.clear()
        self.keyevents_labels.clear()
        self.root.after(10, lambda: self.load_first())
 
    def test_buton_event(self, event, json_key):
        try:
            for ip in self.check_data["choosen_ips"]:
                command = [self.check_data["choosen_path_for_adb"], "-s", ip, "shell", "input", "keyevent", str(int(str(json_key).lstrip("l"))-20)]
                logging.debug("CURRENT COMMAND: \n",command)
                keyevent_process=subprocess.Popen(
                    command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True    
                )
                stdout,stderr= keyevent_process.communicate()
                if keyevent_process.returncode == 0:
                    logging.debug(f"SUCCES: {stdout}")
                else:
                    logging.error(f"ERROR: {stderr}")
        except Exception as e:
            logging.error(f"FAILED: ADB KEYEVENT {e}")
        
        print("CHOOSEN IPS: ",self.check_data["choosen_ips"])
 
    # SEPERATE
    def load_all(self, range_x, range_y, is_last=False):
        logging.debug("[load_all]-Clicked------------------------------------")
        self.root.update_idletasks()
        self.tab2_load_more_btn.pack_forget()
        self.tab2_seperate_scroll_LOAD.pack_forget()
        self.tab2_seperate_scroll_BTN.columnconfigure(0, weight=1)
        for i in range(range_x, range_y):
            json_key=f"l{i+21}"
            row_frame = Frame(self.tab2_seperate_scroll_BTN, bg="#292423")
            row_frame.grid(sticky="ew")
            row_frame.columnconfigure(1, weight=1)
            test_label = Label(
                row_frame,
                text="> STATUS: ONLINE",
                font=("Consolas", 10),
                fg="#aaaaaa",
                bg="#1a1a1a",
                justify="left",
                wraplength=500
            )
 
            test_label.bind(
                "<Enter>", lambda event: self.change_bg(event, "gray")
            )
            test_label.bind(
                "<Leave>", lambda event: self.change_bg_leave(event, "#121212")
            )
            test_label.grid(row=0, column=1, sticky="ew")
            name = f"Input keyevent {i+1}"
            button = Button(
                row_frame,
                text=name,
                font=("Consolas", 10),
                fg="white",
                bg="#2d2d2d",
                activeforeground="white",
                activebackground="#3d3d3d",
                bd=0,
                relief="flat",
                padx=15,
                pady=4,
                cursor="hand2",
                wraplength=450)
            button.grid(row=0, column=0, sticky="w")
            button.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
            button.bind(
                "<Button-1>",
                lambda event, key=json_key: self.test_buton_event(
                    event,key
                )
            )
            button.bind(
                "<Leave>", lambda event: self.change_bg_leave(event, "#2d2d2d")
            )
            self.keyevents_buttons.append(button)
            self.keyevents_labels.append(test_label)
            key = f"l{i+21}"
            self.keyevents_labels[i].configure(
                text=self.get_text(key))
 
        self.root.after(100, lambda: self.tab2_seperate_scroll_LOAD.pack())
        if not is_last:
            self.root.after(101, lambda: self.tab2_load_more_btn.pack())
 
