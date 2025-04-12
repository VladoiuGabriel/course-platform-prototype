from datetime import datetime, timedelta

from app import db
from flask_login import UserMixin

enrollments = db.Table('enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)


    enrolled_courses = db.relationship('Course', secondary=enrollments, back_populates='students')

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_key = db.Column(db.String(64), nullable=False)


    students = db.relationship('User', secondary=enrollments, back_populates='enrolled_courses')
    conference_active = db.Column(db.Boolean, default=False)
class ProfessorKeys(db.Model):
    __tablename__ = 'professor_keys'

    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(255), unique=True, nullable=False)
    is_used = db.Column(db.Integer, nullable=False, default=0)

def current_time_gmt_plus_2():
    return datetime.utcnow() + timedelta(hours=2)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=current_time_gmt_plus_2)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='messages')
    course = db.relationship('Course', backref='messages')

class Material(db.Model):
    __tablename__ = 'material'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    course = db.relationship('Course', backref='materials')