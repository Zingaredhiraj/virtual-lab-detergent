"""
Dashboard routes - Main dashboard with real-time DB data.
"""
from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.db import execute_query

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard showing real-time database statistics."""
    # Total counts using aggregate queries
    stats = {}

    patient_count = execute_query("SELECT COUNT(*) as count FROM patients", fetchone=True)
    stats['total_patients'] = patient_count['count'] if patient_count else 0

    doctor_count = execute_query("SELECT COUNT(*) as count FROM doctors", fetchone=True)
    stats['total_doctors'] = doctor_count['count'] if doctor_count else 0

    staff_count = execute_query("SELECT COUNT(*) as count FROM staff", fetchone=True)
    stats['total_staff'] = staff_count['count'] if staff_count else 0

    dept_count = execute_query("SELECT COUNT(*) as count FROM departments", fetchone=True)
    stats['total_departments'] = dept_count['count'] if dept_count else 0

    # Appointment statistics using GROUP BY
    appointment_stats = execute_query("""
        SELECT status, COUNT(*) as count
        FROM appointments
        GROUP BY status
    """, fetch=True)
    stats['appointments'] = {row['status']: row['count'] for row in appointment_stats} if appointment_stats else {}
    stats['total_appointments'] = sum(stats['appointments'].values())

    # Billing summary using GROUP BY and SUM
    billing_summary = execute_query("""
        SELECT
            payment_status,
            COUNT(*) as count,
            COALESCE(SUM(amount), 0) as total
        FROM bills
        GROUP BY payment_status
    """, fetch=True)
    stats['billing'] = {}
    stats['total_revenue'] = 0
    if billing_summary:
        for row in billing_summary:
            stats['billing'][row['payment_status']] = {
                'count': row['count'],
                'total': float(row['total'])
            }
            stats['total_revenue'] += float(row['total'])

    # Recent appointments using JOIN
    recent_appointments = execute_query("""
        SELECT a.*, p.name AS patient_name, d.name AS doctor_name
        FROM appointments a
        INNER JOIN patients p ON a.patient_id = p.patient_id
        INNER JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC
        LIMIT 5
    """, fetch=True)
    stats['recent_appointments'] = recent_appointments or []

    # Recent bills using JOIN
    recent_bills = execute_query("""
        SELECT b.*, p.name AS patient_name
        FROM bills b
        INNER JOIN patients p ON b.patient_id = p.patient_id
        ORDER BY b.created_at DESC
        LIMIT 5
    """, fetch=True)
    stats['recent_bills'] = recent_bills or []

    # Department-wise doctor count using JOIN and GROUP BY
    dept_doctors = execute_query("""
        SELECT dep.name AS department, COUNT(d.doctor_id) AS doctor_count
        FROM departments dep
        LEFT JOIN doctors d ON dep.department_id = d.department_id
        GROUP BY dep.department_id, dep.name
        ORDER BY doctor_count DESC
    """, fetch=True)
    stats['dept_doctors'] = dept_doctors or []

    # Build appointment_status list for template
    appointment_status = []
    if appointment_stats:
        for row in appointment_stats:
            appointment_status.append({'status': row['status'], 'count': row['count']})

    # Build billing_summary list for template
    billing_summary_list = []
    if billing_summary:
        for row in billing_summary:
            billing_summary_list.append({
                'payment_status': row['payment_status'],
                'total_bills': row['count'],
                'total_amount': float(row['total']),
                'avg_amount': float(row['total']) / row['count'] if row['count'] else 0
            })

    return render_template('dashboard.html',
                           total_patients=stats['total_patients'],
                           total_doctors=stats['total_doctors'],
                           total_appointments=stats['total_appointments'],
                           total_revenue=stats['total_revenue'],
                           appointment_status=appointment_status,
                           billing_summary=billing_summary_list,
                           recent_appointments=stats['recent_appointments'],
                           dept_doctors=stats['dept_doctors'])
