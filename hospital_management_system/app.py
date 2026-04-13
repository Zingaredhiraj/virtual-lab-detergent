"""
Hospital Management System - Main Flask Application
Full-stack web application with MySQL database integration.
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models.db import init_database
from models.user import create_default_users


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.patient import patient_bp
    from routes.doctor import doctor_bp
    from routes.staff import staff_bp
    from routes.department import department_bp
    from routes.appointment import appointment_bp
    from routes.bill import bill_bp
    from routes.prescription import prescription_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(prescription_bp)

    # Context processor to make session data available in all templates
    @app.context_processor
    def inject_user():
        from flask import session
        return {
            'current_user': {
                'username': session.get('username'),
                'role': session.get('role'),
                'user_id': session.get('user_id')
            }
        }

    return app


def setup_database():
    """Initialize database and create default users."""
    print("Initializing database...")
    if init_database():
        print("Creating default users...")
        create_default_users()
        print("Setup complete!")
    else:
        print("Database initialization failed. Please check MySQL connection.")
        sys.exit(1)


if __name__ == '__main__':
    # Initialize database on first run
    setup_database()

    # Create and run the app
    app = create_app()
    print("\n" + "=" * 50)
    print("Hospital Management System is running!")
    print("=" * 50)
    print("URL: http://localhost:5000")
    print("\nDefault Login Credentials:")
    print("  Admin:   admin / admin123")
    print("  Doctor:  doctor1 / doctor123")
    print("  Patient: patient1 / patient123")
    print("  Staff:   staff1 / staff123")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
