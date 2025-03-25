import tkinter as tk
from tkinter import ttk, messagebox
import logging
from config import COLORS, FONTS
import db_contracts as database

logging.basicConfig(filename="contract_log.log", level=logging.DEBUG, 
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

def show_contracts(master, enable_main_callback):
    logging.info("ورود به show_contracts")
    
    contract_frame = tk.Frame(master, bg=COLORS["background"])
    contract_frame.pack(fill="both", expand=True)

    header = tk.Frame(contract_frame, bg=COLORS["contract_color"], height=50)
    header.pack(fill="x")
    tk.Label(header, text="بخش قراردادها", font=FONTS["subtitle"], fg="white", bg=COLORS["contract_color"]).pack(side="right", padx=10)

    sidebar = tk.Frame(contract_frame, bg=COLORS["contract_color"], width=150)
    sidebar.pack(side="right", fill="y")

    content = tk.Frame(contract_frame, bg=COLORS["background"])
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True)

    tk.Label(table_frame, text="لیست قراردادها", font=("IRANSans", 14, "bold"), bg="white", fg=COLORS["text"]).pack(anchor="e", pady=5)

    columns = ("number", "date", "subject", "party", "total_amount", "prepayment")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
    tree.heading("number", text="شماره قرارداد", anchor="e")
    tree.heading("date", text="تاریخ", anchor="e")
    tree.heading("subject", text="موضوع", anchor="e")
    tree.heading("party", text="طرف قرارداد", anchor="e")
    tree.heading("total_amount", text="مبلغ کل (ریال)", anchor="e")
    tree.heading("prepayment", text="پیش‌پرداخت", anchor="e")
    tree.column("number", width=100, anchor="e")
    tree.column("date", width=100, anchor="e")
    tree.column("subject", width=150, anchor="e")
    tree.column("party", width=150, anchor="e")
    tree.column("total_amount", width=120, anchor="e")
    tree.column("prepayment", width=120, anchor="e")
    tree["displaycolumns"] = ("prepayment", "total_amount", "party", "subject", "date", "number")
    tree.pack(fill="both", expand=True)

    def update_table():
        logging.info("به‌روزرسانی جدول")
        for item in tree.get_children():
            tree.delete(item)
        try:
            contracts = database.get_contracts()
            if not contracts:
                logging.warning("هیچ داده‌ای دریافت نشد!")
                messagebox.showinfo("هشدار", "هیچ قراردادی موجود نیست.")
            for contract in contracts:
                prepayment = f"{format_amount(contract[7])} ({contract[6]}%)"
                tree.insert("", "end", values=(
                    contract[1], contract[2], contract[3], contract[4], format_amount(contract[5]), prepayment
                ))
        except Exception as e:
            logging.error(f"خطا در به‌روزرسانی جدول: {str(e)}")
            messagebox.showerror("خطا", f"مشکل در بارگذاری داده‌ها: {str(e)}")

    def open_contract_window():
        window = tk.Toplevel(master)
        window.title("ثبت قرارداد جدید")
        center_window(window, 850, 650)
        window.configure(bg="#F5F6F5")  # پس‌زمینه مدرن

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#00A86B", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#00A86B", height=25, bd=1, relief="raised")
        header.pack(fill="x")
        tk.Label(header, text="قرارداد جدید", font=("IRANSans", 14, "bold"), fg="white", bg="#00A86B").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # اطلاعات قرارداد
        info_frame = tk.LabelFrame(content, text="اطلاعات قرارداد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        info_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        fields = [
            ("شماره قرارداد", ""),
            ("تاریخ (YYYY/MM/DD)", ""),
            ("موضوع", ""),
            ("طرف قرارداد", ""),
            ("مبلغ کل (ریال)", ""),
            ("درصد پیش‌پرداخت", ""),
            ("مبلغ پیش‌پرداخت", ""),
        ]
        entries = {}
        for i, (label_text, default) in enumerate(fields):
            tk.Label(info_frame, text=label_text, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry = tk.Entry(info_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
            entry.insert(0, default)
            entry.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entries[label_text] = entry

        # محاسبه خودکار پیش‌پرداخت
        def calculate_prepayment(*args):
            try:
                total = int(entries["مبلغ کل (ریال)"].get().replace(",", ""))
                percent = float(entries["درصد پیش‌پرداخت"].get())
                prepayment = total * (percent / 100)
                entries["مبلغ پیش‌پرداخت"].delete(0, tk.END)
                entries["مبلغ پیش‌پرداخت"].insert(0, format_amount(int(prepayment)))
            except (ValueError, ZeroDivisionError):
                entries["مبلغ پیش‌پرداخت"].delete(0, tk.END)

        entries["مبلغ کل (ریال)"].bind("<KeyRelease>", calculate_prepayment)
        entries["درصد پیش‌پرداخت"].bind("<KeyRelease>", calculate_prepayment)

        # جزئیات قرارداد
        detail_frame = tk.LabelFrame(content, text="جزئیات قرارداد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        detail_frame.pack(fill="both", expand=True, padx=(0, 10))

        detail_tree = ttk.Treeview(detail_frame, columns=("desc", "qty", "unit", "amount"), show="headings", height=6)
        detail_tree.heading("desc", text="شرح خدمات", anchor="e")
        detail_tree.heading("qty", text="مقدار", anchor="e")
        detail_tree.heading("unit", text="واحد", anchor="e")
        detail_tree.heading("amount", text="مبلغ", anchor="e")
        detail_tree.column("desc", width=320, anchor="e")
        detail_tree.column("qty", width=70, anchor="e")
        detail_tree.column("unit", width=90, anchor="e")
        detail_tree.column("amount", width=90, anchor="e")
        detail_tree["displaycolumns"] = ("amount", "unit", "qty", "desc")
        detail_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # فرم اضافه کردن شرح خدمات
        add_frame = tk.Frame(detail_frame, bg="#F5F6F5")
        add_frame.pack(fill="x", pady=5)

        detail_entries = {
            "شرح خدمات": tk.Entry(add_frame, width=60, font=("IRANSans", 12), bd=1, relief="solid"),
            "مقدار": tk.Entry(add_frame, width=10, font=("IRANSans", 12), bd=1, relief="solid"),
            "واحد": ttk.Combobox(add_frame, values=["متر", "مترمربع", "عدد", "پارسل", "هکتار"], width=10, font=("IRANSans", 12)),
            "مبلغ": tk.Entry(add_frame, width=15, font=("IRANSans", 12), bd=1, relief="solid")
        }
        for i, (label, widget) in enumerate(detail_entries.items()):
            tk.Label(add_frame, text=label, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=5, pady=5, sticky="e")
            widget.grid(row=i, column=0, padx=5, pady=5, sticky="w")

        def add_detail():
            desc = detail_entries["شرح خدمات"].get()
            qty = detail_entries["مقدار"].get()
            unit = detail_entries["واحد"].get()
            amount = detail_entries["مبلغ"].get()
            if desc and qty and unit:
                detail_tree.insert("", "end", values=(desc, qty, unit, format_amount(amount) if amount else "0"))
                for entry in detail_entries.values():
                    entry.delete(0, tk.END)

        tk.Button(add_frame, text="اضافه کردن شرح خدمات", font=("IRANSans", 10), bg="#00A86B", fg="white", command=add_detail, relief="flat", bd=0).grid(row=4, column=0, columnspan=2, pady=5)

        # ویرایش شرح خدمات با دابل‌کلیک
        def edit_detail(event):
            selected = detail_tree.selection()
            if not selected:
                return
            item = detail_tree.item(selected[0])["values"]
            popup = tk.Toplevel(window)
            popup.title("ویرایش شرح خدمات")
            center_window(popup, 550, 300)
            popup.configure(bg="#F5F6F5", bd=2, relief="solid", highlightbackground="#00A86B", highlightthickness=2)

            edit_entries = {
                "شرح خدمات": tk.Entry(popup, width=60, font=("IRANSans", 12), bd=1, relief="solid"),
                "مقدار": tk.Entry(popup, width=10, font=("IRANSans", 12), bd=1, relief="solid"),
                "واحد": ttk.Combobox(popup, values=["متر", "مترمربع", "عدد", "پارسل", "هکتار"], width=10, font=("IRANSans", 12)),
                "مبلغ": tk.Entry(popup, width=15, font=("IRANSans", 12), bd=1, relief="solid")
            }
            for i, (label, widget) in enumerate(edit_entries.items()):
                tk.Label(popup, text=label, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=10, pady=8, sticky="e")
                widget.grid(row=i, column=0, padx=10, pady=8, sticky="w")
                widget.insert(0, item[i])

            def save_edit():
                desc = edit_entries["شرح خدمات"].get()
                qty = edit_entries["مقدار"].get()
                unit = edit_entries["واحد"].get()
                amount = edit_entries["مبلغ"].get()
                if desc and qty and unit:
                    detail_tree.item(selected[0], values=(desc, qty, unit, format_amount(amount) if amount else "0"))
                    popup.destroy()

            tk.Button(popup, text="ذخیره", font=("IRANSans", 10), bg="#00A86B", fg="white", width=12, height=1, command=save_edit, relief="flat", bd=0).grid(row=4, column=0, columnspan=2, pady=10)

        detail_tree.bind("<Double-1>", edit_detail)

        # دکمه‌های سایدبار
        def save_contract():
            try:
                contract_number = entries["شماره قرارداد"].get()
                contract_date = entries["تاریخ (YYYY/MM/DD)"].get()
                contract_subject = entries["موضوع"].get()
                contract_party = entries["طرف قرارداد"].get()
                total_amount = int(entries["مبلغ کل (ریال)"].get().replace(",", ""))
                prepayment_percent = float(entries["درصد پیش‌پرداخت"].get())
                prepayment_amount = int(entries["مبلغ پیش‌پرداخت"].get().replace(",", ""))

                contract_id = database.add_contract(contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount)
                
                for item in detail_tree.get_children():
                    desc, qty, unit, amount = detail_tree.item(item)["values"]
                    amount = int(amount.replace(",", "")) if amount else 0
                    database.add_contract_detail(contract_id, desc, qty, unit, amount)

                messagebox.showinfo("موفقیت", "قرارداد با موفقیت ثبت شد!", font=("IRANSans", 12))
                window.destroy()
                update_table()
            except ValueError as e:
                messagebox.showerror("خطا", "لطفاً مقادیر عددی را درست وارد کنید!", font=("IRANSans", 12))
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ثبت قرارداد: {str(e)}", font=("IRANSans", 12))

        def cancel():
            window.destroy()

        y_pos = 20
        for icon, text, cmd in [("✔️", "تأیید", save_contract), ("❌", "انصراف", cancel)]:
            btn_frame = tk.Frame(btn_sidebar, bg="#00A86B")
            btn_frame.place(x=0, y=y_pos, width=113, height=50)
            tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#00A86B", fg="white").pack(side="right", padx=5)
            btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#00A86B", hover_bg="#008F5A", fg="white", hover_fg="white", anchor="e", command=cmd)
            btn.pack(side="right", fill="x", expand=True)
            y_pos += 60

        # باندینگ Enter
        for entry in entries.values():
            entry.bind("<Return>", lambda e: save_contract())
        detail_entries["مبلغ"].bind("<Return>", lambda e: add_detail())

    def edit_contract():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک قرارداد انتخاب کنید!", font=("IRANSans", 12))
            return
        
        item = tree.item(selected[0])["values"]
        contract_number = item[0]
        contract_id = database.get_contract_id_by_number(contract_number)
        contract = database.get_contract_by_id(contract_id)
        details = database.get_contract_details(contract_id) or [("", "", "", "", 0)]

        window = tk.Toplevel(master)
        window.title("ویرایش قرارداد")
        center_window(window, 850, 650)
        window.configure(bg="#F5F6F5")

        # سایدبار
        btn_sidebar = tk.Frame(window, bg="#EC8B5E", width=113)
        btn_sidebar.pack(side="right", fill="y")

        # هدر
        header = tk.Frame(window, bg="#EC8B5E", height=25, bd=1, relief="raised")
        header.pack(fill="x")
        tk.Label(header, text="ویرایش قرارداد", font=("IRANSans", 14, "bold"), fg="white", bg="#EC8B5E").pack(side="right", padx=10)

        # محتوا
        content = tk.Frame(window, bg="#F5F6F5")
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # اطلاعات قرارداد
        info_frame = tk.LabelFrame(content, text="اطلاعات قرارداد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        info_frame.pack(fill="x", padx=(0, 10), pady=(0, 10))

        fields = [
            ("شماره قرارداد", contract[1]),
            ("تاریخ (YYYY/MM/DD)", contract[2]),
            ("موضوع", contract[3]),
            ("طرف قرارداد", contract[4]),
            ("مبلغ کل (ریال)", str(contract[5])),
            ("درصد پیش‌پرداخت", str(contract[6])),
            ("مبلغ پیش‌پرداخت", str(contract[7])),
        ]
        entries = {}
        for i, (label_text, value) in enumerate(fields):
            tk.Label(info_frame, text=label_text, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry = tk.Entry(info_frame, font=("IRANSans", 12), width=30, bd=1, relief="solid")
            entry.insert(0, value)
            entry.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entries[label_text] = entry

        # محاسبه خودکار پیش‌پرداخت
        def calculate_prepayment(*args):
            try:
                total = int(entries["مبلغ کل (ریال)"].get().replace(",", ""))
                percent = float(entries["درصد پیش‌پرداخت"].get())
                prepayment = total * (percent / 100)
                entries["مبلغ پیش‌پرداخت"].delete(0, tk.END)
                entries["مبلغ پیش‌پرداخت"].insert(0, format_amount(int(prepayment)))
            except (ValueError, ZeroDivisionError):
                entries["مبلغ پیش‌پرداخت"].delete(0, tk.END)

        entries["مبلغ کل (ریال)"].bind("<KeyRelease>", calculate_prepayment)
        entries["درصد پیش‌پرداخت"].bind("<KeyRelease>", calculate_prepayment)

        # جزئیات قرارداد
        detail_frame = tk.LabelFrame(content, text="جزئیات قرارداد", font=("IRANSans", 12, "bold"), bg="#F5F6F5", fg="#333333", bd=2, relief="groove")
        detail_frame.pack(fill="both", expand=True, padx=(0, 10))

        detail_tree = ttk.Treeview(detail_frame, columns=("desc", "qty", "unit", "amount"), show="headings", height=6)
        detail_tree.heading("desc", text="شرح خدمات", anchor="e")
        detail_tree.heading("qty", text="مقدار", anchor="e")
        detail_tree.heading("unit", text="واحد", anchor="e")
        detail_tree.heading("amount", text="مبلغ", anchor="e")
        detail_tree.column("desc", width=320, anchor="e")
        detail_tree.column("qty", width=70, anchor="e")
        detail_tree.column("unit", width=90, anchor="e")
        detail_tree.column("amount", width=90, anchor="e")
        detail_tree["displaycolumns"] = ("amount", "unit", "qty", "desc")
        detail_tree.pack(fill="both", expand=True, padx=5, pady=5)

        for detail in details:
            detail_tree.insert("", "end", values=(detail[2], detail[3], detail[4], format_amount(detail[5])))

        # فرم اضافه کردن شرح خدمات
        add_frame = tk.Frame(detail_frame, bg="#F5F6F5")
        add_frame.pack(fill="x", pady=5)

        detail_entries = {
            "شرح خدمات": tk.Entry(add_frame, width=60, font=("IRANSans", 12), bd=1, relief="solid"),
            "مقدار": tk.Entry(add_frame, width=10, font=("IRANSans", 12), bd=1, relief="solid"),
            "واحد": ttk.Combobox(add_frame, values=["متر", "مترمربع", "عدد", "پارسل", "هکتار"], width=10, font=("IRANSans", 12)),
            "مبلغ": tk.Entry(add_frame, width=15, font=("IRANSans", 12), bd=1, relief="solid")
        }
        for i, (label, widget) in enumerate(detail_entries.items()):
            tk.Label(add_frame, text=label, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=5, pady=5, sticky="e")
            widget.grid(row=i, column=0, padx=5, pady=5, sticky="w")

        def add_detail():
            desc = detail_entries["شرح خدمات"].get()
            qty = detail_entries["مقدار"].get()
            unit = detail_entries["واحد"].get()
            amount = detail_entries["مبلغ"].get()
            if desc and qty and unit:
                detail_tree.insert("", "end", values=(desc, qty, unit, format_amount(amount) if amount else "0"))
                for entry in detail_entries.values():
                    entry.delete(0, tk.END)

        tk.Button(add_frame, text="اضافه کردن شرح خدمات", font=("IRANSans", 10), bg="#EC8B5E", fg="white", command=add_detail, relief="flat", bd=0).grid(row=4, column=0, columnspan=2, pady=5)

        # ویرایش شرح خدمات با دابل‌کلیک
        def edit_detail(event):
            selected = detail_tree.selection()
            if not selected:
                return
            item = detail_tree.item(selected[0])["values"]
            popup = tk.Toplevel(window)
            popup.title("ویرایش شرح خدمات")
            center_window(popup, 550, 300)
            popup.configure(bg="#F5F6F5", bd=2, relief="solid", highlightbackground="#EC8B5E", highlightthickness=2)

            edit_entries = {
                "شرح خدمات": tk.Entry(popup, width=60, font=("IRANSans", 12), bd=1, relief="solid"),
                "مقدار": tk.Entry(popup, width=10, font=("IRANSans", 12), bd=1, relief="solid"),
                "واحد": ttk.Combobox(popup, values=["متر", "مترمربع", "عدد", "پارسل", "هکتار"], width=10, font=("IRANSans", 12)),
                "مبلغ": tk.Entry(popup, width=15, font=("IRANSans", 12), bd=1, relief="solid")
            }
            for i, (label, widget) in enumerate(edit_entries.items()):
                tk.Label(popup, text=label, font=("IRANSans", 12), bg="#F5F6F5", fg="#333333").grid(row=i, column=1, padx=10, pady=8, sticky="e")
                widget.grid(row=i, column=0, padx=10, pady=8, sticky="w")
                widget.insert(0, item[i])

            def save_edit():
                desc = edit_entries["شرح خدمات"].get()
                qty = edit_entries["مقدار"].get()
                unit = edit_entries["واحد"].get()
                amount = edit_entries["مبلغ"].get()
                if desc and qty and unit:
                    detail_tree.item(selected[0], values=(desc, qty, unit, format_amount(amount) if amount else "0"))
                    popup.destroy()

            tk.Button(popup, text="ذخیره", font=("IRANSans", 10), bg="#EC8B5E", fg="white", width=12, height=1, command=save_edit, relief="flat", bd=0).grid(row=4, column=0, columnspan=2, pady=10)

        detail_tree.bind("<Double-1>", edit_detail)

        # دکمه‌های سایدبار
        def save_edit():
            try:
                contract_number = entries["شماره قرارداد"].get()
                contract_date = entries["تاریخ (YYYY/MM/DD)"].get()
                contract_subject = entries["موضوع"].get()
                contract_party = entries["طرف قرارداد"].get()
                total_amount = int(entries["مبلغ کل (ریال)"].get().replace(",", ""))
                prepayment_percent = float(entries["درصد پیش‌پرداخت"].get())
                prepayment_amount = int(entries["مبلغ پیش‌پرداخت"].get().replace(",", ""))

                database.update_contract(contract_id, contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount)
                database.delete_contract_details(contract_id)
                
                for item in detail_tree.get_children():
                    desc, qty, unit, amount = detail_tree.item(item)["values"]
                    amount = int(amount.replace(",", "")) if amount else 0
                    database.add_contract_detail(contract_id, desc, qty, unit, amount)

                messagebox.showinfo("موفقیت", "قرارداد با موفقیت ویرایش شد!", font=("IRANSans", 12))
                window.destroy()
                update_table()
            except ValueError as e:
                messagebox.showerror("خطا", "لطفاً مقادیر عددی را درست وارد کنید!", font=("IRANSans", 12))
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ویرایش قرارداد: {str(e)}", font=("IRANSans", 12))

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

        # باندینگ Enter
        for entry in entries.values():
            entry.bind("<Return>", lambda e: save_edit())
        detail_entries["مبلغ"].bind("<Return>", lambda e: add_detail())

    def delete_contract():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("خطا", "یک قرارداد انتخاب کنید!", font=("IRANSans", 12))
            return
        
        item = tree.item(selected[0])["values"]
        contract_number = item[0]
        contract_id = database.get_contract_id_by_number(contract_number)

        if messagebox.askyesno("تأیید حذف", f"آیا مطمئن هستید که می‌خواهید قرارداد {contract_number} را حذف کنید؟", font=("IRANSans", 12)):
            try:
                database.delete_contract(contract_id)
                messagebox.showinfo("موفقیت", "قرارداد با موفقیت حذف شد!", font=("IRANSans", 12))
                update_table()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف قرارداد: {str(e)}", font=("IRANSans", 12))

    def exit_section():
        for widget in master.winfo_children():
            widget.destroy()
        enable_main_callback()
        master.master.show_section("home")

    buttons = [
        ("📝", "ثبت جدید", open_contract_window),
        ("✏️", "ویرایش", edit_contract),
        ("🗑️", "حذف", delete_contract),
        ("🚪", "خروج", exit_section)
    ]
    y_position = 20
    for icon, text, cmd in buttons:
        btn_frame = tk.Frame(sidebar, bg=COLORS["contract_color"])
        btn_frame.place(x=0, y=y_position, width=150, height=60)
        tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 20), bg=COLORS["contract_color"], fg="white").pack(side="right", padx=15)
        btn = HoverButton(btn_frame, text=text, font=("IRANSans", 12), bg=COLORS["contract_color"], hover_bg=COLORS["accent"], fg="white", hover_fg="white", anchor="e", command=cmd)
        btn.pack(side="right", fill="x", expand=True)
        y_position += 70

    update_table()
    logging.info("خروج از show_contracts")

if __name__ == "__main__":
    root = tk.Tk()
    show_contracts(root, lambda: None)
    root.mainloop()