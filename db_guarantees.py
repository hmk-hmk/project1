from db_manager import get_connection, close_connection, log_info, log_error

def add_guarantee(contract_id, guarantee_type, amount, issue_date, bank, guarantee_number):
    """اضافه کردن ضمانت‌نامه جدید"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO guarantees (contract_id, guarantee_type, amount, issue_date, bank, guarantee_number)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (contract_id, guarantee_type, amount, issue_date, bank, guarantee_number))
        close_connection(conn)
        log_info(f"ضمانت‌نامه جدید برای قرارداد {contract_id} اضافه شد")
    except Exception as e:
        log_error(f"خطا در اضافه کردن ضمانت‌نامه: {str(e)}")
        close_connection(conn)
        raise

def get_guarantees():
    """گرفتن همه ضمانت‌نامه‌ها"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM guarantees")
        guarantees = cursor.fetchall()
        close_connection(conn)
        return guarantees
    except Exception as e:
        log_error(f"خطا در گرفتن ضمانت‌نامه‌ها: {str(e)}")
        close_connection(conn)
        raise

def get_guarantee_by_id(guarantee_id):
    """گرفتن ضمانت‌نامه با شناسه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM guarantees WHERE id = ?", (guarantee_id,))
        guarantee = cursor.fetchone()
        close_connection(conn)
        return guarantee
    except Exception as e:
        log_error(f"خطا در گرفتن ضمانت‌نامه با شناسه {guarantee_id}: {str(e)}")
        close_connection(conn)
        raise

def update_guarantee(guarantee_id, contract_id, guarantee_type, amount, issue_date, bank, guarantee_number):
    """ویرایش ضمانت‌نامه"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''UPDATE guarantees SET contract_id = ?, guarantee_type = ?, amount = ?, issue_date = ?, bank = ?, guarantee_number = ?
                          WHERE id = ?''',
                       (contract_id, guarantee_type, amount, issue_date, bank, guarantee_number, guarantee_id))
        close_connection(conn)
        log_info(f"ضمانت‌نامه با شناسه {guarantee_id} ویرایش شد")
    except Exception as e:
        log_error(f"خطا در ویرایش ضمانت‌نامه با شناسه {guarantee_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_guarantee(guarantee_id):
    """حذف ضمانت‌نامه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM guarantees WHERE id = ?", (guarantee_id,))
        close_connection(conn)
        log_info(f"ضمانت‌نامه با شناسه {guarantee_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف ضمانت‌نامه با شناسه {guarantee_id}: {str(e)}")
        close_connection(conn)
        raise