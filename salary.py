import tkinter as tk
from tkinter import ttk, messagebox
import database
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

logging.basicConfig(filename="salary_log.log", level=logging.DEBUG, 
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

def show_salary(master, enable_main_callback):
    logging.info("ورود به show_salary")
    
    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    # هدر
    header = tk.Frame(main_frame, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="مدیریت حقوق", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(main_frame, bg="#172A3A", width=113)
    sidebar.pack(side="right", fill="y")

    # محتوا
    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # موتور جستجو
    search_frame = tk.Frame(content, bg="#F5F6F5", bd=2, relief="groove")
    search_frame.pack(fill="x", pady=(0, 10))

    tk.Label(search_frame, text="نام و نام خانوادگی:", font=("IRANSans", 10), bg="#F5F6F5").pack(side="right", padx=5)
    name_var = tk.StringVar()
    name_entry = tk.Entry(search_frame, textvariable=name_var, font=("IRANSans", 10), width=15, justify="right")
    name_entry.pack(side="right", padx=5)

    tk.Label(search_frame, text="کد ملی:", font=("IRANSans", 10), bg="#F5F6F5").pack(side="right", padx=5)
    code_var = tk.StringVar()
    code_entry = tk.Entry(search_frame, textvariable=code_var, font=("IRANSans", 10), width=12, justify="right")
    code_entry.pack(side="right", padx=5)

    tk.Label(search_frame, text="طرف قرارداد:", font=("IRANSans", 10), bg="#F5F6F5").pack(side="right", padx=5)
    contract_var = tk.StringVar()
    contracts = ["همه", "شهرداری اراک (ID: 1)", "شهرداری تهران (ID: 2)", "بدون قرارداد"]  # فرضی، باید از دیتابیس بگیریم
    contract_combo = ttk.Combobox(search_frame, textvariable=contract_var, values=contracts, font=("IRANSans", 10), width=15, justify="right")
    contract_combo.pack(side="right", padx=5)
    contract_combo.set("همه")

    tk.Label(search_frame, text="تاریخ استخدام:", font=("IRANSans", 10), bg="#F5F6F5").pack(side="right", padx=5)
    hire_date_var = tk.StringVar()
    hire_date_entry = tk.Entry(search_frame, textvariable=hire_date_var, font=("IRANSans", 10), width=12, justify="right")
    hire_date_entry.pack(side="right", padx=5)

    # جدول
    tree = ttk.Treeview(content, columns=("id", "full_name", "national_code", "contract_id", "days", "overtime", "deduction", "net_salary", "performance"), show="headings")
    tree.heading("id", text="شناسه", anchor="e")
    tree.heading("full_name", text="نام و نام خانوادگی", anchor="e")
    tree.heading("national_code", text="کد ملی", anchor="e")
    tree.heading("contract_id", text="شناسه قرارداد", anchor="e")
    tree.heading("days", text="روز/تعداد کارکرد", anchor="e")
    tree.heading("overtime", text="اضافه‌کاری (ریال)", anchor="e")
    tree.heading("deduction", text="کسورات (ریال)", anchor="e")
    tree.heading("net_salary", text="حقوق خالص (ریال)", anchor="e")
    tree.heading("performance", text="حسن انجام کار (ریال)", anchor="e")
    tree.column("id", width=50, anchor="e")
    tree.column("full_name", width=150, anchor="e")
    tree.column("national_code", width=100, anchor="e")
    tree.column("contract_id", width=100, anchor="e")
    tree.column("days", width=80, anchor="e")
    tree.column("overtime", width=100, anchor="e")
    tree.column("deduction", width=100, anchor="e")
    tree.column("net_salary", width=120, anchor="e")
    tree.column("performance", width=120, anchor="e")
    tree.pack(fill="both", expand=True, pady=5)

    style = ttk.Style()
    style.configure("Treeview", rowheight=25, font=("IRANSans", 11))
    style.configure("Treeview.Heading", font=("IRANSans", 12, "bold"))

    def update_table(*args):
        logging.info("به‌روزرسانی جدول حقوق با فیلتر")
        for item in tree.get_children():
            tree.delete(item)
        employees = database.get_employees()
        name_filter = name_var.get().strip()
        code_filter = code_var.get().strip()
        contract_filter = contract_var.get()
        hire_date_filter = hire_date_var.get().strip()

        for emp in employees:
            full_name = f"{emp[1]} {emp[2]}"
            national_code = emp[5]
            contract_id = emp[18] or "بدون قرارداد"
            hire_date = emp[13] or ""  # فرض می‌کنم تاریخ استخدام توی ستون 13 دیتابیس باشه

            # اعمال فیلترها
            if name_filter and name_filter not in full_name:
                continue
            if code_filter and code_filter not in national_code:
                continue
            if contract_filter != "همه" and contract_filter != contract_id:
                continue
            if hire_date_filter and hire_date_filter not in hire_date:
                continue

            contract_type = emp[15]
            base_salary = int(emp[16]) if emp[16] else 0
            daily_rate = int(emp[19]) if emp[19] else 0
            unit_count = int(emp[20]) if emp[20] else 0
            unit_rate = int(emp[21]) if emp[21] else 0
            days_or_units = 30 if contract_type in ["عادی", "روزمزد"] else unit_count
            overtime = 0
            deduction = 0
            if contract_type == "عادی":
                net_salary = base_salary + overtime - deduction
            elif contract_type == "روزمزد":
                net_salary = daily_rate * days_or_units - deduction
            elif contract_type == "تعدادی":
                net_salary = unit_rate * days_or_units - deduction
            else:
                net_salary = base_salary - deduction
            performance_percentage = float(emp[22]) if len(emp) > 22 and emp[22] else 0
            performance_amount = net_salary * (performance_percentage / 100)
            net_salary -= performance_amount
            if emp[17]:  # بیمه
                net_salary -= base_salary * 0.07
            tree.insert("", "end", values=(emp[0], full_name, national_code, contract_id, days_or_units, format_amount(overtime), format_amount(deduction), format_amount(net_salary), format_amount(performance_amount)))

    # باندینگ برای آپدیت پویا
    name_var.trace("w", update_table)
    code_var.trace("w", update_table)
    contract_var.trace("w", update_table)
    hire_date_var.trace("w", update_table)

    def edit_salary():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یه کارمند رو انتخاب کن!")
            return
        emp_id = tree.item(selected[0])["values"][0]
        emp = database.get_employee_by_id(emp_id)
        
        window = tk.Toplevel(master)
        window.title("ویرایش کارکرد")
        center_window(window, 500, 500)
        window.configure(bg="#F5F6F5")

        header = tk.Frame(window, bg="#EC8B5E", height=40)
        header.pack(fill="x")
        tk.Label(header, text="ویرایش کارکرد", font=("IranNastaliq", 20), fg="white", bg="#EC8B5E").pack(side="right", padx=10)

        btn_sidebar = tk.Frame(window, bg="#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        form_frame = tk.LabelFrame(content, text="جزئیات کارکرد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        form_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        contract_type = emp[15]
        tk.Label(form_frame, text=f"نوع قرارداد: {contract_type}", font=("IRANSans", 12), bg="#F5F6F5").pack(pady=5)

        entries = []
        days_label = "روزهای کارکرد:" if contract_type in ["عادی", "روزمزد"] else "تعداد کارکرد تأییدشده:"
        tk.Label(form_frame, text=days_label, font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        days_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=20, justify="right")
        days_entry.grid(row=0, column=0, pady=5, padx=5)
        days_entry.insert(0, "30" if contract_type in ["عادی", "روزمزد"] else emp[20])
        entries.append(days_entry)

        tk.Label(form_frame, text="اضافه‌کاری (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        overtime_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=20, justify="right")
        overtime_entry.grid(row=1, column=0, pady=5, padx=5)
        overtime_entry.insert(0, "0")
        entries.append(overtime_entry)

        tk.Label(form_frame, text="کسورات (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        deduction_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=20, justify="right")
        deduction_entry.grid(row=2, column=0, pady=5, padx=5)
        deduction_entry.insert(0, "0")
        entries.append(deduction_entry)

        tk.Label(form_frame, text="درصد حسن انجام کار:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        performance_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=20, justify="right")
        performance_entry.grid(row=3, column=0, pady=5, padx=5)
        performance_entry.insert(0, emp[22] if len(emp) > 22 and emp[22] else "0")
        entries.append(performance_entry)

        def save_salary():
            try:
                days_or_units = int(days_entry.get())
                overtime = int(overtime_entry.get() or "0")
                deduction = int(deduction_entry.get() or "0")
                performance_percentage = float(performance_entry.get() or "0")
                base_salary = int(emp[16]) if emp[16] else 0
                daily_rate = int(emp[19]) if emp[19] else 0
                unit_rate = int(emp[21]) if emp[21] else 0
                if contract_type == "عادی":
                    net_salary = base_salary + overtime - deduction
                elif contract_type == "روزمزد":
                    net_salary = daily_rate * days_or_units - deduction
                elif contract_type == "تعدادی":
                    net_salary = unit_rate * days_or_units - deduction
                else:
                    net_salary = base_salary - deduction
                performance_amount = net_salary * (performance_percentage / 100)
                net_salary -= performance_amount
                if emp[17]:  # بیمه
                    net_salary -= base_salary * 0.07
                tree.item(selected, values=(emp[0], f"{emp[1]} {emp[2]}", emp[5], emp[18], days_or_units, format_amount(overtime), format_amount(deduction), format_amount(net_salary), format_amount(performance_amount)))
                database.update_employee(emp_id, performance_percentage=performance_percentage, performance_amount=str(performance_amount))
                window.destroy()
                messagebox.showinfo("موفقیت", "کارکرد ویرایش شد!")
            except ValueError as e:
                logging.error(f"خطا در ذخیره کارکرد: {e}")
                messagebox.showerror("خطا", "لطفاً مقادیر معتبر وارد کنید!")

        def cancel():
            window.destroy()

        for i, entry in enumerate(entries):
            entry.bind("<Down>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())
            entry.bind("<Up>", lambda e, idx=i: entries[(idx - 1) % len(entries)].focus_set())
            entry.bind("<Return>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())

        y_pos = 400
        for icon, text, cmd in [("✔️", "تأیید", save_salary), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg="#EC8B5E")
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#EC8B5E", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#EC8B5E", hover_bg="#D67447", fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    def show_payslip():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یه کارمند رو انتخاب کن!")
            return
        emp_id = tree.item(selected[0])["values"][0]
        emp = database.get_employee_by_id(emp_id)
        values = tree.item(selected[0])["values"]
        
        window = tk.Toplevel(master)
        window.title(f"فیش حقوقی - {emp[1]} {emp[2]}")
        center_window(window, 600, 600)
        window.configure(bg="#F5F6F5")

        header = tk.Frame(window, bg="#00A86B", height=40)
        header.pack(fill="x")
        tk.Label(header, text="فیش حقوقی", font=("IranNastaliq", 20), fg="white", bg="#00A86B").pack(side="right", padx=10)

        btn_sidebar = tk.Frame(window, bg="#00A86B", width=113)
        btn_sidebar.pack(side="right", fill="y")

        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        payslip_frame = tk.Frame(content, bg="#F5F6F5", bd=2, relief="groove")
        payslip_frame.pack(fill="both", expand=True, padx=10, pady=10)

        labels = [
            ("نام و نام خانوادگی:", f"{emp[1]} {emp[2]}"),
            ("کد ملی:", emp[5]),
            ("شناسه قرارداد:", emp[18]),
            ("نوع قرارداد:", emp[15]),
            ("حقوق پایه (ریال):", format_amount(emp[16])),
            ("روز/تعداد کارکرد:", values[4]),
            ("اضافه‌کاری (ریال):", values[5]),
            ("کسورات (ریال):", values[6]),
            ("بیمه (سهم کارگر):", format_amount(int(emp[16]) * 0.07) if emp[17] else "0"),
            ("حسن انجام کار (ریال):", values[8]),
            ("حقوق خالص (ریال):", values[7])
        ]
        
        for i, (label, value) in enumerate(labels):
            tk.Label(payslip_frame, text=label, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333", anchor="e").grid(row=i, column=1, sticky="e", pady=5, padx=5)
            tk.Label(payslip_frame, text=value, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333", anchor="e").grid(row=i, column=0, sticky="e", pady=5, padx=5)

        def print_payslip():
            try:
                c = canvas.Canvas(f"payslip_{emp[5]}.pdf", pagesize=A4)
                c.setFont("Helvetica", 12)
                y = 800
                for label, value in labels:
                    c.drawString(400, y, f"{label} {value}")
                    y -= 30
                c.save()
                messagebox.showinfo("موفقیت", f"فیش در payslip_{emp[5]}.pdf ذخیره شد!")
            except Exception as e:
                logging.error(f"خطا در چاپ فیش: {e}")
                messagebox.showerror("خطا", "خطا در ذخیره PDF!")

        def close_payslip():
            window.destroy()

        y_pos = 500
        for icon, text, cmd in [("🖨️", "چاپ", print_payslip), ("❌", "خروج", close_payslip)]:
            btn_frame = tk.Frame(btn_sidebar, bg="#00A86B")
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#00A86B", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#00A86B", hover_bg="#008F5A", fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    buttons = [
        ("✏️", "ویرایش کارکرد", edit_salary),
        ("📜", "فیش حقوقی", show_payslip),
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

    update_table()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدیریت حقوق")
    center_window(root, 1000, 700)
    show_salary(root, lambda: None)
    root.mainloop()