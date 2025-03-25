import tkinter as tk
from tkinter import ttk
import contracts

root = tk.Tk()
root.title("شرکت مهندسین مشاور پایش هفت اقلیم")
root.attributes('-fullscreen', True)
root.configure(bg="#ADD8E6")

title_frame = tk.Frame(root, bg="#ADD8E6", bd=1, relief="solid")
title_frame.pack(fill="x", padx=10, pady=10)
title_label = tk.Label(title_frame, text="شرکت مهندسین مشاور پایش هفت اقلیم", font=("Arial", 28, "bold"), 
                       bg="#ADD8E6", fg="#000080", pady=15)
title_label.pack()

tab_frame = tk.Frame(root, bg="#ADD8E6", bd=1, relief="solid")
tab_frame.pack(fill="x", padx=10, pady=5)

content_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
content_frame.pack(expand=True, fill="both", padx=10, pady=10)

tab_functions = {
    "قرارداد": contracts.show_contracts,
    "پیش پرداخت": lambda frame: tk.Label(frame, text="بخش پیش پرداخت - در حال توسعه", font=("Arial", 20), bg="white").pack(expand=True),
    "ضمانت نامه": lambda frame: tk.Label(frame, text="بخش ضمانت‌نامه - در حال توسعه", font=("Arial", 20), bg="white").pack(expand=True),
    "پیمانکاران جزء": lambda frame: tk.Label(frame, text="بخش پیمانکاران جزء - در حال توسعه", font=("Arial", 20), bg="white").pack(expand=True),
    "کارکنان": lambda frame: tk.Label(frame, text="بخش کارکنان - در حال توسعه", font=("Arial", 20), bg="white").pack(expand=True)
}

tabs = ["قرارداد", "پیش پرداخت", "ضمانت نامه", "پیمانکاران جزء", "کارکنان"]

def show_tab(tab_name):
    for widget in content_frame.winfo_children():
        widget.destroy()
    tab_functions[tab_name](content_frame)

def show_welcome(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    welcome_label = tk.Label(frame, text="خوش آمدید به سیستم مدیریت پایش هفت اقلیم", 
                             font=("Arial", 20), bg="white", fg="#000080")
    welcome_label.pack(expand=True)

buttons = []
for tab in tabs:
    btn = tk.Button(tab_frame, text=tab, font=("Arial", 16), bg="#87CEEB", fg="#000080",
                    bd=0, relief="flat", padx=20, pady=10, highlightthickness=0,
                    command=lambda t=tab: show_tab(t))
    btn.pack(side="right", padx=2)
    buttons.append(btn)

exit_frame = tk.Frame(root, bg="#ADD8E6", bd=1, relief="solid")
exit_frame.pack(fill="x", padx=10, pady=10)
exit_button = tk.Button(exit_frame, text="خروج", command=root.quit, font=("Arial", 14), 
                        bg="#87CEEB", fg="#000080", padx=10, pady=5)
exit_button.pack(pady=5)

import database
database.init_database()

show_welcome(content_frame)

root.mainloop()