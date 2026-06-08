from tkinter import *
from tkinter import ttk
import random
import time

root = Tk()
root.title("Burada")
root.geometry("400x400")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

frm = ttk.Frame(root, padding=10)

frm.grid(row=0, column=0)

def clicked():
    print("Butona tıklandı")
    rndm_num = random.randint(1,100)
    print(rndm_num)
    say(rndm_num)
    return

def say(sayi):
    num = label["text"]
    num_state = int(num)

    if num_state == sayi:
        return
    
    final = num_state + 1
    label["text"] = final
    print("Değişti")

    kalan = sayi - final
    print("kalan= ", kalan)

    if kalan <= 0:
        print("Bitti")
        return 

    if 3 < kalan <= 7:
        root.after(50, lambda:say(sayi))
        return
    elif kalan <= 3:
        root.after(100, lambda:say(sayi))
        return
    else:
        root.after(2, lambda:say(sayi))

def restart():
    label["text"] = "0"

buton = ttk.Button(frm, text="Tıkla", command=clicked)
del_buton = ttk.Button(frm, text="Delete", command=restart)
label = ttk.Label(frm, text="0", font=("Verdana"))
buton.grid(sticky="nsew")
label.grid(sticky="nsew", padx=40, pady=10)
del_buton.grid(sticky="nsew", pady=50)
root.mainloop()