from flask import Flask, jsonify, request

app = Flask(__name__)

# Fake database (temporary)
students = [
    {"id": 1, "name": "Juan", "grade": 85, "section": "A"},
    {"id": 2, "name": "Maria", "grade": 90, "section": "A"}
]

# HOME
@app.route('/')
def home():
    return "Welcome to your Flask API 🚀"

# GET ALL STUDENTS
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# GET SINGLE STUDENT
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    student = next((s for s in students if s["id"] == id), None)
    if student:
        return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

# ADD STUDENT
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()

    name = data.get("name")
    grade = data.get("grade")
    section = data.get("section")

    # Validation
    if not name or grade is None or not section:
        return jsonify({"error": "Missing data"}), 400

    if grade < 0 or grade > 100:
        return jsonify({"error": "Grade must be 0-100"}), 400

    new_student = {
        "id": len(students) + 1,
        "name": name,
        "grade": grade,
        "section": section,
        "remarks": "Pass" if grade >= 75 else "Fail"
    }

    students.append(new_student)

    return jsonify({"message": "Student added", "student": new_student})

# UPDATE STUDENT
@app.route('/update_student/<int:id>', methods=['PUT'])
def update_student(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    student["name"] = data.get("name", student["name"])
    student["grade"] = data.get("grade", student["grade"])
    student["section"] = data.get("section", student["section"])
    student["remarks"] = "Pass" if student["grade"] >= 75 else "Fail"

    return jsonify({"message": "Updated successfully", "student": student})

# DELETE STUDENT
@app.route('/delete_student/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students
    students = [s for s in students if s["id"] != id]

    return jsonify({"message": "Deleted successfully"})

# SUMMARY (ANALYTICS)
@app.route('/summary')
def summary():
    grades = [s["grade"] for s in students]

    if not grades:
        return jsonify({"message": "No data"})

    avg = sum(grades) / len(grades)
    passed = len([g for g in grades if g >= 75])
    failed = len(grades) - passed

    return jsonify({
        "average": avg,
        "passed": passed,
        "failed": failed
    })

if __name__ == '__main__':
    app.run(debug=True)