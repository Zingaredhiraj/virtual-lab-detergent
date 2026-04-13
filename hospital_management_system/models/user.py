"""
User model for authentication.
Handles login, registration, and session management.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import execute_query


def create_user(username, password, role, reference_id=None):
    """Create a new user with hashed password."""
    password_hash = generate_password_hash(password)
    query = """
        INSERT INTO users (username, password_hash, role, reference_id)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (username, password_hash, role, reference_id), commit=True)


def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    query = "SELECT * FROM users WHERE username = %s AND is_active = 1"
    user = execute_query(query, (username,), fetchone=True)

    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


def get_user_by_id(user_id):
    """Get user by ID."""
    query = "SELECT * FROM users WHERE user_id = %s"
    return execute_query(query, (user_id,), fetchone=True)


def get_all_users():
    """Get all users."""
    query = "SELECT user_id, username, role, reference_id, is_active, created_at FROM users ORDER BY created_at DESC"
    return execute_query(query, fetch=True)


def update_user(user_id, username, role, is_active):
    """Update user details."""
    query = """
        UPDATE users SET username = %s, role = %s, is_active = %s
        WHERE user_id = %s
    """
    return execute_query(query, (username, role, is_active, user_id), commit=True)


def delete_user(user_id):
    """Delete a user."""
    query = "DELETE FROM users WHERE user_id = %s"
    return execute_query(query, (user_id,), commit=True)


def create_default_users():
    """Create default users for demo purposes."""
    defaults = [
        ('admin', 'admin123', 'Admin', None),
        ('doctor1', 'doctor123', 'Doctor', 1),
        ('doctor2', 'doctor123', 'Doctor', 2),
        ('patient1', 'patient123', 'Patient', 1),
        ('patient2', 'patient123', 'Patient', 2),
        ('staff1', 'staff123', 'Staff', 1),
    ]

    for username, password, role, ref_id in defaults:
        # Check if user already exists
        existing = execute_query(
            "SELECT user_id FROM users WHERE username = %s",
            (username,), fetchone=True
        )
        if not existing:
            create_user(username, password, role, ref_id)
