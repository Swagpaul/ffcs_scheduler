from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, UniqueConstraint
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    courses = db.relationship('Course', backref='user', lazy=True)
    professors = db.relationship('Professor', backref='user', lazy=True)
    timetables = db.relationship('GeneratedTimetable', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False) # theory, lab, embedded
    credits = db.Column(db.Integer, default=3)
    offerings = db.relationship('CourseOffering', backref='course', lazy=True, cascade="all, delete-orphan")
    professors = db.relationship('CourseProfessor', backref='course', lazy=True, cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint('name', 'user_id', name='uq_course_name_user'),)

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    courses = db.relationship('CourseProfessor', backref='professor', lazy=True)
    __table_args__ = (UniqueConstraint('name', 'user_id', name='uq_professor_name_user'),)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    score = db.Column(db.Float, default=0.0)
    data = db.Column(db.Text, nullable=False) # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
