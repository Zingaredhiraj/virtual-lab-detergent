"""
Authentication routes - Login, Logout, Session management.
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import authenticate_user, get_user_by_id

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')

        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['reference_id'] = user['reference_id']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
