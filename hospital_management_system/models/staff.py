"""
Staff model - CRUD operations for staff table.
"""
from models.db import execute_query


def get_all_staff(page=1, per_page=10, search=None, sort_by='staff_id', sort_order='ASC'):
    """Get all staff with pagination, search, sorting, and department JOIN."""
    offset = (page - 1) * per_page
    where_clause = ""
    params = []

    if search:
        where_clause = "WHERE s.name LIKE %s OR s.role LIKE %s"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    allowed_sorts = ['staff_id', 'name', 'role', 'contact', 'created_at']
    if sort_by not in allowed_sorts:
        sort_by = 'staff_id'
    if sort_order not in ('ASC', 'DESC'):
        sort_order = 'ASC'

    query = f"""
        SELECT s.*, dep.name AS department_name
        FROM staff s
        LEFT JOIN departments dep ON s.department_id = dep.department_id
        {where_clause}
        GROUP BY s.staff_id
        ORDER BY s.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    return execute_query(query, tuple(params), fetch=True)


def get_staff_count(search=None):
    """Get total staff count."""
    if search:
        query = "SELECT COUNT(*) as count FROM staff WHERE name LIKE %s OR role LIKE %s"
        search_param = f"%{search}%"
        result = execute_query(query, (search_param, search_param), fetchone=True)
    else:
        query = "SELECT COUNT(*) as count FROM staff"
        result = execute_query(query, fetchone=True)
    return result['count'] if result else 0


def get_staff_by_id(staff_id):
    """Get single staff member with department info."""
    query = """
        SELECT s.*, dep.name AS department_name
        FROM staff s
        LEFT JOIN departments dep ON s.department_id = dep.department_id
        WHERE s.staff_id = %s
    """
    return execute_query(query, (staff_id,), fetchone=True)


def add_staff(name, role, contact, email, department_id):
    """Insert new staff."""
    query = """
        INSERT INTO staff (name, role, contact, email, department_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    dept_id = department_id if department_id else None
    return execute_query(query, (name, role, contact, email, dept_id), commit=True)


def update_staff(staff_id, name, role, contact, email, department_id):
    """Update a staff record."""
    query = """
        UPDATE staff SET name = %s, role = %s, contact = %s, email = %s, department_id = %s
        WHERE staff_id = %s
    """
    dept_id = department_id if department_id else None
    return execute_query(query, (name, role, contact, email, dept_id, staff_id), commit=True)


def delete_staff(staff_id):
    """Delete a staff record."""
    query = "DELETE FROM staff WHERE staff_id = %s"
    return execute_query(query, (staff_id,), commit=True)
