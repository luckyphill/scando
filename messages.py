import Tkinter as tk
import ttk

from global_vars import *

def popupmsg(code, msg):
    popup = tk.Tk()
    popup.wm_title("Scando: " + code + " activity")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Cheers bro", command = popup.destroy)
    B1.pack()
    popup.mainloop()