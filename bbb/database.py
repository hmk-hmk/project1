import sqlite3
from cryptography.fernet import Fernet
import hashlib
import json

class SecureDatabase:
    def __init__(self, encryption_key):
        self.conn = sqlite3.connect('enterprise.db')
        self.cipher = Fernet(encryption_key)
        self.create_tables()
        
    def create_tables(self):
        # جدول کارکنان
        self.conn.execute('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            encrypted_data BLOB,
                            signature TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                         )''')
        
        # جدول قراردادها
        self.conn.execute('''CREATE TABLE IF NOT EXISTS contracts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            parties TEXT,
                            amount REAL,
                            encrypted_details BLOB,
                            start_date TEXT,
                            end_date TEXT
                         )''')
        self.conn.commit()
    
    # ----------------- کارکنان -----------------
    def add_employee(self, data):
        try:
            encrypted = self.cipher.encrypt(json.dumps(data).encode())
            signature = hashlib.sha3_512(json.dumps(data).encode()).hexdigest()
            self.conn.execute('INSERT INTO employees (encrypted_data, signature) VALUES (?,?)',
                            (encrypted, signature))
            self.conn.commit()
            return True
        except Exception as e:
            raise DatabaseError(f"خطا در ثبت کارمند: {str(e)}")

    # ----------------- قراردادها -----------------
    def add_contract(self, data):
        try:
            encrypted = self.cipher.encrypt(json.dumps(data['details']).encode())
            self.conn.execute('''INSERT INTO contracts 
                               (title, parties, amount, encrypted_details, start_date, end_date)
                               VALUES (?,?,?,?,?,?)''',
                            (data['title'], 
                             json.dumps(data['parties']),
                             data['amount'],
                             encrypted,
                             data['start_date'],
                             data['end_date']))
            self.conn.commit()
            return True
        except Exception as e:
            raise DatabaseError(f"خطا در ثبت قرارداد: {str(e)}")

class DatabaseError(Exception):
    pass