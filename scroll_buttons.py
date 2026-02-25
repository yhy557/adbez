from tkinter import *
import tkinter as tk


class buttons:
    def __init__(self, tab2_seperate_scroll_BTN, root, tab2_load_more_btn,
                 tab2_seperate_scroll_LOAD, keyevents_buttons,
                 keyevents_labels, data, current_lang, background_color):
        self.tab2_seperate_scroll_BTN = tab2_seperate_scroll_BTN
        self.root = root
        self.tab2_load_more_btn = tab2_load_more_btn
        self.tab2_seperate_scroll_LOAD = tab2_seperate_scroll_LOAD
        self.data = data
        self.current_lang = current_lang
        self.background_color = background_color 

        self.keyevents_buttons = []
        self.keyevents_labels = []
        self.keyevents_labels_2 = []
        self.keyevents_labels_3 = []
        self.keyevents_labels_4 = []

        self.load_clicked = 0
        self.load_first()

    def categorize(self):
        print("Clicked categorize")

    def change_bg(self,event, color):
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
            self.keyevents_labels[i].configure(text=self.data[self.current_lang][key])

    def restart_number(self):
        self.load_clicked = 0

    def called_test_function(self):
        self.load_clicked += 1
        print(f"clicked test: {self.load_clicked}")
        if self.load_clicked == 1:
            self.load_all(60, 120)
        elif self.load_clicked == 2:
            self.load_all(120, 180)
        elif self.load_clicked == 3:
            self.load_all(180, 240)
        elif self.load_clicked == 4:
            self.load_all(240, 288)
        else:
            print("All keyevents loaded")

    # IF LANGUAGES CHANGED, LOAD AGAIN
    def load_again(self):
        for widgets in self.tab2_seperate_scroll_BTN.winfo_children()[:60]:
            widgets.destroy()
            self.keyevents_labels.clear()
            print("Widgets deleting")
        self.keyevents_buttons.clear()
        self.keyevents_labels.clear()
        self.root.after(10, lambda: self.load_first())
     
    # SEPERATE
    def load_all(self, range_x, range_y):
        print("Tıklandı-----------------------------------------")
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
            self.keyevents_labels[i].configure(text=self.data[self.current_lang][key])

        self.root.after(100, lambda: self.tab2_seperate_scroll_LOAD.pack())
        self.root.after(101, lambda: self.tab2_load_more_btn.pack())

