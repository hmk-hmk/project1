import tkinter as tk
from tkinter import ttk, messagebox
from database import SecureDatabase, DatabaseError
import json

class EmployeeSystem(tk.Frame):
    def __init__(self, master, encryption_key):
        super().__init__(master)
        self.db = SecureDatabase(encryption_key)
        self.create_ui()
        
    def create_ui(self):
        # فرم ثبت
        form_frame = ttk.LabelFrame(self, text="فرم ثبت کارمند جدید")
        form_frame.pack(padx=20, pady=20, fill="x")
        
        self.entries = {}
        fields = [
            ("نام کامل", "name"),
            ("کدملی", "national_id"),
            ("سمت", "position"),
            ("حقوق پایه (ریال)", "salary"),
            ("تاریخ استخدام", "hire_date")
        ]
        
        for text, key in fields:
            row = ttk.Frame(form_frame)
            row.pack(fill="x", pady=5)
            
            ttk.Label(row, text=text + ":", width=20).pack(side="right")
            entry = ttk.Entry(row)
            entry.pack(side="right", expand=True, fill="x")
            self.entries[key] = entry
        
        # دکمه‌ها
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="ثبت اطلاعات",
            command=self.submit_employee
        ).pack(side="right", padx=5)
        
        # جدول
        self.create_employee_table()

    def create_employee_table(self):
        columns = ("ID", "نام", "کدملی", "سمت", "حقوق", "تاریخ استخدام")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            employees = self.db.get_employees()
            for emp in employees:
                data = json.loads(emp['data'])
                self.tree.insert("", "end", values=(
                    emp['id'],
                    data.get('name'),
                    data.get('national_id'),
                    data.get('position'),
                    f"{data.get('salary', 0):,}",
                    data.get('hire_date')
                ))
        except DatabaseError as e:
            messagebox.showerror("خطا", str(e))

    def submit_employee(self):
        try:
            data = {
                "name": self.entries['name'].get(),
                "national_id": self.entries['national_id'].get(),
                "position": self.entries['position'].get(),
                "salary": int(self.entries['salary'].get().replace(',', '')),
                "hire_date": self.entries['hire_date'].get()
            }
            
            if self.db.add_employee(data):
                messagebox.showinfo("موفقیت", "کارمند با موفقیت ثبت شد")
                self.load_data()
                self.clear_form()
            else:
                messagebox.showerror("خطا", "عملیات ثبت ناموفق بود")
                
        except ValueError:
            messagebox.showerror("خطا", "مقادیر وارد شده نامعتبر است")
        except DatabaseError as e:
            messagebox.showerror("خطای پایگاه داده", str(e))

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, 'end')