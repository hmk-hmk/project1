import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import logging
import jdatetime
from datetime import datetime
import json

logging.basicConfig(filename="events_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

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

def get_db_connection(db_path="contracts_new.db"):
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_events_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS events")
        cursor.execute('''CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            contract_id INTEGER,
            status_id INTEGER,
            payer TEXT NOT NULL,
            receiver TEXT NOT NULL,
            total_amount REAL NOT NULL,
            deductions_json TEXT,
            vat REAL DEFAULT 0,
            net_amount REAL NOT NULL,
            project TEXT,
            loan_interest REAL DEFAULT 0,
            debit_account TEXT NOT NULL,
            credit_account TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            source TEXT,
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (status_id) REFERENCES statuses(id)
        )''')
        cursor.execute("INSERT INTO events (event_type, contract_id, status_id, payer, receiver, total_amount, deductions_json, vat, net_amount, debit_account, credit_account, date, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("دریافت از شهرداری", 1, 2, "شهرداری اراک", "شرکت مادر", 2000, json.dumps({"insurance": 5, "performance": 10}), 200, 1700, "نقد (شرکت مادر)", "طلب از شهرداری", "1403/12/04", "صورت‌وضعیت 2"))
        cursor.execute("INSERT INTO events (event_type, contract_id, status_id, payer, receiver, total_amount, deductions_json, net_amount, debit_account, credit_account, date, description, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("دریافت از شرکت مادر", 1, 2, "شرکت مادر", "پایش هفت اقلیم", 1700, json.dumps({"social": 16.67, "tax": 6.25, "mother_share": 12}), 1200, "نقد (پایش)", "طلب از شرکت مادر", "1403/12/05", "پرداخت از صورت‌وضعیت 2", "صورت‌وضعیت 2 اراک"))
        cursor.execute("INSERT INTO events (event_type, payer, receiver, total_amount, net_amount, debit_account, credit_account, date, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("پرداخت حقوق", "پایش هفت اقلیم", "پرسنل", 300, 300, "حقوق", "نقد (پایش)", "1403/12/06", "حقوق اسفند"))
        conn.commit()
    logging.info("جدول رویدادها آماده شد")

def calculate_balances():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_type, net_amount, payer, receiver FROM events")
        events = cursor.fetchall()
        mother_balance = 0
        payesh_balance = 0
        for e in events:
            payer = e["payer"] if e["payer"] is not None else ""
            receiver = e["receiver"] if e["receiver"] is not None else ""
            if e["event_type"] == "دریافت از شهرداری" and receiver == "شرکت مادر":
                mother_balance += e["net_amount"]
            elif e["event_type"] == "دریافت از شرکت مادر" and receiver == "پایش هفت اقلیم":
                mother_balance -= e["net_amount"]
                payesh_balance += e["net_amount"]
            elif "پرداخت" in e["event_type"] and payer == "پایش هفت اقلیم":
                payesh_balance -= e["net_amount"]
        return mother_balance, payesh_balance

def show_events(master, enable_main_callback):
    init_events_db()
    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    header = tk.Frame(main_frame, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="دریافت‌ها و پرداخت‌ها", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    sidebar = tk.Frame(main_frame, bg="#172A3A", width=195)
    sidebar.pack(side="right", fill="y")

    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    cards_frame = tk.Frame(content, bg="#F5F6F5")
    cards_frame.pack(pady=20, fill="both", expand=True)

    def add_event(event_type, event_id=None):
        window = tk.Toplevel(master)
        window.title(f"{'ویرایش' if event_id else 'ثبت'} {event_type}")
        center_window(window, 600, 700)
        window.configure(bg="#F5F6F5")

        header = tk.Frame(window, bg="#4A4A4A", height=40)
        header.pack(fill="x")
        tk.Label(header, text=f"{'ویرایش' if event_id else 'ثبت'} {event_type}", font=("IranNastaliq", 20), fg="white", bg="#4A4A4A").pack(side="right", padx=10)

        sidebar_win = tk.Frame(window, bg="#4A4A4A", width=150)
        sidebar_win.pack(side="right", fill="y")

        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        info_frame = ttk.LabelFrame(content, text="اطلاعات اصلی", padding=10)
        info_frame.pack(fill="x", pady=5)

        contracts = ["شهرداری اراک (ID: 1)", "شهرداری تهران (ID: 2)", "بدون قرارداد"]
        tk.Label(info_frame, text="قرارداد:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        contract_var = tk.StringVar()
        contract_combo = ttk.Combobox(info_frame, textvariable=contract_var, values=contracts, font=("IRANSans", 12), justify="right")
        contract_combo.grid(row=0, column=0, pady=5, padx=5)

        statuses = ["شماره 1 (ID: 1)", "شماره 2 (ID: 2)", "علی‌الحساب", "بدون صورت‌وضعیت"]
        tk.Label(info_frame, text="صورت‌وضعیت:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(info_frame, textvariable=status_var, values=statuses, font=("IRANSans", 12), justify="right")
        status_combo.grid(row=1, column=0, pady=5, padx=5)

        payers = ["شهرداری اراک", "شرکت مادر", "پایش هفت اقلیم", "سایر"]
        tk.Label(info_frame, text="پرداخت‌کننده:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        payer_var = tk.StringVar(value="پایش هفت اقلیم" if "پرداخت" in event_type else "شهرداری اراک")
        payer_combo = ttk.Combobox(info_frame, textvariable=payer_var, values=payers, font=("IRANSans", 12), justify="right")
        payer_combo.grid(row=2, column=0, pady=5, padx=5)

        receivers = ["شرکت مادر", "پایش هفت اقلیم", "پیمانکار", "پرسنل", "فروشنده", "سایر"]
        tk.Label(info_frame, text="گیرنده:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        receiver_var = tk.StringVar(value="شرکت مادر" if event_type == "دریافت از شهرداری" else "پایش هفت اقلیم")
        receiver_combo = ttk.Combobox(info_frame, textvariable=receiver_var, values=receivers, font=("IRANSans", 12), justify="right")
        receiver_combo.grid(row=3, column=0, pady=5, padx=5)

        other_receiver_var = tk.StringVar()
        other_receiver_entry = tk.Entry(info_frame, font=("IRANSans", 12), width=20, justify="right", textvariable=other_receiver_var)
        def toggle_other_receiver(*args):
            if receiver_var.get() == "سایر":
                other_receiver_entry.grid(row=4, column=0, pady=5, padx=5)
            else:
                other_receiver_entry.grid_forget()
        receiver_var.trace("w", toggle_other_receiver)

        amount_frame = ttk.LabelFrame(content, text="مبلغ و کسورات", padding=10)
        amount_frame.pack(fill="x", pady=5)

        tk.Label(amount_frame, text="مبلغ کل (میلیون):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        total_entry = tk.Entry(amount_frame, font=("IRANSans", 12), width=20, justify="right")
        total_entry.grid(row=0, column=0, pady=5, padx=5)

        deductions_frame = ttk.Frame(amount_frame, relief="groove", borderwidth=2)
        deductions_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="ew")

        insurance_entry = tk.Entry(deductions_frame, font=("IRANSans", 12), width=10, justify="right")
        performance_entry = tk.Entry(deductions_frame, font=("IRANSans", 12), width=10, justify="right")
        social_entry = tk.Entry(deductions_frame, font=("IRANSans", 12), width=10, justify="right")
        tax_entry = tk.Entry(deductions_frame, font=("IRANSans", 12), width=10, justify="right")
        mother_share_entry = tk.Entry(deductions_frame, font=("IRANSans", 12), width=10, justify="right")

        if event_type == "دریافت از شهرداری":
            tk.Label(deductions_frame, text="حق بیمه:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
            insurance_entry.grid(row=0, column=0, pady=5, padx=5)
            insurance_entry.insert(0, "5")
            tk.Label(deductions_frame, text="حسن انجام کار:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
            performance_entry.grid(row=1, column=0, pady=5, padx=5)
            performance_entry.insert(0, "10")
        elif event_type == "دریافت از شرکت مادر":
            tk.Label(deductions_frame, text="تأمین اجتماعی:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
            social_entry.grid(row=0, column=0, pady=5, padx=5)
            social_entry.insert(0, "16.67")
            tk.Label(deductions_frame, text="مالیات:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
            tax_entry.grid(row=1, column=0, pady=5, padx=5)
            tax_entry.insert(0, "6.25")
            tk.Label(deductions_frame, text="سهم شرکت مادر:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
            mother_share_entry.grid(row=2, column=0, pady=5, padx=5)
            mother_share_entry.insert(0, "12")

        tk.Label(amount_frame, text="ارزش افزوده (%):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        vat_entry = tk.Entry(amount_frame, font=("IRANSans", 12), width=20, justify="right")
        vat_entry.grid(row=2, column=0, pady=5, padx=5)
        vat_entry.insert(0, "10" if event_type == "دریافت از شهرداری" else "0")

        tk.Label(amount_frame, text="مبلغ خالص (میلیون):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        net_label = tk.Label(amount_frame, text="0", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#00A86B")
        net_label.grid(row=3, column=0, pady=5, padx=5)

        details_frame = ttk.LabelFrame(content, text="تاریخ و توضیحات", padding=10)
        details_frame.pack(fill="x", pady=5)

        tk.Label(details_frame, text="تاریخ:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        date_entry = tk.Entry(details_frame, font=("IRANSans", 12), width=20, justify="right")
        date_entry.grid(row=0, column=0, pady=5, padx=5)
        date_entry.insert(0, jdatetime.date.fromgregorian(date=datetime.now()).strftime("%Y/%m/%d"))

        tk.Label(details_frame, text="توضیحات:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        desc_entry = tk.Entry(details_frame, font=("IRANSans", 12), width=20, justify="right")
        desc_entry.grid(row=1, column=0, pady=5, padx=5)

        preview_frame = ttk.Frame(content, relief="sunken", borderwidth=2)
        preview_frame.pack(fill="x", pady=5)
        preview_label = tk.Label(preview_frame, text="پیش‌نمایش حسابداری: -", font=("IRANSans", 11), bg="#F5F6F5")
        preview_label.pack(pady=5)

        if event_id:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
                event = cursor.fetchone()
                contract_var.set(f"{event['contract_id']}" if event['contract_id'] else "بدون قرارداد")
                status_var.set(f"{event['status_id']}" if event['status_id'] else "بدون صورت‌وضعیت")
                payer_var.set(event["payer"])
                receiver_var.set(event["receiver"])
                total_entry.insert(0, event["total_amount"])
                deductions = json.loads(event["deductions_json"] or "{}")
                if "insurance" in deductions:
                    insurance_entry.delete(0, tk.END)
                    insurance_entry.insert(0, deductions["insurance"])
                    performance_entry.delete(0, tk.END)
                    performance_entry.insert(0, deductions["performance"])
                if "social" in deductions:
                    social_entry.delete(0, tk.END)
                    social_entry.insert(0, deductions["social"])
                    tax_entry.delete(0, tk.END)
                    tax_entry.insert(0, deductions["tax"])
                    mother_share_entry.delete(0, tk.END)
                    mother_share_entry.insert(0, deductions["mother_share"])
                vat_entry.delete(0, tk.END)
                vat_entry.insert(0, event["vat"])
                date_entry.delete(0, tk.END)
                date_entry.insert(0, event["date"])
                desc_entry.insert(0, event["description"] or "")

        def update_net_amount(*args):
            try:
                total = float(total_entry.get() or 0)
                deductions = {}
                debit = "نقد (شرکت مادر)" if event_type == "دریافت از شهرداری" else "نقد (پایش)" if "دریافت" in event_type else "هزینه پروژه" if "هزینه" in event_type else "حقوق"
                credit = "طلب از شهرداری" if event_type == "دریافت از شهرداری" else "طلب از شرکت مادر" if event_type == "دریافت از شرکت مادر" else "نقد (پایش)"
                if event_type == "دریافت از شهرداری":
                    deductions["insurance"] = float(insurance_entry.get() or 0)
                    deductions["performance"] = float(performance_entry.get() or 0)
                    vat = total * float(vat_entry.get() or 0) / 100
                    deductions_sum = total * sum(deductions.values()) / 100
                    net = total - deductions_sum + vat
                elif event_type == "دریافت از شرکت مادر":
                    deductions["social"] = float(social_entry.get() or 0)
                    deductions["tax"] = float(tax_entry.get() or 0)
                    deductions["mother_share"] = float(mother_share_entry.get() or 0)
                    deductions_sum = total * sum(deductions.values()) / 100
                    net = total - deductions_sum
                else:
                    net = total
                net_label.config(text=format_amount(net))
                preview_label.config(text=f"پیش‌نمایش حسابداری: {debit} بدهکار {format_amount(net)} - {credit} بستانکار {format_amount(total)}")
            except ValueError:
                net_label.config(text="0")
                preview_label.config(text="پیش‌نمایش حسابداری: -")

        total_entry.bind("<KeyRelease>", update_net_amount)
        insurance_entry.bind("<KeyRelease>", update_net_amount)
        performance_entry.bind("<KeyRelease>", update_net_amount)
        social_entry.bind("<KeyRelease>", update_net_amount)
        tax_entry.bind("<KeyRelease>", update_net_amount)
        mother_share_entry.bind("<KeyRelease>", update_net_amount)
        vat_entry.bind("<KeyRelease>", update_net_amount)

        y_pos = 20
        for icon, text, cmd in [("✔️", "تأیید", lambda: save_event(event_id)), ("❌", "انصراف", window.destroy)]:
            btn_frame = tk.Frame(sidebar_win, bg="#4A4A4A")
            btn_frame.place(x=0, y=y_pos, width=150, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#4A4A4A", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#4A4A4A", hover_bg="#0F1F2A", fg="white", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

        def save_event(eid=None):
            try:
                contract_id = int(contract_var.get().split("ID: ")[-1][:-1]) if "ID" in (contract_var.get() or "") else None
                status_id = int(status_var.get().split("ID: ")[-1][:-1]) if "ID" in (status_var.get() or "") else None
                payer = payer_var.get()
                receiver = receiver_var.get() if receiver_var.get() != "سایر" else other_receiver_var.get()
                total = float(total_entry.get() or 0)
                deductions = {}
                if event_type == "دریافت از شهرداری":
                    deductions["insurance"] = float(insurance_entry.get() or 0)
                    deductions["performance"] = float(performance_entry.get() or 0)
                elif event_type == "دریافت از شرکت مادر":
                    deductions["social"] = float(social_entry.get() or 0)
                    deductions["tax"] = float(tax_entry.get() or 0)
                    deductions["mother_share"] = float(mother_share_entry.get() or 0)
                vat = total * float(vat_entry.get() or 0) / 100 if event_type == "دریافت از شهرداری" else 0
                deductions_sum = total * sum(deductions.values()) / 100
                net = total - deductions_sum + vat if event_type == "دریافت از شهرداری" else total - deductions_sum if event_type == "دریافت از شرکت مادر" else total
                date = date_entry.get()
                desc = desc_entry.get() or ""
                source = f"{status_var.get()} {contract_var.get()}" if status_var.get() != "بدون صورت‌وضعیت" else None
                debit = "نقد (شرکت مادر)" if event_type == "دریافت از شهرداری" else "نقد (پایش)" if "دریافت" in event_type else "هزینه پروژه" if "هزینه" in event_type else "حقوق"
                credit = "طلب از شهرداری" if event_type == "دریافت از شهرداری" else "طلب از شرکت مادر" if event_type == "دریافت از شرکت مادر" else "نقد (پایش)"

                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    if eid:
                        cursor.execute("UPDATE events SET event_type=?, contract_id=?, status_id=?, payer=?, receiver=?, total_amount=?, deductions_json=?, vat=?, net_amount=?, debit_account=?, credit_account=?, date=?, description=?, source=? WHERE id=?",
                                       (event_type, contract_id, status_id, payer, receiver, total, json.dumps(deductions), vat, net, debit, credit, date, desc, source, eid))
                    else:
                        cursor.execute("INSERT INTO events (event_type, contract_id, status_id, payer, receiver, total_amount, deductions_json, vat, net_amount, debit_account, credit_account, date, description, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                       (event_type, contract_id, status_id, payer, receiver, total, json.dumps(deductions), vat, net, debit, credit, date, desc, source))
                    conn.commit()
                window.destroy()
                messagebox.showinfo("موفقیت", f"رویداد {'ویرایش' if eid else 'ثبت'} شد!")
                update_balances()
            except ValueError as e:
                messagebox.showerror("خطا", "مقادیر واردشده معتبر نیستند!")

    def edit_event(tree, event_type):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک رویداد انتخاب کنید!")
            return
        item = tree.item(selected[0])
        event_id = None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM events WHERE event_type=? AND payer=? AND receiver=? AND total_amount=? AND net_amount=? AND date=? AND description=?",
                           (event_type, item["values"][0], item["values"][1], float(item["values"][2].replace(",", "")), float(item["values"][3].replace(",", "")), item["values"][4], item["values"][5] or ""))
            event = cursor.fetchone()
            if event:
                event_id = event["id"]
        if event_id:
            add_event(event_type, event_id)

    cards_data = [
        ("💸", "دریافت از شهرداری", "#00A86B", lambda: add_event("دریافت از شهرداری")),
        ("💰", "دریافت از شرکت مادر", "#FFD700", lambda: add_event("دریافت از شرکت مادر")),
        ("📤", "پرداخت حقوق", "#FF4500", lambda: add_event("پرداخت حقوق")),
        ("📦", "پرداخت هزینه", "#FFA500", lambda: add_event("پرداخت هزینه")),
        ("👷", "پرداخت به پیمانکار", "#4682B4", lambda: add_event("پرداخت به پیمانکار")),
        ("📊", "گزارش دریافت از شهرداری", "#00A86B", lambda: show_report("دریافت از شهرداری")),
        ("📈", "گزارش دریافت از شرکت مادر", "#FFD700", lambda: show_report("دریافت از شرکت مادر")),
        ("📉", "گزارش پرداخت حقوق", "#FF4500", lambda: show_report("پرداخت حقوق")),
        ("📋", "گزارش پرداخت هزینه", "#FFA500", lambda: show_report("پرداخت هزینه")),
        ("📑", "گزارش پرداخت به پیمانکار", "#4682B4", lambda: show_report("پرداخت به پیمانکار"))
    ]

    for idx, (icon, title, color, cmd) in enumerate(cards_data):
        card = HoverButton(
            cards_frame,
            text=f"{icon}\n{title}",
            font=("IRANSans", 12),
            bg="white",
            hover_bg=color,
            fg="#333333",
            hover_fg="white",
            width=7,
            height=2,
            command=cmd
        )
        card.grid(row=idx // 4, column=idx % 4, padx=10, pady=10, sticky="nsew")

    for i in range(4):
        cards_frame.grid_columnconfigure(i, weight=1)
    for i in range(3):
        cards_frame.grid_rowconfigure(i, weight=1)

    mother_balance_label = tk.Label(sidebar, text="موجودی شرکت مادر:\n0", font=("IRANSans", 10, "bold"), bg="#FFD700", fg="#333333", justify="center")
    mother_balance_label.place(x=0, y=20, width=195, height=50)
    payesh_balance_label = tk.Label(sidebar, text="موجودی پایش:\n0", font=("IRANSans", 10, "bold"), bg="#00A86B", fg="white", justify="center")
    payesh_balance_label.place(x=0, y=70, width=195, height=50)

    def update_balances():
        mother_balance, payesh_balance = calculate_balances()
        mother_balance_label.config(text=f"موجودی شرکت مادر:\n{format_amount(mother_balance)}")
        payesh_balance_label.config(text=f"موجودی پایش:\n{format_amount(payesh_balance)}")

    def show_report(event_type):
        report_window = tk.Toplevel(master)
        report_window.title(f"گزارش {event_type}")
        center_window(report_window, 800, 500)
        report_window.configure(bg="#F5F6F5")

        header = tk.Frame(report_window, bg="#172A3A", height=40)
        header.pack(fill="x")
        tk.Label(header, text=f"گزارش {event_type}", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

        sidebar_report = tk.Frame(report_window, bg="#172A3A", width=150)
        sidebar_report.pack(side="right", fill="y")

        content = tk.Frame(report_window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        search_frame = tk.Frame(content, bg="#F5F6F5")
        search_frame.pack(fill="x", pady=5)
        tk.Label(search_frame, text="جستجو:", font=("IRANSans", 12), bg="#F5F6F5").pack(side="right", padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("IRANSans", 12), width=30, justify="right")
        search_entry.pack(side="right")

        tree = ttk.Treeview(content, columns=("payer", "receiver", "total", "net", "date", "desc"), show="headings")
        tree.heading("payer", text="پرداخت‌کننده", anchor="e")
        tree.heading("receiver", text="گیرنده", anchor="e")
        tree.heading("total", text="مبلغ کل (میلیون)", anchor="e")
        tree.heading("net", text="مبلغ خالص (میلیون)", anchor="e")
        tree.heading("date", text="تاریخ", anchor="e")
        tree.heading("desc", text="توضیحات", anchor="e")
        tree.column("payer", width=120, anchor="e")
        tree.column("receiver", width=120, anchor="e")
        tree.column("total", width=100, anchor="e")
        tree.column("net", width=100, anchor="e")
        tree.column("date", width=100, anchor="e")
        tree.column("desc", width=200, anchor="e")
        tree.pack(fill="both", expand=True, pady=10)

        def update_tree(*args):
            tree.delete(*tree.get_children())
            with get_db_connection() as conn:
                cursor = conn.cursor()
                search_term = f"%{search_var.get()}%"
                cursor.execute("SELECT payer, receiver, total_amount, net_amount, date, description FROM events WHERE event_type = ? AND (payer LIKE ? OR receiver LIKE ? OR description LIKE ?)",
                               (event_type, search_term, search_term, search_term))
                events = cursor.fetchall()
                for e in events:
                    tree.insert("", "end", values=(e["payer"], e["receiver"], format_amount(e["total_amount"]), 
                                                   format_amount(e["net_amount"]), e["date"], e["description"] or "-"))

        search_var.trace("w", update_tree)
        update_tree()

        tree.bind("<Double-1>", lambda e: edit_event(tree, event_type))

        y_pos = 20
        for icon, text, cmd in [
            ("🖨️", "چاپ گزارش", lambda: messagebox.showinfo("چاپ", "در حال چاپ گزارش...")),
            ("📑", "خروجی اکسل", lambda: messagebox.showinfo("خروجی", "خروجی به اکسل آماده شد!")),
            ("📄", "خروجی PDF", lambda: messagebox.showinfo("خروجی", "خروجی به PDF آماده شد!")),
            ("🚪", "خروج", report_window.destroy)
        ]:
            btn_frame = tk.Frame(sidebar_report, bg="#172A3A")
            btn_frame.place(x=0, y=y_pos, width=150, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#172A3A", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#172A3A", hover_bg="#0F1F2A", fg="white", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    y_position = 120
    btn_frame = tk.Frame(sidebar, bg="#172A3A")
    btn_frame.place(x=0, y=y_position, width=195, height=50)
    tk.Label(btn_frame, text="🚪", font=("Segoe UI Emoji", 16), bg="#172A3A", fg="white").pack(side="right", padx=5)
    btn = HoverButton(btn_frame, text="خروج", font=("IRANSans", 10), bg="#172A3A", hover_bg="#0F1F2A", fg="white", 
                      command=lambda: [main_frame.destroy(), enable_main_callback(), master.master.show_section("home")])
    btn.pack(side="right", fill="x", expand=True)

    update_balances()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("دریافت‌ها و پرداخت‌ها")
    center_window(root, 1000, 700)
    show_events(root, lambda: None)
    root.mainloop()