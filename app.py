from flask import Flask, jsonify, request, render_template_string
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
# 🔹 API Routes
# -------------------------
@app.route('/')
def home():
    return api_response("success", "Welcome to the Futuristic Flask API 🚀")

@app.route('/students', methods=['GET'])
def get_students():
    return api_response("success", "List of all students", students)

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
    students = [s for s in students if s["id"] != id]
    return api_response("success", f"Student ID {id} deleted")

# -------------------------
# 🔹 Dashboard Route (single-file HTML)
# -------------------------
@app.route('/dashboard')
def dashboard():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>🚀 Futuristic Animated Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
    body { font-family:'Segoe UI',sans-serif; margin:0;padding:0; background: linear-gradient(to right,#0f2027,#203a43,#2c5364); color:#fff; }
    header { text-align:center;padding:2rem;font-size:2rem; background: rgba(0,0,0,0.6); animation: glow 2s infinite alternate; }
    @keyframes glow {0%{text-shadow:0 0 5px #0ff;}50%{text-shadow:0 0 20px #0ff;}100%{text-shadow:0 0 10px #0ff;}}
    .container {width:95%;margin:1rem auto;display:flex;flex-wrap:wrap;justify-content:space-around;}
    .card {background: rgba(255,255,255,0.05);backdrop-filter:blur(15px); border-radius:15px;padding:1rem;margin:1rem;width:350px; box-shadow:0 0 20px rgba(0,255,255,0.3); transition: transform 0.3s;}
    .card:hover {transform: scale(1.05);}
    input,button {margin:5px;padding:5px;border-radius:5px;border:none;}
    button {cursor:pointer;background:#00ff99;color:#000;font-weight:bold;}
    table {width:100%;margin-top:10px;border-collapse:collapse;}
    th,td {border:1px solid #fff;padding:5px;text-align:center;}
    </style>
    </head>
    <body>
    <header>🚀 Futuristic Animated Student Dashboard</header>

    <div class="container">
        <div class="card">
            <h3>Add / Update Student</h3>
            <input type="number" id="studentId" placeholder="ID (for update)"/>
            <input type="text" id="name" placeholder="Name"/>
            <input type="number" id="grade" placeholder="Grade"/>
            <input type="text" id="section" placeholder="Section"/>
            <br>
            <button onclick="addStudent()">Add Student</button>
            <button onclick="updateStudent()">Update Student</button>
            <button onclick="deleteStudent()">Delete Student</button>
        </div>

        <div class="card">
            <h3>Students Table</h3>
            <table id="studentsTable">
                <thead><tr><th>ID</th><th>Name</th><th>Grade</th><th>Section</th><th>Remarks</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="card">
            <h3>Grades Chart</h3>
            <canvas id="gradesChart"></canvas>
        </div>

        <div class="card">
            <h3>Pass / Fail Chart</h3>
            <canvas id="passFailChart"></canvas>
        </div>
    </div>

    <script>
    let students = {{ students | tojson }};

    const gradesCtx = document.getElementById('gradesChart').getContext('2d');
    let gradesChart = new Chart(gradesCtx,{type:'bar',data:{labels:[],datasets:[{label:'Grade',data:[],backgroundColor:[],borderColor:'#fff',borderWidth:1}]},options:{responsive:true,scales:{y:{beginAtZero:true,max:100}},plugins:{legend:{display:false}}}});

    const passCtx = document.getElementById('passFailChart').getContext('2d');
    let passChart = new Chart(passCtx,{type:'doughnut',data:{labels:['Pass ✅','Fail ❌'],datasets:[{data:[],backgroundColor:['rgba(0,255,0,0.6)','rgba(255,0,0,0.6)'],borderColor:'#fff',borderWidth:1}]},options:{responsive:true,plugins:{legend:{position:'bottom'}}}});

    function refreshUI(){
        const tbody=document.querySelector('#studentsTable tbody');tbody.innerHTML='';
        students.forEach(s=>{const tr=document.createElement('tr');tr.innerHTML=`<td>${s.id}</td><td>${s.name}</td><td>${s.grade}</td><td>${s.section}</td><td>${s.remarks}</td>`;tbody.appendChild(tr);});
        const labels=students.map(s=>s.name);const grades=students.map(s=>s.grade);const passFail=students.map(s=>s.grade>=75?'Pass':'Fail');
        gradesChart.data.labels=labels;gradesChart.data.datasets[0].data=grades;gradesChart.data.datasets[0].backgroundColor=grades.map(g=>g>=75?'rgba(0,255,0,0.6)':'rgba(255,0,0,0.6)');gradesChart.update();
        passChart.data.datasets[0].data=[passFail.filter(p=>'Pass'===p).length,passFail.filter(p=>'Fail'===p).length];passChart.update();
    }

    refreshUI();

    function addStudent(){
        const name=document.getElementById('name').value;const grade=parseInt(document.getElementById('grade').value);const section=document.getElementById('section').value;
        fetch('/add_student',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,grade,section})}).then(res=>res.json()).then(data=>{if(data.status==='success'){students.push(data.data);refreshUI();alert('Student Added!');}else alert(data.message);});
    }

    function updateStudent(){
        const id=parseInt(document.getElementById('studentId').value);const name=document.getElementById('name').value;const grade=parseInt(document.getElementById('grade').value);const section=document.getElementById('section').value;
        fetch(`/update_student/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,grade,section})}).then(res=>res.json()).then(data=>{if(data.status==='success'){students=students.map(s=>s.id===id?data.data:s);refreshUI();alert('Student Updated!');}else alert(data.message);});
    }

    function deleteStudent(){
        const id=parseInt(document.getElementById('studentId').value);
        fetch(`/delete_student/${id}`,{method:'DELETE'}).then(res=>res.json()).then(data=>{if(data.status==='success'){students=students.filter(s=>s.id!==id);refreshUI();alert('Student Deleted!');}else alert(data.message);});
    }

    setInterval(()=>{fetch('/students').then(res=>res.json()).then(data=>{if(data.status==='success'){students=data.data;refreshUI();}});},5000);
    </script>
    </body>
    </html>
    """
    return render_template_string(html, students=students)

# -------------------------
# 🔹 Run
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
