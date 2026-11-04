# Student Performance Analyzer

**Developer:** AI Engineer Sayyam Shahid  
**Tagline:** Transforming Student Data into Academic Insights.

A full-stack academic analytics dashboard built with Python, NumPy, Flask, SQLite, HTML, CSS, JavaScript, and Chart.js.

## Features

- Dashboard with total students, class average, pass rate, and highest mark.
- Student CRUD: create, read, update, and delete student records.
- Five subject marks per student: Python, Mathematics, Statistics, Data Science, and Database.
- Search students by name or roll number.
- Subject-wise averages, highest marks, and lowest marks.
- Student rankings and top performers.
- Pass/fail analysis (a student passes when every subject mark is at least 50).
- Statistical analysis: mean, median, standard deviation, minimum, maximum, and totals.
- NumPy array operations: `mean`, `sum`, `max`, `min`, `std`, `median`, `all`, `argsort`, and boolean masks.
- Interactive Chart.js visualizations.
- CSV report export.
- SQLite persistence. Sample records are inserted on the first run.

## Technology

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Numerical engine | NumPy |
| Database | SQLite (`sqlite3`) |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js |

## Folder structure

```text
student-performance-analyzer/
├── app.py
├── analytics.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
├── instance/
│   └── students.db        # generated automatically at runtime
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Requirements

- Python 3.10 or newer
- pip
- A modern web browser
- Internet connection for Google Fonts and the Chart.js CDN used by the dashboard

## Setup on Windows

Open Command Prompt or PowerShell in the project folder.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open the dashboard

Visit:

```text
http://127.0.0.1:5000
```

The SQLite database is created automatically in `instance/students.db`. The first run inserts ten demonstration students. Later runs keep the saved records.

## How NumPy is used

The analytics module turns the students' marks into a two-dimensional NumPy matrix:

```python
matrix = np.array([
    [student["marks"][subject] for subject in SUBJECTS]
    for student in students
], dtype=float)
```

Examples of calculations:

```python
# Average marks for each student (across columns)
student_averages = np.mean(matrix, axis=1)

# Average marks for each subject (down rows)
subject_averages = np.mean(matrix, axis=0)

# Total marks for every student
student_totals = np.sum(matrix, axis=1)

# Students who passed every subject
passed_mask = np.all(matrix >= 50, axis=1)

# Rank students by average marks
ranking_indices = np.argsort(student_averages)[::-1]

# Overall standard deviation
spread = np.std(matrix)
```

### Understanding axis

For a matrix shaped `(number_of_students, number_of_subjects)`:

- `axis=0` calculates down the rows and returns one result per subject.
- `axis=1` calculates across the columns and returns one result per student.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/students` | List all students |
| POST | `/api/students` | Create a student |
| PUT | `/api/students/<id>` | Update a student |
| DELETE | `/api/students/<id>` | Delete a student |
| GET | `/api/analytics` | Get NumPy analytics |
| GET | `/api/export/csv` | Download CSV report |

### Example JSON for creating a student

```json
{
  "name": "Example Student",
  "roll_no": "STU-011",
  "marks": {
    "python": 85,
    "mathematics": 90,
    "statistics": 78,
    "data_science": 88,
    "database": 92
  }
}
```

## Business rules

- Each roll number must be unique.
- Student name and roll number are required.
- Marks must be whole numbers from 0 through 100.
- A student passes only if all five subject marks are 50 or above.
- A student with at least one subject below 50 is marked "Needs improvement".
- Class average is calculated across all saved subject marks.

## Important notes

- This is an educational project and a local development build, not a production-ready school information system.
- The Flask development server is intended for local development. Use a production WSGI server and appropriate deployment configuration before public hosting.
- Add authentication, role-based permissions, CSRF protection, backups, audit logs, and stronger deployment security before using real student records.
- The charts load Chart.js from a CDN, so charts require an internet connection. The rest of the application is served locally.

## Future improvements

- Admin and teacher login with role-based access.
- Import students and marks from CSV/Excel.
- PDF report cards.
- Semester and academic-year management.
- Attendance tracking.
- Email notifications for academic warnings.
- Forecasting and machine-learning-based performance insights.
- Deployment to a cloud platform.

## Author

**AI Engineer Sayyam Shahid**  
Student Performance Analyzer — Python, NumPy & Full-Stack Development.
