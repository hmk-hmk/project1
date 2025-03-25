import tkinter as tk
from tkinter import ttk, messagebox
import database
import jdatetime
import logging

logging.basicConfig(filename="employee_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        self.default_bg = kw.pop('bg', '#F0F0F0')
        self.hover_bg = kw.pop('hover_bg', '#6BBAA7')
        self.default_fg = kw.pop('fg', '#000000')
        self.hover_fg = kw.pop('hover_fg', 'white')
        
        super().__init__(master, **kw)
        self.configure(bg=self.default_bg, fg=self.default_fg, relief='flat', borderwidth=0, activebackground=self.hover_bg, activeforeground=self.hover_fg)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, e):
        if self["state"] != "disabled":
            self.configure(bg=self.hover_bg, fg=self.hover_fg)
        
    def on_leave(self, e):
        if self["state"] != "disabled":
            self.configure(bg=self.default_bg, fg=self.default_fg)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_employees(master, enable_main_callback):
    logging.info("ورود به show_employees")
    
    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    # هدر
    header = tk.Frame(main_frame, bg="#00A86B", height=25, bd=1, relief="raised")
    header.pack(fill="x")
    tk.Label(header, text="مدیریت کارکنان", font=("IRANSans", 14, "bold"), fg="white", bg="#00A86B").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(main_frame, bg="#00A86B", width=113)
    sidebar.pack(side="right", fill="y")

    # محتوا
    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # جدول کارکنان
    table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True)

    tk.Label(table_frame, text="لیست کارکنان", font=("IRANSans", 14, "bold"), bg="white", fg="#333333").pack(anchor="e", pady=5)

    columns = ("hire_date", "contract_type", "position", "father_name", "last_name", "first_name", "id")
    employee_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
    employee_tree.heading("hire_date", text="تاریخ استخدام", anchor="e")
    employee_tree.heading("contract_type", text="نوع قرارداد", anchor="e")
    employee_tree.heading("position", text="سمت", anchor="e")
    employee_tree.heading("father_name", text="نام پدر", anchor="e")
    employee_tree.heading("last_name", text="نام خانوادگی", anchor="e")
    employee_tree.heading("first_name", text="نام", anchor="e")
    employee_tree.heading("id", text="ردیف", anchor="e")
    employee_tree.column("hire_date", width=100, anchor="e")
    employee_tree.column("contract_type", width=80, anchor="e")
    employee_tree.column("position", width=100, anchor="e")
    employee_tree.column("father_name", width=80, anchor="e")
    employee_tree.column("last_name", width=80, anchor="e")
    employee_tree.column("first_name", width=80, anchor="e")
    employee_tree.column("id", width=50, anchor="e")
    employee_tree.tag_configure("evenrow", background="#D3D3D3")
    employee_tree.tag_configure("oddrow", background="#FFFFFF")
    employee_tree.pack(fill="both", expand=True)

    def update_employees():
        logging.info("به‌روزرسانی جدول کارکنان")
        for item in employee_tree.get_children():
            employee_tree.delete(item)
        employees = database.get_employees()
        for i, emp in enumerate(employees):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            hire_date = emp[26] if emp[26] else jdatetime.date.today().strftime("%Y/%m/%d")
            values = (hire_date, emp[15] or "", emp[14] or "", emp[3] or "", emp[2] or "", emp[1] or "", emp[0])
            employee_tree.insert("", "end", values=values, tags=(tag,))
        employee_tree.update()

    def open_employee_window():
        window = tk.Toplevel(master)
        window.title("ثبت کارمند جدید")
        center_window(window, 850, 650)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#00A86B", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#00A86B", height=25, bd=1, relief="raised")
        header.pack(fill="x")
        tk.Label(header, text="کارمند جدید", font=("IRANSans", 14, "bold"), fg="white", bg="#00A86B").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # اطلاعات شخصی
        personal_frame = tk.LabelFrame(content, text="اطلاعات شخصی", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        personal_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        fields = [
            ("*نام", ""),
            ("*نام خانوادگی", ""),
            ("نام پدر", ""),
            ("*کد ملی", ""),
            ("شماره تماس", ""),
            ("آدرس", ""),
        ]
        entries = {}
        for i, (label_text, default) in enumerate(fields):
            tk.Label(personal_frame, text=label_text, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry = tk.Entry(personal_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
            entry.insert(0, default)
            entry.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entries[label_text] = entry

        # اطلاعات قرارداد
        contract_frame = tk.LabelFrame(content, text="اطلاعات قرارداد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        contract_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        tk.Label(contract_frame, text="سمت", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        position_combo = ttk.Combobox(contract_frame, values=["سرممیز", "ممیز", "نقشه‌بردار", "تحلیل‌گر", "ترسیم", "GIS", "تصویربردار", 
                                                              "ورود نرم‌افزار", "مدیر قسمت", "آبدارچی", "راننده", "کارگر ساده", 
                                                              "کارمند ساده", "مشاور", "بایگانی", "حسابدار"], 
                                      font=("IRANSans", 12), width=28, state="readonly", justify="right")
        position_combo.set("کارمند ساده")
        position_combo.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Label(contract_frame, text="*نوع قرارداد", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=1, column=1, padx=5, pady=5, sticky="e")
        contract_type_combo = ttk.Combobox(contract_frame, values=["عادی", "روزمزد", "تعدادی"], font=("IRANSans", 12), width=28, state="readonly", justify="right")
        contract_type_combo.set("عادی")
        contract_type_combo.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        tk.Label(contract_frame, text="تاریخ استخدام", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        hire_date_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        hire_date_entry.insert(0, jdatetime.date.today().strftime("%Y/%m/%d"))
        hire_date_entry.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        salary_label = tk.Label(contract_frame, text="حقوق ثابت (ریال)", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        salary_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        daily_rate_label = tk.Label(contract_frame, text="نرخ روزانه (ریال)", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        daily_rate_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        unit_rate_label = tk.Label(contract_frame, text="نرخ هر واحد (ریال)", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        unit_rate_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        unit_count_label = tk.Label(contract_frame, text="تعداد واحد پیش‌فرض", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        unit_count_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")

        def update_contract_fields(*args):
            for widget in [salary_label, salary_entry, daily_rate_label, daily_rate_entry, unit_rate_label, unit_rate_entry, unit_count_label, unit_count_entry]:
                widget.grid_forget()
            if contract_type_combo.get() == "عادی":
                salary_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
                salary_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            elif contract_type_combo.get() == "روزمزد":
                daily_rate_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
                daily_rate_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            elif contract_type_combo.get() == "تعدادی":
                unit_rate_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
                unit_rate_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")
                unit_count_label.grid(row=4, column=1, padx=5, pady=5, sticky="e")
                unit_count_entry.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        contract_type_combo.bind("<<ComboboxSelected>>", update_contract_fields)
        update_contract_fields()

        # اطلاعات تکمیلی
        additional_frame = tk.LabelFrame(content, text="اطلاعات تکمیلی", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        additional_frame.pack(fill="both", expand=True, padx=(0, 10))

        tk.Label(additional_frame, text="درصد حسن انجام کار", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        performance_entry = tk.Entry(additional_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        performance_entry.insert(0, "0")
        performance_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(additional_frame, text="%", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=2, padx=5, pady=5)

        insurance_var = tk.BooleanVar(value=False)
        tk.Checkbutton(additional_frame, text="بیمه تأمین اجتماعی", variable=insurance_var, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=1, column=1, padx=5, pady=5, sticky="e")

        tk.Label(additional_frame, text="طرف قرارداد", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        contracts = database.get_contracts()
        contract_combo = ttk.Combobox(additional_frame, values=[""] + [c[4] for c in contracts], font=("IRANSans", 12), width=28, state="readonly", justify="right")
        contract_combo.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # دکمه‌های سایدبار
        def save_employee():
            if not all([entries["*نام"].get(), entries["*نام خانوادگی"].get(), entries["*کد ملی"].get(), contract_type_combo.get()]):
                messagebox.showwarning("خطا", "فیلدهای اجباری (*) را پر کنید!")
                return
            contract_id = None
            selected_party = contract_combo.get()
            if selected_party:
                for contract in contracts:
                    if contract[4] == selected_party:
                        contract_id = contract[0]
                        break
            data = {
                "first_name": entries["*نام"].get(),
                "last_name": entries["*نام خانوادگی"].get(),
                "father_name": entries["نام پدر"].get(),
                "national_code": entries["*کد ملی"].get(),
                "phone": entries["شماره تماس"].get(),
                "address": entries["آدرس"].get(),
                "contract_type": contract_type_combo.get(),
                "salary": salary_entry.get() if contract_type_combo.get() == "عادی" else "0",
                "daily_rate": daily_rate_entry.get() if contract_type_combo.get() == "روزمزد" else "0",
                "unit_rate": unit_rate_entry.get() if contract_type_combo.get() == "تعدادی" else "0",
                "unit_count": unit_count_entry.get() if contract_type_combo.get() == "تعدادی" else "0",
                "insurance": 1 if insurance_var.get() else 0,
                "contract_id": contract_id,
                "performance_percentage": performance_entry.get() or "0",
                "position": position_combo.get(),
                "hire_date": hire_date_entry.get() or jdatetime.date.today().strftime("%Y/%m/%d")
            }
            try:
                database.add_employee(data)
                messagebox.showinfo("موفقیت", "کارمند با موفقیت ثبت شد!")
                window.destroy()
                update_employees()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ثبت کارمند: {str(e)}")

        def cancel():
            window.destroy()

        y_pos = 20
        for icon, text, cmd in [("✔️", "تأیید", save_employee), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg="#00A86B")
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#00A86B", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#00A86B", hover_bg="#008F5A", fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

        for entry in entries.values():
            entry.bind("<Return>", lambda e: save_employee())

    def edit_employee():
        selected = employee_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک کارمند انتخاب کنید!")
            return
        emp_id = employee_tree.item(selected[0])["values"][6]
        emp_data = database.get_employee_by_id(emp_id)

        window = tk.Toplevel(master)
        window.title("ویرایش کارمند")
        center_window(window, 850, 650)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#EC8B5E", height=25, bd=1, relief="raised")
        header.pack(fill="x")
        tk.Label(header, text="ویرایش کارمند", font=("IRANSans", 14, "bold"), fg="white", bg="#EC8B5E").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # اطلاعات شخصی
        personal_frame = tk.LabelFrame(content, text="اطلاعات شخصی", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        personal_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        fields = [
            ("*نام", emp_data[1]),
            ("*نام خانوادگی", emp_data[2]),
            ("نام پدر", emp_data[3] or ""),
            ("*کد ملی", emp_data[5]),
            ("شماره تماس", emp_data[6] or ""),
            ("آدرس", emp_data[8] or ""),
        ]
        entries = {}
        for i, (label_text, value) in enumerate(fields):
            tk.Label(personal_frame, text=label_text, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry = tk.Entry(personal_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
            entry.insert(0, value)
            entry.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entries[label_text] = entry

        # اطلاعات قرارداد
        contract_frame = tk.LabelFrame(content, text="اطلاعات قرارداد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        contract_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        tk.Label(contract_frame, text="سمت", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        position_combo = ttk.Combobox(contract_frame, values=["سرممیز", "ممیز", "نقشه‌بردار", "تحلیل‌گر", "ترسیم", "GIS", "تصویربردار", 
                                                              "ورود نرم‌افزار", "مدیر قسمت", "آبدارچی", "راننده", "کارگر ساده", 
                                                              "کارمند ساده", "مشاور", "بایگانی", "حسابدار"], 
                                      font=("IRANSans", 12), width=28, state="readonly", justify="right")
        position_combo.set(emp_data[14] or "کارمند ساده")
        position_combo.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Label(contract_frame, text="*نوع قرارداد", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=1, column=1, padx=5, pady=5, sticky="e")
        contract_type_combo = ttk.Combobox(contract_frame, values=["عادی", "روزمزد", "تعدادی"], font=("IRANSans", 12), width=28, state="readonly", justify="right")
        contract_type_combo.set(emp_data[15] or "عادی")
        contract_type_combo.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        tk.Label(contract_frame, text="تاریخ استخدام", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        hire_date_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        hire_date_entry.insert(0, emp_data[26] or jdatetime.date.today().strftime("%Y/%m/%d"))
        hire_date_entry.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        salary_label = tk.Label(contract_frame, text="حقوق ثابت (ریال)", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        salary_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        salary_entry.insert(0, emp_data[16] or "0")
        daily_rate_label = tk.Label(contract_frame, text="نرخ روزانه (ریال)", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        daily_rate_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        daily_rate_entry.insert(0, emp_data[19] or "0")
        unit_rate_label = tk.Label(contract_frame, text="نرخ هر واحد (ریال)", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        unit_rate_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        unit_rate_entry.insert(0, emp_data[21] or "0")
        unit_count_label = tk.Label(contract_frame, text="تعداد واحد پیش‌فرض", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333")
        unit_count_entry = tk.Entry(contract_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        unit_count_entry.insert(0, emp_data[20] or "0")

        def update_contract_fields(*args):
            for widget in [salary_label, salary_entry, daily_rate_label, daily_rate_entry, unit_rate_label, unit_rate_entry, unit_count_label, unit_count_entry]:
                widget.grid_forget()
            if contract_type_combo.get() == "عادی":
                salary_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
                salary_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            elif contract_type_combo.get() == "روزمزد":
                daily_rate_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
                daily_rate_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            elif contract_type_combo.get() == "تعدادی":
                unit_rate_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
                unit_rate_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")
                unit_count_label.grid(row=4, column=1, padx=5, pady=5, sticky="e")
                unit_count_entry.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        contract_type_combo.bind("<<ComboboxSelected>>", update_contract_fields)
        update_contract_fields()

        # اطلاعات تکمیلی
        additional_frame = tk.LabelFrame(content, text="اطلاعات تکمیلی", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        additional_frame.pack(fill="both", expand=True, padx=(0, 10))

        tk.Label(additional_frame, text="درصد حسن انجام کار", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        performance_entry = tk.Entry(additional_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
        performance_entry.insert(0, emp_data[22] or "0")
        performance_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(additional_frame, text="%", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=0, column=2, padx=5, pady=5)

        insurance_var = tk.BooleanVar(value=bool(emp_data[17]))
        tk.Checkbutton(additional_frame, text="بیمه تأمین اجتماعی", variable=insurance_var, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=1, column=1, padx=5, pady=5, sticky="e")

        tk.Label(additional_frame, text="طرف قرارداد", font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        contracts = database.get_contracts()
        contract_combo = ttk.Combobox(additional_frame, values=[""] + [c[4] for c in contracts], font=("IRANSans", 12), width=28, state="readonly", justify="right")
        if emp_data[18]:
            for contract in contracts:
                if str(contract[0]) == str(emp_data[18]):
                    contract_combo.set(contract[4])
                    break
        contract_combo.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # دکمه‌های سایدبار
        def save_edit():
            if not all([entries["*نام"].get(), entries["*نام خانوادگی"].get(), entries["*کد ملی"].get(), contract_type_combo.get()]):
                messagebox.showwarning("خطا", "فیلدهای اجباری (*) را پر کنید!")
                return
            contract_id = None
            selected_party = contract_combo.get()
            if selected_party:
                for contract in contracts:
                    if contract[4] == selected_party:
                        contract_id = contract[0]
                        break
            data = {
                "first_name": entries["*نام"].get(),
                "last_name": entries["*نام خانوادگی"].get(),
                "father_name": entries["نام پدر"].get(),
                "national_code": entries["*کد ملی"].get(),
                "phone": entries["شماره تماس"].get(),
                "address": entries["آدرس"].get(),
                "contract_type": contract_type_combo.get(),
                "salary": salary_entry.get() if contract_type_combo.get() == "عادی" else "0",
                "daily_rate": daily_rate_entry.get() if contract_type_combo.get() == "روزمزد" else "0",
                "unit_rate": unit_rate_entry.get() if contract_type_combo.get() == "تعدادی" else "0",
                "unit_count": unit_count_entry.get() if contract_type_combo.get() == "تعدادی" else "0",
                "insurance": 1 if insurance_var.get() else 0,
                "contract_id": contract_id,
                "performance_percentage": performance_entry.get() or "0",
                "position": position_combo.get(),
                "hire_date": hire_date_entry.get() or jdatetime.date.today().strftime("%Y/%m/%d")
            }
            try:
                database.update_employee(emp_id, **data)
                messagebox.showinfo("موفقیت", "کارمند با موفقیت ویرایش شد!")
                window.destroy()
                update_employees()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ویرایش کارمند: {str(e)}")

        def cancel():
            window.destroy()

        y_pos = 20
        for icon, text, cmd in [("✔️", "تأیید", save_edit), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg="#EC8B5E")
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#EC8B5E", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#EC8B5E", hover_bg="#D67447", fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

        for entry in entries.values():
            entry.bind("<Return>", lambda e: save_edit())

    def delete_employee():
        selected = employee_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک کارمند انتخاب کنید!")
            return
        emp_id = employee_tree.item(selected[0])["values"][6]
        if messagebox.askyesno("تأیید حذف", f"آیا مطمئن هستید که می‌خواهید کارمند {emp_id} را حذف کنید؟"):
            try:
                database.delete_employee(emp_id)
                messagebox.showinfo("موفقیت", "کارمند با موفقیت حذف شد!")
                update_employees()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف کارمند: {str(e)}")

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    # دکمه‌های سایدبار اصلی
    buttons = [
        ("📝", "ثبت جدید", open_employee_window),
        ("✏️", "ویرایش", edit_employee),
        ("🗑️", "حذف", delete_employee),
        ("🚪", "خروج", exit_section)
    ]
    y_position = 20
    for icon, text, cmd in buttons:
        btn_frame = tk.Frame(sidebar, bg="#00A86B")
        btn_frame.place(x=0, y=y_position, width=113, height=50)
        tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#00A86B", fg="white").pack(side="right", padx=5)
        btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#00A86B", hover_bg="#008F5A", fg="white", hover_fg="white", anchor="e", command=cmd)
        btn.pack(side="right", fill="x", expand=True)
        y_position += 60

    update_employees()
    logging.info("خروج از show_employees")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدیریت کارکنان")
    center_window(root, 800, 600)
    show_employees(root, lambda: None)
    root.mainloop()