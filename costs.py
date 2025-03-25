import tkinter as tk
from tkinter import ttk, messagebox
import db_costs as database
import db_contracts
import logging

logging.basicConfig(filename="costs_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

def format_amount(amount):
    try:
        return "{:,}".format(int(str(amount).replace(",", "")))
    except (ValueError, TypeError):
        return amount if amount else "0"

def validate_number_input(P):
    return P.isdigit() or P == ""

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

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_costs(master, enable_main_callback):
    logging.info("ورود به show_costs")
    
    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    # هدر
    header = tk.Frame(main_frame, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="مدیریت هزینه‌ها", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(main_frame, bg="#172A3A", width=113)
    sidebar.pack(side="right", fill="y")

    # محتوا
    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    notebook = ttk.Notebook(content)
    notebook.pack(fill="both", expand=True)

    costs_tab = tk.Frame(notebook, bg="white")
    notebook.add(costs_tab, text="هزینه‌ها")

    assets_tab = tk.Frame(notebook, bg="white")
    notebook.add(assets_tab, text="دارایی‌ها")

    # --- بخش هزینه‌ها ---
    tk.Label(costs_tab, text="لیست هزینه‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#333333").pack(anchor="e", pady=5)

    columns = ("id", "contract_number", "cost_code", "cost_type", "amount", "tax", "discount", "final_amount", 
               "payer", "invoice_number", "status", "date", "description")
    costs_tree = ttk.Treeview(costs_tab, columns=columns, show="headings", height=15)
    costs_tree.heading("id", text="شناسه", anchor="e")
    costs_tree.heading("contract_number", text="شماره قرارداد", anchor="e")
    costs_tree.heading("cost_code", text="کد هزینه", anchor="e")
    costs_tree.heading("cost_type", text="نوع هزینه", anchor="e")
    costs_tree.heading("amount", text="مبلغ پایه (ریال)", anchor="e")
    costs_tree.heading("tax", text="مالیات (ریال)", anchor="e")
    costs_tree.heading("discount", text="تخفیف (ریال)", anchor="e")
    costs_tree.heading("final_amount", text="مبلغ نهایی (ریال)", anchor="e")
    costs_tree.heading("payer", text="پرداخت‌کننده", anchor="e")
    costs_tree.heading("invoice_number", text="شماره فاکتور", anchor="e")
    costs_tree.heading("status", text="وضعیت پرداخت", anchor="e")
    costs_tree.heading("date", text="تاریخ", anchor="e")
    costs_tree.heading("description", text="توضیحات", anchor="e")
    costs_tree.column("id", width=50, anchor="e")
    costs_tree.column("contract_number", width=100, anchor="e")
    costs_tree.column("cost_code", width=80, anchor="e")
    costs_tree.column("cost_type", width=120, anchor="e")
    costs_tree.column("amount", width=120, anchor="e")
    costs_tree.column("tax", width=80, anchor="e")
    costs_tree.column("discount", width=80, anchor="e")
    costs_tree.column("final_amount", width=120, anchor="e")
    costs_tree.column("payer", width=100, anchor="e")
    costs_tree.column("invoice_number", width=100, anchor="e")
    costs_tree.column("status", width=100, anchor="e")
    costs_tree.column("date", width=100, anchor="e")
    costs_tree.column("description", width=200, anchor="e")
    costs_tree.pack(fill="both", expand=True, pady=5)

    def update_costs_table():
        for item in costs_tree.get_children():
            costs_tree.delete(item)
        costs = database.get_costs()
        for cost in costs:
            costs_tree.insert("", "end", values=(
                cost[0], cost[1], cost[2], cost[3], format_amount(cost[4]), format_amount(cost[5]), 
                format_amount(cost[6]), format_amount(cost[7]), cost[8], cost[9], cost[10], cost[11], cost[12]
            ))

    def open_cost_window(mode="new", cost_id=None):
        contracts = db_contracts.get_contracts()
        if not contracts:
            messagebox.showwarning("خطا", "هیچ قراردادی ثبت نشده! اول یه قرارداد ثبت کن.")
            return

        window = tk.Toplevel(master)
        window.title("هزینه جدید" if mode == "new" else "ویرایش هزینه")
        center_window(window, 600, 700)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", height=40)
        header.pack(fill="x")
        tk.Label(header, text="ثبت هزینه جدید" if mode == "new" else "ویرایش هزینه", 
                 font=("IranNastaliq", 20), fg="white", bg="#00A86B" if mode == "new" else "#EC8B5E").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # فرم
        form_frame = tk.LabelFrame(content, text="جزئیات هزینه", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        form_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        contract_numbers = [contract[1] for contract in contracts]
        contract_ids = {contract[1]: contract[0] for contract in contracts}
        cost_types = [
            "هزینه‌های جاری", "هزینه خرید لوازم اداری", "هزینه خرید لباس کارکنان", 
            "خرید میز و صندلی", "هزینه تجهیزات اداری", "هزینه لوازم التحریر", 
            "هزینه چاپ", "هزینه سفر", "هزینه غذا"
        ]
        statuses = ["پرداخت‌شده", "در انتظار پرداخت", "لغو شده"]

        entries = []
        tk.Label(form_frame, text="شماره قرارداد:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        contract_combo = ttk.Combobox(form_frame, values=contract_numbers, font=("IRANSans", 12), width=30, justify="right")
        contract_combo.grid(row=0, column=0, pady=5, padx=5)
        entries.append(contract_combo)

        tk.Label(form_frame, text="کد هزینه:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        cost_code_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        cost_code_entry.grid(row=1, column=0, pady=5, padx=5)
        entries.append(cost_code_entry)

        tk.Label(form_frame, text="نوع هزینه:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        cost_type_combo = ttk.Combobox(form_frame, values=cost_types, font=("IRANSans", 12), width=30, justify="right")
        cost_type_combo.set("هزینه‌های جاری")
        cost_type_combo.grid(row=2, column=0, pady=5, padx=5)
        entries.append(cost_type_combo)

        tk.Label(form_frame, text="مبلغ پایه (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        amount_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right", validate="key", validatecommand=(master.register(validate_number_input), '%P'))
        amount_entry.grid(row=3, column=0, pady=5, padx=5)
        entries.append(amount_entry)

        tk.Label(form_frame, text="مالیات (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=4, column=1, pady=5, padx=5, sticky="e")
        tax_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right", validate="key", validatecommand=(master.register(validate_number_input), '%P'))
        tax_entry.grid(row=4, column=0, pady=5, padx=5)
        entries.append(tax_entry)

        tk.Label(form_frame, text="تخفیف (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=5, column=1, pady=5, padx=5, sticky="e")
        discount_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right", validate="key", validatecommand=(master.register(validate_number_input), '%P'))
        discount_entry.grid(row=5, column=0, pady=5, padx=5)
        entries.append(discount_entry)

        tk.Label(form_frame, text="مبلغ نهایی (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=6, column=1, pady=5, padx=5, sticky="e")
        final_amount_label = tk.Label(form_frame, text="0", font=("IRANSans", 12), bg="#F5F6F5", width=30, anchor="e")
        final_amount_label.grid(row=6, column=0, pady=5, padx=5)

        tk.Label(form_frame, text="پرداخت‌کننده:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=7, column=1, pady=5, padx=5, sticky="e")
        payer_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        payer_entry.grid(row=7, column=0, pady=5, padx=5)
        entries.append(payer_entry)

        tk.Label(form_frame, text="شماره فاکتور:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=8, column=1, pady=5, padx=5, sticky="e")
        invoice_number_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        invoice_number_entry.grid(row=8, column=0, pady=5, padx=5)
        entries.append(invoice_number_entry)

        tk.Label(form_frame, text="وضعیت پرداخت:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=9, column=1, pady=5, padx=5, sticky="e")
        status_combo = ttk.Combobox(form_frame, values=statuses, font=("IRANSans", 12), width=30, justify="right")
        status_combo.set("در انتظار پرداخت")
        status_combo.grid(row=9, column=0, pady=5, padx=5)
        entries.append(status_combo)

        tk.Label(form_frame, text="تاریخ:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=10, column=1, pady=5, padx=5, sticky="e")
        date_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        date_entry.grid(row=10, column=0, pady=5, padx=5)
        entries.append(date_entry)

        tk.Label(form_frame, text="توضیحات:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=11, column=1, pady=5, padx=5, sticky="ne")
        description_entry = tk.Text(form_frame, font=("IRANSans", 12), width=32, height=4)
        description_entry.grid(row=11, column=0, pady=5, padx=5)
        entries.append(description_entry)

        def update_final_amount(*args):
            try:
                amount = int(amount_entry.get().replace(",", "") or 0)
                tax = int(tax_entry.get().replace(",", "") or 0)
                discount = int(discount_entry.get().replace(",", "") or 0)
                final = amount + tax - discount
                final_amount_label.config(text=format_amount(final))
            except ValueError:
                final_amount_label.config(text="0")

        amount_entry.bind("<KeyRelease>", update_final_amount)
        tax_entry.bind("<KeyRelease>", update_final_amount)
        discount_entry.bind("<KeyRelease>", update_final_amount)

        if mode == "new":
            amount_entry.insert(0, "0")
            tax_entry.insert(0, "0")
            discount_entry.insert(0, "0")
            amount_entry.bind("<FocusIn>", lambda e: amount_entry.delete(0, tk.END) if amount_entry.get() == "0" else None)
            tax_entry.bind("<FocusIn>", lambda e: tax_entry.delete(0, tk.END) if tax_entry.get() == "0" else None)
            discount_entry.bind("<FocusIn>", lambda e: discount_entry.delete(0, tk.END) if discount_entry.get() == "0" else None)

        if mode == "edit" and cost_id:
            cost = database.get_cost_by_id(cost_id)
            if cost:
                contract_number = [c[1] for c in contracts if c[0] == cost[1]][0]
                contract_combo.set(contract_number)
                cost_code_entry.insert(0, cost[2] or "")
                cost_type_combo.set(cost[3])
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, str(cost[4]))
                tax_entry.delete(0, tk.END)
                tax_entry.insert(0, str(cost[5] or "0"))
                discount_entry.delete(0, tk.END)
                discount_entry.insert(0, str(cost[6] or "0"))
                payer_entry.insert(0, cost[8] or "")
                invoice_number_entry.insert(0, cost[9] or "")
                status_combo.set(cost[10])
                date_entry.insert(0, cost[11])
                description_entry.insert("1.0", cost[12] or "")
                update_final_amount()

        def save_cost():
            try:
                contract_number = contract_combo.get()
                cost_code = cost_code_entry.get()
                cost_type = cost_type_combo.get()
                amount = amount_entry.get()
                tax = tax_entry.get() or "0"
                discount = discount_entry.get() or "0"
                payer = payer_entry.get()
                invoice_number = invoice_number_entry.get()
                status = status_combo.get()
                date = date_entry.get()
                description = description_entry.get("1.0", tk.END).strip()

                if not all([contract_number, cost_type, amount, date]):
                    messagebox.showwarning("خطا", "فیلدهای اجباری (شماره قرارداد، نوع هزینه، مبلغ، تاریخ) را پر کنید!")
                    return

                contract_id = contract_ids.get(contract_number)
                if not contract_id:
                    raise ValueError(f"شماره قرارداد {contract_number} پیدا نشد!")
                final_amount = int(amount.replace(",", "") or 0) + int(tax.replace(",", "") or 0) - int(discount.replace(",", "") or 0)

                if mode == "new":
                    database.add_cost(contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description)
                    messagebox.showinfo("موفقیت", "هزینه ثبت شد!")
                elif mode == "edit" and cost_id:
                    database.update_cost(cost_id, contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description)
                    messagebox.showinfo("موفقیت", "هزینه ویرایش شد!")
                update_costs_table()
                window.destroy()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ثبت/ویرایش هزینه: {str(e)}")

        def cancel():
            window.destroy()

        # کلیدهای Enter و Arrow
        for i, entry in enumerate(entries):
            entry.bind("<Down>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())
            entry.bind("<Up>", lambda e, idx=i: entries[(idx - 1) % len(entries)].focus_set())
            entry.bind("<Return>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())

        # دکمه‌ها پایین سایدبار
        sidebar_color = "#00A86B" if mode == "new" else "#EC8B5E"
        hover_color = "#008F5A" if mode == "new" else "#D67447"
        y_pos = 600  # پایین پنجره
        for icon, text, cmd in [("✔️", "تأیید", save_cost), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg=sidebar_color)
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg=sidebar_color, fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg=sidebar_color, hover_bg=hover_color, fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    def edit_cost():
        selected = costs_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک هزینه انتخاب کنید!")
            return
        cost_id = costs_tree.item(selected[0])["values"][0]
        open_cost_window(mode="edit", cost_id=cost_id)

    def delete_cost():
        selected = costs_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک هزینه انتخاب کنید!")
            return
        cost_id = costs_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این هزینه را حذف کنید؟"):
            database.delete_cost(cost_id)
            update_costs_table()
            messagebox.showinfo("موفقیت", "هزینه حذف شد!")

    # --- بخش دارایی‌ها ---
    tk.Label(assets_tab, text="لیست دارایی‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#333333").pack(anchor="e", pady=5)

    fixed_frame = tk.Frame(assets_tab, bg="white", bd=1, relief="solid")
    fixed_frame.pack(fill="both", expand=True)

    fixed_columns = ("id", "asset_type", "item_name", "description", "amount", "date")
    assets_tree = ttk.Treeview(fixed_frame, columns=fixed_columns, show="headings", height=10)
    assets_tree.heading("id", text="شناسه", anchor="e")
    assets_tree.heading("asset_type", text="نوع", anchor="e")
    assets_tree.heading("item_name", text="نام قلم", anchor="e")
    assets_tree.heading("description", text="توضیحات", anchor="e")
    assets_tree.heading("amount", text="مبلغ (ریال)", anchor="e")
    assets_tree.heading("date", text="تاریخ", anchor="e")
    assets_tree.column("id", width=50, anchor="e")
    assets_tree.column("asset_type", width=80, anchor="e")
    assets_tree.column("item_name", width=120, anchor="e")
    assets_tree.column("description", width=200, anchor="e")
    assets_tree.column("amount", width=120, anchor="e")
    assets_tree.column("date", width=100, anchor="e")
    assets_tree.pack(fill="both", expand=True)

    def update_assets_table():
        for item in assets_tree.get_children():
            assets_tree.delete(item)
        assets = database.get_assets()
        for asset in assets:
            assets_tree.insert("", "end", values=(asset[0], asset[1], asset[2], asset[3], format_amount(asset[4]), asset[5]))

    def open_asset_window(mode="new", asset_id=None):
        window = tk.Toplevel(master)
        window.title("دارایی جدید" if mode == "new" else "ویرایش دارایی")
        center_window(window, 500, 500)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", height=40)
        header.pack(fill="x")
        tk.Label(header, text="ثبت دارایی جدید" if mode == "new" else "ویرایش دارایی", 
                 font=("IranNastaliq", 20), fg="white", bg="#00A86B" if mode == "new" else "#EC8B5E").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # فرم
        form_frame = tk.LabelFrame(content, text="جزئیات دارایی", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        form_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        asset_types = ["منقول", "غیرمنقول"]
        item_mapping = {
            "لپ‌تاپ": "منقول", "موبایل": "منقول", "میز": "منقول", "صندلی": "منقول", 
            "ماشین": "منقول", "ساختمان": "غیرمنقول", "زمین": "غیرمنقول", "کارخانه": "غیرمنقول"
        }

        entries = []
        tk.Label(form_frame, text="نام قلم:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        item_name_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        item_name_entry.grid(row=0, column=0, pady=5, padx=5)
        entries.append(item_name_entry)

        tk.Label(form_frame, text="نوع دارایی:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        asset_type_combo = ttk.Combobox(form_frame, values=asset_types, font=("IRANSans", 12), width=30, justify="right")
        asset_type_combo.set("منقول")
        asset_type_combo.grid(row=1, column=0, pady=5, padx=5)
        entries.append(asset_type_combo)

        tk.Label(form_frame, text="توضیحات:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        description_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        description_entry.grid(row=2, column=0, pady=5, padx=5)
        entries.append(description_entry)

        tk.Label(form_frame, text="مبلغ (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        amount_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right", validate="key", validatecommand=(master.register(validate_number_input), '%P'))
        amount_entry.grid(row=3, column=0, pady=5, padx=5)
        entries.append(amount_entry)

        tk.Label(form_frame, text="تاریخ:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=4, column=1, pady=5, padx=5, sticky="e")
        date_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        date_entry.grid(row=4, column=0, pady=5, padx=5)
        entries.append(date_entry)

        if mode == "new":
            amount_entry.insert(0, "0")
            amount_entry.bind("<FocusIn>", lambda e: amount_entry.delete(0, tk.END) if amount_entry.get() == "0" else None)

        def auto_set_asset_type(*args):
            item_name = item_name_entry.get().strip()
            asset_type = item_mapping.get(item_name, "منقول")
            asset_type_combo.set(asset_type)

        item_name_entry.bind("<KeyRelease>", auto_set_asset_type)

        if mode == "edit" and asset_id:
            asset = database.get_asset_by_id(asset_id)
            if asset:
                item_name_entry.insert(0, asset[2] or "")
                asset_type_combo.set(asset[1])
                description_entry.insert(0, asset[3] or "")
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, str(asset[4]))
                date_entry.insert(0, asset[5])

        def save_asset():
            try:
                asset_type = asset_type_combo.get()
                item_name = item_name_entry.get()
                description = description_entry.get()
                amount = amount_entry.get()
                date = date_entry.get()
                if not all([item_name, amount, date]):
                    messagebox.showwarning("خطا", "فیلدهای اجباری (نام قلم، مبلغ، تاریخ) را پر کنید!")
                    return
                if mode == "new":
                    database.add_asset(asset_type, item_name, description, amount, date)
                    messagebox.showinfo("موفقیت", "دارایی ثبت شد!")
                elif mode == "edit" and asset_id:
                    database.update_asset(asset_id, asset_type, item_name, description, amount, date)
                    messagebox.showinfo("موفقیت", "دارایی ویرایش شد!")
                update_assets_table()
                window.destroy()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ثبت/ویرایش دارایی: {str(e)}")

        def cancel():
            window.destroy()

        # کلیدهای Enter و Arrow
        for i, entry in enumerate(entries):
            entry.bind("<Down>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())
            entry.bind("<Up>", lambda e, idx=i: entries[(idx - 1) % len(entries)].focus_set())
            entry.bind("<Return>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus_set())

        # دکمه‌ها پایین سایدبار
        sidebar_color = "#00A86B" if mode == "new" else "#EC8B5E"
        hover_color = "#008F5A" if mode == "new" else "#D67447"
        y_pos = 400  # پایین پنجره
        for icon, text, cmd in [("✔️", "تأیید", save_asset), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg=sidebar_color)
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg=sidebar_color, fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg=sidebar_color, hover_bg=hover_color, fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    def edit_asset():
        selected = assets_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک دارایی انتخاب کنید!")
            return
        asset_id = assets_tree.item(selected[0])["values"][0]
        open_asset_window(mode="edit", asset_id=asset_id)

    def delete_asset():
        selected = assets_tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک دارایی انتخاب کنید!")
            return
        asset_id = assets_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این دارایی را حذف کنید؟"):
            database.delete_asset(asset_id)
            update_assets_table()
            messagebox.showinfo("موفقیت", "دارایی حذف شد!")

    def get_active_tab():
        return notebook.tab(notebook.select(), "text")

    def open_new_window():
        if get_active_tab() == "هزینه‌ها":
            open_cost_window(mode="new")
        elif get_active_tab() == "دارایی‌ها":
            open_asset_window(mode="new")

    def edit_selected():
        if get_active_tab() == "هزینه‌ها":
            edit_cost()
        elif get_active_tab() == "دارایی‌ها":
            edit_asset()

    def delete_selected():
        if get_active_tab() == "هزینه‌ها":
            delete_cost()
        elif get_active_tab() == "دارایی‌ها":
            delete_asset()

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    # دکمه‌های سایدبار اصلی
    buttons = [
        ("📝", "ثبت جدید", open_new_window),
        ("✏️", "ویرایش", edit_selected),
        ("🗑️", "حذف", delete_selected),
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

    update_costs_table()
    update_assets_table()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدیریت هزینه‌ها")
    center_window(root, 900, 700)
    show_costs(root, lambda: None)
    root.mainloop()