from db_manager import get_connection, close_connection, log_info, log_error

def add_prepayment(contract_id, prepayment_date, prepayment_amount, description, bank):
    """اضافه کردن پیش‌پرداخت جدید"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO prepayments (contract_id, prepayment_date, prepayment_amount, description, bank)
                          VALUES (?, ?, ?, ?, ?)''',
                       (contract_id, prepayment_date, prepayment_amount, description, bank))
        close_connection(conn)
        log_info(f"پیش‌پرداخت جدید برای قرارداد {contract_id} اضافه شد")
    except Exception as e:
        log_error(f"خطا در اضافه کردن پیش‌پرداخت: {str(e)}")
        close_connection(conn)
        raise

def get_prepayments():
    """گرفتن همه پیش‌پرداخت‌ها"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM prepayments")
        prepayments = cursor.fetchall()
        close_connection(conn)
        return prepayments
    except Exception as e:
        log_error(f"خطا در گرفتن پیش‌پرداخت‌ها: {str(e)}")
        close_connection(conn)
        raise

def get_prepayment_by_id(prepayment_id):
    """گرفتن پیش‌پرداخت با شناسه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM prepayments WHERE id = ?", (prepayment_id,))
        prepayment = cursor.fetchone()
        close_connection(conn)
        return prepayment
    except Exception as e:
        log_error(f"خطا در گرفتن پیش‌پرداخت با شناسه {prepayment_id}: {str(e)}")
        close_connection(conn)
        raise

def update_prepayment(prepayment_id, contract_id, prepayment_date, prepayment_amount, description, bank):
    """ویرایش پیش‌پرداخت"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''UPDATE prepayments SET contract_id = ?, prepayment_date = ?, prepayment_amount = ?, description = ?, bank = ?
                          WHERE id = ?''',
                       (contract_id, prepayment_date, prepayment_amount, description, bank, prepayment_id))
        close_connection(conn)
        log_info(f"پیش‌پرداخت با شناسه {prepayment_id} ویرایش شد")
    except Exception as e:
        log_error(f"خطا در ویرایش پیش‌پرداخت با شناسه {prepayment_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_prepayment(prepayment_id):
    """حذف پیش‌پرداخت"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM prepayments WHERE id = ?", (prepayment_id,))
        close_connection(conn)
        log_info(f"پیش‌پرداخت با شناسه {prepayment_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف پیش‌پرداخت با شناسه {prepayment_id}: {str(e)}")
        close_connection(conn)
        raise

def get_total_prepayments_for_contract(contract_id):
    """گرفتن مجموع پیش‌پرداخت‌ها برای یه قرارداد"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT SUM(CAST(prepayment_amount AS INTEGER)) FROM prepayments WHERE contract_id = ?", (contract_id,))
        total = cursor.fetchone()[0]
        close_connection(conn)
        return total if total else 0
    except Exception as e:
        log_error(f"خطا در گرفتن مجموع پیش‌پرداخت‌ها برای قرارداد {contract_id}: {str(e)}")
        close_connection(conn)
        raise