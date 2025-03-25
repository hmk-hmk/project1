import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
from tkcalendar import DateEntry
import webbrowser

class ProfessionalEmployeeManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("سامانه مدیریت پرسنل حرفه‌ای")
        self.style = ttk.Style()
        self.configure_styles()
        self.center_window(1200, 700)
        self.root.configure(bg="#f5f7fa")
        self.current_employee = None
        self.employees_data = self.load_data()
        
        # Initialize UI
        self.create_main_frame()
        self.create_sidebar()
        self.create_search_section()
        self.create_employee_table()
        
        # Test data (remove in production)
        if not self.employees_data:
            self.create_sample_data()

    def configure_styles(self):
        """Configure modern ttk styles"""
        self.style.theme_use('clam')
        
        # Configure colors
        self.style.configure('TFrame', background='#f5f7fa')
        self.style.configure('TLabel', background='#f5f7fa', font=('IRANSans', 10))
        self.style.configure('TButton', font=('IRANSans', 10), padding=6)
        self.style.configure('Header.TLabel', font=('IRANSans', 14, 'bold'), foreground='#2c3e50')
        self.style.configure('Secondary.TLabel', font=('IRANSans', 10), foreground='#7f8c8d')
        self.style.configure('Primary.TButton', foreground='white', background='#3498db')
        self.style.map('Primary.TButton',
                      background=[('active', '#2980b9'), ('pressed', '#1c6ca8')])
        self.style.configure('Success.TButton', foreground='white', background='#2ecc71')
        self.style.map('Success.TButton',
                      background=[('active', '#27ae60'), ('pressed', '#1e8449')])
        self.style.configure('Treeview', font=('IRANSans', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('IRANSans', 10, 'bold'))
        self.style.map('Treeview', background=[('selected', '#3498db')])

    def center_window(self, width, height):
        """Center the window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1000, 600)

    def create_main_frame(self):
        """Create the main container frame"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = ttk.Frame(self.main_frame, width=200, style='Primary.TFrame')
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Logo section
        logo_frame = ttk.Frame(sidebar)
        logo_frame.pack(pady=20)
        
        ttk.Label(logo_frame, text="مدیریت پرسنل", style='Header.TLabel').pack()
        ttk.Label(logo_frame, text="نسخه حرفه‌ای", style='Secondary.TLabel').pack()
        
        # Navigation buttons
        nav_buttons = [
            ("📊 داشبورد", self.show_dashboard),
            ("💰 حقوق و دستمزد", self.show_payroll),
            ("📊 گزارشات", self.show_reports),
            ("⚙️ تنظیمات", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(sidebar, text=text, style='Primary.TButton', 
                            command=command, width=20)
            btn.pack(pady=5, padx=10, ipady=8)
        
        # Separator
        ttk.Separator(sidebar).pack(fill=tk.X, pady=20)
        
        # System buttons
        ttk.Button(sidebar, text="🔄 به‌روزرسانی", style='Secondary.TButton').pack(pady=5)
        ttk.Button(sidebar, text="🆘 راهنما", style='Secondary.TButton', 
                  command=self.show_help).pack(pady=5)
        ttk.Button(sidebar, text="🚪 خروج", style='Secondary.TButton', 
                  command=self.root.quit).pack(pady=5)

    def create_search_section(self):
        """Create the search and filter section"""
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search entry
        search_label = ttk.Label(search_frame, text="جستجوی پرسنل:")
        search_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.RIGHT)
        search_entry.bind('<KeyRelease>', self.filter_employees)
        
        # Add employee button
        add_btn = ttk.Button(search_frame, text="➕ افزودن پرسنل جدید", 
                            style='Success.TButton', command=self.add_employee)
        add_btn.pack(side=tk.LEFT)
        
        # Filter options
        filter_frame = ttk.Frame(self.main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="فیلتر بر اساس:").pack(side=tk.RIGHT, padx=(10, 0))
        
        self.filter_var = tk.StringVar(value='all')
        filters = [('همه', 'all'), ('فعال', 'active'), ('غیرفعال', 'inactive')]
        
        for text, value in filters:
            rb = ttk.Radiobutton(filter_frame, text=text, value=value, 
                                variable=self.filter_var, command=self.filter_employees)
            rb.pack(side=tk.RIGHT, padx=5)

    def create_employee_table(self):
        """Create the employee data table"""
        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.employee_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'name', 'national_code', 'department', 'position', 'status', 'hire_date'),
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode='browse'
        )
        
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        
        scroll_y.config(command=self.employee_tree.yview)
        scroll_x.config(command=self.employee_tree.xview)
        
        # Configure columns
        self.employee_tree.heading('#0', text='#')
        self.employee_tree.column('#0', width=40, stretch=False)
        
        columns = {
            'id': {'text': 'کد پرسنلی', 'width': 80},
            'name': {'text': 'نام و نام خانوادگی', 'width': 150},
            'national_code': {'text': 'کد ملی', 'width': 100},
            'department': {'text': 'دپارتمان', 'width': 120},
            'position': {'text': 'سمت', 'width': 120},
            'status': {'text': 'وضعیت', 'width': 80},
            'hire_date': {'text': 'تاریخ استخدام', 'width': 100}
        }
        
        for col, config in columns.items():
            self.employee_tree.heading(col, text=config['text'])
            self.employee_tree.column(col, width=config['width'], anchor='center')
        
        # Bind double click event
        self.employee_tree.bind('<Double-1>', self.show_employee_details)
        
        # Populate table
        self.populate_employee_table()
        
        # Action buttons frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        actions = [
            ('👁️ مشاهده جزئیات', self.show_employee_details),
            ('✏️ ویرایش', self.edit_employee),
            ('🗑️ حذف', self.delete_employee),
            ('📊 کارکرد', self.show_work_records),
            ('💰 فیش حقوق', self.show_payslip)
        ]
        
        for text, cmd in actions:
            btn = ttk.Button(btn_frame, text=text, style='Primary.TButton', command=cmd)
            btn.pack(side=tk.RIGHT, padx=5)

    def populate_employee_table(self):
        """Populate the employee table with data"""
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
            
        for idx, emp in enumerate(self.employees_data.values(), start=1):
            status = "فعال" if emp.get('active', True) else "غیرفعال"
            self.employee_tree.insert(
                '', 'end', 
                values=(
                    emp['id'],
                    emp['name'],
                    emp['national_code'],
                    emp.get('department', ''),
                    emp.get('position', ''),
                    status,
                    emp.get('hire_date', '')
                ),
                tags=(status,)
            )
            
            # Color inactive employees differently
            if not emp.get('active', True):
                self.employee_tree.tag_configure('غیرفعال', foreground='#95a5a6')

    def filter_employees(self, event=None):
        """Filter employees based on search and filter criteria"""
        search_term = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        
        for item in self.employee_tree.get_children():
            values = self.employee_tree.item(item, 'values')
            name_match = search_term in values[1].lower()
            
            if filter_type == 'all':
                status_match = True
            elif filter_type == 'active':
                status_match = values[5] == 'فعال'
            else:
                status_match = values[5] == 'غیرفعال'
                
            self.employee_tree.item(item, open=name_match and status_match)

    def show_employee_details(self, event=None):
        """Show detailed employee information in a new window"""
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک پرسنل را انتخاب کنید")
            return
            
        emp_id = self.employee_tree.item(selected, 'values')[0]
        self.current_employee = self.employees_data.get(emp_id)
        
        if not self.current_employee:
            messagebox.showerror("خطا", "پرسنل انتخاب شده یافت نشد")
            return
            
        # Create details window
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"جزئیات پرسنل - {self.current_employee['name']}")
        detail_win.geometry("900x650")
        self.center_window_on_parent(detail_win, 900, 650)
        
        # Notebook for tabs
        notebook = ttk.Notebook(detail_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Personal Info Tab
        personal_frame = ttk.Frame(notebook)
        notebook.add(personal_frame, text="اطلاعات فردی")
        self.create_personal_info_tab(personal_frame)
        
        # Employment Tab
        employment_frame = ttk.Frame(notebook)
        notebook.add(employment_frame, text="اطلاعات شغلی")
        self.create_employment_tab(employment_frame)
        
        # Financial Tab
        financial_frame = ttk.Frame(notebook)
        notebook.add(financial_frame, text="اطلاعات مالی")
        self.create_financial_tab(financial_frame)
        
        # Documents Tab
        docs_frame = ttk.Frame(notebook)
        notebook.add(docs_frame, text="مستندات")
        self.create_documents_tab(docs_frame)

    def create_personal_info_tab(self, parent):
        """Create personal information tab"""
        fields = [
            ("نام و نام خانوادگی", "name"),
            ("کد ملی", "national_code"),
            ("تاریخ تولد", "birth_date"),
            ("جنسیت", "gender"),
            ("وضعیت تأهل", "marital_status"),
            ("تلفن همراه", "mobile"),
            ("آدرس", "address"),
            ("تحصیلات", "education"),
            ("رشته تحصیلی", "field_of_study")
        ]
        
        for i, (label, key) in enumerate(fields):
            row = i // 2
            col = i % 2
            
            frame = ttk.Frame(parent)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            ttk.Label(frame, text=f"{label}:").pack(side=tk.RIGHT)
            
            value = self.current_employee.get(key, '')
            ttk.Label(frame, text=value, font=('IRANSans', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Photo frame
        photo_frame = ttk.Frame(parent)
        photo_frame.grid(row=0, column=2, rowspan=5, padx=20, pady=10, sticky='ns')
        
        # Placeholder for photo
        photo_label = ttk.Label(photo_frame, text="تصویر پرسنل", 
                              style='Secondary.TLabel')
        photo_label.pack()
        
        # In a real app, you would load the actual employee photo
        ttk.Button(photo_frame, text="آپلود تصویر", 
                  command=self.upload_photo).pack(pady=10)

    def create_employment_tab(self, parent):
        """Create employment information tab"""
        fields = [
            ("کد پرسنلی", "id"),
            ("تاریخ استخدام", "hire_date"),
            ("دپارتمان", "department"),
            ("سمت", "position"),
            ("واحد", "unit"),
            ("نوع قرارداد", "contract_type"),
            ("مدت قرارداد", "contract_duration"),
            ("تاریخ پایان قرارداد", "contract_end_date"),
            ("وضعیت", "active")
        ]
        
        for i, (label, key) in enumerate(fields):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame, text=f"{label}:").pack(side=tk.RIGHT)
            
            value = self.current_employee.get(key, '')
            if key == 'active':
                value = "فعال" if value else "غیرفعال"
            ttk.Label(frame, text=value, font=('IRANSans', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Separator
        ttk.Separator(parent).pack(fill=tk.X, pady=10)
        
        # Work history
        ttk.Label(parent, text="سوابق شغلی:", style='Header.TLabel').pack(anchor='e', padx=10)
        
        history_frame = ttk.Frame(parent)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for work history
        columns = ('date', 'position', 'department', 'description')
        history_tree = ttk.Treeview(
            history_frame, 
            columns=columns,
            show='headings',
            height=5
        )
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=100)
        
        history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add sample data (replace with actual data in real app)
        sample_history = [
            ("1402/01/15", "برنامه‌نویس", "فناوری اطلاعات", "ارتقاء به برنامه‌نویس ارشد"),
            ("1401/03/01", "برنامه‌نویس", "فناوری اطلاعات", "استخدام اولیه")
        ]
        
        for item in sample_history:
            history_tree.insert('', 'end', values=item)

    def create_financial_tab(self, parent):
        """Create financial information tab"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Salary Info
        salary_frame = ttk.Frame(notebook)
        notebook.add(salary_frame, text="حقوق و مزایا")
        
        salary_fields = [
            ("حقوق پایه", "base_salary"),
            ("حق مسکن", "housing_allowance"),
            ("حق خواربار", "food_allowance"),
            ("حق ایاب و ذهاب", "transportation_allowance"),
            ("پاداش", "bonus"),
            ("حق بیمه", "insurance"),
            ("حق سنوات", "seniority_pay")
        ]
        
        for i, (label, key) in enumerate(salary_fields):
            frame = ttk.Frame(salary_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame, text=f"{label}:").pack(side=tk.RIGHT)
            
            value = self.format_currency(self.current_employee.get(key, 0))
            ttk.Label(frame, text=value, font=('IRANSans', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Bank Info
        bank_frame = ttk.Frame(notebook)
        notebook.add(bank_frame, text="اطلاعات بانکی")
        
        bank_fields = [
            ("نام بانک", "bank_name"),
            ("شماره حساب", "account_number"),
            ("شماره کارت", "card_number"),
            ("شبا", "sheba_number")
        ]
        
        for i, (label, key) in enumerate(bank_fields):
            frame = ttk.Frame(bank_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame, text=f"{label}:").pack(side=tk.RIGHT)
            
            value = self.current_employee.get(key, '')
            ttk.Label(frame, text=value, font=('IRANSans', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Payment History
        payment_frame = ttk.Frame(notebook)
        notebook.add(payment_frame, text="سوابق پرداخت")
        
        columns = ('date', 'amount', 'type', 'description')
        payment_tree = ttk.Treeview(
            payment_frame, 
            columns=columns,
            show='headings',
            height=8
        )
        
        for col in columns:
            payment_tree.heading(col, text=col)
            payment_tree.column(col, width=120)
        
        payment_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample data (replace with actual data in real app)
        sample_payments = [
            ("1402/06/01", "12,500,000", "حقوق", "پرداخت حقوق تیر 1402"),
            ("1402/05/01", "12,000,000", "حقوق", "پرداخت حقوق خرداد 1402")
        ]
        
        for item in sample_payments:
            payment_tree.insert('', 'end', values=item)

    def create_documents_tab(self, parent):
        """Create documents tab"""
        ttk.Label(parent, text="مستندات پیوست شده:", style='Header.TLabel').pack(anchor='e', padx=10)
        
        # Document list
        doc_frame = ttk.Frame(parent)
        doc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('date', 'type', 'title', 'actions')
        doc_tree = ttk.Treeview(
            doc_frame, 
            columns=columns,
            show='headings',
            height=6
        )
        
        for col in columns:
            doc_tree.heading(col, text=col)
            doc_tree.column(col, width=120)
        
        doc_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add sample data (replace with actual data in real app)
        sample_docs = [
            ("1402/01/10", "قرارداد", "قرارداد کار", "مشاهده"),
            ("1401/12/15", "مدارک", "تصویر کارت ملی", "مشاهده")
        ]
        
        for item in sample_docs:
            doc_tree.insert('', 'end', values=item)
        
        # Upload button
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="📤 آپلود سند جدید", 
                  command=self.upload_document).pack(side=tk.LEFT)

    def upload_photo(self):
        """Handle photo upload"""
        file_path = filedialog.askopenfilename(
            title="انتخاب تصویر پرسنل",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            # In a real app, you would save the photo and update the employee record
            messagebox.showinfo("موفقیت", "تصویر با موفقیت آپلود شد")

    def upload_document(self):
        """Handle document upload"""
        file_path = filedialog.askopenfilename(
            title="انتخاب سند",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            # In a real app, you would save the document and update the employee record
            messagebox.showinfo("موفقیت", "سند با موفقیت آپلود شد")

    def format_currency(self, amount):
        """Format numbers as currency"""
        try:
            return "{:,} تومان".format(int(amount))
        except (ValueError, TypeError):
            return str(amount)

    def add_employee(self):
        """Open add employee dialog"""
        add_win = tk.Toplevel(self.root)
        add_win.title("افزودن پرسنل جدید")
        self.center_window_on_parent(add_win, 600, 700)
        
        notebook = ttk.Notebook(add_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Personal Info Tab
        personal_frame = ttk.Frame(notebook)
        notebook.add(personal_frame, text="اطلاعات فردی")
        self.create_add_personal_tab(personal_frame)
        
        # Employment Tab
        employment_frame = ttk.Frame(notebook)
        notebook.add(employment_frame, text="اطلاعات شغلی")
        self.create_add_employment_tab(employment_frame)
        
        # Buttons
        btn_frame = ttk.Frame(add_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="ذخیره", style='Success.TButton',
                  command=lambda: self.save_employee(add_win)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="انصراف", command=add_win.destroy).pack(side=tk.LEFT)

    def create_add_personal_tab(self, parent):
        """Create personal info tab for add employee"""
        fields = [
            ("نام و نام خانوادگی", "name", True),
            ("کد ملی", "national_code", True),
            ("تاریخ تولد", "birth_date", False),
            ("جنسیت", "gender", False),
            ("وضعیت تأهل", "marital_status", False),
            ("تلفن همراه", "mobile", False),
            ("آدرس", "address", False),
            ("تحصیلات", "education", False),
            ("رشته تحصیلی", "field_of_study", False)
        ]
        
        self.add_employee_data = {}
        
        for i, (label, key, required) in enumerate(fields):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add asterisk for required fields
            label_text = f"{label}:" + (" *" if required else "")
            ttk.Label(frame, text=label_text).pack(side=tk.RIGHT)
            
            if key == 'birth_date':
                # Use date picker for birth date
                entry = DateEntry(frame, locale='fa_IR', date_pattern='yyyy/mm/dd')
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            elif key == 'gender':
                # Radio buttons for gender
                gender_frame = ttk.Frame(frame)
                gender_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                
                gender_var = tk.StringVar()
                ttk.Radiobutton(gender_frame, text="مرد", value="male", 
                               variable=gender_var).pack(side=tk.RIGHT)
                ttk.Radiobutton(gender_frame, text="زن", value="female", 
                               variable=gender_var).pack(side=tk.RIGHT)
                self.add_employee_data[key] = gender_var
            elif key == 'marital_status':
                # Radio buttons for marital status
                marital_frame = ttk.Frame(frame)
                marital_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                
                marital_var = tk.StringVar()
                ttk.Radiobutton(marital_frame, text="متأهل", value="married", 
                               variable=marital_var).pack(side=tk.RIGHT)
                ttk.Radiobutton(marital_frame, text="مجرد", value="single", 
                               variable=marital_var).pack(side=tk.RIGHT)
                self.add_employee_data[key] = marital_var
            else:
                # Regular text entry
                entry = ttk.Entry(frame)
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                self.add_employee_data[key] = entry

    def create_add_employment_tab(self, parent):
        """Create employment info tab for add employee"""
        fields = [
            ("کد پرسنلی", "id", True),
            ("تاریخ استخدام", "hire_date", True),
            ("دپارتمان", "department", True),
            ("سمت", "position", True),
            ("واحد", "unit", False),
            ("نوع قرارداد", "contract_type", True),
            ("مدت قرارداد (ماه)", "contract_duration", False),
            ("تاریخ پایان قرارداد", "contract_end_date", False)
        ]
        
        for i, (label, key, required) in enumerate(fields):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add asterisk for required fields
            label_text = f"{label}:" + (" *" if required else "")
            ttk.Label(frame, text=label_text).pack(side=tk.RIGHT)
            
            if key in ['hire_date', 'contract_end_date']:
                # Use date picker for dates
                entry = DateEntry(frame, locale='fa_IR', date_pattern='yyyy/mm/dd')
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                self.add_employee_data[key] = entry
            elif key == 'contract_type':
                # Dropdown for contract type
                contract_var = tk.StringVar()
                options = ["دائمی", "پیمانی", "پروژه‌ای", "ساعتی"]
                entry = ttk.Combobox(frame, textvariable=contract_var, values=options)
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                self.add_employee_data[key] = contract_var
            else:
                # Regular text entry
                entry = ttk.Entry(frame)
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                self.add_employee_data[key] = entry
        
        # Active checkbox
        active_frame = ttk.Frame(parent)
        active_frame.pack(fill=tk.X, padx=10, pady=10)
        
        active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(active_frame, text="پرسنل فعال باشد", 
                       variable=active_var).pack(side=tk.RIGHT)
        self.add_employee_data['active'] = active_var

    def save_employee(self, window):
        """Save new employee data"""
        # Validate required fields
        required_fields = ['name', 'national_code', 'id', 'hire_date', 
                         'department', 'position', 'contract_type']
        
        for field in required_fields:
            value = None
            widget = self.add_employee_data[field]
            
            if isinstance(widget, (tk.Entry, DateEntry)):
                value = widget.get()
            elif isinstance(widget, tk.StringVar):
                value = widget.get()
            
            if not value or value.strip() == '':
                messagebox.showerror("خطا", f"فیلد {field} الزامی است")
                return
        
        # Create employee dictionary
        new_employee = {
            'id': self.add_employee_data['id'].get(),
            'name': self.add_employee_data['name'].get(),
            'national_code': self.add_employee_data['national_code'].get(),
            'birth_date': self.add_employee_data['birth_date'].get_date().strftime('%Y/%m/%d') 
                        if hasattr(self.add_employee_data['birth_date'], 'get_date') 
                        else self.add_employee_data['birth_date'].get(),
            'gender': self.add_employee_data['gender'].get(),
            'marital_status': self.add_employee_data['marital_status'].get(),
            'mobile': self.add_employee_data['mobile'].get(),
            'address': self.add_employee_data['address'].get(),
            'education': self.add_employee_data['education'].get(),
            'field_of_study': self.add_employee_data['field_of_study'].get(),
            'hire_date': self.add_employee_data['hire_date'].get_date().strftime('%Y/%m/%d') 
                        if hasattr(self.add_employee_data['hire_date'], 'get_date') 
                        else self.add_employee_data['hire_date'].get(),
            'department': self.add_employee_data['department'].get(),
            'position': self.add_employee_data['position'].get(),
            'unit': self.add_employee_data['unit'].get(),
            'contract_type': self.add_employee_data['contract_type'].get(),
            'contract_duration': self.add_employee_data['contract_duration'].get(),
            'contract_end_date': self.add_employee_data['contract_end_date'].get_date().strftime('%Y/%m/%d') 
                                if hasattr(self.add_employee_data['contract_end_date'], 'get_date') 
                                else self.add_employee_data['contract_end_date'].get(),
            'active': self.add_employee_data['active'].get(),
            'created_at': datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        }
        
        # Add to employees data
        self.employees_data[new_employee['id']] = new_employee
        self.save_data()
        
        # Refresh table
        self.populate_employee_table()
        
        messagebox.showinfo("موفقیت", "پرسنل جدید با موفقیت اضافه شد")
        window.destroy()

    def edit_employee(self):
        """Edit selected employee"""
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک پرسنل را انتخاب کنید")
            return
            
        emp_id = self.employee_tree.item(selected, 'values')[0]
        self.current_employee = self.employees_data.get(emp_id)
        
        if not self.current_employee:
            messagebox.showerror("خطا", "پرسنل انتخاب شده یافت نشد")
            return
            
        # Open edit window (similar to add window but with existing data)
        messagebox.showinfo("اطلاع", "این بخش در نسخه کامل پیاده‌سازی می‌شود")

    def delete_employee(self):
        """Delete selected employee"""
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک پرسنل را انتخاب کنید")
            return
            
        emp_id = self.employee_tree.item(selected, 'values')[0]
        emp_name = self.employee_tree.item(selected, 'values')[1]
        
        if messagebox.askyesno("تأیید", f"آیا از حذف پرسنل {emp_name} مطمئن هستید؟"):
            del self.employees_data[emp_id]
            self.save_data()
            self.populate_employee_table()
            messagebox.showinfo("موفقیت", "پرسنل با موفقیت حذف شد")

    def show_work_records(self):
        """Show work records for selected employee"""
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک پرسنل را انتخاب کنید")
            return
            
        emp_id = self.employee_tree.item(selected, 'values')[0]
        emp_name = self.employee_tree.item(selected, 'values')[1]
        
        messagebox.showinfo("اطلاع", f"نمایش سوابق کارکرد برای {emp_name}\nاین بخش در نسخه کامل پیاده‌سازی می‌شود")

    def show_payslip(self):
        """Show payslip for selected employee"""
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک پرسنل را انتخاب کنید")
            return
            
        emp_id = self.employee_tree.item(selected, 'values')[0]
        emp_name = self.employee_tree.item(selected, 'values')[1]
        
        messagebox.showinfo("اطلاع", f"نمایش فیش حقوق برای {emp_name}\nاین بخش در نسخه کامل پیاده‌سازی می‌شود")

    def show_dashboard(self):
        """Show dashboard view"""
        messagebox.showinfo("اطلاع", "داشبورد مدیریت\nاین بخش در نسخه کامل پیاده‌سازی می‌شود")

    def show_payroll(self):
        """Show payroll view"""
        messagebox.showinfo("اطلاع", "مدیریت حقوق و دستمزد\nاین بخش در نسخه کامل پیاده‌سازی می‌شود")

    def show_reports(self):
        """Show reports view"""
        messagebox.showinfo("اطلاع", "گزارشات سیستم\nاین بخش در نسخه کامل پیاده‌سازی می‌شود")

    def show_settings(self):
        """Show settings view"""
        messagebox.showinfo("اطلاع", "تنظیمات سیستم\nاین بخش در نسخه کامل پیاده‌سازی می‌شود")

    def show_help(self):
        """Show help documentation"""
        webbrowser.open("https://example.com/help")

    def center_window_on_parent(self, window, width, height):
        """Center a window relative to its parent"""
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def load_data(self):
        """Load employee data from file"""
        try:
            if os.path.exists('employees.json'):
                with open('employees.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {str(e)}")
            return {}

    def save_data(self):
        """Save employee data to file"""
        try:
            with open('employees.json', 'w', encoding='utf-8') as f:
                json.dump(self.employees_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره داده‌ها: {str(e)}")

    def create_sample_data(self):
        """Create sample data for testing"""
        self.employees_data = {
            "1001": {
                "id": "1001",
                "name": "علی احمدی",
                "national_code": "1234567890",
                "birth_date": "1370/05/15",
                "gender": "male",
                "marital_status": "married",
                "mobile": "09123456789",
                "address": "تهران، خیابان انقلاب، پلاک ۱۲۳",
                "education": "کارشناسی ارشد",
                "field_of_study": "مهندسی نرم‌افزار",
                "hire_date": "1400/03/01",
                "department": "فناوری اطلاعات",
                "position": "برنامه‌نویس ارشد",
                "unit": "توسعه نرم‌افزار",
                "contract_type": "دائمی",
                "contract_duration": "",
                "contract_end_date": "",
                "active": True,
                "base_salary": 15000000,
                "housing_allowance": 5000000,
                "food_allowance": 2000000,
                "transportation_allowance": 1000000,
                "created_at": "1402/01/01 10:00:00"
            },
            "1002": {
                "id": "1002",
                "name": "فاطمه محمدی",
                "national_code": "0987654321",
                "birth_date": "1375/08/20",
                "gender": "female",
                "marital_status": "single",
                "mobile": "09198765432",
                "address": "کرج، بلوار دانشجو، پلاک ۴۵",
                "education": "کارشناسی",
                "field_of_study": "مدیریت مالی",
                "hire_date": "1401/06/15",
                "department": "مالی",
                "position": "حسابدار",
                "unit": "حسابداری",
                "contract_type": "پیمانی",
                "contract_duration": "12",
                "contract_end_date": "1402/06/15",
                "active": True,
                "base_salary": 12000000,
                "housing_allowance": 3000000,
                "food_allowance": 1500000,
                "transportation_allowance": 800000,
                "created_at": "1402/01/01 10:05:00"
            }
        }
        self.save_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalEmployeeManagement(root)
    root.mainloop()