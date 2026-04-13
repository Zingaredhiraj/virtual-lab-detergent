"""
Department routes - CRUD operations for department management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models.department import (
    get_all_departments, get_department_by_id,
    add_department, update_department, delete_department
)

department_bp = Blueprint('departments', __name__, url_prefix='/departments')


@department_bp.route('/')
@login_required
def list_departments():
    """List all departments with doctor and staff counts."""
    departments = get_all_departments()
    return render_template('departments/list.html', departments=departments)


@department_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add():
    """Add a new department."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Department name is required.', 'danger')
            return render_template('departments/add.html')

        result = add_department(name, description)
        if result is not None:
            flash('Department added successfully!', 'success')
            return redirect(url_for('departments.list_departments'))
        else:
            flash('Error adding department. Name may already exist.', 'danger')

    return render_template('departments/add.html')


@department_bp.route('/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit(department_id):
    """Edit a department."""
    department = get_department_by_id(department_id)
    if not department:
        flash('Department not found.', 'danger')
        return redirect(url_for('departments.list_departments'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Department name is required.', 'danger')
            return render_template('departments/edit.html', department=department)

        result = update_department(department_id, name, description)
        if result is not None:
            flash('Department updated successfully!', 'success')
            return redirect(url_for('departments.list_departments'))
        else:
            flash('Error updating department.', 'danger')

    return render_template('departments/edit.html', department=department)


@department_bp.route('/delete/<int:department_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(department_id):
    """Delete a department."""
    result = delete_department(department_id)
    if result is not None:
        flash('Department deleted successfully!', 'success')
    else:
        flash('Error deleting department.', 'danger')
    return redirect(url_for('departments.list_departments'))
