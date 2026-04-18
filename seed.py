from app.main import create_app
from app.models.models import db, Course, Professor, Slot

app = create_app('development')

def seed_database():
    with app.app_context():
        # Add basic slots if they do not exist
        slots = [
            {"slot_code": "A1", "day": "Monday", "start_time": "08:00", "end_time": "08:50"},
            {"slot_code": "B1", "day": "Monday", "start_time": "09:00", "end_time": "09:50"},
            {"slot_code": "C1", "day": "Monday", "start_time": "10:00", "end_time": "10:50"},
            {"slot_code": "D1", "day": "Monday", "start_time": "11:00", "end_time": "11:50"},
            {"slot_code": "L1", "day": "Monday", "start_time": "14:00", "end_time": "15:40"},
            {"slot_code": "A2", "day": "Tuesday", "start_time": "08:00", "end_time": "08:50"},
            {"slot_code": "B2", "day": "Tuesday", "start_time": "09:00", "end_time": "09:50"},
            {"slot_code": "C2", "day": "Tuesday", "start_time": "10:00", "end_time": "10:50"},
            {"slot_code": "D2", "day": "Tuesday", "start_time": "11:00", "end_time": "11:50"},
            {"slot_code": "L2", "day": "Tuesday", "start_time": "14:00", "end_time": "15:40"},
        ]
        
        for s in slots:
            if not Slot.query.filter_by(slot_code=s['slot_code']).first():
                slot = Slot(**s)
                db.session.add(slot)
                
        # Add Sample courses
        sample_courses = [
            {"name": "Data Structures", "type": "theory", "credits": 3},
            {"name": "Operating Systems", "type": "theory", "credits": 3},
            {"name": "Database Management", "type": "theory", "credits": 3},
            {"name": "Machine Learning Lab", "type": "lab", "credits": 2}
        ]
        
        for c in sample_courses:
            if not Course.query.filter_by(name=c['name']).first():
                course = Course(**c)
                db.session.add(course)
                
        # Add sample professors
        sample_profs = [
            {"name": "Dr. Smith"},
            {"name": "Dr. Johnson"},
            {"name": "Dr. Alan Turing"},
            {"name": "Prof. Ada Lovelace"}
        ]
        
        for p in sample_profs:
            if not Professor.query.filter_by(name=p['name']).first():
                prof = Professor(**p)
                db.session.add(prof)

        db.session.commit()
        print("Database seeded successfully with slots, courses, and professors!")

if __name__ == '__main__':
    seed_database()
