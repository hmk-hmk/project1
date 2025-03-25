import tkinter as tk
from tkinter import ttk, messagebox
import db_prepayments as database
import db_contracts
import logging

logging.basicConfig(filename="prepayments_log.log", level=logging.DEBUG, 
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

def show_prepayments(master, enable_main_callback):
    logging.info("ورود به show_prepayments")
    
    main_frame = tk.Frame(master, bg="#F5F6F5")
    main_frame.pack(fill="both", expand=True)

    # هدر
    header = tk.Frame(main_frame, bg="#172A3A", height=40)
    header.pack(fill="x")
    tk.Label(header, text="مدیریت پیش‌پرداخت‌ها", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(main_frame, bg="#172A3A", width=113)
    sidebar.pack(side="right", fill="y")

    # محتوا
    content = tk.Frame(main_frame, bg="#F5F6F5")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True)

    tk.Label(table_frame, text="لیست پیش‌پرداخت‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#333333").pack(anchor="e", pady=5)

    columns = ("id", "contract_number", "date", "amount", "bank", "description")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
    tree.heading("id", text="شناسه", anchor="e")
    tree.heading("contract_number", text="شماره قرارداد", anchor="e")
    tree.heading("date", text="تاریخ پیش‌پرداخت", anchor="e")
    tree.heading("amount", text="مبلغ (ریال)", anchor="e")
    tree.heading("bank", text="بانک عامل", anchor="e")
    tree.heading("description", text="توضیحات", anchor="e")
    tree.column("id", width=50, anchor="e")
    tree.column("contract_number", width=100, anchor="e")
    tree.column("date", width=100, anchor="e")
    tree.column("amount", width=120, anchor="e")
    tree.column("bank", width=100, anchor="e")
    tree.column("description", width=200, anchor="e")
    tree.pack(fill="both", expand=True)

    def update_table():
        logging.info("به‌روزرسانی جدول پیش‌پرداخت‌ها")
        for item in tree.get_children():
            tree.delete(item)
        prepayments = database.get_prepayments()
        for prepayment in prepayments:
            tree.insert("", "end", values=(
                prepayment[0], prepayment[1], prepayment[2], format_amount(prepayment[3]), 
                prepayment[5], prepayment[4] or ""
            ))

    def open_prepayment_window(mode="new", prepayment_id=None):
        logging.info(f"باز کردن پنجره پیش‌پرداخت - mode: {mode}, prepayment_id: {prepayment_id}")
        
        contracts = db_contracts.get_contracts()
        if not contracts:
            messagebox.showwarning("خطا", "هیچ قراردادی ثبت نشده! اول یه قرارداد ثبت کن.")
            return

        window = tk.Toplevel(master)
        window.title("پیش‌پرداخت جدید" if mode == "new" else "ویرایش پیش‌پرداخت")
        center_window(window, 500, 500)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#00A86B" if mode == "new" else "#EC8B5E", height=40)
        header.pack(fill="x")
        tk.Label(header, text="ثبت پیش‌پرداخت جدید" if mode == "new" else "ویرایش پیش‌پرداخت", 
                 font=("IranNastaliq", 20), fg="white", bg="#00A86B" if mode == "new" else "#EC8B5E").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # فرم
        form_frame = tk.LabelFrame(content, text="جزئیات پیش‌پرداخت", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        form_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        contract_numbers = [contract[1] for contract in contracts]
        contract_ids = {contract[1]: contract[0] for contract in contracts}
        contract_prepayments = {contract[1]: contract[7] for contract in contracts}
        banks = ["ملی", "ملت", "صادرات", "سپه", "تجارت", "پارسیان", "سامان", "پاسارگاد", "اقتصاد نوین", "رفاه", "مسکن"]

        prepayment_limit_label = tk.Label(form_frame, text="حد مجاز پیش‌پرداخت: 0", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333")
        prepayment_limit_label.grid(row=0, column=0, columnspan=2, pady=5)

        entries = []
        tk.Label(form_frame, text="شماره قرارداد:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        contract_combo = ttk.Combobox(form_frame, values=contract_numbers, font=("IRANSans", 12), width=30, justify="right")
        contract_combo.grid(row=1, column=0, pady=5, padx=5)
        entries.append(contract_combo)

        tk.Label(form_frame, text="تاریخ پیش‌پرداخت:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        date_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        date_entry.grid(row=2, column=0, pady=5, padx=5)
        entries.append(date_entry)

        tk.Label(form_frame, text="مبلغ (ریال):", font=("IRANSans", 12), bg="#F5F6F5").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        amount_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right", validate="key", validatecommand=(master.register(validate_number_input), '%P'))
        amount_entry.grid(row=3, column=0, pady=5, padx=5)
        entries.append(amount_entry)

        tk.Label(form_frame, text="بانک عامل:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=4, column=1, pady=5, padx=5, sticky="e")
        bank_combo = ttk.Combobox(form_frame, values=banks, font=("IRANSans", 12), width=30, justify="right")
        bank_combo.set("ملی")
        bank_combo.grid(row=4, column=0, pady=5, padx=5)
        entries.append(bank_combo)

        tk.Label(form_frame, text="توضیحات:", font=("IRANSans", 12), bg="#F5F6F5").grid(row=5, column=1, pady=5, padx=5, sticky="e")
        description_entry = tk.Entry(form_frame, font=("IRANSans", 12), width=32, justify="right")
        description_entry.grid(row=5, column=0, pady=5, padx=5)
        entries.append(description_entry)

        def update_prepayment_limit(*args):
            contract_number = contract_combo.get()
            if contract_number in contract_prepayments:
                limit = contract_prepayments[contract_number]
                prepayment_limit_label.config(text=f"حد مجاز پیش‌پرداخت: {format_amount(limit)}")
            else:
                prepayment_limit_label.config(text="حد مجاز پیش‌پرداخت: 0")

        contract_combo.bind("<<ComboboxSelected>>", update_prepayment_limit)

        if mode == "new":
            amount_entry.insert(0, "0")
            amount_entry.bind("<FocusIn>", lambda e: amount_entry.delete(0, tk.END) if amount_entry.get() == "0" else None)

        if mode == "edit" and prepayment_id:
            prepayment = database.get_prepayment_by_id(prepayment_id)
            if prepayment:
                contract = db_contracts.get_contract_by_id(prepayment[1])
                contract_combo.set(contract[1])
                date_entry.insert(0, prepayment[2])
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, str(prepayment[3]))
                bank_combo.set(prepayment[5] or "ملی")
                description_entry.insert(0, prepayment[4] or "")
                update_prepayment_limit()

        def save_prepayment():
            try:
                contract_number = contract_combo.get()
                prepayment_date = date_entry.get()
                prepayment_amount = amount_entry.get()
                bank = bank_combo.get()
                description = description_entry.get()

                if not all([contract_number, prepayment_date, prepayment_amount]):
                    messagebox.showwarning("خطا", "فیلدهای اجباری (شماره قرارداد، تاریخ، مبلغ) را پر کنید!")
                    return

                contract_id = contract_ids[contract_number]
                total_prepayments = database.get_total_prepayments_for_contract(contract_id)
                max_prepayment = int(str(contract_prepayments[contract_number]).replace(",", ""))
                new_amount = int(prepayment_amount.replace(",", "") or "0")
                new_total = total_prepayments + new_amount

                if mode == "edit" and prepayment_id:
                    old_amount = int(str(database.get_prepayment_by_id(prepayment_id)[3]).replace(",", ""))
                    new_total = total_prepayments - old_amount + new_amount

                if new_total > max_prepayment:
                    messagebox.showwarning("خطا", f"جمع پیش‌پرداخت‌ها ({format_amount(new_total)}) نمی‌تواند بیشتر از مبلغ پیش‌پرداخت قرارداد ({format_amount(max_prepayment)}) باشد!")
                    return

                if mode == "new":
                    database.add_prepayment(contract_id, prepayment_date, prepayment_amount, description, bank)
                    logging.info(f"پیش‌پرداخت جدید برای قرارداد {contract_number} ثبت شد")
                    messagebox.showinfo("موفقیت", "پیش‌پرداخت ثبت شد!")
                elif mode == "edit" and prepayment_id:
                    database.update_prepayment(prepayment_id, contract_id, prepayment_date, prepayment_amount, description, bank)
                    logging.info(f"پیش‌پرداخت با شناسه {prepayment_id} ویرایش شد")
                    messagebox.showinfo("موفقیت", "پیش‌پرداخت ویرایش شد!")
                
                update_table()
                window.destroy()
            except Exception as e:
                logging.error(f"خطا در ذخیره پیش‌پرداخت: {str(e)}")
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
        for icon, text, cmd in [("✔️", "تأیید", save_prepayment), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg=sidebar_color)
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg=sidebar_color, fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg=sidebar_color, hover_bg=hover_color, fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

    def edit_prepayment():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک پیش‌پرداخت انتخاب کنید!")
            return
        prepayment_id = tree.item(selected[0])["values"][0]
        open_prepayment_window(mode="edit", prepayment_id=prepayment_id)

    def delete_prepayment():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک پیش‌پرداخت انتخاب کنید!")
            return
        prepayment_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این پیش‌پرداخت را حذف کنید؟"):
            database.delete_prepayment(prepayment_id)
            update_table()
            messagebox.showinfo("موفقیت", "پیش‌پرداخت حذف شد!")

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    # دکمه‌های سایدبار اصلی
    buttons = [
        ("📝", "ثبت جدید", lambda: open_prepayment_window(mode="new")),
        ("✏️", "ویرایش", edit_prepayment),
        ("🗑️", "حذف", delete_prepayment),
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
    root.title("مدیریت پیش‌پرداخت‌ها")
    center_window(root, 900, 700)
    show_prepayments(root, lambda: None)
    root.mainloop()