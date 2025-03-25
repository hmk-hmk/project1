from db_manager import get_connection, close_connection, log_info, log_error

def add_contract(contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount):
    """اضافه کردن قرارداد جدید"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO contracts (contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount))
        contract_id = cursor.lastrowid
        close_connection(conn)
        log_info(f"قرارداد جدید با شماره {contract_number} اضافه شد")
        return contract_id
    except Exception as e:
        log_error(f"خطا در اضافه کردن قرارداد: {str(e)}")
        close_connection(conn)
        raise

def get_contracts():
    """گرفتن همه قراردادها"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM contracts")
        contracts = cursor.fetchall()
        close_connection(conn)
        return contracts
    except Exception as e:
        log_error(f"خطا در گرفتن قراردادها: {str(e)}")
        close_connection(conn)
        raise

def get_contract_by_id(contract_id):
    """گرفتن قرارداد با شناسه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
        contract = cursor.fetchone()
        close_connection(conn)
        return contract
    except Exception as e:
        log_error(f"خطا در گرفتن قرارداد با شناسه {contract_id}: {str(e)}")
        close_connection(conn)
        raise

def update_contract(contract_id, contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount):
    """ویرایش قرارداد"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''UPDATE contracts SET contract_number = ?, contract_date = ?, contract_subject = ?, contract_party = ?, 
                          total_amount = ?, prepayment_percent = ?, prepayment_amount = ? WHERE id = ?''',
                       (contract_number, contract_date, contract_subject, contract_party, total_amount, prepayment_percent, prepayment_amount, contract_id))
        close_connection(conn)
        log_info(f"قرارداد با شناسه {contract_id} ویرایش شد")
    except Exception as e:
        log_error(f"خطا در ویرایش قرارداد با شناسه {contract_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_contract(contract_id):
    """حذف قرارداد"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
        close_connection(conn)
        log_info(f"قرارداد با شناسه {contract_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف قرارداد با شناسه {contract_id}: {str(e)}")
        close_connection(conn)
        raise

def get_contract_id_by_number(contract_number):
    """گرفتن شناسه قرارداد با شماره"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT id FROM contracts WHERE contract_number = ?", (contract_number,))
        result = cursor.fetchone()
        close_connection(conn)
        return result[0] if result else None
    except Exception as e:
        log_error(f"خطا در گرفتن شناسه قرارداد با شماره {contract_number}: {str(e)}")
        close_connection(conn)
        raise

def add_contract_detail(contract_id, description, quantity, unit, amount):
    """اضافه کردن جزئیات قرارداد"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO contract_details (contract_id, description, quantity, unit, amount)
                          VALUES (?, ?, ?, ?, ?)''',
                       (contract_id, description, quantity, unit, amount))
        close_connection(conn)
        log_info(f"جزئیات قرارداد برای قرارداد {contract_id} اضافه شد")
    except Exception as e:
        log_error(f"خطا در اضافه کردن جزئیات قرارداد: {str(e)}")
        close_connection(conn)
        raise

def get_contract_details(contract_id):
    """گرفتن جزئیات قرارداد"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM contract_details WHERE contract_id = ?", (contract_id,))
        details = cursor.fetchall()
        close_connection(conn)
        return details
    except Exception as e:
        log_error(f"خطا در گرفتن جزئیات قرارداد {contract_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_contract_details(contract_id):
    """حذف جزئیات قرارداد"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM contract_details WHERE contract_id = ?", (contract_id,))
        close_connection(conn)
        log_info(f"جزئیات قرارداد با شناسه {contract_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف جزئیات قرارداد با شناسه {contract_id}: {str(e)}")
        close_connection(conn)
        raise