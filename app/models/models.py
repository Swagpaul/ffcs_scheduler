from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime
import json

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(20), nullable=False) # theory, lab, embedded
    credits = db.Column(db.Integer, default=3)
    offerings = db.relationship('CourseOffering', backref='course', lazy=True, cascade="all, delete-orphan")
    professors = db.relationship('CourseProfessor', backref='course', lazy=True, cascade="all, delete-orphan")

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    courses = db.relationship('CourseProfessor', backref='professor', lazy=True)

class CourseProfessor(db.Model):
    __tablename__ = 'course_professors'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False, index=True)
    priority = db.Column(db.Integer, default=1) # 1 is best

class Slot(db.Model):
    __tablename__ = 'slots'
    id = db.Column(db.Integer, primary_key=True)
    slot_code = db.Column(db.String(10), nullable=False, unique=True, index=True) # A1, B1, L1...
    day = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False) # HH:MM
    end_time = db.Column(db.String(10), nullable=False)

class CourseOffering(db.Model):
    __tablename__ = 'course_offerings'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False, index=True)
    theory_slot = db.Column(db.String(10), nullable=True)
    lab_slot = db.Column(db.String(10), nullable=True)

class GeneratedTimetable(db.Model):
    __tablename__ = 'generated_timetables'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, default=0.0)
    data = db.Column(db.Text, nullable=False) # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
