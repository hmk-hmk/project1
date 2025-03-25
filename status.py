import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sqlite3
import jdatetime
from datetime import datetime

logging.basicConfig(filename="status_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")
logging.getLogger().addHandler(logging.StreamHandler())

def format_amount(amount):
    try:
        return "{:,}".format(int(str(amount).replace(",", "")))
    except (ValueError, TypeError):
        return amount if amount else "0"

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def get_db_connection(db_path="contracts_new.db"):
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"خطا در اتصال به دیتابیس: {e}")
        return None

def migrate_db(db_path="contracts_new.db"):
    with get_db_connection(db_path) as conn:
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_number TEXT NOT NULL,
            contract_date TEXT NOT NULL,
            contract_subject TEXT NOT NULL,
            contract_party TEXT NOT NULL,
            total_amount TEXT NOT NULL,
            prepayment_percent TEXT NOT NULL,
            prepayment_amount TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS contract_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            description TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            number INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
        )''')
        cursor.execute("DROP TABLE IF EXISTS status_details")
        cursor.execute('''CREATE TABLE status_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_id INTEGER,
            detail_id INTEGER,
            performance REAL NOT NULL,
            new_amount REAL NOT NULL,
            FOREIGN KEY (status_id) REFERENCES statuses(id),
            FOREIGN KEY (detail_id) REFERENCES contract_details(id)
        )''')
        cursor.execute("INSERT OR IGNORE INTO contracts (id, contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       (1, "C001", "1403/01/01", "پروژه تست", "شرکت الف", "1500000000", "20", "300000000"))
        cursor.execute("INSERT OR IGNORE INTO contract_details (id, contract_id, description, quantity, unit, amount) VALUES (?, ?, ?, ?, ?, ?)", 
                       (1, 1, "نقشه‌برداری", 10, "هکتار", 1000000000))
        cursor.execute("INSERT OR IGNORE INTO contract_details (id, contract_id, description, quantity, unit, amount) VALUES (?, ?, ?, ?, ?, ?)", 
                       (2, 1, "طراحی پل", 5, "عدد", 500000000))
        conn.commit()
    logging.info("دیتابیس مهاجرت و به‌روزرسانی شد")

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        self.default_bg = kw.pop('bg', '#172A3A')
        self.hover_bg = kw.pop('hover_bg', '#0F1F2A')
        self.default_fg = kw.pop('fg', 'white')
        self.hover_fg = kw.pop('hover_fg', 'white')
        super().__init__(master, **kw)
        self.configure(bg=self.default_bg, fg=self.default_fg, relief='flat', borderwidth=0, 
                       activebackground=self.hover_bg, activeforeground=self.hover_fg)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, e):
        if self["state"] != "disabled":
            self.configure(bg=self.hover_bg, fg=self.hover_fg)
        
    def on_leave(self, e):
        if self["state"] != "disabled":
            self.configure(bg=self.default_bg, fg=self.default_fg)

def show_status(master, enable_main_callback):
    logging.info("ورود به show_status")
    migrate_db()

    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    # هدر
    header = tk.Frame(main_frame, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="مدیریت صورت‌وضعیت‌ها", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(main_frame, bg="#172A3A", width=113)
    sidebar.pack(side="right", fill="y")

    # محتوا
    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    contract_frame = ttk.LabelFrame(content, text="لیست قراردادها", padding=10)
    contract_frame.pack(fill="both", expand=True, padx=5, pady=5)

    columns = ("number", "date", "subject", "party", "total_amount")
    contract_tree = ttk.Treeview(contract_frame, columns=columns, show="headings", height=10)
    contract_tree.heading("number", text="شماره قرارداد", anchor="e")
    contract_tree.heading("date", text="تاریخ", anchor="e")
    contract_tree.heading("subject", text="موضوع", anchor="e")
    contract_tree.heading("party", text="طرف قرارداد", anchor="e")
    contract_tree.heading("total_amount", text="مبلغ کل (ریال)", anchor="e")
    contract_tree.column("number", width=100, anchor="e")
    contract_tree.column("date", width=100, anchor="e")
    contract_tree.column("subject", width=150, anchor="e")
    contract_tree.column("party", width=150, anchor="e")
    contract_tree.column("total_amount", width=120, anchor="e")
    contract_tree.pack(fill="both", expand=True)

    style = ttk.Style()
    style.configure("Treeview", rowheight=25, font=("IRANSans", 11))
    style.configure("Treeview.Heading", font=("IRANSans", 12, "bold"))

    def update_contracts():
        with get_db_connection() as conn:
            if not conn:
                messagebox.showerror("خطا", "نمی‌توان به دیتابیس متصل شد!")
                return
            cursor = conn.cursor()
            cursor.execute("SELECT contract_number, contract_date, contract_subject, contract_party, total_amount FROM contracts")
            contracts = cursor.fetchall()
            for item in contract_tree.get_children():
                contract_tree.delete(item)
            for contract in contracts:
                contract_tree.insert("", "end", values=(contract["contract_number"], contract["contract_date"], 
                                                        contract["contract_subject"], contract["contract_party"], 
                                                        format_amount(contract["total_amount"])))

    def get_next_status_number(contract_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(number) FROM statuses WHERE contract_id = ?", (contract_id,))
            max_number = cursor.fetchone()[0]
            return (max_number or 0) + 1

    def show_status_details(status_id):
        logging.info(f"نمایش جزئیات صورت‌وضعیت با ID: {status_id}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date, total_amount FROM statuses WHERE id = ?", (status_id,))
            status = cursor.fetchone()
            if not status:
                logging.error(f"صورت‌وضعیت با ID {status_id} پیدا نشد!")
                messagebox.showerror("خطا", f"صورت‌وضعیت با شماره {status_id} پیدا نشد!")
                return
            popup = tk.Toplevel()
            popup.title(f"جزئیات صورت‌وضعیت شماره {status_id}")
            center_window(popup, 600, 400)
            popup.configure(bg="#F5F6F5")
            tk.Label(popup, text=f"تاریخ: {status['date']} | مبلغ کل: {format_amount(status['total_amount'])} ریال", 
                     font=("IRANSans", 14), bg="#F5F6F5", fg="#333333").pack(pady=10)
            tree = ttk.Treeview(popup, columns=("desc", "perf", "amount"), show="headings")
            tree.heading("desc", text="شرح خدمات", anchor="e")
            tree.heading("perf", text="مقدار اضافه‌شده", anchor="e")
            tree.heading("amount", text="مبلغ (ریال)", anchor="e")
            tree.column("desc", width=200, anchor="e")
            tree.column("perf", width=100, anchor="e")
            tree.column("amount", width=150, anchor="e")
            tree.pack(fill="both", expand=True, padx=10, pady=10)
            cursor.execute("SELECT cd.description, sd.performance, sd.new_amount FROM status_details sd JOIN contract_details cd ON sd.detail_id = cd.id WHERE sd.status_id = ?", (status_id,))
            details = cursor.fetchall()
            for detail in details:
                tree.insert("", "end", values=(detail["description"], detail["performance"], format_amount(detail["new_amount"])))

    def delete_all_statuses(contract_id, update_func, status_data, prev_labels, details):
        if messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید همه صورت‌وضعیت‌ها را حذف کنید؟"):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM status_details WHERE status_id IN (SELECT id FROM statuses WHERE contract_id = ?)", (contract_id,))
                cursor.execute("DELETE FROM statuses WHERE contract_id = ?", (contract_id,))
                conn.commit()
                logging.info(f"همه صورت‌وضعیت‌ها برای قرارداد {contract_id} حذف شدند")
                for detail in details:
                    detail_id = detail["id"]
                    status_data[detail_id]["prev"] = 0
                    prev_labels[detail_id].config(text="0")
                update_func()
                messagebox.showinfo("موفقیت", "همه صورت‌وضعیت‌ها حذف شدند!")

    def open_status_window(event=None):
        selected = contract_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک قرارداد انتخاب کنید!")
            return
        contract_number = contract_tree.item(selected[0])["values"][0]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, contract_number, contract_date, contract_party, total_amount FROM contracts WHERE contract_number = ?", (contract_number,))
            contract = cursor.fetchone()
            if not contract:
                messagebox.showerror("خطا", "قرارداد پیدا نشد!")
                return
            contract_id = contract["id"]

        status_window = tk.Toplevel(master)
        status_window.title(f"صورت‌وضعیت قرارداد {contract_number}")
        center_window(status_window, 1000, 700)
        status_window.configure(bg="#F5F6F5")

        # هدر
        header = tk.Frame(status_window, bg="#00A86B", height=40)
        header.pack(fill="x")
        tk.Label(header, text=f"ثبت صورت‌وضعیت قرارداد {contract_number}", font=("IranNastaliq", 20), fg="white", bg="#00A86B").pack(side="right", padx=10)

        # سایدبار
        btn_sidebar = tk.Frame(status_window, bg="#00A86B", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # محتوا
        content = tk.Frame(status_window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        info_frame = ttk.LabelFrame(content, text="اطلاعات قرارداد", padding=10)
        info_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(info_frame, text=f"شماره: {contract['contract_number']} | تاریخ: {contract['contract_date']} | طرف قرارداد: {contract['contract_party']} | مبلغ کل: {format_amount(contract['total_amount'])} ریال", 
                 font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").pack(anchor="e")

        status_list_frame = ttk.LabelFrame(content, text="صورت‌وضعیت‌های موجود", padding=10)
        status_list_frame.pack(fill="x", padx=5, pady=5)
        status_list = ttk.Treeview(status_list_frame, columns=("id", "number", "date", "total"), show="headings", height=5)
        status_list.heading("id", text="شناسه", anchor="e")
        status_list.heading("number", text="شماره", anchor="e")
        status_list.heading("date", text="تاریخ", anchor="e")
        status_list.heading("total", text="مبلغ کل (ریال)", anchor="e")
        status_list.column("id", width=50, anchor="e")
        status_list.column("number", width=50, anchor="e")
        status_list.column("date", width=100, anchor="e")
        status_list.column("total", width=150, anchor="e")
        status_list.pack(fill="x", expand=True)

        details_frame = ttk.LabelFrame(content, text="جزئیات و ثبت جدید", padding=10)
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)

        header_frame = tk.Frame(details_frame, bg="#F5F6F5")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="شرح خدمات", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", width=20).grid(row=0, column=0, padx=5)
        tk.Label(header_frame, text="مقدار کل", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", width=10).grid(row=0, column=1, padx=5)
        tk.Label(header_frame, text="واحد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", width=10).grid(row=0, column=2, padx=5)
        tk.Label(header_frame, text="جمع قبلی", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", width=10).grid(row=0, column=3, padx=5)
        tk.Label(header_frame, text="مقدار جدید", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", width=10).grid(row=0, column=4, padx=5)
        tk.Label(header_frame, text="مبلغ جدید", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", width=15).grid(row=0, column=5, padx=5)

        details_container = tk.Frame(details_frame, bg="#F5F6F5")
        details_container.pack(fill="both", expand=True)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, quantity, unit, amount FROM contract_details WHERE contract_id = ?", (contract_id,))
            details = cursor.fetchall()
            if not details:
                messagebox.showwarning("هشدار", "جزئیات قرارداد پیدا نشد!")
                status_window.destroy()
                return
            status_data = {}
            entries = {}
            amount_labels = {}
            prev_labels = {}
            for i, detail in enumerate(details):
                quantity = float(detail["quantity"])
                amount = float(detail["amount"])
                unit_price = amount / quantity
                cursor.execute("SELECT SUM(performance) FROM status_details WHERE detail_id = ?", (detail["id"],))
                total_prev = cursor.fetchone()[0] or 0
                status_data[detail["id"]] = {"prev": total_prev, "new": tk.StringVar(value="0"), "unit_price": unit_price}

                row_frame = tk.Frame(details_container, bg="#F5F6F5")
                row_frame.pack(fill="x", pady=2)
                tk.Label(row_frame, text=detail["description"], font=("IRANSans", 11), bg="#F5F6F5", fg="#333333", width=20, anchor="e").grid(row=0, column=0, padx=5)
                tk.Label(row_frame, text=str(detail["quantity"]), font=("IRANSans", 11), bg="#F5F6F5", fg="#333333", width=10, anchor="e").grid(row=0, column=1, padx=5)
                tk.Label(row_frame, text=detail["unit"], font=("IRANSans", 11), bg="#F5F6F5", fg="#333333", width=10, anchor="e").grid(row=0, column=2, padx=5)
                prev_label = tk.Label(row_frame, text=str(total_prev), font=("IRANSans", 11), bg="#F5F6F5", fg="#333333", width=10, anchor="e")
                prev_label.grid(row=0, column=3, padx=5)
                prev_labels[detail["id"]] = prev_label
                entry = ttk.Entry(row_frame, textvariable=status_data[detail["id"]]["new"], width=10, justify="right")
                entry.grid(row=0, column=4, padx=5)
                entries[detail["id"]] = entry
                amount_label = tk.Label(row_frame, text="0", font=("IRANSans", 11), bg="#F5F6F5", fg="#333333", width=15, anchor="e")
                amount_label.grid(row=0, column=5, padx=5)
                amount_labels[detail["id"]] = amount_label

        def update_status_list():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, number, date, total_amount FROM statuses WHERE contract_id = ?", (contract_id,))
                statuses = cursor.fetchall()
                for item in status_list.get_children():
                    status_list.delete(item)
                for status in statuses:
                    status_list.insert("", "end", values=(status["id"], status["number"], status["date"], format_amount(status["total_amount"])))

        def update_amounts():
            total_new = 0
            for detail in details:
                detail_id = detail["id"]
                entry_value = entries[detail_id].get().strip() or "0"
                try:
                    new_value = float(entry_value)
                except ValueError:
                    new_value = 0
                new_amount = new_value * status_data[detail_id]["unit_price"]
                total_new += new_amount
                amount_labels[detail_id].config(text=format_amount(new_amount))
            total_label.config(text=f"مبلغ جدید: {format_amount(total_new)} ریال")

        def save_status():
            date = jdatetime.date.fromgregorian(date=datetime.now()).strftime("%Y/%m/%d")
            total_new = 0
            values = {}
            for detail in details:
                detail_id = detail["id"]
                entry_value = entries[detail_id].get().strip() or "0"
                try:
                    new_value = float(entry_value)
                except ValueError:
                    messagebox.showwarning("خطا", f"مقدار واردشده برای {detail['description']} معتبر نیست!")
                    return
                if new_value < 0:
                    messagebox.showwarning("خطا", f"مقدار جدید برای {detail['description']} نمی‌تواند منفی باشد!")
                    return
                if new_value + status_data[detail_id]["prev"] > float(detail["quantity"]):
                    messagebox.showwarning("خطا", f"مقدار جدید برای {detail['description']} از سقف بیشتر است!")
                    return
                new_amount = new_value * status_data[detail_id]["unit_price"]
                total_new += new_amount
                values[detail_id] = (new_value, new_amount)
            if total_new == 0:
                messagebox.showwarning("خطا", "هیچ مقدار جدیدی وارد نشده!")
                return
            if messagebox.askyesno("تأیید", "مطمئن هستید که می‌خواهید ثبت کنید؟"):
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    status_number = get_next_status_number(contract_id)
                    cursor.execute("INSERT INTO statuses (contract_id, number, date, status, total_amount) VALUES (?, ?, ?, ?, ?)", 
                                  (contract_id, status_number, date, "موقت", total_new))
                    status_id = cursor.lastrowid
                    for detail in details:
                        detail_id = detail["id"]
                        if values[detail_id][0] > 0:
                            cursor.execute("INSERT INTO status_details (status_id, detail_id, performance, new_amount) VALUES (?, ?, ?, ?)", 
                                          (status_id, detail_id, values[detail_id][0], values[detail_id][1]))
                    conn.commit()
                    logging.info(f"صورت‌وضعیت شماره {status_number} در دیتابیس ثبت شد")
                    update_status_list()
                    for detail in details:
                        detail_id = detail["id"]
                        status_data[detail_id]["prev"] += values[detail_id][0]
                        status_data[detail_id]["new"].set("0")
                        entries[detail_id].delete(0, tk.END)
                        entries[detail_id].insert(0, "0")
                        prev_labels[detail_id].config(text=str(status_data[detail_id]["prev"]))
                    update_amounts()
                    messagebox.showinfo("موفقیت", f"صورت‌وضعیت شماره {status_number} ثبت شد!")
                    status_window.destroy()

        def cancel():
            status_window.destroy()

        # کلیدهای Enter و Arrow برای Entry‌ها
        entry_list = list(entries.values())
        for i, entry in enumerate(entry_list):
            entry.bind("<Down>", lambda e, idx=i: entry_list[(idx + 1) % len(entry_list)].focus_set())
            entry.bind("<Up>", lambda e, idx=i: entry_list[(idx - 1) % len(entry_list)].focus_set())
            entry.bind("<Return>", lambda e, idx=i: entry_list[(idx + 1) % len(entry_list)].focus_set())

        # دکمه‌ها پایین سایدبار
        y_pos = 600  # پایین پنجره (700 - 100 برای دو دکمه)
        for icon, text, cmd in [("✔️", "تأیید", save_status), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg="#00A86B")
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#00A86B", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#00A86B", hover_bg="#008F5A", fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

        total_label = tk.Label(content, text="مبلغ جدید: 0 ریال", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333")
        total_label.pack(side="bottom", pady=10)

        status_list.bind("<Double-1>", lambda e: show_status_details(int(status_list.item(status_list.selection()[0])["values"][0])) if status_list.selection() else None)
        update_status_list()
        update_amounts()

    def open_status_window_wrapper():
        open_status_window()

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    # دکمه‌های سایدبار اصلی
    buttons = [
        ("📝", "ثبت صورت‌وضعیت", open_status_window_wrapper),
        ("🚪", "خروج", exit_section)
    ]
    y_position = 20
    for icon, text, cmd in buttons:
        btn_frame = tk.Frame(sidebar, bg="#172A3A")
        btn_frame.place(x=0, y=y_position, width=113, height=50)
        tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#172A3A", fg="white").pack(side="right", padx=5)
        btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#172A3A", hover_bg="#0F1F2A", fg="white", hover_fg="white", anchor="e", command=cmd)
        btn.pack(side="right", fill="x", expand=True)
        y_position += 60

    update_contracts()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدیریت صورت‌وضعیت‌ها")
    center_window(root, 1000, 700)
    show_status(root, lambda: None)
    root.mainloop()