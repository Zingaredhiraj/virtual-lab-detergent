# Virtual Lab: Detergent Making Practical

An interactive educational web application that simulates the detergent manufacturing process step-by-step. Built with Flask, SQLite, HTML5, CSS3, and JavaScript.

## Features

- **Step-by-step simulation** — Neutralization, Mixing, Additives, Drying, Packaging
- **Interactive animations** — Bubbles, spinning mixer, spray drying, conveyor packaging
- **Process flow diagram** — Visual pipeline with real-time progress highlighting
- **Progress tracking** — Backend saves student progress to SQLite database
- **Admin dashboard** — View all student records with sortable table and stats
- **Completion certificate** — Auto-generated on experiment completion
- **Responsive design** — Works on desktop, tablet, and mobile

## Project Structure

```
/virtual-lab-detergent
├── app.py                  # Flask backend (routes + API + database)
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (auto-created on first run)
├── templates/
│   ├── index.html          # Homepage
│   ├── lab.html            # Virtual lab simulation
│   └── admin.html          # Admin dashboard
├── static/
│   ├── css/style.css       # All styles, animations, responsive layout
│   └── js/script.js        # Client-side logic, Fetch API, animations
└── README.md
```

## Database Schema

```sql
CREATE TABLE student_progress (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    class           TEXT NOT NULL,
    step_completed  TEXT NOT NULL,
    timestamp       TEXT NOT NULL
);
```

## API Endpoints

| Method | Route            | Description                        |
|--------|------------------|------------------------------------|
| GET    | `/`              | Homepage                           |
| GET    | `/lab`           | Virtual lab simulation             |
| GET    | `/admin`         | Admin dashboard                    |
| POST   | `/save-progress` | Save/update student progress       |
| GET    | `/get-progress`  | Retrieve progress by student name  |

### POST `/save-progress`

```json
{
  "name": "Student Name",
  "class": "B.Tech CSE",
  "step_completed": "Neutralization"
}
```

### GET `/get-progress?name=Student+Name`

Returns the student's current progress record.

## Setup & Run

### Prerequisites

- Python 3.8+

### Installation

```bash
# Clone the repository
git clone https://github.com/Zingaredhiraj/virtual-lab-detergent.git
cd virtual-lab-detergent

# Install dependencies
pip install flask

# Run the application
python app.py
```

### Access

Open your browser and navigate to: **http://localhost:5000**

| Page  | URL                        |
|-------|----------------------------|
| Home  | http://localhost:5000/      |
| Lab   | http://localhost:5000/lab   |
| Admin | http://localhost:5000/admin |

## Experiment Steps

1. **Neutralization** — LABSA reacts with Na₂CO₃ to form the detergent base
2. **Mixing** — Thorough blending for uniform consistency
3. **Additives** — Builders, enzymes, fragrances, optical brighteners
4. **Drying** — Spray drying converts slurry into powder granules
5. **Packaging** — Weighing, quality check, and sealing

## Technologies Used

- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Icons:** Font Awesome 6
- **Templating:** Jinja2

## License

This project is for educational purposes.
