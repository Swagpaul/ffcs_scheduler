from flask import Blueprint, request, jsonify
from app.models.models import db, Course, Professor, CourseProfessor, Slot, CourseOffering, GeneratedTimetable
from app.services.scheduler import Scheduler
from app.services.scorer import calculate_score
from app.services.ai_ranker import AIRanker
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/add_course', methods=['POST'])
def add_course():
    data = request.json
    name = data['name'].strip()
    
    # Check if course already exists
    existing = Course.query.filter_by(name=name).first()
    if existing:
        return jsonify({"message": "Course already exists", "id": existing.id, "already_exists": True})
        
    course = Course(name=name, type=data['type'], credits=data.get('credits', 3))
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course added", "id": course.id})

@api_bp.route('/add_professor', methods=['POST'])
def add_professor():
    data = request.json
    name = data['name'].strip()
    
    # Check if professor already exists
    existing = Professor.query.filter_by(name=name).first()
    if existing:
        return jsonify({"message": "Professor already exists", "id": existing.id, "already_exists": True})
        
    prof = Professor(name=name)
    db.session.add(prof)
    db.session.commit()
    return jsonify({"message": "Professor added", "id": prof.id})

@api_bp.route('/assign_slot', methods=['POST'])
def assign_slot():
    data = request.json
    # data: {course_id, professor_id, priority, theory_slot, lab_slot}
    
    # Check if CourseProfessor exists
    cp = CourseProfessor.query.filter_by(course_id=data['course_id'], professor_id=data['professor_id']).first()
    if not cp:
        cp = CourseProfessor(course_id=data['course_id'], professor_id=data['professor_id'], priority=data.get('priority', 1))
        db.session.add(cp)
    else:
        cp.priority = data.get('priority', cp.priority)

    # Check if Offering exists
    offering = CourseOffering.query.filter_by(course_id=data['course_id'], professor_id=data['professor_id']).first()
    if not offering:
        offering = CourseOffering(
            course_id=data['course_id'], 
            professor_id=data['professor_id'],
            theory_slot=data.get('theory_slot'),
            lab_slot=data.get('lab_slot')
        )
        db.session.add(offering)
    else:
        offering.theory_slot = data.get('theory_slot', offering.theory_slot)
        offering.lab_slot = data.get('lab_slot', offering.lab_slot)

    db.session.commit()
    return jsonify({"message": "Slot assigned successfully"})

@api_bp.route('/generate', methods=['POST'])
def generate():
    # Fetch all courses and their offerings
    courses = Course.query.all()
    scheduler_input = []
    
    for c in courses:
        options = []
        offerings = CourseOffering.query.filter_by(course_id=c.id).all()
        for off in offerings:
            cp = CourseProfessor.query.filter_by(course_id=c.id, professor_id=off.professor_id).first()
            prof = Professor.query.get(off.professor_id)
            options.append({
                'prof_id': off.professor_id,
                'prof_name': prof.name,
                'theory_slot': off.theory_slot,
                'lab_slot': off.lab_slot,
                'priority': cp.priority if cp else 3
            })
        
        if options:
            scheduler_input.append({
                'id': c.id,
                'name': c.name,
                'type': c.type,
                'options': options
            })

    if not scheduler_input:
        return jsonify({"error": "No course offerings found"}), 400

    scheduler = Scheduler(scheduler_input)
    timetables = scheduler.generate()
    
    # Score them
    results = []
    for i, tt in enumerate(timetables):
        score = calculate_score(tt)
        results.append({
            'id': i + 1,
            'score': score,
            'data': tt
        })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Save top 100 to DB (clear old ones first for simplicity in this demo)
    GeneratedTimetable.query.delete()
    for res in results[:100]:
        gt = GeneratedTimetable(score=res['score'], data=json.dumps(res['data']))
        db.session.add(gt)
    db.session.commit()

    return jsonify({"count": len(results), "top_results": results[:20]})

@api_bp.route('/timetables', methods=['GET'])
def get_timetables():
    tts = GeneratedTimetable.query.order_by(GeneratedTimetable.score.desc()).limit(50).all()
    output = []
    for tt in tts:
        output.append({
            'id': tt.id,
            'score': tt.score,
            'data': json.loads(tt.data)
        })
    return jsonify(output)

@api_bp.route('/best', methods=['GET'])
def get_best():
    # Use AI to rank
    tts = GeneratedTimetable.query.order_by(GeneratedTimetable.score.desc()).limit(10).all()
    if not tts:
        return jsonify({"error": "No generated timetables found"}), 404
    
    timetables_for_ai = []
    for tt in tts:
        timetables_for_ai.append({
            'id': tt.id,
            'score': tt.score,
            'data': json.loads(tt.data)
        })
    
    ai = AIRanker()
    ranking_data = ai.rank_and_explain(timetables_for_ai)
    return jsonify(ranking_data)

@api_bp.route('/data', methods=['GET'])
def get_all_data():
    courses = Course.query.all()
    profs = Professor.query.all()
    offerings = CourseOffering.query.all()
    
    return jsonify({
        "courses": [{"id": c.id, "name": c.name, "type": c.type, "credits": c.credits} for c in courses],
        "professors": [{"id": p.id, "name": p.name} for p in profs],
        "offerings": [{
            "id": o.id, 
            "course_id": o.course_id, 
            "professor_id": o.professor_id,
            "theory_slot": o.theory_slot,
            "lab_slot": o.lab_slot
        } for o in offerings]
    })

@api_bp.route('/delete_offering/<int:id>', methods=['DELETE'])
def delete_offering(id):
    offering = CourseOffering.query.get(id)
    if offering:
        db.session.delete(offering)
        db.session.commit()
        return jsonify({"message": "Offering deleted"})
    return jsonify({"error": "Offering not found"}), 404
