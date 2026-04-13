"""
Appointment routes - CRUD operations for appointment management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models.appointment import (
    get_all_appointments, get_appointment_count, get_appointment_by_id,
    add_appointment, update_appointment, update_appointment_status,
    delete_appointment
)
from models.patient import get_all_patients
from models.doctor import get_all_doctors_list
from config import Config

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointment_bp.route('/')
@login_required
def list_appointments():
    """List all appointments with filters."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status_filter = request.args.get('status', '', type=str).strip()
    sort_by = request.args.get('sort_by', 'appointment_date', type=str)
    sort_order = request.args.get('sort_order', 'DESC', type=str)

    appointments = get_all_appointments(
        page=page, per_page=Config.ITEMS_PER_PAGE,
        search=search or None, status_filter=status_filter or None,
        sort_by=sort_by, sort_order=sort_order
    )
    total = get_appointment_count(search=search or None, status_filter=status_filter or None)
    total_pages = (total + Config.ITEMS_PER_PAGE - 1) // Config.ITEMS_PER_PAGE

    return render_template('appointments/list.html',
                           appointments=appointments or [],
                           page=page, total_pages=total_pages, total=total,
                           search=search, status_filter=status_filter,
                           sort_by=sort_by, sort_order=sort_order)


@appointment_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Staff', 'Doctor')
def add():
    """Add a new appointment."""
    patients = get_all_patients(page=1, per_page=1000) or []
    doctors = get_all_doctors_list()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        appointment_date = request.form.get('appointment_date', '').strip()
        status = request.form.get('status', 'Pending')
        notes = request.form.get('notes', '').strip()

        if not patient_id or not doctor_id or not appointment_date:
            flash('Please fill in all required fields.', 'danger')
            return render_template('appointments/add.html', patients=patients, doctors=doctors)

        result = add_appointment(patient_id, doctor_id, appointment_date, status, notes)
        if result is not None:
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('appointments.list_appointments'))
        else:
            flash('Error scheduling appointment.', 'danger')

    return render_template('appointments/add.html', patients=patients, doctors=doctors)


@appointment_bp.route('/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Staff', 'Doctor')
def edit(appointment_id):
    """Edit an appointment."""
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    patients = get_all_patients(page=1, per_page=1000) or []
    doctors = get_all_doctors_list()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        appointment_date = request.form.get('appointment_date', '').strip()
        status = request.form.get('status', 'Pending')
        notes = request.form.get('notes', '').strip()

        if not patient_id or not doctor_id or not appointment_date:
            flash('Please fill in all required fields.', 'danger')
            return render_template('appointments/edit.html',
                                   appointment=appointment, patients=patients, doctors=doctors)

        result = update_appointment(appointment_id, patient_id, doctor_id, appointment_date, status, notes)
        if result is not None:
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('appointments.list_appointments'))
        else:
            flash('Error updating appointment.', 'danger')

    return render_template('appointments/edit.html',
                           appointment=appointment, patients=patients, doctors=doctors)


@appointment_bp.route('/status/<int:appointment_id>/<status>', methods=['POST'])
@login_required
@role_required('Admin', 'Staff', 'Doctor')
def change_status(appointment_id, status):
    """Quick status update for an appointment."""
    valid_statuses = ['Pending', 'Confirmed', 'Completed', 'Cancelled']
    if status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    result = update_appointment_status(appointment_id, status)
    if result is not None:
        flash(f'Appointment status updated to {status}.', 'success')
    else:
        flash('Error updating appointment status.', 'danger')
    return redirect(url_for('appointments.list_appointments'))


@appointment_bp.route('/delete/<int:appointment_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(appointment_id):
    """Delete an appointment."""
    result = delete_appointment(appointment_id)
    if result is not None:
        flash('Appointment deleted successfully!', 'success')
    else:
        flash('Error deleting appointment.', 'danger')
    return redirect(url_for('appointments.list_appointments'))
