"""
Prescription routes - CRUD operations for prescriptions.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required, role_required
from models.prescription import (
    get_all_prescriptions, get_prescription_count, get_prescription_by_id,
    get_prescriptions_by_patient, add_prescription, update_prescription,
    delete_prescription
)
from models.patient import get_all_patients
from models.doctor import get_all_doctors_list
from config import Config

prescription_bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')


@prescription_bp.route('/')
@login_required
def list_prescriptions():
    """List all prescriptions."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    sort_by = request.args.get('sort_by', 'prescribed_date', type=str)
    sort_order = request.args.get('sort_order', 'DESC', type=str)

    # If patient role, show only their prescriptions
    if session.get('role') == 'Patient' and session.get('reference_id'):
        prescriptions = get_prescriptions_by_patient(session['reference_id'])
        return render_template('prescriptions/list.html',
                               prescriptions=prescriptions or [],
                               page=1, total_pages=1, total=len(prescriptions or []),
                               search='', sort_by=sort_by, sort_order=sort_order)

    prescriptions = get_all_prescriptions(
        page=page, per_page=Config.ITEMS_PER_PAGE,
        search=search or None, sort_by=sort_by, sort_order=sort_order
    )
    total = get_prescription_count(search=search or None)
    total_pages = (total + Config.ITEMS_PER_PAGE - 1) // Config.ITEMS_PER_PAGE

    return render_template('prescriptions/list.html',
                           prescriptions=prescriptions or [],
                           page=page, total_pages=total_pages, total=total,
                           search=search, sort_by=sort_by, sort_order=sort_order)


@prescription_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Doctor')
def add():
    """Add a new prescription."""
    patients = get_all_patients(page=1, per_page=1000) or []
    doctors = get_all_doctors_list()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        medicines = request.form.get('medicines', '').strip()
        dosage = request.form.get('dosage', '').strip()
        notes = request.form.get('notes', '').strip()
        prescribed_date = request.form.get('prescribed_date', '').strip()

        if not patient_id or not doctor_id or not medicines or not prescribed_date:
            flash('Please fill in all required fields.', 'danger')
            return render_template('prescriptions/add.html', patients=patients, doctors=doctors)

        result = add_prescription(patient_id, doctor_id, medicines, dosage, notes, prescribed_date)
        if result is not None:
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('prescriptions.list_prescriptions'))
        else:
            flash('Error adding prescription.', 'danger')

    return render_template('prescriptions/add.html', patients=patients, doctors=doctors)


@prescription_bp.route('/edit/<int:prescription_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Doctor')
def edit(prescription_id):
    """Edit a prescription."""
    prescription = get_prescription_by_id(prescription_id)
    if not prescription:
        flash('Prescription not found.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))

    patients = get_all_patients(page=1, per_page=1000) or []
    doctors = get_all_doctors_list()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        medicines = request.form.get('medicines', '').strip()
        dosage = request.form.get('dosage', '').strip()
        notes = request.form.get('notes', '').strip()
        prescribed_date = request.form.get('prescribed_date', '').strip()

        if not patient_id or not doctor_id or not medicines or not prescribed_date:
            flash('Please fill in all required fields.', 'danger')
            return render_template('prescriptions/edit.html',
                                   prescription=prescription, patients=patients, doctors=doctors)

        result = update_prescription(prescription_id, patient_id, doctor_id,
                                     medicines, dosage, notes, prescribed_date)
        if result is not None:
            flash('Prescription updated successfully!', 'success')
            return redirect(url_for('prescriptions.list_prescriptions'))
        else:
            flash('Error updating prescription.', 'danger')

    return render_template('prescriptions/edit.html',
                           prescription=prescription, patients=patients, doctors=doctors)


@prescription_bp.route('/view/<int:prescription_id>')
@login_required
def view(prescription_id):
    """View prescription details."""
    prescription = get_prescription_by_id(prescription_id)
    if not prescription:
        flash('Prescription not found.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))
    return render_template('prescriptions/view.html', prescription=prescription)


@prescription_bp.route('/delete/<int:prescription_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(prescription_id):
    """Delete a prescription."""
    result = delete_prescription(prescription_id)
    if result is not None:
        flash('Prescription deleted successfully!', 'success')
    else:
        flash('Error deleting prescription.', 'danger')
    return redirect(url_for('prescriptions.list_prescriptions'))
