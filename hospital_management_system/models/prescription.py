"""
Prescription model - CRUD operations for prescriptions table.
"""
from models.db import execute_query


def get_all_prescriptions(page=1, per_page=10, search=None,
                          sort_by='prescribed_date', sort_order='DESC'):
    """Get all prescriptions with patient and doctor names using JOINs."""
    offset = (page - 1) * per_page
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR d.name LIKE %s OR pr.medicines LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    allowed_sorts = ['prescription_id', 'prescribed_date', 'created_at']
    if sort_by not in allowed_sorts:
        sort_by = 'prescribed_date'
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'DESC'

    query = f"""
        SELECT pr.*, p.name AS patient_name, d.name AS doctor_name,
               d.specialization
        FROM prescriptions pr
        INNER JOIN patients p ON pr.patient_id = p.patient_id
        INNER JOIN doctors d ON pr.doctor_id = d.doctor_id
        {where_clause}
        ORDER BY pr.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    return execute_query(query, tuple(params), fetch=True)


def get_prescription_count(search=None):
    """Get total prescription count."""
    if search:
        query = """
            SELECT COUNT(*) as count FROM prescriptions pr
            INNER JOIN patients p ON pr.patient_id = p.patient_id
            INNER JOIN doctors d ON pr.doctor_id = d.doctor_id
            WHERE p.name LIKE %s OR d.name LIKE %s OR pr.medicines LIKE %s
        """
        search_param = f"%{search}%"
        result = execute_query(query, (search_param, search_param, search_param), fetchone=True)
    else:
        query = "SELECT COUNT(*) as count FROM prescriptions"
        result = execute_query(query, fetchone=True)
    return result['count'] if result else 0


def get_prescription_by_id(prescription_id):
    """Get single prescription with patient and doctor info."""
    query = """
        SELECT pr.*, p.name AS patient_name, d.name AS doctor_name,
               d.specialization
        FROM prescriptions pr
        INNER JOIN patients p ON pr.patient_id = p.patient_id
        INNER JOIN doctors d ON pr.doctor_id = d.doctor_id
        WHERE pr.prescription_id = %s
    """
    return execute_query(query, (prescription_id,), fetchone=True)


def get_prescriptions_by_patient(patient_id):
    """Get prescriptions for a specific patient."""
    query = """
        SELECT pr.*, d.name AS doctor_name, d.specialization
        FROM prescriptions pr
        INNER JOIN doctors d ON pr.doctor_id = d.doctor_id
        WHERE pr.patient_id = %s
        ORDER BY pr.prescribed_date DESC
    """
    return execute_query(query, (patient_id,), fetch=True)


def get_prescriptions_by_doctor(doctor_id):
    """Get prescriptions by a specific doctor."""
    query = """
        SELECT pr.*, p.name AS patient_name
        FROM prescriptions pr
        INNER JOIN patients p ON pr.patient_id = p.patient_id
        WHERE pr.doctor_id = %s
        ORDER BY pr.prescribed_date DESC
    """
    return execute_query(query, (doctor_id,), fetch=True)


def add_prescription(patient_id, doctor_id, medicines, dosage, notes, prescribed_date):
    """Insert a new prescription."""
    query = """
        INSERT INTO prescriptions (patient_id, doctor_id, medicines, dosage, notes, prescribed_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(
        query,
        (patient_id, doctor_id, medicines, dosage, notes, prescribed_date),
        commit=True
    )


def update_prescription(prescription_id, patient_id, doctor_id, medicines, dosage, notes, prescribed_date):
    """Update a prescription."""
    query = """
        UPDATE prescriptions
        SET patient_id = %s, doctor_id = %s, medicines = %s,
            dosage = %s, notes = %s, prescribed_date = %s
        WHERE prescription_id = %s
    """
    return execute_query(
        query,
        (patient_id, doctor_id, medicines, dosage, notes, prescribed_date, prescription_id),
        commit=True
    )


def delete_prescription(prescription_id):
    """Delete a prescription."""
    query = "DELETE FROM prescriptions WHERE prescription_id = %s"
    return execute_query(query, (prescription_id,), commit=True)
