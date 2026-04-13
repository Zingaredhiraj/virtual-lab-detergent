"""
Doctor routes - CRUD operations for doctor management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models.doctor import (
    get_all_doctors, get_doctor_count, get_doctor_by_id,
    add_doctor, update_doctor, delete_doctor
)
from models.department import get_all_departments
from config import Config

doctor_bp = Blueprint('doctors', __name__, url_prefix='/doctors')


@doctor_bp.route('/')
@login_required
def list_doctors():
    """List all doctors with pagination, search, and sorting."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    sort_by = request.args.get('sort_by', 'doctor_id', type=str)
    sort_order = request.args.get('sort_order', 'ASC', type=str)

    doctors = get_all_doctors(
        page=page, per_page=Config.ITEMS_PER_PAGE,
        search=search or None, sort_by=sort_by, sort_order=sort_order
    )
    total = get_doctor_count(search=search or None)
    total_pages = (total + Config.ITEMS_PER_PAGE - 1) // Config.ITEMS_PER_PAGE

    return render_template('doctors/list.html',
                           doctors=doctors or [],
                           page=page, total_pages=total_pages, total=total,
                           search=search, sort_by=sort_by, sort_order=sort_order)


@doctor_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add():
    """Add a new doctor."""
    departments = get_all_departments()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        department_id = request.form.get('department_id', type=int)
        schedule = request.form.get('schedule', '').strip()

        if not name or not specialization or not contact:
            flash('Please fill in all required fields.', 'danger')
            return render_template('doctors/add.html', departments=departments)

        result = add_doctor(name, specialization, contact, email, department_id, schedule)
        if result is not None:
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('doctors.list_doctors'))
        else:
            flash('Error adding doctor.', 'danger')

    return render_template('doctors/add.html', departments=departments)


@doctor_bp.route('/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit(doctor_id):
    """Edit a doctor record."""
    doctor = get_doctor_by_id(doctor_id)
    departments = get_all_departments()

    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('doctors.list_doctors'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        department_id = request.form.get('department_id', type=int)
        schedule = request.form.get('schedule', '').strip()

        if not name or not specialization or not contact:
            flash('Please fill in all required fields.', 'danger')
            return render_template('doctors/edit.html', doctor=doctor, departments=departments)

        result = update_doctor(doctor_id, name, specialization, contact, email, department_id, schedule)
        if result is not None:
            flash('Doctor updated successfully!', 'success')
            return redirect(url_for('doctors.list_doctors'))
        else:
            flash('Error updating doctor.', 'danger')

    return render_template('doctors/edit.html', doctor=doctor, departments=departments)


@doctor_bp.route('/delete/<int:doctor_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(doctor_id):
    """Delete a doctor record."""
    result = delete_doctor(doctor_id)
    if result is not None:
        flash('Doctor deleted successfully!', 'success')
    else:
        flash('Error deleting doctor.', 'danger')
    return redirect(url_for('doctors.list_doctors'))
