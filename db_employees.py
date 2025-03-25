import sqlite3
from db_manager import get_connection, close_connection, log_info, log_error

def add_employee(first_name, last_name, father_name, id_number, national_code, phone, emergency_phone, address, degree, major, university, prev_company, duration, position, contract_type, salary, insurance, contract_id, daily_rate, unit_count, unit_rate, performance_percentage=0, performance_amount="0", overtime="0", deduction="0"):
    """اضافه کردن کارمند جدید"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''INSERT INTO employees (first_name, last_name, father_name, id_number, national_code, phone, emergency_phone, address, degree, major, university, prev_company, duration, position, contract_type, salary, insurance, contract_id, daily_rate, unit_count, unit_rate, performance_percentage, performance_amount, overtime, deduction)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (first_name, last_name, father_name, id_number, national_code, phone, emergency_phone, address, degree, major, university, prev_company, duration, position, contract_type, salary, int(insurance), contract_id, daily_rate, unit_count, unit_rate, performance_percentage, performance_amount, overtime, deduction))
        close_connection(conn)
        log_info("کارمند جدید اضافه شد")
    except Exception as e:
        log_error(f"خطا در اضافه کردن کارمند: {str(e)}")
        close_connection(conn)
        raise

def get_employees():
    """گرفتن همه کارکنان"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        close_connection(conn)
        return employees
    except Exception as e:
        log_error(f"خطا در گرفتن کارکنان: {str(e)}")
        close_connection(conn)
        raise

def get_employee_by_id(emp_id):
    """گرفتن کارمند با شناسه"""
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        employee = cursor.fetchone()
        close_connection(conn)
        return employee
    except Exception as e:
        log_error(f"خطا در گرفتن کارمند با شناسه {emp_id}: {str(e)}")
        close_connection(conn)
        raise

def update_employee(emp_id, first_name, last_name, father_name, id_number, national_code, phone, emergency_phone, address, degree, major, university, prev_company, duration, position, contract_type, salary, insurance, contract_id, daily_rate, unit_count, unit_rate, performance_percentage=0, performance_amount="0", overtime="0", deduction="0"):
    """ویرایش کارمند"""
    conn, cursor = get_connection()
    try:
        cursor.execute('''UPDATE employees SET first_name = ?, last_name = ?, father_name = ?, id_number = ?, national_code = ?, phone = ?, emergency_phone = ?, address = ?, degree = ?, major = ?, university = ?, prev_company = ?, duration = ?, position = ?, contract_type = ?, salary = ?, insurance = ?, contract_id = ?, daily_rate = ?, unit_count = ?, unit_rate = ?, performance_percentage = ?, performance_amount = ?, overtime = ?, deduction = ?
                          WHERE id = ?''',
                       (first_name, last_name, father_name, id_number, national_code, phone, emergency_phone, address, degree, major, university, prev_company, duration, position, contract_type, salary, int(insurance), contract_id, daily_rate, unit_count, unit_rate, performance_percentage, performance_amount, overtime, deduction, emp_id))
        close_connection(conn)
        log_info(f"کارمند با شناسه {emp_id} ویرایش شد")
    except Exception as e:
        log_error(f"خطا در ویرایش کارمند با شناسه {emp_id}: {str(e)}")
        close_connection(conn)
        raise

def delete_employee(emp_id):
    """حذف کارمند"""
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        close_connection(conn)
        log_info(f"کارمند با شناسه {emp_id} حذف شد")
    except Exception as e:
        log_error(f"خطا در حذف کارمند با شناسه {emp_id}: {str(e)}")
        close_connection(conn)
        raise