"""
Department model - CRUD operations for departments table.
"""
from models.db import execute_query


def get_all_departments():
    """Get all departments with doctor and staff counts using JOINs and GROUP BY."""
    query = """
        SELECT dep.*,
               COUNT(DISTINCT d.doctor_id) AS doctor_count,
               COUNT(DISTINCT s.staff_id) AS staff_count
        FROM departments dep
        LEFT JOIN doctors d ON dep.department_id = d.department_id
        LEFT JOIN staff s ON dep.department_id = s.department_id
        GROUP BY dep.department_id
        ORDER BY dep.name
    """
    return execute_query(query, fetch=True) or []


def get_department_by_id(department_id):
    """Get single department."""
    query = "SELECT * FROM departments WHERE department_id = %s"
    return execute_query(query, (department_id,), fetchone=True)


def add_department(name, description):
    """Insert a new department."""
    query = "INSERT INTO departments (name, description) VALUES (%s, %s)"
    return execute_query(query, (name, description), commit=True)


def update_department(department_id, name, description):
    """Update a department."""
    query = "UPDATE departments SET name = %s, description = %s WHERE department_id = %s"
    return execute_query(query, (name, description, department_id), commit=True)


def delete_department(department_id):
    """Delete a department."""
    query = "DELETE FROM departments WHERE department_id = %s"
    return execute_query(query, (department_id,), commit=True)
