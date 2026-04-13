"""
Doctor model - CRUD operations for doctors table.
"""
from models.db import execute_query


def get_all_doctors(page=1, per_page=10, search=None, sort_by='doctor_id', sort_order='ASC'):
    """Get all doctors with pagination, search, sorting, and department JOIN."""
    offset = (page - 1) * per_page
    where_clause = ""
    params = []

    if search:
        where_clause = "WHERE d.name LIKE %s OR d.specialization LIKE %s"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    allowed_sorts = ['doctor_id', 'name', 'specialization', 'contact', 'created_at']
    if sort_by not in allowed_sorts:
        sort_by = 'doctor_id'
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'ASC'

    query = f"""
        SELECT d.*, dep.name AS department_name,
               COUNT(DISTINCT a.appointment_id) AS total_appointments
        FROM doctors d
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
        {where_clause}
        GROUP BY d.doctor_id
        ORDER BY d.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    return execute_query(query, tuple(params), fetch=True)


def get_doctor_count(search=None):
    """Get total doctor count."""
    if search:
        query = "SELECT COUNT(*) as count FROM doctors WHERE name LIKE %s OR specialization LIKE %s"
        search_param = f"%{search}%"
        result = execute_query(query, (search_param, search_param), fetchone=True)
    else:
        query = "SELECT COUNT(*) as count FROM doctors"
        result = execute_query(query, fetchone=True)
    return result['count'] if result else 0


def get_doctor_by_id(doctor_id):
    """Get single doctor with department info."""
    query = """
        SELECT d.*, dep.name AS department_name
        FROM doctors d
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        WHERE d.doctor_id = %s
    """
    return execute_query(query, (doctor_id,), fetchone=True)


def get_all_doctors_list():
    """Get simple list of all doctors for dropdowns."""
    query = "SELECT doctor_id, name, specialization FROM doctors ORDER BY name"
    return execute_query(query, fetch=True) or []


def add_doctor(name, specialization, contact, email, department_id, schedule):
    """Insert a new doctor."""
    query = """
        INSERT INTO doctors (name, specialization, contact, email, department_id, schedule)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    dept_id = department_id if department_id else None
    return execute_query(query, (name, specialization, contact, email, dept_id, schedule), commit=True)


def update_doctor(doctor_id, name, specialization, contact, email, department_id, schedule):
    """Update a doctor record."""
    query = """
        UPDATE doctors
        SET name = %s, specialization = %s, contact = %s,
            email = %s, department_id = %s, schedule = %s
        WHERE doctor_id = %s
    """
    dept_id = department_id if department_id else None
    return execute_query(
        query,
        (name, specialization, contact, email, dept_id, schedule, doctor_id),
        commit=True
    )


def delete_doctor(doctor_id):
    """Delete a doctor record."""
    query = "DELETE FROM doctors WHERE doctor_id = %s"
    return execute_query(query, (doctor_id,), commit=True)
