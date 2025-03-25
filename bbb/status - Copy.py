import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sqlite3
import jdatetime
from datetime import datetime
import re

# لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")
logging.getLogger().addHandler(logging.StreamHandler())

def format_amount(amount):
    try:
        return "{:,}".format(int(str(amount).replace(",", "")))
    except (ValueError, TypeError):
        return amount

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

def show_status(frame):
    logging.info("ورود به show_status")
    migrate_db()

    main_frame = tk.Frame(frame, bg="#F0F4F8")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(main_frame, text="صورت‌وضعیت‌ها", font=("Arial", 18, "bold"), bg="#F0F4F8", fg="#2C3E50").pack(pady=10)

    contract_frame = ttk.LabelFrame(main_frame, text="لیست قراردادها", padding=10)
    contract_frame.pack(fill="both", expand=True, padx=5, pady=5)

    columns = ("number", "date", "subject", "party", "total_amount")
    contract_tree = ttk.Treeview(contract_frame, columns=columns, show="headings", height=10)
    contract_tree.heading("number", text="شماره قرارداد")
    contract_tree.heading("date", text="تاریخ")
    contract_tree.heading("subject", text="موضوع")
    contract_tree.heading("party", text="طرف قرارداد")
    contract_tree.heading("total_amount", text="مبلغ کل (ریال)")
    contract_tree.column("number", width=100, anchor="e")
    contract_tree.column("date", width=100, anchor="e")
    contract_tree.column("subject", width=150, anchor="e")
    contract_tree.column("party", width=150, anchor="e")
    contract_tree.column("total_amount", width=120, anchor="e")
    contract_tree.pack(fill="both", expand=True)

    style = ttk.Style()
    style.configure("Treeview", rowheight=25, font=("Arial", 11))
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

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

    def create_status_window(contract_id, contract, status_window, details_frame, details_tree, status_data, update_total, save_status, status_id=None):
        is_edit = status_id is not None
        popup = tk.Toplevel(status_window)
        popup.title("ویرایش صورت‌وضعیت" if is_edit else "ایجاد صورت‌وضعیت جدید")
        center_window(popup, 800, 600)
        popup.configure(bg="#DDE4E6")
        popup.grab_set()

        # کانواس با اسکرول
        canvas = tk.Canvas(popup, bg="#DDE4E6")
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#DDE4E6")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(scrollable_frame, text=popup.title(), font=("Arial", 18, "bold"), bg="#DDE4E6", fg="#2C3E50").pack(pady=20)

        date_frame = tk.Frame(scrollable_frame, bg="#DDE4E6")
        date_frame.pack(pady=10)
        tk.Label(date_frame, text="تاریخ صورت‌وضعیت (مثال: 1404/01/03):", font=("Arial", 14), bg="#DDE4E6", fg="#34495E").pack(side="right", padx=10)
        date_var = tk.StringVar(value=jdatetime.date.fromgregorian(date=datetime.now()).strftime("%Y/%m/%d") if not is_edit else "")
        if is_edit:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT date FROM statuses WHERE id = ?", (status_id,))
                date_var.set(cursor.fetchone()["date"])
        ttk.Entry(date_frame, textvariable=date_var, font=("Arial", 14), justify="right", width=15).pack(side="right")

        details_frame_popup = ttk.LabelFrame(scrollable_frame, text="عملکرد", padding=15)
        details_frame_popup.pack(fill="both", expand=True, padx=20, pady=10)
        perf_entries = {}
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, quantity, unit, amount FROM contract_details WHERE contract_id = ?", (contract_id,))
            details = cursor.fetchall()
            logging.info(f"داده‌های contract_details برای contract_id={contract_id}: {[dict(d) for d in details]}")
            if not details:
                messagebox.showwarning("هشدار", "جزئیات قرارداد پیدا نشد! لطفاً ابتدا جزئیات را اضافه کنید.")
                popup.destroy()
                return
            cursor.execute("PRAGMA table_info(status_details)")
            logging.info(f"ستون‌های جدول status_details: {[col['name'] for col in cursor.fetchall()]}")
            for i, detail in enumerate(details):
                detail_id = detail["id"]
                cursor.execute("SELECT SUM(performance) FROM status_details WHERE detail_id = ?", (detail_id,))
                total_perf = cursor.fetchone()[0] or 0
                current_perf = total_perf
                if is_edit:
                    cursor.execute("SELECT performance FROM status_details WHERE status_id = ? AND detail_id = ?", (status_id, detail_id))
                    result = cursor.fetchone()
                    current_perf = result["performance"] if result else total_perf
                row_frame = tk.Frame(details_frame_popup, bg="#DDE4E6")
                row_frame.grid(row=i, column=0, columnspan=2, pady=10, sticky="ew")
                tk.Label(row_frame, text=f"{detail['description']} (تا حالا: {total_perf} {detail['unit']} از {detail['quantity']}):", 
                         font=("Arial", 14), bg="#DDE4E6", fg="#34495E").grid(row=0, column=1, padx=10, sticky="e")
                entry = ttk.Entry(row_frame, font=("Arial", 14), width=10, justify="right")
                entry.insert(0, str(current_perf))
                entry.grid(row=0, column=0, padx=10)
                perf_entries[detail_id] = (entry, float(detail["quantity"]), total_perf)

        def confirm_status():
            date = date_var.get()
            if not re.match(r"^\d{4}/\d{2}/\d{2}$", date) or not (1400 <= int(date[:4]) <= 1500 and 1 <= int(date[5:7]) <= 12 and 1 <= int(date[8:10]) <= 31):
                messagebox.showwarning("خطا", "تاریخ شمسی باید به فرمت 1404/01/03 و معتبر باشد!")
                return
            values = {}
            for detail_id, (entry, qty, total_perf) in perf_entries.items():
                perf = entry.get()
                try:
                    perf_float = float(perf)
                    if perf_float > qty:
                        messagebox.showwarning("خطا", f"عملکرد {detail_id} از سقف {qty} بیشتر است!")
                        return
                    if perf_float < total_perf and not is_edit:
                        messagebox.showwarning("خطا", f"عملکرد {detail_id} نمی‌تواند از مقدار قبلی ({total_perf}) کمتر باشد!")
                        return
                    values[detail_id] = perf_float
                except ValueError:
                    messagebox.showwarning("خطا", "مقادیر عملکرد باید عدد باشند!")
                    return
            if all(v == total_perf for (_, _, total_perf), v in zip(perf_entries.values(), values.values())) and not is_edit:
                messagebox.showwarning("خطا", "حداقل یک مقدار باید تغییر کند!")
                return
            if messagebox.askyesno("تأیید", "مطمئن هستید که مقادیر واردشده درست است؟"):
                for detail_id, value in values.items():
                    status_data[detail_id]["perf"].set(value)
                popup.destroy()
                details_frame.config(text=f"جزئیات صورت‌وضعیت - {date}")
                update_total()
                save_status("موقت", date, status_id)

        # دکمه‌ها همیشه پایین پنجره
        button_frame = tk.Frame(popup, bg="#DDE4E6")
        button_frame.pack(side="bottom", fill="x", pady=10)
        tk.Button(button_frame, text="تأیید", font=("Arial", 14, "bold"), bg="#2ECC71", fg="white", command=confirm_status, width=10).pack(side="right", padx=10)
        tk.Button(button_frame, text="انصراف", font=("Arial", 14, "bold"), bg="#E74C3C", fg="white", command=popup.destroy, width=10).pack(side="right")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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

        status_window = tk.Toplevel(frame)
        status_window.title(f"صورت‌وضعیت قرارداد {contract_number}")
        center_window(status_window, 1200, 800)
        status_window.configure(bg="#ECF0F1")
        status_window.grab_set()

        main_frame = tk.Frame(status_window, bg="#ECF0F1")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        info_frame = ttk.LabelFrame(main_frame, text="اطلاعات قرارداد", padding=10)
        info_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(info_frame, text=f"شماره: {contract['contract_number']} | تاریخ: {contract['contract_date']} | طرف قرارداد: {contract['contract_party']} | مبلغ کل: {format_amount(contract['total_amount'])} ریال", 
                 font=("Arial", 12), bg="#ECF0F1", fg="#2C3E50").pack(anchor="e")

        status_list_frame = ttk.LabelFrame(main_frame, text="صورت‌وضعیت‌های موجود", padding=10)
        status_list_frame.pack(fill="x", padx=5, pady=5)
        status_list = ttk.Treeview(status_list_frame, columns=("number", "date", "status", "total"), show="headings", height=5)
        status_list.heading("number", text="شماره")
        status_list.heading("date", text="تاریخ")
        status_list.heading("status", text="وضعیت")
        status_list.heading("total", text="مبلغ (ریال)")
        status_list.column("number", width=50, anchor="e")
        status_list.column("date", width=100, anchor="e")
        status_list.column("status", width=100, anchor="e")
        status_list.column("total", width=120, anchor="e")
        status_list.pack(fill="x", expand=True)

        details_frame = ttk.LabelFrame(main_frame, text="جزئیات صورت‌وضعیت جدید", padding=10)
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("desc", "qty", "unit", "amount", "prev", "perf", "new", "progress")
        details_tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=15)
        details_tree.heading("desc", text="شرح خدمات")
        details_tree.heading("qty", text="مقدار کل")
        details_tree.heading("unit", text="واحد")
        details_tree.heading("amount", text="مبلغ کل (ریال)")
        details_tree.heading("prev", text="عملکرد قبلی")
        details_tree.heading("perf", text="عملکرد جدید")
        details_tree.heading("new", text="مبلغ جدید (ریال)")
        details_tree.heading("progress", text="درصد پیشرفت")
        details_tree.column("desc", width=250, anchor="e")
        details_tree.column("qty", width=70, anchor="e")
        details_tree.column("unit", width=80, anchor="e")
        details_tree.column("amount", width=100, anchor="e")
        details_tree.column("prev", width=120, anchor="e")
        details_tree.column("perf", width=100, anchor="e")
        details_tree.column("new", width=120, anchor="e")
        details_tree.column("progress", width=100, anchor="e")
        details_tree.pack(fill="both", expand=True)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, quantity, unit, amount FROM contract_details WHERE contract_id = ?", (contract_id,))
            details = cursor.fetchall()
            logging.info(f"داده‌های contract_details برای contract_id={contract_id}: {[dict(d) for d in details]}")
            if not details:
                messagebox.showwarning("هشدار", "جزئیات قرارداد پیدا نشد! لطفاً ابتدا جزئیات را اضافه کنید.")
                status_window.destroy()
                return
            status_data = {}
            for detail in details:
                try:
                    quantity = float(detail["quantity"])
                    amount = float(detail["amount"])
                    unit_price = amount / quantity
                    cursor.execute("SELECT SUM(performance) FROM status_details WHERE detail_id = ?", (detail["id"],))
                    total_perf = cursor.fetchone()[0] or 0
                    status_data[detail["id"]] = {"perf": tk.StringVar(value=str(total_perf)), "prev": total_perf, "new": 0, "unit_price": unit_price}
                except (ValueError, TypeError) as e:
                    logging.error(f"خطا در تبدیل داده‌ها برای detail_id={detail['id']}: {e}")
                    messagebox.showerror("خطا", f"داده‌های جزئیات قرارداد (quantity یا amount) معتبر نیست: {detail['description']}")
                    status_window.destroy()
                    return

        def update_status_list():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT number, date, status, total_amount FROM statuses WHERE contract_id = ?", (contract_id,))
                statuses = cursor.fetchall()
                for item in status_list.get_children():
                    status_list.delete(item)
                for status in statuses:
                    status_list.insert("", "end", values=(status["number"], status["date"], status["status"], format_amount(status["total_amount"])))

        def load_status():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                for item in details_tree.get_children():
                    details_tree.delete(item)
                total_prev = 0
                total_new = 0
                for detail in details:
                    detail_id = detail["id"]
                    cursor.execute("SELECT SUM(performance) FROM status_details WHERE detail_id = ?", (detail_id,))
                    total_perf = cursor.fetchone()[0] or 0
                    perf = float(status_data[detail_id]["perf"].get() or "0")
                    new_perf = perf - total_perf if perf > total_perf else 0
                    new_amount = new_perf * status_data[detail_id]["unit_price"]
                    status_data[detail_id]["prev"] = total_perf
                    status_data[detail_id]["new"] = new_amount
                    total_prev += total_perf * status_data[detail_id]["unit_price"]
                    total_new += new_amount
                    details_tree.insert("", "end", values=(detail["description"], detail["quantity"], detail["unit"], format_amount(detail["amount"]), 
                                                           total_perf, new_perf, format_amount(new_amount), 
                                                           f"{perf / float(detail['quantity']) * 100:.2f}%"))
                total_prev_label.config(text=f"جمع قبلی: {format_amount(total_prev)} ریال")
                total_new_label.config(text=f"جمع جدید: {format_amount(total_new)} ریال")

        def update_total():
            total_new = 0
            for i, item in enumerate(details_tree.get_children()):
                detail_id = details[i]["id"]
                try:
                    perf = float(status_data[detail_id]["perf"].get() or "0")
                    unit_price = status_data[detail_id]["unit_price"]
                    new_perf = perf - status_data[detail_id]["prev"] if perf > status_data[detail_id]["prev"] else 0
                    new_amount = new_perf * unit_price
                    status_data[detail_id]["new"] = new_amount
                    total_new += new_amount
                    total_prev = status_data[detail_id]["prev"] * unit_price
                    details_tree.item(item, values=(details[i]["description"], details[i]["quantity"], details[i]["unit"], format_amount(details[i]["amount"]), 
                                                    status_data[detail_id]["prev"], new_perf, format_amount(new_amount), 
                                                    f"{perf / float(details[i]['quantity']) * 100:.2f}%"))
                except ValueError as e:
                    logging.error(f"خطا در محاسبه ردیف {i}: {e}")
            total_prev = sum(status_data[d]["prev"] * status_data[d]["unit_price"] for d in status_data)
            total_new_label.config(text=f"جمع جدید: {format_amount(total_new)} ریال")
            total_prev_label.config(text=f"جمع قبلی: {format_amount(total_prev)} ریال")

        def save_status(status_type, date=None, status_id=None):
            update_total()
            date = date or jdatetime.date.fromgregorian(date=datetime.now()).strftime("%Y/%m/%d")
            total_new = sum(status_data[d]["new"] for d in status_data)
            if total_new == 0:
                messagebox.showwarning("خطا", "مبلغ جدید صفر است. چیزی برای ثبت نیست!")
                return
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if status_id and cursor.execute("SELECT id FROM statuses WHERE id = ?", (status_id,)).fetchone():
                    cursor.execute("UPDATE statuses SET date = ?, status = ?, total_amount = ? WHERE id = ?", 
                                  (date, status_type, total_new, status_id))
                    cursor.execute("DELETE FROM status_details WHERE status_id = ?", (status_id,))
                else:
                    status_number = get_next_status_number(contract_id)
                    cursor.execute("INSERT INTO statuses (contract_id, number, date, status, total_amount) VALUES (?, ?, ?, ?, ?)", 
                                  (contract_id, status_number, date, status_type, total_new))
                    status_id = cursor.lastrowid
                for detail in details:
                    detail_id = detail["id"]
                    perf = float(status_data[detail_id]["perf"].get() or 0)
                    prev = status_data[detail_id]["prev"]
                    if perf > prev:
                        cursor.execute("INSERT INTO status_details (status_id, detail_id, performance, new_amount) VALUES (?, ?, ?, ?)", 
                                      (status_id, detail_id, perf - prev, status_data[detail_id]["new"]))
                conn.commit()
                update_status_list()
                messagebox.showinfo("موفقیت", f"صورت‌وضعیت {date} {status_type} شد!")
                details_frame.config(text="جزئیات صورت‌وضعیت جدید")
                load_status()

        button_frame = tk.Frame(main_frame, bg="#ECF0F1")
        button_frame.pack(fill="x", pady=10)
        total_prev_label = tk.Label(button_frame, text="جمع قبلی: 0 ریال", font=("Arial", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        total_prev_label.pack(side="right", padx=10)
        total_new_label = tk.Label(button_frame, text="جمع جدید: 0 ریال", font=("Arial", 12, "bold"), bg="#ECF0F1", fg="#2C3E50")
        total_new_label.pack(side="right", padx=10)

        tk.Button(button_frame, text="ایجاد صورت‌وضعیت جدید", font=("Arial", 12), bg="#2ECC71", fg="white", 
                  command=lambda: create_status_window(contract_id, contract, status_window, details_frame, details_tree, status_data, update_total, save_status)).pack(side="left", padx=5)
        tk.Button(button_frame, text="ثبت موقت", font=("Arial", 12), bg="#3498DB", fg="white", 
                  command=lambda: save_status("موقت") if sum(float(status_data[d]["perf"].get() or 0) > status_data[d]["prev"] for d in status_data) > 0 else messagebox.showwarning("خطا", "اول مقادیر جدید را وارد کنید!")).pack(side="left", padx=5)

        status_list.bind("<Double-1>", lambda e: create_status_window(contract_id, contract, status_window, details_frame, details_tree, status_data, update_total, save_status, 
                                                                      int(status_list.item(status_list.selection()[0])["values"][0]) if status_list.selection() else None))
        update_status_list()
        load_status()

    contract_tree.bind("<Double-1>", open_status_window)
    update_contracts()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدیریت صورت‌وضعیت‌ها")
    center_window(root, 1000, 700)
    show_status(root)
    root.mainloop()