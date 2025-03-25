from db_manager import get_connection, close_connection, log_info, log_error

# --- توابع هزینه‌ها ---
def add_cost(contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description):
    """اضافه کردن هزینه جدید"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO costs (contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description))
        close_connection(conn)
        log_info(f"هزینه جدید با کد {cost_code} اضافه شد")
    except Exception as e:
        log_error(f"خطا در اضافه کردن هزینه: {str(e)}")
        close_connection(conn)
        raise

def get_costs():
    """گرفتن همه هزینه‌ها"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM costs")
        costs = cursor.fetchall()
        close_connection(conn)
        return costs
    except Exception as e:
        log_error(f"خطا در گرفتن هزینه‌ها: {str(e)}")
        close_connection(conn)
        raise

def get_cost_by_id(cost_id):
    """گرفتن هزینه با شناسه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM costs WHERE id = ?", (cost_id,))
        cost = cursor.fetchone()
        close_connection(conn)
        return cost
    except Exception as e:
        log_error(f"خطا در گرفتن هزینه با شناسه {cost_id}: {str(e)}")
        close_connection(conn)
        raise

def update_cost(cost_id, contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description):
    """ویرایش هزینه"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''UPDATE costs SET contract_id = ?, cost_code = ?, cost_type = ?, amount = ?, tax = ?, discount = ?, final_amount = ?, payer = ?, invoice_number = ?, status = ?, date = ?, description = ?
                          WHERE id = ?''',
                       (contract_id, cost_code, cost_type, amount, tax, discount, final_amount, payer, invoice_number, status, date, description, cost_id))
        close_connection(conn)
        log_info(f"هزینه با شناسه {cost_id} ویرایش شد")
    except Exception as e:
        log_error(f"خطا در ویرایش هزینه با شناسه {cost_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_cost(cost_id):
    """حذف هزینه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM costs WHERE id = ?", (cost_id,))
        close_connection(conn)
        log_info(f"هزینه با شناسه {cost_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف هزینه با شناسه {cost_id}: {str(e)}")
        close_connection(conn)
        raise

# --- توابع دارایی‌ها ---
def add_asset(asset_type, item_name, description, amount, date):
    """اضافه کردن دارایی جدید"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO assets (asset_type, item_name, description, amount, date)
                          VALUES (?, ?, ?, ?, ?)''',
                       (asset_type, item_name, description, amount, date))
        close_connection(conn)
        log_info(f"دارایی جدید با نام {item_name} اضافه شد")
    except Exception as e:
        log_error(f"خطا در اضافه کردن دارایی: {str(e)}")
        close_connection(conn)
        raise

def get_assets():
    """گرفتن همه دارایی‌ها"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM assets")
        assets = cursor.fetchall()
        close_connection(conn)
        return assets
    except Exception as e:
        log_error(f"خطا در گرفتن دارایی‌ها: {str(e)}")
        close_connection(conn)
        raise

def get_asset_by_id(asset_id):
    """گرفتن دارایی با شناسه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
        asset = cursor.fetchone()
        close_connection(conn)
        return asset
    except Exception as e:
        log_error(f"خطا در گرفتن دارایی با شناسه {asset_id}: {str(e)}")
        close_connection(conn)
        raise

def update_asset(asset_id, asset_type, item_name, description, amount, date):
    """ویرایش دارایی"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''UPDATE assets SET asset_type = ?, item_name = ?, description = ?, amount = ?, date = ?
                          WHERE id = ?''',
                       (asset_type, item_name, description, amount, date, asset_id))
        close_connection(conn)
        log_info(f"دارایی با شناسه {asset_id} ویرایش شد")
    except Exception as e:
        log_error(f"خطا در ویرایش دارایی با شناسه {asset_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_asset(asset_id):
    """حذف دارایی"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
        close_connection(conn)
        log_info(f"دارایی با شناسه {asset_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف دارایی با شناسه {asset_id}: {str(e)}")
        close_connection(conn)
        raise