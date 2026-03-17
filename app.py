from flask import Flask, jsonify, request, render_template
from datetime import datetime

app = Flask(__name__)

# -------------------------
# 🔹 Fake Database
# -------------------------
students = [
    {"id": 1, "name": "Juan", "grade": 85, "section": "A"},
    {"id": 2, "name": "Maria", "grade": 90, "section": "A"}
]

# -------------------------
# 🔹 Helper Functions
# -------------------------
def api_response(status: str, message: str, data=None):
    return jsonify({
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message": message,
        "data": data
    })

def calculate_remarks(grade):
    return "Pass ✅" if grade >= 75 else "Fail ❌"

# -------------------------
# 🔹 ROUTES
# -------------------------
@app.route('/')
def home():
    return api_response("success", "Welcome to the Futuristic Flask API 🚀")

@app.route('/students', methods=['GET'])
def get_students():
    return api_response("success", "List of all students", students)

@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    student = next((s for s in students if s["id"] == id), None)
    if student:
        return api_response("success", f"Student ID {id} found", student)
    return api_response("error", f"Student ID {id} not found"), 404

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json() or {}
    name = data.get("name")
    grade = data.get("grade")
    section = data.get("section")
    if not name or grade is None or not section:
        return api_response("error", "Missing data"), 400
    if grade < 0 or grade > 100:
        return api_response("error", "Grade must be 0-100"), 400
    new_student = {
        "id": len(students) + 1,
        "name": name,
        "grade": grade,
        "section": section,
        "remarks": calculate_remarks(grade)
    }
    students.append(new_student)
    return api_response("success", "Student added", new_student)

@app.route('/update_student/<int:id>', methods=['PUT'])
def update_student(id):
    student = next((s for s in students if s["id"] == id), None)
    if not student:
        return api_response("error", f"Student ID {id} not found"), 404
    data = request.get_json() or {}
    student["name"] = data.get("name", student["name"])
    student["grade"] = data.get("grade", student["grade"])
    student["section"] = data.get("section", student["section"])
    student["remarks"] = calculate_remarks(student["grade"])
    return api_response("success", f"Student ID {id} updated", student)

@app.route('/delete_student/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students
    if not any(s["id"]==id for s in students):
        return api_response("error", f"Student ID {id} not found"), 404
    students = [s for s in students if s["id"]!=id]
    return api_response("success", f"Student ID {id} deleted")

# -------------------------
# 🔹 DASHBOARD
# -------------------------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', students=students)

# -------------------------
# 🔹 Error Handlers
# -------------------------
@app.errorhandler(404)
def not_found(e):
    return api_response("error", "Endpoint not found"), 404

@app.errorhandler(500)
def server_error(e):
    return api_response("error", "Internal server error"), 500

# -------------------------
# 🔹 RUN
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
