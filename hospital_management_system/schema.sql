-- ============================================================
-- Hospital Management System - MySQL Database Schema
-- Normalized to 3NF with proper PKs, FKs, and constraints
-- ============================================================

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ============================================================
-- 1. Departments Table
-- ============================================================
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 2. Doctors Table
-- ============================================================
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id       INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    specialization  VARCHAR(100) NOT NULL,
    contact         VARCHAR(15) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    department_id   INT,
    schedule        VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 3. Patients Table
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    patient_id      INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    age             INT NOT NULL CHECK (age > 0 AND age < 150),
    gender          ENUM('Male', 'Female', 'Other') NOT NULL,
    contact         VARCHAR(15) NOT NULL,
    email           VARCHAR(100),
    address         TEXT,
    medical_history TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 4. Staff Table
-- ============================================================
CREATE TABLE IF NOT EXISTS staff (
    staff_id        INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    role            VARCHAR(50) NOT NULL,
    contact         VARCHAR(15) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    department_id   INT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 5. Appointments Table
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id  INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status          ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Pending',
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 6. Bills Table (with transaction support)
-- ============================================================
CREATE TABLE IF NOT EXISTS bills (
    bill_id         INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    amount          DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    description     VARCHAR(255),
    payment_status  ENUM('Unpaid', 'Paid', 'Partial') DEFAULT 'Unpaid',
    payment_date    DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 7. Prescriptions Table
-- ============================================================
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    medicines       TEXT NOT NULL,
    dosage          VARCHAR(255),
    notes           TEXT,
    prescribed_date DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 8. Users Table (Authentication)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('Admin', 'Doctor', 'Patient', 'Staff') NOT NULL,
    reference_id    INT COMMENT 'Links to doctor_id, patient_id, or staff_id based on role',
    is_active       TINYINT(1) DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- Indexes for faster queries
-- ============================================================
CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_doctors_specialization ON doctors(specialization);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_bills_payment_status ON bills(payment_status);
CREATE INDEX idx_prescriptions_date ON prescriptions(prescribed_date);

-- ============================================================
-- Sample Data
-- ============================================================

-- Departments
INSERT INTO departments (name, description) VALUES
('Cardiology', 'Heart and cardiovascular system'),
('Neurology', 'Brain and nervous system'),
('Orthopedics', 'Bones, joints, and muscles'),
('Pediatrics', 'Children and infant care'),
('Dermatology', 'Skin, hair, and nails'),
('General Medicine', 'General health and wellness'),
('Ophthalmology', 'Eye care and vision'),
('ENT', 'Ear, Nose, and Throat');

-- Doctors
INSERT INTO doctors (name, specialization, contact, email, department_id, schedule) VALUES
('Dr. Rajesh Kumar', 'Cardiologist', '9876543210', 'rajesh@hospital.com', 1, 'Mon-Fri 9AM-5PM'),
('Dr. Priya Sharma', 'Neurologist', '9876543211', 'priya@hospital.com', 2, 'Mon-Sat 10AM-4PM'),
('Dr. Amit Patel', 'Orthopedic Surgeon', '9876543212', 'amit@hospital.com', 3, 'Tue-Sat 9AM-3PM'),
('Dr. Sneha Reddy', 'Pediatrician', '9876543213', 'sneha@hospital.com', 4, 'Mon-Fri 8AM-2PM'),
('Dr. Vikram Singh', 'Dermatologist', '9876543214', 'vikram@hospital.com', 5, 'Wed-Sun 10AM-6PM'),
('Dr. Anita Desai', 'General Physician', '9876543215', 'anita@hospital.com', 6, 'Mon-Sat 9AM-5PM');

-- Patients
INSERT INTO patients (name, age, gender, contact, email, address, medical_history) VALUES
('Rahul Verma', 35, 'Male', '9123456780', 'rahul@email.com', '123 MG Road, Mumbai', 'Hypertension, Diabetes'),
('Sunita Devi', 45, 'Female', '9123456781', 'sunita@email.com', '456 Park Street, Kolkata', 'Asthma'),
('Arjun Nair', 28, 'Male', '9123456782', 'arjun@email.com', '789 Brigade Road, Bangalore', 'None'),
('Meera Joshi', 60, 'Female', '9123456783', 'meera@email.com', '321 Civil Lines, Delhi', 'Heart Disease, Arthritis'),
('Karan Malhotra', 22, 'Male', '9123456784', 'karan@email.com', '654 Lake Road, Pune', 'Allergies'),
('Deepa Iyer', 50, 'Female', '9123456785', 'deepa@email.com', '987 Anna Nagar, Chennai', 'Thyroid disorder');

-- Staff
INSERT INTO staff (name, role, contact, email, department_id) VALUES
('Nurse Kavita', 'Head Nurse', '9234567890', 'kavita@hospital.com', 1),
('Suresh Kumar', 'Lab Technician', '9234567891', 'suresh@hospital.com', 6),
('Pooja Mehta', 'Receptionist', '9234567892', 'pooja@hospital.com', 6),
('Ramesh Gupta', 'Pharmacist', '9234567893', 'ramesh@hospital.com', 6),
('Anjali Das', 'Nurse', '9234567894', 'anjali@hospital.com', 4),
('Manoj Tiwari', 'Ward Boy', '9234567895', 'manoj@hospital.com', 3);

-- Appointments
INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes) VALUES
(1, 1, '2025-06-15 10:00:00', 'Confirmed', 'Regular checkup for blood pressure'),
(2, 6, '2025-06-15 11:00:00', 'Pending', 'Breathing difficulty'),
(3, 3, '2025-06-16 09:00:00', 'Confirmed', 'Knee pain consultation'),
(4, 1, '2025-06-16 14:00:00', 'Completed', 'Follow-up ECG'),
(5, 5, '2025-06-17 10:30:00', 'Pending', 'Skin rash treatment'),
(6, 2, '2025-06-17 15:00:00', 'Confirmed', 'Migraine consultation');

-- Bills
INSERT INTO bills (patient_id, amount, description, payment_status, payment_date) VALUES
(1, 1500.00, 'Consultation + ECG', 'Paid', '2025-06-15'),
(2, 800.00, 'General Consultation', 'Unpaid', NULL),
(3, 2500.00, 'X-Ray + Consultation', 'Paid', '2025-06-16'),
(4, 5000.00, 'ECG + Blood Tests + Consultation', 'Partial', NULL),
(5, 600.00, 'Dermatology Consultation', 'Unpaid', NULL),
(6, 3000.00, 'MRI Scan + Consultation', 'Paid', '2025-06-17');

-- Prescriptions
INSERT INTO prescriptions (patient_id, doctor_id, medicines, dosage, notes, prescribed_date) VALUES
(1, 1, 'Amlodipine 5mg, Metformin 500mg', 'Twice daily after meals', 'Monitor BP weekly', '2025-06-15'),
(2, 6, 'Salbutamol Inhaler, Montelukast 10mg', 'Inhaler as needed, tablet once daily', 'Avoid dust exposure', '2025-06-15'),
(3, 3, 'Diclofenac 50mg, Calcium tablets', 'Diclofenac twice daily, Calcium once daily', 'Physiotherapy recommended', '2025-06-16'),
(4, 1, 'Aspirin 75mg, Atorvastatin 20mg', 'Once daily at night', 'Low salt diet advised', '2025-06-16'),
(5, 5, 'Cetirizine 10mg, Betamethasone cream', 'Tablet once daily, cream apply twice', 'Avoid scratching', '2025-06-17'),
(6, 2, 'Sumatriptan 50mg, Amitriptyline 10mg', 'Sumatriptan as needed, Amitriptyline at bedtime', 'Maintain sleep schedule', '2025-06-17');

-- Users (passwords are hashed versions of simple passwords for demo)
-- Default passwords: admin/admin123, doctor1/doctor123, patient1/patient123, staff1/staff123
-- These will be inserted by the application's init_db command with proper hashing
