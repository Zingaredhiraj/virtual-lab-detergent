"""
Patient routes - CRUD operations for patient management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models.patient import (
    get_all_patients, get_patient_count, get_patient_by_id,
    add_patient, update_patient, delete_patient
)
from config import Config

patient_bp = Blueprint('patients', __name__, url_prefix='/patients')


@patient_bp.route('/')
@login_required
def list_patients():
    """List all patients with pagination, search, and sorting."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    sort_by = request.args.get('sort_by', 'patient_id', type=str)
    sort_order = request.args.get('sort_order', 'ASC', type=str)

    patients = get_all_patients(
        page=page, per_page=Config.ITEMS_PER_PAGE,
        search=search or None, sort_by=sort_by, sort_order=sort_order
    )
    total = get_patient_count(search=search or None)
    total_pages = (total + Config.ITEMS_PER_PAGE - 1) // Config.ITEMS_PER_PAGE

    return render_template('patients/list.html',
                           patients=patients or [],
                           page=page, total_pages=total_pages, total=total,
                           search=search, sort_by=sort_by, sort_order=sort_order)


@patient_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Staff')
def add():
    """Add a new patient."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        medical_history = request.form.get('medical_history', '').strip()

        if not name or not age or not gender or not contact:
            flash('Please fill in all required fields.', 'danger')
            return render_template('patients/add.html')

        result = add_patient(name, age, gender, contact, email, address, medical_history)
        if result is not None:
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients.list_patients'))
        else:
            flash('Error adding patient. Please try again.', 'danger')

    return render_template('patients/add.html')


@patient_bp.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Staff')
def edit(patient_id):
    """Edit a patient record."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        medical_history = request.form.get('medical_history', '').strip()

        if not name or not age or not gender or not contact:
            flash('Please fill in all required fields.', 'danger')
            return render_template('patients/edit.html', patient=patient)

        result = update_patient(patient_id, name, age, gender, contact, email, address, medical_history)
        if result is not None:
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('patients.list_patients'))
        else:
            flash('Error updating patient.', 'danger')

    return render_template('patients/edit.html', patient=patient)


@patient_bp.route('/view/<int:patient_id>')
@login_required
def view(patient_id):
    """View patient details."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))

    # Get related appointments and prescriptions
    from models.appointment import get_appointments_by_patient
    from models.prescription import get_prescriptions_by_patient
    from models.bill import get_bills_by_patient

    appointments = get_appointments_by_patient(patient_id)
    prescriptions = get_prescriptions_by_patient(patient_id)
    bills = get_bills_by_patient(patient_id)

    return render_template('patients/view.html',
                           patient=patient,
                           appointments=appointments or [],
                           prescriptions=prescriptions or [],
                           bills=bills or [])


@patient_bp.route('/delete/<int:patient_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(patient_id):
    """Delete a patient record."""
    result = delete_patient(patient_id)
    if result is not None:
        flash('Patient deleted successfully!', 'success')
    else:
        flash('Error deleting patient.', 'danger')
    return redirect(url_for('patients.list_patients'))
