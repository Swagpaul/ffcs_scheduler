from flask import Blueprint, request, jsonify, session
from app.models.models import User, db, Course, Professor, CourseProfessor, Slot, CourseOffering, GeneratedTimetable
from app.services.scheduler import Scheduler
from app.services.scorer import calculate_score
from app.services.slot_engine import check_clash, get_all_slots
import json

api_bp = Blueprint('api', __name__)

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


@api_bp.route('/add_course', methods=['POST'])
def add_course():
    data = request.json
    name = data['name'].strip()
    
    # Check if course already exists
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    existing = Course.query.filter_by(name=name, user_id=user_id).first()
    if existing:
        return jsonify({"message": "Course already exists", "id": existing.id, "already_exists": True})
        
    course = Course(name=name, type=data['type'], credits=data.get('credits', 3), user_id=user_id)
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course added", "id": course.id})

@api_bp.route('/add_professor', methods=['POST'])
def add_professor():
    data = request.json
    name = data['name'].strip()
    
    # Check if professor already exists
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    existing = Professor.query.filter_by(name=name, user_id=user_id).first()
    if existing:
        return jsonify({"message": "Professor already exists", "id": existing.id, "already_exists": True})
        
    prof = Professor(name=name, user_id=user_id)
    db.session.add(prof)
    db.session.commit()
    return jsonify({"message": "Professor added", "id": prof.id})

@api_bp.route('/assign_slot', methods=['POST'])
def assign_slot():
    data = request.json
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    
    course_id = data.get('course_id')
    professor_id = data.get('professor_id')
    
    # Verify ownership
    course = Course.query.filter_by(id=course_id, user_id=user_id).first()
    prof = Professor.query.filter_by(id=professor_id, user_id=user_id).first()
    
    if not course or not prof:
        return jsonify({"error": "Course or Professor not found or unauthorized"}), 404

    # Slot validation
    from app.services.slot_engine import is_valid_slot
    theory_slot = data.get('theory_slot')
    lab_slot = data.get('lab_slot')
    
    if theory_slot and not is_valid_slot(theory_slot):
        return jsonify({"error": f"Invalid theory slot: {theory_slot}"}), 400
    if lab_slot and not is_valid_slot(lab_slot):
        return jsonify({"error": f"Invalid lab slot: {lab_slot}"}), 400

    # Set priority directly to the offering
    priority_val = int(data.get('priority', 1))

    # Check if exact Offering already exists
    offering = CourseOffering.query.filter_by(
        course_id=course_id, 
        professor_id=professor_id,
        theory_slot=theory_slot or None,
        lab_slot=lab_slot or None
    ).first()
    
    if not offering:
        offering = CourseOffering(
            course_id=course_id, 
            professor_id=professor_id,
            theory_slot=theory_slot or None,
            lab_slot=lab_slot or None,
            priority=priority_val
        )
        db.session.add(offering)
    else:
        offering.priority = priority_val

    db.session.commit()
    return jsonify({"message": "Slot assigned successfully"})

@api_bp.route('/generate', methods=['POST'])
def generate():
    # Fetch all courses and their offerings
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    courses = Course.query.filter_by(user_id=user_id).all()
    scheduler_input = []
    
    for c in courses:
        options = []
        offerings = CourseOffering.query.filter_by(course_id=c.id).all()
        for off in offerings:
            prof = Professor.query.get(off.professor_id)
            options.append({
                'prof_id': off.professor_id,
                'prof_name': prof.name,
                'theory_slot': off.theory_slot,
                'lab_slot': off.lab_slot,
                'priority': off.priority
            })
        
        if options:
            scheduler_input.append({
                'id': c.id,
                'name': c.name,
                'type': c.type,
                'credits': c.credits,
                'options': options
            })

    if not scheduler_input:
        return jsonify({"error": "No course offerings found"}), 400

    # Collect all course names so the frontend can detect omitted courses
    all_course_names = {c['id']: c['name'] for c in scheduler_input}

    scheduler = Scheduler(scheduler_input)
    timetables = scheduler.generate()
    
    if not timetables:
        error_msg = scheduler.get_clash_reasons()
        return jsonify({"error": error_msg}), 400
    
    # Score them and compute dropped courses for each timetable
    results = []
    for i, tt in enumerate(timetables):
        score = calculate_score(tt)
        scheduled_ids = {entry['course_id'] for entry in tt}
        dropped = [all_course_names[cid] for cid in all_course_names if cid not in scheduled_ids]
        results.append({
            'id': i + 1,
            'score': score,
            'data': tt,
            'dropped_courses': dropped
        })
    
    # Sort by score (timetables with no dropped courses rank higher)
    results.sort(key=lambda x: (len(x['dropped_courses']), -x['score']))
    
    # Save top 100 to DB (clear old ones first for simplicity in this demo)
    GeneratedTimetable.query.filter_by(user_id=user_id).delete()
    for res in results[:100]:
        gt = GeneratedTimetable(
            score=res['score'],
            data=json.dumps({'entries': res['data'], 'dropped_courses': res['dropped_courses']}),
            user_id=user_id
        )
        db.session.add(gt)
    db.session.commit()

    return jsonify({"count": len(results), "top_results": results[:20]})

@api_bp.route('/timetables', methods=['GET'])
def get_timetables():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    tts = GeneratedTimetable.query.filter_by(user_id=user_id).order_by(GeneratedTimetable.score.desc()).limit(50).all()
    output = []
    for tt in tts:
        raw = json.loads(tt.data)
        # Handle both old format (list) and new format (dict with entries + dropped_courses)
        if isinstance(raw, list):
            entries = raw
            dropped = []
        else:
            entries = raw.get('entries', [])
            dropped = raw.get('dropped_courses', [])
        output.append({
            'id': tt.id,
            'score': tt.score,
            'data': entries,
            'dropped_courses': dropped
        })
    return jsonify(output)



@api_bp.route('/data', methods=['GET'])
def get_all_data():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    
    courses = Course.query.filter_by(user_id=user_id).all()
    profs = Professor.query.filter_by(user_id=user_id).all()
    course_ids = [c.id for c in courses]
    
    offerings = CourseOffering.query.filter(CourseOffering.course_id.in_(course_ids)).all() if course_ids else []
    
    return jsonify({
        "courses": [{"id": c.id, "name": c.name, "type": c.type, "credits": c.credits} for c in courses],
        "professors": [{"id": p.id, "name": p.name} for p in profs],
        "offerings": [{
            "id": o.id, 
            "course_id": o.course_id, 
            "professor_id": o.professor_id,
            "theory_slot": o.theory_slot,
            "lab_slot": o.lab_slot,
            "priority": o.priority
        } for o in offerings]
    })

@api_bp.route('/delete_offering/<int:id>', methods=['DELETE'])
def delete_offering(id):
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    
    offering = CourseOffering.query.get(id)
    if not offering:
        return jsonify({"error": "Offering not found"}), 404
        
    # Check ownership via course
    course = Course.query.get(offering.course_id)
    if not course or course.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    db.session.delete(offering)
    db.session.commit()
    return jsonify({"message": "Offering deleted"})


@api_bp.route('/update_offering/<int:id>', methods=['PUT'])
def update_offering(id):
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    
    offering = CourseOffering.query.get(id)
    if not offering:
        return jsonify({"error": "Offering not found"}), 404
        
    # Check ownership via course
    course = Course.query.get(offering.course_id)
    if not course or course.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    course_id = data.get('course_id')
    professor_id = data.get('professor_id')
    theory_slot = data.get('theory_slot', '').strip().upper()
    lab_slot = data.get('lab_slot', '').strip().upper()
    priority = data.get('priority')

    # Validate slots if provided
    from app.services.slot_engine import is_valid_slot
    if theory_slot and not is_valid_slot(theory_slot):
        return jsonify({"error": f"Invalid theory slot: {theory_slot}"}), 400
    if lab_slot and not is_valid_slot(lab_slot):
        return jsonify({"error": f"Invalid lab slot: {lab_slot}"}), 400

    # Ensure course exists and belongs to user
    if course_id:
        new_course = Course.query.get(course_id)
        if not new_course or new_course.user_id != user_id:
            return jsonify({"error": "Invalid course"}), 400
        offering.course_id = course_id

    # Ensure professor exists and belongs to user
    if professor_id:
        new_prof = Professor.query.get(professor_id)
        if not new_prof or new_prof.user_id != user_id:
            return jsonify({"error": "Invalid professor"}), 400
        offering.professor_id = professor_id

    offering.theory_slot = theory_slot or None
    offering.lab_slot = lab_slot or None
    if priority is not None:
        offering.priority = int(priority)

    db.session.commit()
    return jsonify({"message": "Offering updated successfully"})
