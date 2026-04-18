import os

# Update api.py
with open("app/routes/api.py", "r") as f:
    api_content = f.read()

# Add imports
api_content = api_content.replace(
    "from flask import Blueprint, request, jsonify",
    "from flask import Blueprint, request, jsonify, session\nfrom app.models.models import User"
)

auth_routes = """
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
        
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"})

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({"message": "Logged in successfully"})
    return jsonify({"error": "Invalid credentials"}), 401

@api_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({"message": "Logged out successfully"})

"""

api_content = api_content.replace("api_bp = Blueprint('api', __name__)\n", "api_bp = Blueprint('api', __name__)\n" + auth_routes)

# Replace all queries to filter by user_id
api_content = api_content.replace(
    "existing = Course.query.filter_by(name=name).first()",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    existing = Course.query.filter_by(name=name, user_id=user_id).first()"
)
api_content = api_content.replace(
    "course = Course(name=name, type=data['type'], credits=data.get('credits', 3))",
    "course = Course(name=name, type=data['type'], credits=data.get('credits', 3), user_id=user_id)"
)
api_content = api_content.replace(
    "existing = Professor.query.filter_by(name=name).first()",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    existing = Professor.query.filter_by(name=name, user_id=user_id).first()"
)
api_content = api_content.replace(
    "prof = Professor(name=name)",
    "prof = Professor(name=name, user_id=user_id)"
)
api_content = api_content.replace(
    "cp = CourseProfessor.query.filter_by(course_id=data['course_id'], professor_id=data['professor_id']).first()",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    cp = CourseProfessor.query.filter_by(course_id=data['course_id'], professor_id=data['professor_id']).first()"
)

api_content = api_content.replace(
    "courses = Course.query.all()",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    courses = Course.query.filter_by(user_id=user_id).all()"
)
api_content = api_content.replace(
    "GeneratedTimetable.query.delete()",
    "GeneratedTimetable.query.filter_by(user_id=user_id).delete()"
)
api_content = api_content.replace(
    "gt = GeneratedTimetable(score=res['score'], data=json.dumps(res['data']))",
    "gt = GeneratedTimetable(score=res['score'], data=json.dumps(res['data']), user_id=user_id)"
)
api_content = api_content.replace(
    "tts = GeneratedTimetable.query.order_by(GeneratedTimetable.score.desc()).limit(50).all()",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    tts = GeneratedTimetable.query.filter_by(user_id=user_id).order_by(GeneratedTimetable.score.desc()).limit(50).all()"
)
api_content = api_content.replace(
    "tts = GeneratedTimetable.query.order_by(GeneratedTimetable.score.desc()).limit(10).all()",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    tts = GeneratedTimetable.query.filter_by(user_id=user_id).order_by(GeneratedTimetable.score.desc()).limit(10).all()"
)

api_content = api_content.replace(
    "courses = Course.query.all()",
    "user_id = session.get('user_id')\n    courses = Course.query.filter_by(user_id=user_id).all() if user_id else []"
)
api_content = api_content.replace(
    "profs = Professor.query.all()",
    "user_id = session.get('user_id')\n    profs = Professor.query.filter_by(user_id=user_id).all() if user_id else []"
)

# Fix double user_id check in get_all_data
api_content = api_content.replace(
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    user_id = session.get('user_id')\n    courses = Course.query.filter_by(user_id=user_id).all() if user_id else []",
    "user_id = session.get('user_id')\n    if not user_id: return jsonify({'error': 'Unauthorized'}), 401\n    courses = Course.query.filter_by(user_id=user_id).all()"
)

# For offerings in get_all_data, we need to join or filter
api_content = api_content.replace(
    "offerings = CourseOffering.query.all()",
    "course_ids = [c.id for c in courses]\n    offerings = CourseOffering.query.filter(CourseOffering.course_id.in_(course_ids)).all() if course_ids else []"
)

with open("app/routes/api.py", "w") as f:
    f.write(api_content)
