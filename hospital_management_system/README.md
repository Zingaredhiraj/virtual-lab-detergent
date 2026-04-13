# Hospital Management System

A complete **Full Stack Hospital Management System** built with **Flask**, **MySQL**, and responsive **HTML/CSS**. This application demonstrates complete database integration with CRUD operations, normalized schema design, and advanced SQL features.

## Features

### Functional Modules
- **Authentication System** — Role-based login/logout (Admin, Doctor, Patient, Staff) with session management
- **Patient Management** — Add, view, update, delete patient records with medical history
- **Doctor Management** — Doctor profiles with department assignment and scheduling
- **Staff Management** — Hospital staff records with role and department tracking
- **Department Management** — Hospital departments with doctor/staff counts
- **Appointment System** — Schedule, confirm, complete, or cancel appointments
- **Billing System** — Generate bills with transaction handling and payment tracking
- **Prescription System** — Doctors create prescriptions, patients view their records

### Database Features
- **Normalized Schema** (1NF, 2NF, 3NF) with 8 tables
- **Primary Keys & Foreign Keys** with referential integrity
- **JOIN Queries** — INNER JOIN, LEFT JOIN for cross-table data retrieval
- **GROUP BY & Aggregates** — COUNT, SUM, AVG for dashboard statistics
- **Prepared Statements** — SQL injection prevention
- **Transaction Handling** — Atomic billing operations with rollback support
- **Search, Sort, Filter** — Dynamic query building with pagination
- **Indexes** — Performance optimization on frequently queried columns

### Frontend Features
- **Responsive Design** — Works on desktop, tablet, and mobile
- **Dynamic Dashboard** — Real-time statistics from database
- **Interactive Tables** — Sortable columns, search, pagination
- **Role-Based UI** — Different actions visible based on user role
- **Flash Messages** — Success/error notifications
- **Print-Friendly** — Bill receipts optimized for printing

## Database Schema

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  departments │     │   doctors    │     │   patients   │
│──────────────│     │──────────────│     │──────────────│
│ department_id│◄────│ department_id│     │ patient_id   │
│ name         │     │ doctor_id    │     │ name         │
│ description  │     │ name         │     │ age          │
└──────────────┘     │ specialization│    │ gender       │
       ▲             │ contact      │     │ contact      │
       │             │ schedule     │     │ address      │
       │             └──────┬───────┘     │ medical_hist │
       │                    │             └──────┬───────┘
┌──────┴───────┐            │                    │
│    staff     │     ┌──────┴────────────────────┴──────┐
│──────────────│     │          appointments            │
│ staff_id     │     │─────────────────────────────────│
│ name         │     │ appointment_id                   │
│ role         │     │ patient_id (FK)                  │
│ contact      │     │ doctor_id (FK)                   │
│ department_id│     │ appointment_date                 │
└──────────────┘     │ status                           │
                     └─────────────────────────────────┘

┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│    bills     │     │  prescriptions   │     │    users     │
│──────────────│     │──────────────────│     │──────────────│
│ bill_id      │     │ prescription_id  │     │ user_id      │
│ patient_id   │     │ patient_id (FK)  │     │ username     │
│ amount       │     │ doctor_id (FK)   │     │ password_hash│
│ payment_stat │     │ medicines        │     │ role         │
│ payment_date │     │ dosage           │     │ reference_id │
└──────────────┘     │ prescribed_date  │     └──────────────┘
                     └──────────────────┘
```

## Project Structure

```
hospital_management_system/
├── app.py                      # Main Flask application
├── config.py                   # Database & app configuration
├── schema.sql                  # MySQL database schema + sample data
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── models/
│   ├── __init__.py
│   ├── db.py                   # Database connection & query helpers
│   ├── user.py                 # User authentication model
│   ├── patient.py              # Patient CRUD operations
│   ├── doctor.py               # Doctor CRUD operations
│   ├── staff.py                # Staff CRUD operations
│   ├── department.py           # Department CRUD operations
│   ├── appointment.py          # Appointment CRUD operations
│   ├── bill.py                 # Billing with transactions
│   └── prescription.py         # Prescription CRUD operations
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Login/Logout routes
│   ├── dashboard.py            # Dashboard with statistics
│   ├── patient.py              # Patient management routes
│   ├── doctor.py               # Doctor management routes
│   ├── staff.py                # Staff management routes
│   ├── department.py           # Department management routes
│   ├── appointment.py          # Appointment management routes
│   ├── bill.py                 # Billing routes
│   └── prescription.py         # Prescription routes
├── templates/
│   ├── base.html               # Base template with sidebar
│   ├── login.html              # Login page
│   ├── dashboard.html          # Dashboard with statistics
│   ├── patients/               # Patient templates (list, add, edit, view)
│   ├── doctors/                # Doctor templates (list, add, edit)
│   ├── staff/                  # Staff templates (list, add, edit)
│   ├── departments/            # Department templates (list, add, edit)
│   ├── appointments/           # Appointment templates (list, add, edit)
│   ├── bills/                  # Billing templates (list, add, edit, view)
│   └── prescriptions/          # Prescription templates (list, add, edit, view)
└── static/
    ├── css/style.css           # Complete responsive stylesheet
    └── js/main.js              # Client-side JavaScript
```

## Setup & Installation

### Prerequisites
- **Python 3.8+**
- **MySQL Server 5.7+** (or MariaDB)
- **pip** (Python package manager)

### Step 1: Install MySQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Start MySQL service
sudo systemctl start mysql
```

### Step 2: Configure MySQL
```bash
# Login to MySQL
mysql -u root -p
# Password: 12345

# The schema will be auto-created when you run the app
```

### Step 3: Install Python Dependencies
```bash
cd hospital_management_system
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Access the Application
Open your browser and navigate to: **http://localhost:5000**

## Default Login Credentials

| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | admin    | admin123   |
| Doctor  | doctor1  | doctor123  |
| Patient | patient1 | patient123 |
| Staff   | staff1   | staff123   |

## Database Connectivity

The application connects to MySQL using the `mysql-connector-python` library:

```python
# config.py
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '12345'
MYSQL_DB = 'hospital_db'
MYSQL_PORT = 3306
```

### Key Database Operations Demonstrated:
1. **INSERT** — Adding new records (patients, appointments, bills)
2. **SELECT** — Fetching data with JOINs and filters
3. **UPDATE** — Modifying existing records
4. **DELETE** — Removing records with cascade
5. **JOIN** — Combining data from multiple tables
6. **GROUP BY** — Aggregating data for statistics
7. **Transactions** — Atomic billing operations
8. **Prepared Statements** — Preventing SQL injection
9. **Pagination** — LIMIT/OFFSET for large datasets
10. **Search** — LIKE queries for filtering

## Technologies Used

- **Backend:** Python 3, Flask 3.1
- **Database:** MySQL with mysql-connector-python
- **Frontend:** HTML5, CSS3, JavaScript (ES6)
- **Icons:** Font Awesome 6
- **Templating:** Jinja2
- **Security:** Werkzeug password hashing, session-based auth

## License

This project is for educational purposes — suitable for final-year DBMS project submission.
