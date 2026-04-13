"""
Bill model - CRUD operations with transaction handling.
"""
from models.db import execute_query, execute_transaction


def get_all_bills(page=1, per_page=10, search=None, status_filter=None,
                  sort_by='created_at', sort_order='DESC'):
    """Get all bills with patient names using JOINs."""
    offset = (page - 1) * per_page
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR b.description LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if status_filter:
        conditions.append("b.payment_status = %s")
        params.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    allowed_sorts = ['bill_id', 'amount', 'payment_status', 'created_at']
    if sort_by not in allowed_sorts:
        sort_by = 'created_at'
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'DESC'

    query = f"""
        SELECT b.*, p.name AS patient_name
        FROM bills b
        INNER JOIN patients p ON b.patient_id = p.patient_id
        {where_clause}
        ORDER BY b.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    return execute_query(query, tuple(params), fetch=True)


def get_bill_count(search=None, status_filter=None):
    """Get total bill count."""
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR b.description LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if status_filter:
        conditions.append("b.payment_status = %s")
        params.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT COUNT(*) as count FROM bills b
        INNER JOIN patients p ON b.patient_id = p.patient_id
        {where_clause}
    """
    result = execute_query(query, tuple(params), fetchone=True)
    return result['count'] if result else 0


def get_bill_by_id(bill_id):
    """Get single bill with patient details."""
    query = """
        SELECT b.*, p.name AS patient_name, p.contact AS patient_contact
        FROM bills b
        INNER JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.bill_id = %s
    """
    return execute_query(query, (bill_id,), fetchone=True)


def get_bills_by_patient(patient_id):
    """Get all bills for a patient."""
    query = """
        SELECT b.* FROM bills b
        WHERE b.patient_id = %s
        ORDER BY b.created_at DESC
    """
    return execute_query(query, (patient_id,), fetch=True)


def add_bill(patient_id, amount, description, payment_status, payment_date=None):
    """Insert a new bill using transaction handling."""
    queries = [
        (
            """INSERT INTO bills (patient_id, amount, description, payment_status, payment_date)
               VALUES (%s, %s, %s, %s, %s)""",
            (patient_id, amount, description, payment_status, payment_date)
        )
    ]
    return execute_transaction(queries)


def update_bill(bill_id, patient_id, amount, description, payment_status, payment_date=None):
    """Update a bill using transaction handling."""
    queries = [
        (
            """UPDATE bills
               SET patient_id = %s, amount = %s, description = %s,
                   payment_status = %s, payment_date = %s
               WHERE bill_id = %s""",
            (patient_id, amount, description, payment_status, payment_date, bill_id)
        )
    ]
    return execute_transaction(queries)


def delete_bill(bill_id):
    """Delete a bill."""
    query = "DELETE FROM bills WHERE bill_id = %s"
    return execute_query(query, (bill_id,), commit=True)


def get_billing_summary():
    """Get billing summary using GROUP BY and aggregate functions."""
    query = """
        SELECT
            payment_status,
            COUNT(*) AS total_bills,
            SUM(amount) AS total_amount,
            AVG(amount) AS avg_amount
        FROM bills
        GROUP BY payment_status
    """
    return execute_query(query, fetch=True)
