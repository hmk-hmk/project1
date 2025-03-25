import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from contracts import show_contracts, HoverButton
from employees import show_employees
from costs import show_costs
from config import COLORS, FONTS
import prepayments
import guarantees
import status
import salary
import events  # جایگزین transactions
import hashlib
import sqlite3

logging.basicConfig(
    filename="G:/tachra_project/back6/main_log.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def get_db_connection(db_path="auth.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )''')
        default_username = "admin"
        default_password = "password123"
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", 
                       (default_username, password_hash))
        conn.commit()
    logging.info("دیتابیس احراز هویت آماده شد")

def verify_password(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result["password_hash"] == password_hash:
            return True
    return False

def show_login_window(root, on_success):
    login_window = tk.Toplevel(root)
    login_window.title("ورود به برنامه")
    center_window(login_window, 400, 300)
    login_window.configure(bg="#F5F6F5")
    login_window.grab_set()

    header = tk.Frame(login_window, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="ورود به پایش هفت اقلیم", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    form_frame = tk.Frame(login_window, bg="#F5F6F5")
    form_frame.pack(pady=20)

    tk.Label(form_frame, text="نام کاربری:", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=1, pady=10, padx=5, sticky="e")
    username_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=20, justify="right")
    username_entry.grid(row=0, column=0, pady=10, padx=5)
    username_entry.insert(0, "admin")

    tk.Label(form_frame, text="رمز عبور:", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=1, column=1, pady=10, padx=5, sticky="e")
    password_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=20, show="*", justify="right")
    password_entry.grid(row=1, column=0, pady=10, padx=5)

    entries = [username_entry, password_entry]
    for i, entry in enumerate(entries):
        entry.bind("<Down>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())
        entry.bind("<Up>", lambda e, idx=i: entries[(idx - 1) % len(entries)].focus_set())
        entry.bind("<Return>", lambda e: try_login())

    def try_login():
        username = username_entry.get()
        password = password_entry.get()
        if not password:  # پسورد خالی برای ورود موقت
            logging.info(f"ورود بدون رمز برای کاربر: {username}")
            login_window.destroy()
            on_success()
        elif verify_password(username, password):
            logging.info(f"ورود موفق برای کاربر: {username}")
            login_window.destroy()
            on_success()
        else:
            messagebox.showerror("خطا", "نام کاربری یا رمز عبور اشتباه است!")
            password_entry.delete(0, tk.END)

    btn_frame = tk.Frame(login_window, bg="#F5F6F5")
    btn_frame.pack(pady=20)
    login_btn = HoverButton(btn_frame, text="ورود", font=("IRANSans", 12), bg="#00A86B", hover_bg="#008F5A", fg="white", command=try_login)
    login_btn.pack(side="right", padx=5)
    exit_btn = HoverButton(btn_frame, text="خروج", font=("IRANSans", 12), bg="#FF4500", hover_bg="#D63A00", fg="white", command=root.quit)
    exit_btn.pack(side="right", padx=5)

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("پایش هفت اقلیم | نسخه حرفه‌ای")
        self.geometry("1440x900")
        self.configure(bg=COLORS["background"])
        self.withdraw()  # مخفی کردن پنجره اصلی تا لاگین
        init_auth_db()
        show_login_window(self, self.start_app)

    def start_app(self):
        self.deiconify()  # نمایش پنجره اصلی بعد از لاگین
        self.header_frame = tk.Frame(self, bg=COLORS["primary"], height=100)
        self.header_frame.pack(fill="x", side="top")
        
        self.header_label = tk.Label(
            self.header_frame,
            text="پایش هفت اقلیم",
            font=FONTS["title"],
            fg="white",
            bg=COLORS["primary"],
            anchor="e"
        )
        self.header_label.pack(side="right", padx=30)
        
        self.sidebar = tk.Canvas(self, bg=COLORS["primary"], width=200, height=800, highlightthickness=0)
        self.sidebar.pack(side="right", fill="y")
        
        self.main_content = tk.Frame(self, bg=COLORS["background"])
        self.main_content.pack(side="left", fill="both", expand=True)
        
        self.create_content()
        self.create_sidebar()
        self.sidebar_buttons = []

    def create_content(self):
        self.cards_frame = tk.Frame(self.main_content, bg=COLORS["background"])
        self.cards_frame.pack(pady=(20, 40), padx=30, fill="both", expand=True)
        self.create_dashboard_cards()

    def create_dashboard_cards(self):
        cards_data = [
            ("📄", "قراردادها", COLORS["success"], lambda: self.show_section("contracts")),
            ("💰", "پیش‌پرداخت‌ها", COLORS["warning"], lambda: self.show_section("prepayments")),
            ("📜", "ضمانت‌نامه‌ها", COLORS["accent"], lambda: self.show_section("guarantees")),
            ("💸", "هزینه‌ها", COLORS["secondary"], lambda: self.show_section("costs")),
            ("👥", "کارکنان", COLORS["success"], lambda: self.show_section("employees")),
            ("👷", "پیمانکاران", COLORS["warning"], lambda: self.show_section("subcontractors")),
            ("💵", "حقوق", COLORS["accent"], lambda: self.show_section("salary")),
            ("📊", "گزارشات", COLORS["secondary"], lambda: self.show_section("reports")),
            ("📋", "صورت‌وضعیت‌ها", COLORS["success"], lambda: self.show_section("status")),
            ("💳", "دریافت‌ها و پرداخت‌ها", COLORS["warning"], lambda: self.show_section("events"))
        ]
        
        for idx, (icon, title, color, cmd) in enumerate(cards_data):
            card = HoverButton(
                self.cards_frame,
                text=f"{icon}\n{title}",
                font=FONTS["header"],
                bg="white",
                hover_bg=color,
                fg=COLORS["text"],
                hover_fg="white",
                width=15,
                height=7,
                command=cmd
            )
            card.grid(row=idx // 3, column=idx % 3, padx=20, pady=20, sticky="nsew")
        
        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.cards_frame.grid_rowconfigure(i, weight=1)

    def create_sidebar(self):
        menu_items = [
            ("🏠", "صفحه اصلی", lambda: self.show_section("home")),
            ("📊", "داشبورد", lambda: self.show_section("dashboard")),
            ("👥", "کاربران", lambda: self.show_section("users")),
            ("⚙️", "تنظیمات", lambda: self.show_section("settings")),
            ("🎨", "تم", lambda: self.show_section("theme")),
            ("🚪", "خروج", self.quit)
        ]
        
        y_position = 20
        self.sidebar_buttons = []
        for icon, text, cmd in menu_items:
            btn_frame = tk.Frame(self.sidebar, bg=COLORS["primary"])
            btn_frame.place(x=0, y=y_position, width=200, height=60)
            
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 20), bg=COLORS["primary"], fg="white").pack(side="right", padx=15)
            btn = HoverButton(btn_frame, text=text, font=FONTS["button"], bg=COLORS["primary"], hover_bg=COLORS["accent"], fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            self.sidebar_buttons.append(btn)
            y_position += 70

    def disable_main(self):
        logging.info("غیرفعال کردن سایدبار اصلی")
        for btn in self.sidebar_buttons:
            btn.config(state="disabled", bg="#5A6A80", fg="gray", relief="flat")
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
            btn.unbind("<Button-1>")
            btn.unbind("<ButtonRelease-1>")
            btn["command"] = None

    def enable_main(self):
        logging.info("فعال کردن سایدبار اصلی")
        for btn, cmd in zip(self.sidebar_buttons, [
            lambda: self.show_section("home"), 
            lambda: self.show_section("dashboard"), 
            lambda: self.show_section("users"), 
            lambda: self.show_section("settings"), 
            lambda: self.show_section("theme"), 
            self.quit
        ]):
            btn.config(state="normal", bg=COLORS["primary"], fg="white", relief="flat")
            btn.bind("<Enter>", btn.on_enter)
            btn.bind("<Leave>", btn.on_leave)
            btn.bind("<Button-1>", lambda e, b=btn: b.invoke())
            btn["command"] = cmd

    def show_section(self, section_name):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        if section_name == "home" or section_name == "dashboard":
            self.enable_main()
            self.cards_frame = tk.Frame(self.main_content, bg=COLORS["background"])
            self.cards_frame.pack(pady=(20, 40), padx=30, fill="both", expand=True)
            self.create_dashboard_cards()
        elif section_name == "contracts":
            self.disable_main()
            show_contracts(self.main_content, self.enable_main)
        elif section_name == "employees":
            self.disable_main()
            show_employees(self.main_content, self.enable_main)
        elif section_name == "costs":
            self.disable_main()
            show_costs(self.main_content, self.enable_main)
        elif section_name == "prepayments":
            self.disable_main()
            prepayments.show_prepayments(self.main_content, self.enable_main)
        elif section_name == "guarantees":
            self.disable_main()
            guarantees.show_guarantees(self.main_content, self.enable_main)
        elif section_name == "status":
            self.disable_main()
            status.show_status(self.main_content, self.enable_main)
        elif section_name == "salary":
            self.disable_main()
            salary.show_salary(self.main_content, self.enable_main)
        elif section_name == "events":
            self.disable_main()
            events.show_events(self.main_content, self.enable_main)
        else:
            self.enable_main()
            content_frame = tk.Frame(self.main_content, bg=COLORS["background"])
            content_frame.pack(pady=(20, 0), fill="both", expand=True)
            tk.Label(content_frame, text=f"{section_name.capitalize()} - در حال توسعه", font=FONTS["header"], bg=COLORS["background"]).pack(expand=True)

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()