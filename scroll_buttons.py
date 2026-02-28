from tkinter import Button, Frame, Label
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


class buttons:
    def __init__(self, tab2_seperate_scroll_BTN, root, tab2_load_more_btn,
                 tab2_seperate_scroll_LOAD, keyevents_buttons,
                 keyevents_labels, data, current_lang, background_color,
                 canvas2, up_bar):
        self.tab2_seperate_scroll_BTN = tab2_seperate_scroll_BTN
        self.root = root
        self.tab2_load_more_btn = tab2_load_more_btn
        self.tab2_seperate_scroll_LOAD = tab2_seperate_scroll_LOAD
        self.data = data
        self.current_lang = current_lang
        self.background_color = background_color
        self.canvas2 = canvas2
        self.up_bar = up_bar

        self.keyevents_buttons = []
        self.keyevents_labels = []
        self.keyevents_labels_2 = []
        self.keyevents_labels_3 = []
        self.keyevents_labels_4 = []
        self.back_btn_list = []

        self.load_clicked = 0
        self.load_first()

    def back_all(self):
        print(f"Clicked back button")
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[:60]:
            widgets.destroy()
            self.keyevents_labels.clear()
        if self.new_back_btn.winfo_exists():
            for b in self.back_btn_list:
                self.root.after(0, lambda b=b: b.grid_forget())
        self.load_again()

    def categorize(self, text):
        self.new_back_btn = Button(self.up_bar, text="Back", command=self.back_all)
        self.back_btn_list.append(self.new_back_btn)
        if self.new_back_btn.winfo_exists():
            self.root.after(0, lambda: self.new_back_btn.grid_forget())
            for b in self.back_btn_list:
                self.root.after(0, lambda b=b: b.grid_forget())
        self.root.after(0, lambda: self.new_back_btn.grid(row=0, column=3, sticky="ne"))
        logging.debug(f"[categorize]-Clicked {text}")
        self.canvas2.yview_moveto(0)
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[:60]:
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
            row_frame = Frame(self.tab2_seperate_scroll_BTN)
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
            button.bind("<Leave>", lambda event: self.change_bg_leave(event, "#2d2d2d"))
            self.keyevents_buttons.append(button)
            self.keyevents_labels.append(test_label)

        if text == "l310":
            self.now_btn[0].configure(text=self.data[self.current_lang]["l23"])
            self.now_btn[1].configure(text=self.data[self.current_lang]["l24"])
            self.now_btn[2].configure(text=self.data[self.current_lang]["l39"])
            self.now_btn[3].configure(text=self.data[self.current_lang]["l40"])
            self.now_btn[4].configure(text=self.data[self.current_lang]["l41"])
            self.now_btn[5].configure(text=self.data[self.current_lang]["l42"])
            self.now_btn[6].configure(text=self.data[self.current_lang]["l43"])
            self.now_btn[7].configure(text=self.data[self.current_lang]["l24"])
            self.now_btn[8].configure(
                text=self.data[self.current_lang]["l112"]
            )
            self.now_btn[9].configure(
                text=self.data[self.current_lang]["l113"]
            )
            self.now_btn[10].configure(
                text=self.data[self.current_lang]["l142"]
            )
            self.now_btn[11].configure(
                text=self.data[self.current_lang]["l143"])
            self.now_btn[12].configure(
                text=self.data[self.current_lang]["l145"])
            self.now_btn[13].configure(
                text=self.data[self.current_lang]["l280"])
            self.now_btn[14].configure(
                text=self.data[self.current_lang]["l281"])
            self.now_btn[15].configure(
                text=self.data[self.current_lang]["l282"])
            self.now_btn[16].configure(
                text=self.data[self.current_lang]["l283"])
            self.now_btn[17].configure(
                text=self.data[self.current_lang]["l288"])
            self.now_btn[18].configure(
                text=self.data[self.current_lang]["l289"])
            self.now_btn[19].configure(
                text=self.data[self.current_lang]["l290"])
            self.now_btn[20].configure(
                text=self.data[self.current_lang]["l291"])
            self.now_btn[21].configure(
                text=self.data[self.current_lang]["l300"])
            self.now_btn[22].configure(
                text=self.data[self.current_lang]["l301"])
            self.now_btn[23].configure(
                text=self.data[self.current_lang]["l302"])
            self.now_btn[24].configure(
                text=self.data[self.current_lang]["l303"])

        elif text == "l311":
            self.now_btn[0].configure(text=self.data[self.current_lang]["l44"])
            self.now_btn[1].configure(text=self.data[self.current_lang]["l45"])
            self.now_btn[2].configure(
                text=self.data[self.current_lang]["l105"])
            self.now_btn[3].configure(
                text=self.data[self.current_lang]["l106"])
            self.now_btn[4].configure(
                text=self.data[self.current_lang]["l107"])
            self.now_btn[5].configure(
                text=self.data[self.current_lang]["l108"])
            self.now_btn[6].configure(
                text=self.data[self.current_lang]["l109"])
            self.now_btn[7].configure(
                text=self.data[self.current_lang]["l110"])
            self.now_btn[8].configure(
                text=self.data[self.current_lang]["l111"])
            self.now_btn[9].configure(
                text=self.data[self.current_lang]["l146"])
            self.now_btn[10].configure(
                text=self.data[self.current_lang]["l147"])
            self.now_btn[11].configure(
                text=self.data[self.current_lang]["l148"])
            self.now_btn[12].configure(
                text=self.data[self.current_lang]["l149"])
            self.now_btn[13].configure(
                text=self.data[self.current_lang]["l150"])
            self.now_btn[14].configure(
                text=self.data[self.current_lang]["l184"])
            self.now_btn[15].configure(
                text=self.data[self.current_lang]["l240"])
            self.now_btn[16].configure(
                text=self.data[self.current_lang]["l241"])
            self.now_btn[17].configure(
                text=self.data[self.current_lang]["l242"])
            self.now_btn[18].configure(
                text=self.data[self.current_lang]["l292"])
            self.now_btn[19].configure(
                text=self.data[self.current_lang]["l293"])
            self.now_btn[20].configure(
                text=self.data[self.current_lang]["l294"])
            self.now_btn[21].configure(
                text=self.data[self.current_lang]["l295"])

        elif text == "l312":
            for i in range(0, 10):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+27}"]
                )

            self.now_btn[10].configure(
                text=self.data[self.current_lang]["l37"])
            self.now_btn[11].configure(
                text=self.data[self.current_lang]["l38"])

            for i in range(12, 38):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+37}"]
                )
            for i in range(38, 44):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+37}"]
                )

            self.now_btn[44].configure(
                text=self.data[self.current_lang]["l82"])
            self.now_btn[45].configure(
                text=self.data[self.current_lang]["l83"])

            for i in range(46, 57):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+42}"]
                )

            self.now_btn[57].configure(
                text=self.data[self.current_lang]["l101"])

            for i in range(58, 65):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+75}"]
                )

            for i in range(65, 98):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+86}"]
                )

        elif text == "l313":
            self.now_btn[0].configure(text=self.data[self.current_lang]["l48"])
            self.now_btn[1].configure(text=self.data[self.current_lang]["l81"])
            self.now_btn[2].configure(text=self.data[self.current_lang]["l86"])
            self.now_btn[3].configure(text=self.data[self.current_lang]["l87"])
            self.now_btn[4].configure(
                text=self.data[self.current_lang]["l131"])
            self.now_btn[5].configure(
                text=self.data[self.current_lang]["l132"])
            self.now_btn[6].configure(
                text=self.data[self.current_lang]["l144"])
            self.now_btn[7].configure(
                text=self.data[self.current_lang]["l297"])
            self.now_btn[8].configure(
                text=self.data[self.current_lang]["l298"])
            self.now_btn[9].configure(
                text=self.data[self.current_lang]["l299"])

        elif text == "l314":
            self.now_btn[0].configure(text=self.data[self.current_lang]["l46"])
            self.now_btn[1].configure(
                text=self.data[self.current_lang]["l102"])
            self.now_btn[2].configure(
                text=self.data[self.current_lang]["l140"])
            self.now_btn[3].configure(
                text=self.data[self.current_lang]["l141"])
            self.now_btn[4].configure(
                text=self.data[self.current_lang]["l207"])
            self.now_btn[5].configure(
                text=self.data[self.current_lang]["l224"])
            self.now_btn[6].configure(
                text=self.data[self.current_lang]["l243"])
            self.now_btn[7].configure(
                text=self.data[self.current_lang]["l244"])
            self.now_btn[8].configure(
                text=self.data[self.current_lang]["l245"])
            self.now_btn[9].configure(
                text=self.data[self.current_lang]["l296"])
            self.now_btn[10].configure(
                text=self.data[self.current_lang]["l304"])
            self.now_btn[11].configure(
                text=self.data[self.current_lang]["l305"])
            self.now_btn[12].configure(
                text=self.data[self.current_lang]["l308"])

        elif text == "l315":
            for i in range(0, 10):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+186}"]
                )

            self.now_btn[10].configure(
                text=self.data[self.current_lang]["l197"])
            for i in range(11, 20):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+187}"]
                )

            self.now_btn[20].configure(
                text=self.data[self.current_lang]["l247"])
            self.now_btn[21].configure(
                text=self.data[self.current_lang]["l248"])
            self.now_btn[22].configure(
                text=self.data[self.current_lang]["l249"])
            self.now_btn[23].configure(
                text=self.data[self.current_lang]["l250"])
            self.now_btn[24].configure(
                text=self.data[self.current_lang]["l252"])

            for i in range(25, 51):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+228}"]
                )

        elif text == "l316":
            self.now_btn[0].configure(text=self.data[self.current_lang]["l25"])
            self.now_btn[1].configure(text=self.data[self.current_lang]["l26"])
            self.now_btn[2].configure(text=self.data[self.current_lang]["l47"])
            self.now_btn[3].configure(text=self.data[self.current_lang]["l84"])
            self.now_btn[4].configure(text=self.data[self.current_lang]["l85"])
            self.now_btn[5].configure(
                text=self.data[self.current_lang]["l100"])
            self.now_btn[6].configure(
                text=self.data[self.current_lang]["l103"])
            self.now_btn[7].configure(
                text=self.data[self.current_lang]["l104"])
            self.now_btn[8].configure(
                text=self.data[self.current_lang]["l185"])
            self.now_btn[9].configure(
                text=self.data[self.current_lang]["l196"])
            self.now_btn[10].configure(
                text=self.data[self.current_lang]["l227"])
            self.now_btn[11].configure(
                text=self.data[self.current_lang]["l228"])
            self.now_btn[12].configure(
                text=self.data[self.current_lang]["l229"])
            self.now_btn[13].configure(
                text=self.data[self.current_lang]["l230"])
            self.now_btn[14].configure(
                text=self.data[self.current_lang]["l251"])

        elif text == "l317":

            self.now_btn[0].configure(text=self.data[self.current_lang]["l21"])
            self.now_btn[1].configure(text=self.data[self.current_lang]["l22"])
            self.now_btn[2].configure(text=self.data[self.current_lang]["l99"])
            self.now_btn[3].configure(
                text=self.data[self.current_lang]["l114"])
            self.now_btn[4].configure(
                text=self.data[self.current_lang]["l115"])

            for i in range(5, 20):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+111}"]
                )

            for i in range(20, 36):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+188}"]
                )

            self.now_btn[36].configure(
                text=self.data[self.current_lang]["l225"])
            self.now_btn[37].configure(
                text=self.data[self.current_lang]["l226"])

            for i in range(38, 46):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+193}"]
                )

            self.now_btn[46].configure(
                text=self.data[self.current_lang]["l279"])

            for i in range(47, 51):
                self.now_btn[i].configure(
                    text=self.data[self.current_lang][f"l{i+237}"]
                )

            self.now_btn[51].configure(
                text=self.data[self.current_lang]["l306"])
            self.now_btn[52].configure(
                text=self.data[self.current_lang]["l307"])

    def change_bg(self, event, color):
        event.widget.configure(background=color)

    def change_bg_leave(self, event, color):
        event.widget.configure(background=color)

    def load_first(self):
        self.tab2_seperate_scroll_BTN.columnconfigure(0, weight=1)
        for i in range(60):
            row_frame = Frame(self.tab2_seperate_scroll_BTN)
            row_frame.grid(sticky="ew")
            row_frame.columnconfigure(1, weight=1)
            test_label = Label(
                row_frame,
                text="> STATUS: ONLINE",
                fg="#aaaaaa", bg="#1a1a1a",
                justify="left", wraplength=350
            )

            """
            THIS FEATURE WAS PUTTING A 0.4% - 0.5% LOAD ON THE CPU, SO I DISABLED IT FOR THAT REASON
            test_label.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
            test_label.bind("<Leave>", lambda event: self.change_bg_leave(event, "#121212"))
            """
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
                cursor="hand2"
            )
            button.grid(row=0, column=0, sticky="w")
            button.bind("<Enter>", lambda event: self.change_bg(event, "gray"))
            button.bind(
                "<Leave>", lambda event: self.change_bg_leave(event, "#2d2d2d")
            )
            self.keyevents_buttons.append(button)
            self.keyevents_labels.append(test_label)

            key = f"l{i+21}"
            self.keyevents_labels[i].configure(
                text=self.data[self.current_lang][key])

    def restart_number(self):
        self.load_clicked = 0

    def called_test_function(self):
        self.load_clicked += 1
        logging.debug("[called_test_function]-clicked test: %s", self.load_clicked)
        if self.load_clicked == 1:
            self.load_all(60, 120)
        elif self.load_clicked == 2:
            self.load_all(120, 180)
        elif self.load_clicked == 3:
            self.load_all(180, 240)
        elif self.load_clicked == 4:
            self.load_all(240, 288)
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

    # SEPERATE
    def load_all(self, range_x, range_y):
        logging.debug("[load_all]-Clicked------------------------------------")
        self.root.update_idletasks()
        self.tab2_load_more_btn.pack_forget()
        self.tab2_seperate_scroll_LOAD.pack_forget()
        self.tab2_seperate_scroll_BTN.columnconfigure(0, weight=1)
        for i in range(range_x, range_y):
            row_frame = Frame(self.tab2_seperate_scroll_BTN)
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
                "<Leave>", lambda event: self.change_bg_leave(event, "#2d2d2d")
            )
            self.keyevents_buttons.append(button)
            self.keyevents_labels.append(test_label)
            key = f"l{i+21}"
            self.keyevents_labels[i].configure(
                text=self.data[self.current_lang][key])

        self.root.after(100, lambda: self.tab2_seperate_scroll_LOAD.pack())
        self.root.after(101, lambda: self.tab2_load_more_btn.pack())
