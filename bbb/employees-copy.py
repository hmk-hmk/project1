import tkinter as tk
from tkinter import ttk, messagebox
import database

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_employees(frame):
    main_frame = tk.Frame(frame, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(main_frame, text="مدیریت کارکنان", font=("Arial", 18, "bold"), bg="white", fg="#000080", justify="right").pack(pady=10)

    search_frame = tk.LabelFrame(main_frame, text="جست‌وجوی کارکنان", font=("Arial", 12), bg="#F5F5F5", fg="#000080", bd=1, relief="solid")
    search_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(search_frame, text="کد ملی:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    national_code_search = tk.Entry(search_frame, font=("Arial", 12), width=15, justify="right")
    national_code_search.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(search_frame, text="نام و نام خانوادگی:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
    name_search = tk.Entry(search_frame, font=("Arial", 12), width=20, justify="right")
    name_search.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(search_frame, text="شماره کارمندی:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=4, padx=5, pady=5, sticky="e")
    id_search = tk.Entry(search_frame, font=("Arial", 12), width=10, justify="right")
    id_search.grid(row=0, column=5, padx=5, pady=5)

    tk.Label(search_frame, text="نوع قرارداد:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    contract_type_search = ttk.Combobox(search_frame, values=["", "عادی", "روزمزد", "تعدادی"], font=("Arial", 12), width=13, state="readonly", justify="right")
    contract_type_search.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(search_frame, text="طرف قرارداد:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
    contract_party_search = ttk.Combobox(search_frame, values=[""] + [c[4] for c in database.get_contracts()], font=("Arial", 12), width=18, state="readonly", justify="right")
    contract_party_search.grid(row=1, column=3, padx=5, pady=5)

    contract_frame = tk.LabelFrame(main_frame, text="قراردادها", font=("Arial", 12), bg="white", fg="#000080", bd=1, relief="solid")
    contract_frame.pack(side="right", fill="y", padx=5, pady=5)
    contract_tree = ttk.Treeview(contract_frame, columns=("count", "party", "subject", "number"), show="headings", height=15)
    contract_tree.heading("count", text="تعداد کارمندها", anchor="e")
    contract_tree.heading("party", text="طرف قرارداد", anchor="e")
    contract_tree.heading("subject", text="موضوع قرارداد", anchor="e")
    contract_tree.heading("number", text="شماره قرارداد", anchor="e")
    contract_tree.column("count", width=80, anchor="e")
    contract_tree.column("party", width=100, anchor="e")
    contract_tree.column("subject", width=120, anchor="e")
    contract_tree.column("number", width=80, anchor="e")
    contract_tree.pack(fill="y", expand=True)

    employee_frame = tk.LabelFrame(main_frame, text="کارکنان", font=("Arial", 12), bg="white", fg="#000080", bd=1, relief="solid")
    employee_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    style = ttk.Style()
    style.configure("Treeview", rowheight=25, font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), anchor="e")
    style.map("Treeview", background=[("selected", "#4682B4")])

    employee_tree = ttk.Treeview(employee_frame, columns=("hire_date", "contract_type", "position", "father_name", "last_name", "first_name", "id"), show="headings")
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

    # تعریف متغیر selected_contract توی محدوده show_employees
    selected_contract = None

    def update_contracts():
        for item in contract_tree.get_children():
            contract_tree.delete(item)
        contracts = database.get_contracts()
        employees = database.get_employees()
        for contract in contracts:
            count = sum(1 for emp in employees if str(emp[18]) == str(contract[0]))
            contract_tree.insert("", "end", values=(count, contract[4], contract[3], contract[1]), tags=(str(contract[0]),))
            print(f"Contract ID: {contract[0]}, Values: {count, contract[4], contract[3], contract[1]}, Tag: {str(contract[0])}")

    def update_employees(*args):
        nonlocal selected_contract
        for item in employee_tree.get_children():
            employee_tree.delete(item)
        employees = database.get_employees()
        
        sel = contract_tree.selection()
        if sel:
            selected_contract = contract_tree.item(sel[0])["tags"][0]
            print(f"Selected Contract ID: {selected_contract}")
        else:
            selected_contract = None
            print("No contract selected")

        filtered_employees = employees
        if national_code_search.get():
            filtered_employees = [emp for emp in filtered_employees if national_code_search.get() in emp[5]]
        if name_search.get():
            filtered_employees = [emp for emp in filtered_employees if name_search.get() in f"{emp[1]} {emp[2]}"]
        if id_search.get():
            filtered_employees = [emp for emp in filtered_employees if id_search.get() == str(emp[0])]
        if contract_type_search.get():
            filtered_employees = [emp for emp in filtered_employees if contract_type_search.get() == emp[15]]
        if contract_party_search.get():
            filtered_employees = [emp for emp in filtered_employees if any(c[4] == contract_party_search.get() and str(emp[18]) == str(c[0]) for c in database.get_contracts())]

        for i, emp in enumerate(filtered_employees):
            emp_contract_id = str(emp[18]) if emp[18] is not None else None
            print(f"Employee ID: {emp[0]}, Name: {emp[1]} {emp[2]}, Contract ID: {emp_contract_id}, Selected Contract: {selected_contract}")
            if selected_contract is None or emp_contract_id == selected_contract:
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                hire_date = emp[24] if emp[24] is not None else ""
                employee_tree.insert("", "end", values=(hire_date, emp[15] or "", emp[14] or "", emp[3] or "", emp[2] or "", emp[1] or "", emp[0]), tags=(tag,))
                print(f"Adding Employee ID: {emp[0]} to Treeview")
            else:
                print(f"Skipped Employee ID: {emp[0]} (Contract ID {emp_contract_id} != {selected_contract})")

    update_contracts()
    update_employees()

    search_button_frame = tk.Frame(search_frame, bg="#F5F5F5")
    search_button_frame.grid(row=1, column=4, columnspan=2, pady=5)
    tk.Button(search_button_frame, text="جست‌وجو", font=("Arial", 12), bg="#32CD32", fg="white", width=10, command=update_employees).pack(side="right", padx=5)
    tk.Button(search_button_frame, text="پاک کردن", font=("Arial", 12), bg="#FF4500", fg="white", width=10, command=lambda: [national_code_search.delete(0, "end"), name_search.delete(0, "end"), id_search.delete(0, "end"), contract_type_search.set(""), contract_party_search.set(""), update_employees()]).pack(side="right", padx=5)

    contract_tree.bind("<<TreeviewSelect>>", update_employees)
    contract_tree.bind("<Return>", update_employees)

    button_frame = tk.Frame(employee_frame, bg="white")
    button_frame.pack(fill="x", pady=5)
    tk.Button(button_frame, text="نمایش همه", font=("Arial", 12), bg="#4682B4", fg="white", command=lambda: [contract_tree.selection_remove(contract_tree.selection()), update_employees()]).pack(side="right", padx=5)
    tk.Button(button_frame, text="حذف کارمند", font=("Arial", 12), bg="#FF4500", fg="white", command=lambda: delete_employee()).pack(side="right", padx=5)
    tk.Button(button_frame, text="ویرایش کارمند", font=("Arial", 12), bg="#FFD700", fg="#000080", command=lambda: edit_employee()).pack(side="right", padx=5)
    tk.Button(button_frame, text="افزودن کارمند جدید", font=("Arial", 12), bg="#32CD32", fg="#000080", command=lambda: employee_form("افزودن کارمند جدید")).pack(side="right", padx=5)

    def employee_form(title, emp_data=None):
        window = tk.Toplevel(frame)
        window.title(title)
        center_window(window, 400, 700)
        window.configure(bg="#F5F5F5")
        window.grab_set()

        canvas = tk.Canvas(window, bg="#F5F5F5", width=380)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F5F5F5")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        title_frame = tk.Frame(scrollable_frame, bg="#4682B4", height=40)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text=title, font=("Arial", 14, "bold"), bg="#4682B4", fg="white").pack(pady=5)

        personal_frame = tk.LabelFrame(scrollable_frame, text="اطلاعات شخصی", font=("Arial", 12, "bold"), bg="#F5F5F5", fg="#000080", bd=1, relief="solid")
        personal_frame.pack(padx=5, pady=5)

        tk.Label(personal_frame, text="*نام:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        first_name_entry = ttk.Entry(personal_frame, font=("Arial", 12), width=20, justify="right")
        first_name_entry.grid(row=0, column=1, padx=5, pady=5)
        if emp_data: first_name_entry.insert(0, emp_data[1])

        tk.Label(personal_frame, text="*نام خانوادگی:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        last_name_entry = ttk.Entry(personal_frame, font=("Arial", 12), width=20, justify="right")
        last_name_entry.grid(row=1, column=1, padx=5, pady=5)
        if emp_data: last_name_entry.insert(0, emp_data[2])

        tk.Label(personal_frame, text="نام پدر:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        father_name_entry = ttk.Entry(personal_frame, font=("Arial", 12), width=20, justify="right")
        father_name_entry.grid(row=2, column=1, padx=5, pady=5)
        if emp_data: father_name_entry.insert(0, emp_data[3] or "")

        tk.Label(personal_frame, text="*کد ملی:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        national_code_entry = ttk.Entry(personal_frame, font=("Arial", 12), width=20, justify="right")
        national_code_entry.grid(row=3, column=1, padx=5, pady=5)
        if emp_data: national_code_entry.insert(0, emp_data[5])

        tk.Label(personal_frame, text="شماره تماس:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=4, column=0, padx=5, pady=5, sticky="e")
        phone_entry = ttk.Entry(personal_frame, font=("Arial", 12), width=20, justify="right")
        phone_entry.grid(row=4, column=1, padx=5, pady=5)
        if emp_data: phone_entry.insert(0, emp_data[6] or "")

        tk.Label(personal_frame, text="آدرس:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=5, column=0, padx=5, pady=5, sticky="e")
        address_entry = ttk.Entry(personal_frame, font=("Arial", 12), width=20, justify="right")
        address_entry.grid(row=5, column=1, padx=5, pady=5)
        if emp_data: address_entry.insert(0, emp_data[8] or "")

        contract_frame = tk.LabelFrame(scrollable_frame, text="اطلاعات قرارداد", font=("Arial", 12, "bold"), bg="#F5F5F5", fg="#000080", bd=1, relief="solid")
        contract_frame.pack(padx=5, pady=5)

        tk.Label(contract_frame, text="سمت:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        position_combo = ttk.Combobox(contract_frame, values=["سرممیز", "ممیز", "نقشه‌بردار", "تحلیل‌گر", "ترسیم", "GIS", "تصویربردار", 
                                                              "ورود نرم‌افزار", "مدیر قسمت", "آبدارچی", "راننده", "کارگر ساده", 
                                                              "کارمند ساده", "مشاور", "بایگانی", "حسابدار"], 
                                      font=("Arial", 12), width=18, state="readonly", justify="right")
        position_combo.grid(row=0, column=1, padx=5, pady=5)
        position_combo.set("کارمند ساده" if not emp_data else emp_data[14] or "")

        tk.Label(contract_frame, text="*نوع قرارداد:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        contract_type_combo = ttk.Combobox(contract_frame, values=["عادی", "روزمزد", "تعدادی"], font=("Arial", 12), width=18, state="readonly", justify="right")
        contract_type_combo.grid(row=1, column=1, padx=5, pady=5)
        contract_type_combo.set("عادی" if not emp_data else emp_data[15])

        tk.Label(contract_frame, text="تاریخ استخدام:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        hire_date_entry = ttk.Entry(contract_frame, font=("Arial", 12), width=20, justify="right")
        hire_date_entry.grid(row=2, column=1, padx=5, pady=5)
        if emp_data and emp_data[24] is not None:
            hire_date_entry.insert(0, emp_data[24])

        salary_label = tk.Label(contract_frame, text="حقوق ثابت (ریال):", bg="#F5F5F5", fg="#000080", font=("Arial", 12))
        salary_entry = ttk.Entry(contract_frame, font=("Arial", 12), width=20, justify="right")
        daily_rate_label = tk.Label(contract_frame, text="نرخ روزانه (ریال):", bg="#F5F5F5", fg="#000080", font=("Arial", 12))
        daily_rate_entry = ttk.Entry(contract_frame, font=("Arial", 12), width=20, justify="right")
        unit_rate_label = tk.Label(contract_frame, text="نرخ هر واحد (ریال):", bg="#F5F5F5", fg="#000080", font=("Arial", 12))
        unit_rate_entry = ttk.Entry(contract_frame, font=("Arial", 12), width=20, justify="right")
        unit_count_label = tk.Label(contract_frame, text="تعداد واحد پیش‌فرض:", bg="#F5F5F5", fg="#000080", font=("Arial", 12))
        unit_count_entry = ttk.Entry(contract_frame, font=("Arial", 12), width=20, justify="right")

        if emp_data:
            if emp_data[15] == "عادی": salary_entry.insert(0, emp_data[16] or "0")
            elif emp_data[15] == "روزمزد": daily_rate_entry.insert(0, emp_data[19] or "0")
            elif emp_data[15] == "تعدادی":
                unit_rate_entry.insert(0, emp_data[21] or "0")
                unit_count_entry.insert(0, emp_data[20] or "0")

        def update_contract_fields(*args):
            for widget in [salary_label, salary_entry, daily_rate_label, daily_rate_entry, unit_rate_label, unit_rate_entry, unit_count_label, unit_count_entry]:
                widget.grid_forget()
            if contract_type_combo.get() == "عادی":
                salary_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
                salary_entry.grid(row=3, column=1, padx=5, pady=5)
            elif contract_type_combo.get() == "روزمزد":
                daily_rate_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
                daily_rate_entry.grid(row=3, column=1, padx=5, pady=5)
            elif contract_type_combo.get() == "تعدادی":
                unit_rate_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
                unit_rate_entry.grid(row=3, column=1, padx=5, pady=5)
                unit_count_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
                unit_count_entry.grid(row=4, column=1, padx=5, pady=5)

        contract_type_combo.bind("<<ComboboxSelected>>", update_contract_fields)
        update_contract_fields()

        additional_frame = tk.LabelFrame(scrollable_frame, text="اطلاعات تکمیلی", font=("Arial", 12, "bold"), bg="#F5F5F5", fg="#000080", bd=1, relief="solid")
        additional_frame.pack(padx=5, pady=5)

        tk.Label(additional_frame, text="درصد حسن انجام کار:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        performance_entry = ttk.Entry(additional_frame, font=("Arial", 12), width=20, justify="right")
        performance_entry.grid(row=0, column=1, padx=5, pady=5)
        performance_entry.insert(0, emp_data[22] if emp_data and emp_data[22] is not None else "0")
        tk.Label(additional_frame, text="%", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5)

        insurance_var = tk.BooleanVar(value=emp_data[17] if emp_data else False)
        tk.Checkbutton(additional_frame, text="بیمه تأمین اجتماعی:", variable=insurance_var, bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")

        tk.Label(additional_frame, text="طرف قرارداد:", bg="#F5F5F5", fg="#000080", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        contracts = database.get_contracts()
        contract_combo = ttk.Combobox(additional_frame, values=[""] + [c[4] for c in contracts], font=("Arial", 12), width=18, state="readonly", justify="right")
        contract_combo.grid(row=2, column=1, padx=5, pady=5)
        if emp_data and emp_data[18]:
            for contract in contracts:
                if str(contract[0]) == str(emp_data[18]):
                    contract_combo.set(contract[4])
                    break

        button_frame = tk.Frame(scrollable_frame, bg="#F5F5F5")
        button_frame.pack(pady=20)
        button_container = tk.Frame(button_frame, bg="#F5F5F5")
        button_container.pack(anchor="center")
        save_button = tk.Button(button_container, text="ذخیره", font=("Arial", 12), bg="#32CD32", fg="white", width=10, command=lambda: save_employee(emp_data[0] if emp_data else None))
        save_button.pack(side="right", padx=10)
        cancel_button = tk.Button(button_container, text="انصراف", font=("Arial", 12), bg="#FF4500", fg="white", width=10, command=window.destroy)
        cancel_button.pack(side="right", padx=10)

        entries = [position_combo, first_name_entry, last_name_entry, father_name_entry, national_code_entry, phone_entry, 
                   address_entry, hire_date_entry, contract_type_combo, salary_entry, daily_rate_entry, unit_rate_entry, 
                   unit_count_entry, performance_entry, contract_combo, save_button, cancel_button]

        def focus_next(event):
            current = window.focus_get()
            if current in entries:
                next_index = (entries.index(current) + 1) % len(entries)
                while not entries[next_index].winfo_ismapped():
                    next_index = (next_index + 1) % len(entries)
                entries[next_index].focus_set()
            return "break"

        def focus_prev(event):
            current = window.focus_get()
            if current in entries:
                prev_index = (entries.index(current) - 1) % len(entries)
                while not entries[prev_index].winfo_ismapped():
                    prev_index = (prev_index - 1) % len(entries)
                entries[prev_index].focus_set()
            return "break"

        for entry in entries:
            if isinstance(entry, (tk.Entry, ttk.Entry)) or isinstance(entry, ttk.Combobox):
                entry.bind("<Return>", focus_next)
                entry.bind("<Down>", focus_next)
                entry.bind("<Up>", focus_prev)
            elif isinstance(entry, tk.Button):
                entry.bind("<Return>", lambda e: entry.invoke())

        def save_employee(emp_id=None):
            if not all([first_name_entry.get(), last_name_entry.get(), national_code_entry.get(), contract_type_combo.get()]):
                messagebox.showwarning("خطا", "فیلدهای اجباری (*) را پر کنید!")
                return
            contract_id = None
            selected_party = contract_combo.get()
            if selected_party:
                for contract in database.get_contracts():
                    if contract[4] == selected_party:
                        contract_id = contract[0]
                        break
            data = {
                "first_name": first_name_entry.get(),
                "last_name": last_name_entry.get(),
                "father_name": father_name_entry.get(),
                "national_code": national_code_entry.get(),
                "phone": phone_entry.get(),
                "address": address_entry.get(),
                "contract_type": contract_type_combo.get(),
                "salary": salary_entry.get() if contract_type_combo.get() == "عادی" else "0",
                "daily_rate": daily_rate_entry.get() if contract_type_combo.get() == "روزمزد" else "0",
                "unit_rate": unit_rate_entry.get() if contract_type_combo.get() == "تعدادی" else "0",
                "unit_count": unit_count_entry.get() if contract_type_combo.get() == "تعدادی" else "0",
                "insurance": 1 if insurance_var.get() else 0,
                "contract_id": contract_id,
                "performance_percentage": performance_entry.get() or "0",
                "position": position_combo.get(),
                "hire_date": hire_date_entry.get() or ""
            }
            if emp_id:
                database.update_employee(emp_id, **data)
                messagebox.showinfo("موفقیت", "کارمند با موفقیت ویرایش شد.")
            else:
                database.add_employee(data)
                messagebox.showinfo("موفقیت", "کارمند با موفقیت ثبت شد.")
            update_employees()
            update_contracts()
            window.destroy()

    def edit_employee():
        selected = employee_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک کارمند انتخاب کنید!")
            return
        emp_id = employee_tree.item(selected[0])["values"][6]
        emp_data = database.get_employee_by_id(emp_id)
        employee_form("ویرایش کارمند", emp_data)

    def delete_employee():
        selected = employee_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک کارمند انتخاب کنید!")
            return
        emp_id = employee_tree.item(selected[0])["values"][6]
        if messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید این کارمند را حذف کنید؟"):
            database.delete_employee(emp_id)
            update_employees()
            update_contracts()
            messagebox.showinfo("موفقیت", "کارمند با موفقیت حذف شد.")

    employee_tree.bind("<Double-1>", lambda e: edit_employee())
    employee_tree.bind("<Return>", lambda e: edit_employee())