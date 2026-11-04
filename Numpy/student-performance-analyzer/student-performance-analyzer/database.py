import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "students.db"

SUBJECTS = ["python", "mathematics", "statistics", "data_science", "database"]


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT NOT NULL UNIQUE,
                python INTEGER NOT NULL DEFAULT 0 CHECK(python BETWEEN 0 AND 100),
                mathematics INTEGER NOT NULL DEFAULT 0 CHECK(mathematics BETWEEN 0 AND 100),
                statistics INTEGER NOT NULL DEFAULT 0 CHECK(statistics BETWEEN 0 AND 100),
                data_science INTEGER NOT NULL DEFAULT 0 CHECK(data_science BETWEEN 0 AND 100),
                database INTEGER NOT NULL DEFAULT 0 CHECK(database BETWEEN 0 AND 100),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            sample_students = [
                ("Ayesha Khan", "STU-001", 85, 90, 78, 88, 92),
                ("Hamza Ali", "STU-002", 70, 65, 80, 75, 72),
                ("Sara Ahmed", "STU-003", 95, 92, 90, 96, 94),
                ("Usman Malik", "STU-004", 45, 55, 60, 50, 48),
                ("Fatima Noor", "STU-005", 80, 85, 88, 90, 86),
                ("Bilal Shah", "STU-006", 62, 74, 69, 71, 77),
                ("Hira Iqbal", "STU-007", 91, 89, 94, 87, 93),
                ("Danish Raza", "STU-008", 55, 58, 52, 61, 57),
                ("Maham Tariq", "STU-009", 76, 82, 79, 84, 80),
                ("Zain Abbas", "STU-010", 88, 79, 85, 90, 83),
            ]
            conn.executemany("""
                INSERT INTO students
                (name, roll_no, python, mathematics, statistics, data_science, database)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_students)
