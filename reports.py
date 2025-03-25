import tkinter as tk
from tkinter import ttk, messagebox
import database
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

logging.basicConfig(filename="reports_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

def format_amount(amount):
    try:
        return "{:,}".format(int(str(amount).replace(",", "")))
    except (ValueError, TypeError):
        return amount if amount else ""

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_reports(frame):
    logging.info("ورود به show_reports")
    main_frame = tk.Frame(frame, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(main_frame, text="گزارشات", font=("Arial", 18, "bold"), bg="white", fg="#000080").pack(pady=10)

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)

    # تب گزارش کلی
    general_frame = tk.Frame(notebook, bg="white")
    notebook.add(general_frame, text="گزارش کلی")

    general_tree = ttk.Treeview(general_frame, columns=("id", "full_name", "national_code", "contract_id", "net_salary", "performance"), show="headings")
    general_tree.heading("id", text="شناسه")
    general_tree.heading("full_name", text="نام و نام خانوادگی")
    general_tree.heading("national_code", text="کد ملی")
    general_tree.heading("contract_id", text="شناسه قرارداد")
    general_tree.heading("net_salary", text="حقوق خالص (ریال)")
    general_tree.heading("performance", text="حسن انجام کار (ریال)")
    general_tree.column("id", width=50, anchor="center")
    general_tree.column("full_name", width=150, anchor="center")
    general_tree.column("national_code", width=100, anchor="center")
    general_tree.column("contract_id", width=100, anchor="center")
    general_tree.column("net_salary", width=120, anchor="e")
    general_tree.column("performance", width=120, anchor="e")
    general_tree.pack(fill="both", expand=True, pady=5)

    def update_general_table():
        logging.info("به‌روزرسانی جدول گزارش کلی")
        for item in general_tree.get_children():
            general_tree.delete(item)
        employees = database.get_employees()
        for emp in employees:
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
            general_tree.insert("", "end", values=(emp[0], f"{emp[1]} {emp[2]}", emp[5], emp[18], format_amount(net_salary), format_amount(performance_amount)))

    # تب گزارش قرارداد
    contract_frame = tk.Frame(notebook, bg="white")
    notebook.add(contract_frame, text="گزارش قرارداد")

    contract_tree = ttk.Treeview(contract_frame, columns=("id", "contract_number", "total_amount", "prepayment_amount"), show="headings")
    contract_tree.heading("id", text="شناسه")
    contract_tree.heading("contract_number", text="شماره قرارداد")
    contract_tree.heading("total_amount", text="مبلغ کل (ریال)")
    contract_tree.heading("prepayment_amount", text="پیش‌پرداخت (ریال)")
    contract_tree.column("id", width=50, anchor="center")
    contract_tree.column("contract_number", width=150, anchor="center")
    contract_tree.column("total_amount", width=120, anchor="e")
    contract_tree.column("prepayment_amount", width=120, anchor="e")
    contract_tree.pack(fill="both", expand=True, pady=5)

    def update_contract_table():
        logging.info("به‌روزرسانی جدول گزارش قرارداد")
        for item in contract_tree.get_children():
            contract_tree.delete(item)
        contracts = database.get_contracts()
        for contract in contracts:
            contract_tree.insert("", "end", values=(contract[0], contract[1], format_amount(contract[5]), format_amount(contract[7])))

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(fill="x", pady=10)

    def export_general_report():
        employees = database.get_employees()
        c = canvas.Canvas("general_report.pdf", pagesize=A4)
        c.setFont("Helvetica", 12)
        y = 800
        c.drawString(100, y, "گزارش کلی کارکنان")
        y -= 30
        for emp in employees:
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
            c.drawString(100, y, f"{emp[1]} {emp[2]} - حقوق خالص: {format_amount(net_salary)} - حسن انجام کار: {format_amount(performance_amount)}")
            y -= 30
            if y < 50:
                c.showPage()
                y = 800
        c.save()
        messagebox.showinfo("موفقیت", "گزارش کلی در general_report.pdf ذخیره شد!")

    def export_contract_report():
        contracts = database.get_contracts()
        c = canvas.Canvas("contract_report.pdf", pagesize=A4)
        c.setFont("Helvetica", 12)
        y = 800
        c.drawString(100, y, "گزارش قراردادها")
        y -= 30
        for contract in contracts:
            c.drawString(100, y, f"{contract[1]} - مبلغ کل: {format_amount(contract[5])} - پیش‌پرداخت: {format_amount(contract[7])}")
            y -= 30
            if y < 50:
                c.showPage()
                y = 800
        c.save()
        messagebox.showinfo("موفقیت", "گزارش قرارداد در contract_report.pdf ذخیره شد!")

    tk.Button(button_frame, text="صدور گزارش کلی", command=export_general_report, font=("Arial", 12), bg="#87CEEB", fg="#000080").pack(side="right", padx=5)
    tk.Button(button_frame, text="صدور گزارش قرارداد", command=export_contract_report, font=("Arial", 12), bg="#87CEEB", fg="#000080").pack(side="right", padx=5)

    update_general_table()
    update_contract_table()