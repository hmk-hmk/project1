import sqlite3
import logging

logging.basicConfig(filename="database_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

def migrate_db():
    conn = sqlite3.connect('contracts_new.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_number TEXT NOT NULL,
        contract_date TEXT NOT NULL,
        contract_subject TEXT NOT NULL,
        contract_party TEXT NOT NULL,
        total_amount TEXT NOT NULL,
        prepayment_percent TEXT NOT NULL,
        prepayment_amount TEXT NOT NULL,
        some_field TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        father_name TEXT,
        id_number TEXT,
        national_code TEXT NOT NULL,
        phone TEXT,
        emergency_phone TEXT,
        address TEXT,
        degree TEXT,
        major TEXT,
        university TEXT,
        prev_company TEXT,
        duration TEXT,
        position TEXT,
        contract_type TEXT,
        salary TEXT,
        insurance INTEGER DEFAULT 0,
        contract_id INTEGER,
        daily_rate TEXT DEFAULT '0',
        unit_count INTEGER DEFAULT 0,
        unit_rate TEXT DEFAULT '0',
        performance_percentage REAL DEFAULT 0,
        performance_amount TEXT DEFAULT '0',
        hire_date TEXT DEFAULT '',
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
    )''')

    cursor.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in cursor.fetchall()]
    if "father_name" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN father_name TEXT DEFAULT ''")
        logging.info("ستون father_name به جدول employees اضافه شد")
    if "address" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN address TEXT DEFAULT ''")
        logging.info("ستون address به جدول employees اضافه شد")
    if "hire_date" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN hire_date TEXT DEFAULT ''")
        logging.info("ستون hire_date به جدول employees اضافه شد")

    conn.commit()
    conn.close()
    logging.info("دیتابیس مهاجرت و به‌روزرسانی شد")

def get_contracts():
    migrate_db()
    conn = sqlite3.connect('contracts_new.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts")
    contracts = cursor.fetchall()
    conn.close()
    return contracts

def add_contract(contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount, some_field):
    migrate_db()
    conn = sqlite3.connect('contracts_new.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO contracts (contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount, some_field)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount, some_field))
    conn.commit()
    conn.close()
    logging.info(f"قرارداد جدید با شماره {contract_number} اضافه شد")

def get_employees():
    migrate_db()
    conn = sqlite3.connect('contracts_new.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

def get_employee_by_id(emp_id, db_path="contracts_new.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id=?", (emp_id,))
    employee = cursor.fetchone()
    conn.close()
    return employee

def add_employee(data, db_path="contracts_new.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO employees (first_name, last_name, father_name, national_code, phone, address, 
                      contract_type, salary, daily_rate, unit_rate, unit_count, insurance, contract_id, 
                      performance_percentage, position, hire_date)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (data["first_name"], data["last_name"], data["father_name"], data["national_code"], 
                    data["phone"], data["address"], data["contract_type"], data["salary"], data["daily_rate"], 
                    data["unit_rate"], data["unit_count"], data["insurance"], data["contract_id"], 
                    data["performance_percentage"], data["position"], data["hire_date"]))
    conn.commit()
    conn.close()
    logging.info(f"کارمند جدید {data['first_name']} {data['last_name']} با contract_id={data['contract_id']} اضافه شد")

def update_employee(emp_id, first_name, last_name, father_name, national_code, phone, address, contract_type, 
                    salary, daily_rate, unit_rate, unit_count, insurance, contract_id, performance_percentage, 
                    position, hire_date, db_path="contracts_new.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''UPDATE employees SET first_name=?, last_name=?, father_name=?, national_code=?, phone=?, 
                      address=?, contract_type=?, salary=?, daily_rate=?, unit_rate=?, unit_count=?, insurance=?, 
                      contract_id=?, performance_percentage=?, position=?, hire_date=?
                      WHERE id=?''',
                   (first_name, last_name, father_name, national_code, phone, address, contract_type, salary, 
                    daily_rate, unit_rate, unit_count, insurance, contract_id, performance_percentage, position, 
                    hire_date, emp_id))
    conn.commit()
    conn.close()
    logging.info(f"کارمند با شناسه {emp_id} با contract_id={contract_id} ویرایش شد")

def delete_employee(emp_id, db_path="contracts_new.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()
    logging.info(f"کارمند با شناسه {emp_id} حذف شد")

migrate_db()