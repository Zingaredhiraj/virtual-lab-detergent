"""
Staff routes - CRUD operations for staff management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models.staff import (
    get_all_staff, get_staff_count, get_staff_by_id,
    add_staff, update_staff, delete_staff
)
from models.department import get_all_departments
from config import Config

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/')
@login_required
def list_staff():
    """List all staff."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    sort_by = request.args.get('sort_by', 'staff_id', type=str)
    sort_order = request.args.get('sort_order', 'ASC', type=str)

    staff_members = get_all_staff(
        page=page, per_page=Config.ITEMS_PER_PAGE,
        search=search or None, sort_by=sort_by, sort_order=sort_order
    )
    total = get_staff_count(search=search or None)
    total_pages = (total + Config.ITEMS_PER_PAGE - 1) // Config.ITEMS_PER_PAGE

    return render_template('staff/list.html',
                           staff_members=staff_members or [],
                           page=page, total_pages=total_pages, total=total,
                           search=search, sort_by=sort_by, sort_order=sort_order)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add():
    """Add new staff."""
    departments = get_all_departments()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        role = request.form.get('role', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        department_id = request.form.get('department_id', type=int)

        if not name or not role or not contact:
            flash('Please fill in all required fields.', 'danger')
            return render_template('staff/add.html', departments=departments)

        result = add_staff(name, role, contact, email, department_id)
        if result is not None:
            flash('Staff member added successfully!', 'success')
            return redirect(url_for('staff.list_staff'))
        else:
            flash('Error adding staff member.', 'danger')

    return render_template('staff/add.html', departments=departments)


@staff_bp.route('/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit(staff_id):
    """Edit a staff record."""
    staff_member = get_staff_by_id(staff_id)
    departments = get_all_departments()

    if not staff_member:
        flash('Staff member not found.', 'danger')
        return redirect(url_for('staff.list_staff'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        role = request.form.get('role', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        department_id = request.form.get('department_id', type=int)

        if not name or not role or not contact:
            flash('Please fill in all required fields.', 'danger')
            return render_template('staff/edit.html', staff_member=staff_member, departments=departments)

        result = update_staff(staff_id, name, role, contact, email, department_id)
        if result is not None:
            flash('Staff member updated successfully!', 'success')
            return redirect(url_for('staff.list_staff'))
        else:
            flash('Error updating staff member.', 'danger')

    return render_template('staff/edit.html', staff_member=staff_member, departments=departments)


@staff_bp.route('/delete/<int:staff_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(staff_id):
    """Delete a staff record."""
    result = delete_staff(staff_id)
    if result is not None:
        flash('Staff member deleted successfully!', 'success')
    else:
        flash('Error deleting staff member.', 'danger')
    return redirect(url_for('staff.list_staff'))
