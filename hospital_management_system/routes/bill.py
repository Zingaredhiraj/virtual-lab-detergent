"""
Billing routes - CRUD with transaction handling.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models.bill import (
    get_all_bills, get_bill_count, get_bill_by_id,
    add_bill, update_bill, delete_bill, get_billing_summary
)
from models.patient import get_all_patients
from config import Config

bill_bp = Blueprint('bills', __name__, url_prefix='/bills')


@bill_bp.route('/')
@login_required
def list_bills():
    """List all bills with filters."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status_filter = request.args.get('status', '', type=str).strip()
    sort_by = request.args.get('sort_by', 'created_at', type=str)
    sort_order = request.args.get('sort_order', 'DESC', type=str)

    bills = get_all_bills(
        page=page, per_page=Config.ITEMS_PER_PAGE,
        search=search or None, status_filter=status_filter or None,
        sort_by=sort_by, sort_order=sort_order
    )
    total = get_bill_count(search=search or None, status_filter=status_filter or None)
    total_pages = (total + Config.ITEMS_PER_PAGE - 1) // Config.ITEMS_PER_PAGE

    # Get billing summary
    summary = get_billing_summary()

    return render_template('bills/list.html',
                           bills=bills or [],
                           page=page, total_pages=total_pages, total=total,
                           search=search, status_filter=status_filter,
                           sort_by=sort_by, sort_order=sort_order,
                           summary=summary or [])


@bill_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Staff')
def add():
    """Generate a new bill."""
    patients = get_all_patients(page=1, per_page=1000) or []

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', '').strip()
        payment_status = request.form.get('payment_status', 'Unpaid')
        payment_date = request.form.get('payment_date', '').strip() or None

        if not patient_id or not amount:
            flash('Please fill in all required fields.', 'danger')
            return render_template('bills/add.html', patients=patients)

        result = add_bill(patient_id, amount, description, payment_status, payment_date)
        if result:
            flash('Bill generated successfully!', 'success')
            return redirect(url_for('bills.list_bills'))
        else:
            flash('Error generating bill. Transaction rolled back.', 'danger')

    return render_template('bills/add.html', patients=patients)


@bill_bp.route('/edit/<int:bill_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Staff')
def edit(bill_id):
    """Edit a bill."""
    bill = get_bill_by_id(bill_id)
    if not bill:
        flash('Bill not found.', 'danger')
        return redirect(url_for('bills.list_bills'))

    patients = get_all_patients(page=1, per_page=1000) or []

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', '').strip()
        payment_status = request.form.get('payment_status', 'Unpaid')
        payment_date = request.form.get('payment_date', '').strip() or None

        if not patient_id or not amount:
            flash('Please fill in all required fields.', 'danger')
            return render_template('bills/edit.html', bill=bill, patients=patients)

        result = update_bill(bill_id, patient_id, amount, description, payment_status, payment_date)
        if result:
            flash('Bill updated successfully!', 'success')
            return redirect(url_for('bills.list_bills'))
        else:
            flash('Error updating bill. Transaction rolled back.', 'danger')

    return render_template('bills/edit.html', bill=bill, patients=patients)


@bill_bp.route('/view/<int:bill_id>')
@login_required
def view(bill_id):
    """View bill details."""
    bill = get_bill_by_id(bill_id)
    if not bill:
        flash('Bill not found.', 'danger')
        return redirect(url_for('bills.list_bills'))
    return render_template('bills/view.html', bill=bill)


@bill_bp.route('/delete/<int:bill_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete(bill_id):
    """Delete a bill."""
    result = delete_bill(bill_id)
    if result is not None:
        flash('Bill deleted successfully!', 'success')
    else:
        flash('Error deleting bill.', 'danger')
    return redirect(url_for('bills.list_bills'))
