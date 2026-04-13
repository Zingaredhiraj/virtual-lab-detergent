"""
Patient model - CRUD operations for patients table.
"""
from models.db import execute_query


def get_all_patients(page=1, per_page=10, search=None, sort_by='patient_id', sort_order='ASC'):
    """
    Get all patients with pagination, search, and sorting.
    Uses JOIN queries and GROUP BY for report data.
    """
    offset = (page - 1) * per_page

    where_clause = ""
    params = []

    if search:
        where_clause = "WHERE p.name LIKE %s OR p.contact LIKE %s OR p.address LIKE %s"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])

    # Validate sort columns to prevent SQL injection
    allowed_sorts = ['patient_id', 'name', 'age', 'gender', 'contact', 'created_at']
    if sort_by not in allowed_sorts:
        sort_by = 'patient_id'
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'ASC'

    query = f"""
        SELECT p.*,
               COUNT(DISTINCT a.appointment_id) AS total_appointments,
               COUNT(DISTINCT pr.prescription_id) AS total_prescriptions
        FROM patients p
        LEFT JOIN appointments a ON p.patient_id = a.patient_id
        LEFT JOIN prescriptions pr ON p.patient_id = pr.patient_id
        {where_clause}
        GROUP BY p.patient_id
        ORDER BY p.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])

    return execute_query(query, tuple(params), fetch=True)


def get_patient_count(search=None):
    """Get total patient count for pagination."""
    if search:
        query = "SELECT COUNT(*) as count FROM patients WHERE name LIKE %s OR contact LIKE %s"
        search_param = f"%{search}%"
        result = execute_query(query, (search_param, search_param), fetchone=True)
    else:
        query = "SELECT COUNT(*) as count FROM patients"
        result = execute_query(query, fetchone=True)

    return result['count'] if result else 0


def get_patient_by_id(patient_id):
    """Get a single patient by ID with related data using JOINs."""
    query = """
        SELECT p.*,
               COUNT(DISTINCT a.appointment_id) AS total_appointments,
               COUNT(DISTINCT b.bill_id) AS total_bills,
               COALESCE(SUM(b.amount), 0) AS total_bill_amount
        FROM patients p
        LEFT JOIN appointments a ON p.patient_id = a.patient_id
        LEFT JOIN bills b ON p.patient_id = b.patient_id
        WHERE p.patient_id = %s
        GROUP BY p.patient_id
    """
    return execute_query(query, (patient_id,), fetchone=True)


def add_patient(name, age, gender, contact, email, address, medical_history):
    """Insert a new patient record."""
    query = """
        INSERT INTO patients (name, age, gender, contact, email, address, medical_history)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (name, age, gender, contact, email, address, medical_history), commit=True)


def update_patient(patient_id, name, age, gender, contact, email, address, medical_history):
    """Update an existing patient record."""
    query = """
        UPDATE patients
        SET name = %s, age = %s, gender = %s, contact = %s,
            email = %s, address = %s, medical_history = %s
        WHERE patient_id = %s
    """
    return execute_query(
        query,
        (name, age, gender, contact, email, address, medical_history, patient_id),
        commit=True
    )


def delete_patient(patient_id):
    """Delete a patient record."""
    query = "DELETE FROM patients WHERE patient_id = %s"
    return execute_query(query, (patient_id,), commit=True)
