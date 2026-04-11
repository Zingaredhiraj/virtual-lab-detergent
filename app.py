"""
Virtual Lab: Detergent Making Practical
========================================
A Flask-based interactive educational web application that simulates
a detergent manufacturing experiment step-by-step.

Routes:
    /              - Homepage with project info and team members
    /lab           - Virtual lab simulation page
    /admin         - Admin dashboard showing all student records
    /save-progress - POST API to save student experiment progress
    /get-progress  - GET API to retrieve student progress by name
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Database configuration
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

# Valid experiment steps in order
VALID_STEPS = [
    "Neutralization",
    "Mixing",
    "Additives",
    "Drying",
    "Packaging",
]


def get_db():
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create the student_progress table if needed."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            step_completed TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Render the homepage with project description and team info."""
    return render_template("index.html")


@app.route("/lab")
def lab():
    """Render the virtual lab simulation page."""
    return render_template("lab.html")


@app.route("/admin")
def admin():
    """
    Admin dashboard: display all student records with progress status.
    Records are ordered by most recent first.
    """
    conn = get_db()
    try:
        records = conn.execute(
            "SELECT * FROM student_progress ORDER BY timestamp DESC"
        ).fetchall()
    finally:
        conn.close()
    return render_template("admin.html", records=records)


@app.route("/save-progress", methods=["POST"])
def save_progress():
    """
    Save or update a student's experiment progress.

    Expected JSON body:
        {
            "name": "Student Name",
            "class": "Class/Section",
            "step_completed": "Neutralization"
        }

    Returns:
        JSON response with success/error status.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    name = data.get("name", "").strip()
    student_class = data.get("class", "").strip()
    step_completed = data.get("step_completed", "").strip()

    # Validate required fields
    if not name or not student_class or not step_completed:
        return jsonify({"error": "All fields (name, class, step_completed) are required"}), 400

    # Validate step name
    if step_completed not in VALID_STEPS:
        return jsonify({"error": f"Invalid step. Must be one of: {', '.join(VALID_STEPS)}"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    try:
        # Check if student already has a record
        existing = conn.execute(
            "SELECT id FROM student_progress WHERE name = ? AND class = ?",
            (name, student_class),
        ).fetchone()

        if existing:
            # Update existing record
            conn.execute(
                "UPDATE student_progress SET step_completed = ?, timestamp = ? WHERE id = ?",
                (step_completed, timestamp, existing["id"]),
            )
        else:
            # Insert new record
            conn.execute(
                "INSERT INTO student_progress (name, class, step_completed, timestamp) VALUES (?, ?, ?, ?)",
                (name, student_class, step_completed, timestamp),
            )

        conn.commit()
        return jsonify({
            "success": True,
            "message": f"Progress saved: {step_completed}",
            "data": {
                "name": name,
                "class": student_class,
                "step_completed": step_completed,
                "timestamp": timestamp,
            },
        })
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()


@app.route("/get-progress", methods=["GET"])
def get_progress():
    """
    Retrieve a student's experiment progress by name.

    Query parameters:
        name - Student name to look up

    Returns:
        JSON response with the student's progress record.
    """
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name parameter is required"}), 400

    conn = get_db()
    try:
        record = conn.execute(
            "SELECT * FROM student_progress WHERE name = ?", (name,)
        ).fetchone()
    finally:
        conn.close()

    if record:
        return jsonify({
            "success": True,
            "data": {
                "id": record["id"],
                "name": record["name"],
                "class": record["class"],
                "step_completed": record["step_completed"],
                "timestamp": record["timestamp"],
            },
        })
    else:
        return jsonify({"success": False, "message": "No record found for this student"})


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0", port=5000)
