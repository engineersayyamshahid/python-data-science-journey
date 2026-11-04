import numpy as np
from database import SUBJECTS


def build_analytics(students):
    if not students:
        return {
            "summary": {
                "total_students": 0, "class_average": 0, "pass_rate": 0,
                "highest_mark": 0, "passed_students": 0, "failed_students": 0
            },
            "subjects": [], "students": [], "top_students": [],
            "distribution": {"labels": ["0-49", "50-59", "60-69", "70-79", "80-89", "90-100"],
                             "values": [0, 0, 0, 0, 0, 0]}
        }

    names = [student["name"] for student in students]
    roll_numbers = [student["roll_no"] for student in students]
    matrix = np.array([[student["marks"][subject] for subject in SUBJECTS]
                       for student in students], dtype=float)

    student_averages = np.mean(matrix, axis=1)
    student_totals = np.sum(matrix, axis=1)
    subject_averages = np.mean(matrix, axis=0)
    subject_highs = np.max(matrix, axis=0)
    subject_lows = np.min(matrix, axis=0)
    passed_mask = np.all(matrix >= 50, axis=1)

    student_results = []
    for index, name in enumerate(names):
        student_results.append({
            "name": name,
            "roll_no": roll_numbers[index],
            "total": int(student_totals[index]),
            "average": round(float(student_averages[index]), 2),
            "status": "Pass" if passed_mask[index] else "Needs improvement",
        })

    ranking_indices = np.argsort(student_averages)[::-1]
    top_students = [student_results[int(i)] for i in ranking_indices[:5]]

    subject_results = []
    for index, subject in enumerate(SUBJECTS):
        subject_results.append({
            "name": subject.replace("_", " ").title(),
            "average": round(float(subject_averages[index]), 2),
            "highest": int(subject_highs[index]),
            "lowest": int(subject_lows[index]),
        })

    all_marks = matrix.flatten()
    bins = [(0, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, 100)]
    distribution_values = [
        int(np.sum((all_marks >= low) & (all_marks <= high)))
        for low, high in bins
    ]

    total_students = len(students)
    passed_count = int(np.sum(passed_mask))
    return {
        "summary": {
            "total_students": total_students,
            "class_average": round(float(np.mean(matrix)), 2),
            "pass_rate": round((passed_count / total_students) * 100, 1),
            "highest_mark": int(np.max(matrix)),
            "passed_students": passed_count,
            "failed_students": total_students - passed_count,
            "median": round(float(np.median(matrix)), 2),
            "standard_deviation": round(float(np.std(matrix)), 2),
        },
        "subjects": subject_results,
        "students": student_results,
        "top_students": top_students,
        "distribution": {
            "labels": ["0–49", "50–59", "60–69", "70–79", "80–89", "90–100"],
            "values": distribution_values,
        },
    }
