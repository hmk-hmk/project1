import tkinter as tk
from tkinter import ttk, messagebox
import db_guarantees as database
import db_contracts
import logging

logging.basicConfig(filename="guarantees_log.log", level=logging.DEBUG, 
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

def show_guarantees(master, enable_main_callback):
    logging.info("ورود به show_guarantees")
    
    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    # هدر
    header = tk.Frame(main_frame, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="مدیریت ضمانت‌نامه‌ها", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(main_frame, bg="#172A3A", width=113)
    sidebar.pack(side="right", fill="y")

    # محتوا
    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True)

    tk.Label(table_frame, text="لیست ضمانت‌نامه‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#333333").pack(anchor="e", pady=5)

    columns = ("id", "contract_number", "guarantee_number", "type", "amount", "issue_date", "bank")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
    tree.heading("id", text="شناسه", anchor="e")
    tree.heading("contract_number", text="شماره قرارداد", anchor="e")
    tree.heading("guarantee_number", text="شماره ضمانت‌نامه", anchor="e")
    tree.heading("type", text="نوع ضمانت‌نامه", anchor="e")
    tree.heading("amount", text="مبلغ (ریال)", anchor="e")
    tree.heading("issue_date", text="تاریخ صدور", anchor="e")
    tree.heading("bank", text="بانک", anchor="e")
    tree.column("id", width=50, anchor="e")
    tree.column("contract_number", width=100, anchor="e")
    tree.column("guarantee_number", width=100, anchor="e")
    tree.column("type", width=100, anchor="e")
    tree.column("amount", width=120, anchor="e")
    tree.column("issue_date", width=100, anchor="e")
    tree.column("bank", width=100, anchor="e")
    tree.pack(fill="both", expand=True)

    def update_table():
        logging.info("به‌روزرسانی جدول ضمانت‌نامه‌ها")
        for item in tree.get_children():
            tree.delete(item)
        guarantees = database.get_guarantees()
        for guarantee in guarantees:
            contract = db_contracts.get_contract_by_id(guarantee[1])
            contract_number = contract[1] if contract else str(guarantee[1])
            tree.insert("", "end", values=(
                guarantee[0], contract_number, guarantee[2], guarantee[7], format_amount(guarantee[4]), 
                guarantee[3], guarantee[5]
            ))

    def open_guarantee_window(mode="new", guarantee_id=None):
        logging.info(f"باز کردن پنجره ضمانت‌نامه - mode: {mode}, guarantee_id: {guarantee_id}")
        
        contracts = db_contracts.get_contracts()
        if not contracts:
            messagebox.showwarning("خطا", "هیچ قراردادی ثبت نشده! اول یه قرارداد ثبت کن.")
            return

        window = tk.Toplevel(master)
        window.title("ضمانت‌نامه جدید" if mode == "new" else "ویرایش ضمانت‌نامه")
        center_window(window, 600, 500)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", height=40)
        header.pack(fill="x")
        tk.Label(header, text="ثبت ضمانت‌نامه جدید" if mode == "new" else "ویرایش ضمانت‌نامه", 
                 font=("IranNastaliq", 20), fg="white", bg="#00A86B" if mode == "new" else "#EC8B5E").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # فرم
        form_frame = tk.LabelFrame(content, text="جزئیات ضمانت‌نامه", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        form_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        contract_numbers = [contract[1] for contract in contracts]
        contract_ids = {contract[1]: contract[0] for contract in contracts}
        guarantee_types = ["حسن انجام کار", "پیش‌پرداخت", "مناقصه"]
        banks = ["ملی", "ملت", "صادرات", "سپه", "تجارت", "پارسیان", "سامان", "پاسارگاد", "اقتصاد نوین", "رفاه", "مسکن"]

        entries = []
        tk.Label(form_frame, text="شماره قرارداد:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=0, column=1, pady=5, padx=5, sticky="e")
        contract_combo = ttk.Combobox(form_frame, values=contract_numbers, font=("IRANSans", 12), width=30, justify="right")
        contract_combo.grid(row=0, column=0, pady=5, padx=5)
        entries.append(contract_combo)

        tk.Label(form_frame, text="شماره ضمانت‌نامه:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        guarantee_number_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        guarantee_number_entry.grid(row=1, column=0, pady=5, padx=5)
        entries.append(guarantee_number_entry)

        tk.Label(form_frame, text="نوع ضمانت‌نامه:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        guarantee_type_combo = ttk.Combobox(form_frame, values=guarantee_types, font=("IRANSans", 12), width=30, justify="right")
        guarantee_type_combo.set("حسن انجام کار")
        guarantee_type_combo.grid(row=2, column=0, pady=5, padx=5)
        entries.append(guarantee_type_combo)

        tk.Label(form_frame, text="مبلغ (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        amount_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right", validate="key", validatecommand=(master.register(validate_number_input), '%P'))
        amount_entry.grid(row=3, column=0, pady=5, padx=5)
        entries.append(amount_entry)

        tk.Label(form_frame, text="تاریخ صدور:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=4, column=1, pady=5, padx=5, sticky="e")
        issue_date_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        issue_date_entry.grid(row=4, column=0, pady=5, padx=5)
        entries.append(issue_date_entry)

        tk.Label(form_frame, text="بانک:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=5, column=1, pady=5, padx=5, sticky="e")
        bank_combo = ttk.Combobox(form_frame, values=banks, font=("IRANSans", 12), width=30, justify="right")
        bank_combo.set("ملی")
        bank_combo.grid(row=5, column=0, pady=5, padx=5)
        entries.append(bank_combo)

        if mode == "new":
            amount_entry.insert(0, "0")
            amount_entry.bind("<FocusIn>", lambda e: amount_entry.delete(0, tk.END) if amount_entry.get() == "0" else None)

        if mode == "edit" and guarantee_id:
            guarantee = database.get_guarantee_by_id(guarantee_id)
            if guarantee:
                contract = db_contracts.get_contract_by_id(guarantee[1])
                contract_combo.set(contract[1])
                guarantee_number_entry.insert(0, guarantee[2])
                guarantee_type_combo.set(guarantee[7])
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, str(guarantee[4]))
                issue_date_entry.insert(0, guarantee[3])
                bank_combo.set(guarantee[5] or "ملی")

        def save_guarantee():
            try:
                contract_number = contract_combo.get()
                guarantee_number = guarantee_number_entry.get()
                guarantee_type = guarantee_type_combo.get()
                amount = amount_entry.get().replace(",", "")
                issue_date = issue_date_entry.get()
                bank = bank_combo.get()

                if not all([contract_number, guarantee_number, guarantee_type, amount, issue_date]):
                    messagebox.showwarning("خطا", "فیلدهای اجباری (شماره قرارداد، شماره ضمانت‌نامه، نوع، مبلغ، تاریخ) را پر کنید!")
                    return

                contract_id = contract_ids[contract_number]
                if mode == "new":
                    database.add_guarantee(contract_id, guarantee_type, amount, issue_date, bank, guarantee_number)
                    logging.info(f"ضمانت‌نامه جدید برای قرارداد {contract_number} ثبت شد")
                    messagebox.showinfo("موفقیت", "ضمانت‌نامه ثبت شد!")
                elif mode == "edit" and guarantee_id:
                    database.update_guarantee(guarantee_id, contract_id, guarantee_type, amount, issue_date, bank, guarantee_number)
                    logging.info(f"ضمانت‌نامه با شناسه {guarantee_id} ویرایش شد")
                    messagebox.showinfo("موفقیت", "ضمانت‌نامه ویرایش شد!")
                
                update_table()
                window.destroy()
            except Exception as e:
                logging.error(f"خطا در ذخیره ضمانت‌نامه: {str(e)}")
                messagebox.showerror("خطا", f"خطا در ذخیره: {str(e)}")

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
        y_pos = 400  # پایین پنجره (500 - 100 برای دو دکمه)
        for icon, text, cmd in [("✔️", "تأیید", save_guarantee), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg=sidebar_color)
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg=sidebar_color, fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg=sidebar_color, hover_bg=hover_color, fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    def edit_guarantee():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک ضمانت‌نامه انتخاب کنید!")
            return
        guarantee_id = tree.item(selected[0])["values"][0]
        open_guarantee_window(mode="edit", guarantee_id=guarantee_id)

    def delete_guarantee():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک ضمانت‌نامه انتخاب کنید!")
            return
        guarantee_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این ضمانت‌نامه را حذف کنید؟"):
            database.delete_guarantee(guarantee_id)
            update_table()
            messagebox.showinfo("موفقیت", "ضمانت‌نامه حذف شد!")

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    # دکمه‌های سایدبار اصلی
    buttons = [
        ("📝", "ثبت جدید", lambda: open_guarantee_window(mode="new")),
        ("✏️", "ویرایش", edit_guarantee),
        ("🗑️", "حذف", delete_guarantee),
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
    logging.info("خروج از show_guarantees")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدیریت ضمانت‌نامه‌ها")
    center_window(root, 900, 700)
    show_guarantees(root, lambda: None)
    root.mainloop()