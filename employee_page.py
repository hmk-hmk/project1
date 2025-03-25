import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# دیتابیس موقت (دیکشنری)
employee_db = {}

# تابع فرمت کردن اعداد
def format_amount(amount):
    try:
        return "{:,}".format(int(str(amount).replace(",", "")))
    except (ValueError, TypeError):
        return amount if amount else "0"

# تابع مرکزی کردن پنجره
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# کلاس دکمه با هاور
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

# تابع محاسبه مانده‌ها
def calculate_balances(employee_data):
    total_work_value = sum(w['amount'] * r for w, r in zip(employee_data['work_history'], employee_data['rate_history']))
    performance_amount = total_work_value * (employee_data['performance_percent'] / 100)
    total_payment = sum(p['amount'] for p in employee_data['payment_history'])
    balance_with_performance = total_work_value - total_payment
    balance_without_performance = (total_work_value - performance_amount) - total_payment
    return balance_with_performance, balance_without_performance

# تابع صفحه کارمند
def show_employee_page(master, employee_id):
    # اگر کارمند جدیده، به دیتابیس اضافه کن
    if employee_id not in employee_db:
        employee_db[employee_id] = {
            "name": "علی احمدی",
            "national_code": "1234567890",
            "contract": "شهرداری اراک",
            "hire_date": "1403/10/01",
            "work_history": [{"date": "1403/10/01", "amount": 1000}],  # تاریخچه کارکرد
            "performance_percent": 10,
            "rate_history": [25000],  # تاریخچه نرخ‌ها
            "payment_history": [{"date": "1403/10/15", "amount": 20000000, "type": "علی‌الحساب"}]  # تاریخچه پرداخت‌ها
        }
    
    employee_data = employee_db[employee_id]
    
    window = tk.Toplevel(master)
    window.title(f"پرونده کارمند - {employee_data['name']}")
    center_window(window, 900, 700)
    window.configure(bg="white")

    # هدر
    header = tk.Frame(window, bg="#172A3A", height=50)
    header.pack(fill="x")
    tk.Label(header, text=f"پرونده کارمند: {employee_data['name']}", font=("IranNastaliq", 20), fg="white", bg="#172A3A").pack(side="right", padx=10)

    # سایدبار
    sidebar = tk.Frame(window, bg="#172A3A", width=150)
    sidebar.pack(side="right", fill="y")

    # بدنه اصلی
    content = tk.Frame(window, bg="white")
    content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    # اطلاعات اصلی
    info_frame = tk.LabelFrame(content, text="🧑 اطلاعات اصلی", font=("IRANSans", 14, "bold"), bg="white", fg="#172A3A", bd=1, relief="solid")
    info_frame.pack(fill="x", pady=(0, 20))
    tk.Label(info_frame, text=f"نام و نام خانوادگی: {employee_data['name']}", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(info_frame, text=f"کد ملی: {employee_data['national_code']}", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(info_frame, text=f"طرف قرارداد: {employee_data['contract']}", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(info_frame, text=f"تاریخ استخدام: {employee_data['hire_date']}", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")

    # کارکرد
    work_frame = tk.LabelFrame(content, text="📅 کارکرد", font=("IRANSans", 14, "bold"), bg="white", fg="#172A3A", bd=1, relief="solid")
    work_frame.pack(fill="x", pady=(0, 20))
    total_work = sum(w['amount'] for w in employee_data['work_history'])
    tk.Label(work_frame, text=f"جمع کارکرد قبلی: {total_work} واحد", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(work_frame, text="کارکرد جدید (واحد):", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    work_entry = tk.Entry(work_frame, font=("IRANSans", 12), width=30, justify="right", bg="#F5F6F5", fg="#333333", relief="flat", bd=1)
    work_entry.pack(anchor="e", padx=15, pady=5)
    tk.Label(work_frame, text="درصد حسن انجام کار:", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    performance_entry = tk.Entry(work_frame, font=("IRANSans", 12), width=30, justify="right", bg="#F5F6F5", fg="#333333", relief="flat", bd=1)
    performance_entry.pack(anchor="e", padx=15, pady=5)
    performance_entry.insert(0, str(employee_data['performance_percent']))

    # نرخ‌ها
    rate_frame = tk.LabelFrame(content, text="💰 نرخ‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#172A3A", bd=1, relief="solid")
    rate_frame.pack(fill="x", pady=(0, 20))
    current_rate = employee_data['rate_history'][-1]  # آخرین نرخ
    tk.Label(rate_frame, text=f"نرخ فعلی: {format_amount(current_rate)} تومان", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(rate_frame, text="تغییر نرخ (تومان):", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    new_rate_entry = tk.Entry(rate_frame, font=("IRANSans", 12), width=30, justify="right", bg="#F5F6F5", fg="#333333", relief="flat", bd=1)
    new_rate_entry.pack(anchor="e", padx=15, pady=5)
    tk.Label(rate_frame, text="تاریخ شروع نرخ جدید (YYYY/MM/DD):", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    rate_date_entry = tk.Entry(rate_frame, font=("IRANSans", 12), width=30, justify="right", bg="#F5F6F5", fg="#333333", relief="flat", bd=1)
    rate_date_entry.pack(anchor="e", padx=15, pady=5)
    previous_work = sum(w['amount'] for w in employee_data['work_history'][:-1]) if len(employee_data['work_history']) > 1 else 0
    tk.Label(rate_frame, text=f"مقدار قبلی با نرخ قدیم: {previous_work} واحد", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")

    # پرداخت‌ها
    payment_frame = tk.LabelFrame(content, text="💸 پرداخت‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#172A3A", bd=1, relief="solid")
    payment_frame.pack(fill="x", pady=(0, 20))
    total_payment = sum(p['amount'] for p in employee_data['payment_history'])
    tk.Label(payment_frame, text=f"جمع پرداختی‌ها: {format_amount(total_payment)} تومان", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(payment_frame, text="پرداخت جدید (تومان):", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    payment_entry = tk.Entry(payment_frame, font=("IRANSans", 12), width=30, justify="right", bg="#F5F6F5", fg="#333333", relief="flat", bd=1)
    payment_entry.pack(anchor="e", padx=15, pady=5)
    payment_type = tk.StringVar(value="علی‌الحساب")
    tk.Radiobutton(payment_frame, text="علی‌الحساب", variable=payment_type, value="علی‌الحساب", font=("IRANSans", 12), bg="white", fg="#333333", selectcolor="#D1D5DB").pack(anchor="e", padx=15, pady=5)
    tk.Radiobutton(payment_frame, text="تسویه", variable=payment_type, value="تسویه", font=("IRANSans", 12), bg="white", fg="#333333", selectcolor="#D1D5DB").pack(anchor="e", padx=15, pady=5)

    # مانده‌ها
    balance_frame = tk.LabelFrame(content, text="📊 مانده‌ها", font=("IRANSans", 14, "bold"), bg="white", fg="#172A3A", bd=1, relief="solid")
    balance_frame.pack(fill="x", pady=(0, 20))
    balance_with, balance_without = calculate_balances(employee_data)
    tk.Label(balance_frame, text=f"مانده با حسن انجام کار: {format_amount(balance_with)} تومان", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")
    tk.Label(balance_frame, text=f"مانده بدون حسن انجام کار: {format_amount(balance_without)} تومان", font=("IRANSans", 12), bg="white", fg="#333333").pack(anchor="e", padx=15, pady=5, fill="x")

    # دکمه‌های سایدبار
    def register_work():
        try:
            new_work = int(work_entry.get().replace(",", ""))
            new_performance = float(performance_entry.get())
            employee_data['work_history'].append({"date": datetime.now().strftime("%Y/%m/%d"), "amount": new_work})
            employee_data['performance_percent'] = new_performance
            messagebox.showinfo("ثبت", "کارکرد با موفقیت ثبت شد!")
            window.destroy()
            show_employee_page(master, employee_id)  # صفحه رو رفرش کن
        except ValueError:
            messagebox.showerror("خطا", "لطفاً مقادیر معتبر وارد کنید!")

    def update_rate():
        try:
            new_rate = int(new_rate_entry.get().replace(",", ""))
            rate_date = rate_date_entry.get()
            # چک کردن فرمت تاریخ
            datetime.strptime(rate_date, "%Y/%m/%d")
            employee_data['rate_history'].append(new_rate)
            messagebox.showinfo("ثبت", "نرخ جدید با موفقیت ثبت شد!")
            window.destroy()
            show_employee_page(master, employee_id)
        except ValueError:
            messagebox.showerror("خطا", "لطفاً نرخ معتبر و تاریخ به فرمت YYYY/MM/DD وارد کنید!")

    def register_payment():
        try:
            new_payment = int(payment_entry.get().replace(",", ""))
            payment_data = {"date": datetime.now().strftime("%Y/%m/%d"), "amount": new_payment, "type": payment_type.get()}
            employee_data['payment_history'].append(payment_data)
            messagebox.showinfo("ثبت", "پرداخت با موفقیت ثبت شد!")
            window.destroy()
            show_employee_page(master, employee_id)
        except ValueError:
            messagebox.showerror("خطا", "لطفاً مقدار معتبر وارد کنید!")

    def print_current_payslip():
        balance_with, balance_without = calculate_balances(employee_data)
        payslip = (
            f"فیش حقوق جاری - {employee_data['name']}\n"
            f"تاریخ: {datetime.now().strftime('%Y/%m/%d')}\n"
            f"جمع کارکرد: {sum(w['amount'] for w in employee_data['work_history'])} واحد\n"
            f"نرخ فعلی: {format_amount(employee_data['rate_history'][-1])} تومان\n"
            f"جمع پرداختی‌ها: {format_amount(sum(p['amount'] for p in employee_data['payment_history']))} تومان\n"
            f"مانده با حسن انجام کار: {format_amount(balance_with)} تومان\n"
            f"مانده بدون حسن انجام کار: {format_amount(balance_without)} تومان"
        )
        messagebox.showinfo("فیش حقوق جاری", payslip)

    def print_all_work():
        work_text = "\n".join([f"{w['date']}: {w['amount']} واحد" for w in employee_data['work_history']])
        messagebox.showinfo("کل کارکرد", f"تاریخچه کارکرد - {employee_data['name']}\n{work_text}")

    def print_all_payments():
        payment_text = "\n".join([f"{p['date']}: {format_amount(p['amount'])} تومان ({p['type']})" for p in employee_data['payment_history']])
        messagebox.showinfo("کل دریافتی‌ها", f"تاریخچه پرداخت‌ها - {employee_data['name']}\n{payment_text}")

    def exit_page():
        window.destroy()

    # دکمه‌ها
    buttons = [
        ("✏️", "ثبت کارکرد", lambda: [register_work(), update_rate()]),  # ثبت کارکرد و نرخ با هم
        ("📜", "چاپ فیش جاری", print_current_payslip),
        ("📋", "چاپ کل کارکرد", print_all_work),
        ("💸", "چاپ کل دریافتی‌ها", print_all_payments),
        ("🚪", "خروج", exit_page)
    ]
    y_position = 20
    for icon, text, cmd in buttons:
        btn_frame = tk.Frame(sidebar, bg="#172A3A")
        btn_frame.place(x=0, y=y_position, width=150, height=50)
        tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 16), bg="#172A3A", fg="white").pack(side="right", padx=5)
        btn = HoverButton(btn_frame, text=text, font=("IRANSans", 10), bg="#172A3A", hover_bg="#0F1F2A", fg="white", anchor="e", command=cmd)
        btn.pack(side="right", fill="x", expand=True)
        y_position += 60

    # دکمه جدا برای ثبت پرداخت
    payment_btn = tk.Button(payment_frame, text="ثبت پرداخت", font=("IRANSans", 10), bg="#172A3A", fg="white", relief="flat", command=register_payment)
    payment_btn.pack(anchor="e", padx=15, pady=5)

# تست نمونه
if __name__ == "__main__":
    root = tk.Tk()
    root.title("تست صفحه کارمند")
    center_window(root, 300, 200)
    tk.Button(root, text="باز کردن صفحه کارمند", font=("IRANSans", 12), command=lambda: show_employee_page(root, "emp1")).pack(pady=50)
    root.mainloop()