from flask import Flask, jsonify, render_template, request, send_file
import csv
import io
from database import init_db, get_connection, SUBJECTS
from analytics import build_analytics

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

init_db()


def student_dict(row):
    data = dict(row)
    data["marks"] = {subject: data[subject] for subject in SUBJECTS}
    return data


@app.get("/")
def index():
    return render_template("index.html", subjects=SUBJECTS)


@app.get("/api/students")
def get_students():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return jsonify([student_dict(row) for row in rows])


@app.post("/api/students")
def create_student():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    roll_no = str(payload.get("roll_no", "")).strip()

    if not name or not roll_no:
        return jsonify({"error": "Student name and roll number are required."}), 400

    marks = payload.get("marks", {})
    try:
        values = [int(marks.get(subject, 0)) for subject in SUBJECTS]
    except (TypeError, ValueError):
        return jsonify({"error": "All marks must be whole numbers."}), 400

    if any(mark < 0 or mark > 100 for mark in values):
        return jsonify({"error": "Marks must be between 0 and 100."}), 400

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO students
                (name, roll_no, python, mathematics, statistics, data_science, database)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, roll_no, *values),
            )
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM students WHERE id = ?", (new_id,)).fetchone()
        return jsonify(student_dict(row)), 201
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            return jsonify({"error": "That roll number already exists."}), 409
        raise


@app.put("/api/students/<int:student_id>")
def update_student(student_id):
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    roll_no = str(payload.get("roll_no", "")).strip()
    marks = payload.get("marks", {})

    if not name or not roll_no:
        return jsonify({"error": "Student name and roll number are required."}), 400

    try:
        values = [int(marks.get(subject, 0)) for subject in SUBJECTS]
    except (TypeError, ValueError):
        return jsonify({"error": "All marks must be whole numbers."}), 400

    if any(mark < 0 or mark > 100 for mark in values):
        return jsonify({"error": "Marks must be between 0 and 100."}), 400

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """UPDATE students SET name=?, roll_no=?, python=?, mathematics=?,
                statistics=?, data_science=?, database=? WHERE id=?""",
                (name, roll_no, *values, student_id),
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Student not found."}), 404
            row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
        return jsonify(student_dict(row))
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            return jsonify({"error": "That roll number already exists."}), 409
        raise


@app.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404
    return jsonify({"message": "Student deleted successfully."})


@app.get("/api/analytics")
def analytics():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    records = [student_dict(row) for row in rows]
    return jsonify(build_analytics(records))


@app.get("/api/export/csv")
def export_csv():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY roll_no").fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Roll Number", *SUBJECTS, "Total", "Average", "Status"])
    for row in rows:
        values = [row[s] for s in SUBJECTS]
        total = sum(values)
        average = total / len(SUBJECTS)
        status = "Pass" if all(mark >= 50 for mark in values) else "Needs improvement"
        writer.writerow([row["name"], row["roll_no"], *values, total, round(average, 2), status])

    memory_file = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="student-performance-report.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
