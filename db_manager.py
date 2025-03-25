import sqlite3
import logging

# تنظیم لاگ مرکزی
logging.basicConfig(filename="app_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

DB_NAME = "contracts_new.db"

def get_connection():
    """اتصال به دیتابیس و برگرداندن connection و cursor"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        log_error(f"خطا در اتصال به دیتابیس: {str(e)}")
        raise

def close_connection(conn):
    """بستن اتصال به دیتابیس"""
    try:
        conn.commit()
        conn.close()
    except Exception as e:
        log_error(f"خطا در بستن اتصال: {str(e)}")

def log_info(message):
    """لاگ کردن پیام اطلاعاتی"""
    logging.info(message)

def log_error(message):
    """لاگ کردن پیام خطا"""
    logging.error(message)

def migrate_db():
    """مهاجرت دیتابیس و ساخت جدول‌ها"""
    conn, cursor = get_connection()

    cursor.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_number TEXT NOT NULL,
        contract_date TEXT NOT NULL,
        contract_subject TEXT NOT NULL,
        contract_party TEXT NOT NULL,
        total_amount TEXT NOT NULL,
        prepayment_percent TEXT NOT NULL,
        prepayment_amount TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS contract_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        description TEXT NOT NULL,
        quantity TEXT NOT NULL,
        unit TEXT NOT NULL,
        amount TEXT NOT NULL,
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
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
        overtime TEXT DEFAULT '0',
        deduction TEXT DEFAULT '0',
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS prepayments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        prepayment_date TEXT NOT NULL,
        prepayment_amount TEXT NOT NULL,
        description TEXT,
        bank TEXT,
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS guarantees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        guarantee_number TEXT NOT NULL,
        issue_date TEXT NOT NULL,
        amount TEXT NOT NULL,
        bank TEXT,
        description TEXT,
        guarantee_type TEXT,
        guarantee_basis TEXT,
        blocked_amount TEXT,
        issuance_cost TEXT,
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        cost_code TEXT,
        cost_type TEXT NOT NULL,
        amount TEXT NOT NULL,
        tax TEXT,
        discount TEXT,
        final_amount TEXT NOT NULL,
        payer TEXT,
        invoice_number TEXT,
        status TEXT,
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_type TEXT NOT NULL,
        item_name TEXT,
        description TEXT,
        amount TEXT NOT NULL,
        date TEXT NOT NULL
    )''')

    close_connection(conn)
    log_info("دیتابیس مهاجرت و به‌روزرسانی شد")

if __name__ == "__main__":
    migrate_db()