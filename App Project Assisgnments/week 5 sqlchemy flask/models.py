from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#create a Flask Instance
app=Flask(__name__)
# Add Database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
#Initialize the database
db=SQLAlchemy(app)

#create Model
class Student(db.Model):
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number=db.Column(db.String(100), nullable=False, unique=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100))

class Course(db.Model):
    course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code=db.Column(db.String(100), nullable=False, unique=True)
    course_name=db.Column(db.String(100), nullable=False)
    course_description=db.Column(db.String(100))


class Enrollments(db.Model):
    enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    estudent_id=db.Column(db.Integer, db.ForeignKey('student.student_id'),nullable=False)
    ecourse_id=db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
