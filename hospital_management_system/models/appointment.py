"""
Appointment model - CRUD operations for appointments table.
"""
from models.db import execute_query


def get_all_appointments(page=1, per_page=10, search=None, status_filter=None,
                         sort_by='appointment_date', sort_order='DESC'):
    """Get all appointments with patient and doctor names using JOINs."""
    offset = (page - 1) * per_page
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR d.name LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if status_filter:
        conditions.append("a.status = %s")
        params.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    allowed_sorts = ['appointment_id', 'appointment_date', 'status', 'created_at']
    if sort_by not in allowed_sorts:
        sort_by = 'appointment_date'
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'DESC'

    query = f"""
        SELECT a.*, p.name AS patient_name, d.name AS doctor_name,
               d.specialization
        FROM appointments a
        INNER JOIN patients p ON a.patient_id = p.patient_id
        INNER JOIN doctors d ON a.doctor_id = d.doctor_id
        {where_clause}
        ORDER BY a.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    return execute_query(query, tuple(params), fetch=True)


def get_appointment_count(search=None, status_filter=None):
    """Get total appointment count with optional filters."""
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR d.name LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if status_filter:
        conditions.append("a.status = %s")
        params.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT COUNT(*) as count FROM appointments a
        INNER JOIN patients p ON a.patient_id = p.patient_id
        INNER JOIN doctors d ON a.doctor_id = d.doctor_id
        {where_clause}
    """
    result = execute_query(query, tuple(params), fetchone=True)
    return result['count'] if result else 0


def get_appointment_by_id(appointment_id):
    """Get single appointment with patient and doctor details."""
    query = """
        SELECT a.*, p.name AS patient_name, d.name AS doctor_name,
               d.specialization
        FROM appointments a
        INNER JOIN patients p ON a.patient_id = p.patient_id
        INNER JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = %s
    """
    return execute_query(query, (appointment_id,), fetchone=True)


def get_appointments_by_doctor(doctor_id):
    """Get appointments for a specific doctor."""
    query = """
        SELECT a.*, p.name AS patient_name
        FROM appointments a
        INNER JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date DESC
    """
    return execute_query(query, (doctor_id,), fetch=True)


def get_appointments_by_patient(patient_id):
    """Get appointments for a specific patient."""
    query = """
        SELECT a.*, d.name AS doctor_name, d.specialization
        FROM appointments a
        INNER JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC
    """
    return execute_query(query, (patient_id,), fetch=True)


def add_appointment(patient_id, doctor_id, appointment_date, status, notes):
    """Insert a new appointment."""
    query = """
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(query, (patient_id, doctor_id, appointment_date, status, notes), commit=True)


def update_appointment(appointment_id, patient_id, doctor_id, appointment_date, status, notes):
    """Update an appointment."""
    query = """
        UPDATE appointments
        SET patient_id = %s, doctor_id = %s, appointment_date = %s,
            status = %s, notes = %s
        WHERE appointment_id = %s
    """
    return execute_query(
        query,
        (patient_id, doctor_id, appointment_date, status, notes, appointment_id),
        commit=True
    )


def update_appointment_status(appointment_id, status):
    """Update only the status of an appointment."""
    query = "UPDATE appointments SET status = %s WHERE appointment_id = %s"
    return execute_query(query, (status, appointment_id), commit=True)


def delete_appointment(appointment_id):
    """Delete an appointment."""
    query = "DELETE FROM appointments WHERE appointment_id = %s"
    return execute_query(query, (appointment_id,), commit=True)
