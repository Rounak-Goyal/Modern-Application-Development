from flask import Flask, render_template, request, redirect, make_response
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException, NotFound
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
api = Api(app)


# Models
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)
    courses = db.relationship("Course",secondary = "enrollment")

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)
    

# Validations
class NotFoundError(HTTPException):
    def __init__(self, status_code, message = ''):
        self.response = make_response(message, status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

# Output Fields in JSON Format
course_fields = {
    "course_id": fields.Integer,
    "course_name": fields.String,
    "course_code": fields.String,
    "course_description": fields.String
}

student_fields = {
    "student_id": fields.Integer,
    "first_name": fields.String,
    "last_name": fields.String,
    "roll_number": fields.String
}


# Create Parsers to handle data in request body
update_course_parser = reqparse.RequestParser()
update_course_parser.add_argument("course_name")
update_course_parser.add_argument("course_code")
update_course_parser.add_argument("course_description")

create_course_parser = reqparse.RequestParser()
create_course_parser.add_argument("course_name")
create_course_parser.add_argument("course_code")
create_course_parser.add_argument("course_description")

update_student_parser = reqparse.RequestParser()
update_student_parser.add_argument("first_name")
update_student_parser.add_argument("last_name")
update_student_parser.add_argument("roll_number")

create_student_parser = reqparse.RequestParser()
create_student_parser.add_argument("first_name")
create_student_parser.add_argument("last_name")
create_student_parser.add_argument("roll_number")

create_enroll_parser = reqparse.RequestParser()
create_enroll_parser.add_argument("course_id")


# API Classes
class CourseAPI(Resource):
    @marshal_with(course_fields)
    def get(self, course_id):        
        # Get the course details from the database
        course = Course.query.filter(Course.course_id == course_id).scalar()
        
        if course:
            # course exists in database, hence return the course object which will be marshalled to json
            return course
        else:
            # Return 404 Error
            raise NotFoundError(status_code = 404)
    
    @marshal_with(course_fields)
    def put(self, course_id): # Update        
        course = Course.query.filter(Course.course_id == course_id).scalar()
        
        if course is None:
            raise NotFoundError(status_code= 404)
        
        # Get the data from request body
        args = update_course_parser.parse_args()
        course_name = args.get("course_name", None)
        course_code = args.get("course_code", None)
        course_description = args.get("course_description", None)
        
        if (course_name is None) or (course_name.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "COURSE001",
                error_message= "Course Name is required and should be string."                
            )
        
        if (course_code is None) or (course_code.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "COURSE002",
                error_message= "Course Code is required and should be string."                
            )
            
        if (course_description is not None) and (course_description.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "COURSE003",
                error_message= "Course Description should be string."
            )
            
        
        course.course_name = course_name
        course.course_code = course_code
        course.course_description = course_description
        db.session.commit()
        return course
        
    
    def delete(self, course_id):        
        # check if course exists
        course = Course.query.filter(Course.course_id == course_id).scalar()
        
        if course is None:
            raise NotFoundError(status_code= 404)
        
        enrolls = Enrollment.query.filter(Enrollment.course_id == course_id).all()
        
        for enroll in enrolls:
            db.session.delete(enroll)
        db.session.commit()
        
        db.session.delete(course)
        db.session.commit()
        return "",200
    
    @marshal_with(course_fields)
    def post(self):
        # Get the data from request body
        args = create_course_parser.parse_args()
        course_name = args.get("course_name", None)
        course_code = args.get("course_code", None)
        course_description = args.get("course_description", None)
        
        course = Course.query.filter(Course.course_code == course_code).scalar()
        
        if course is not None:
            return "",409
        
        if (course_name is None) or (course_name.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "COURSE001",
                error_message= "Course Name is required and should be string."                
            )
        
        if (course_code is None) or (course_code.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "COURSE002",
                error_message= "Course Code is required and should be string."                
            )
            
        if (course_description is not None) and (course_description.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "COURSE003",
                error_message= "Course Description should be string."
            )
            
        course = Course(
            course_name = course_name,
            course_code = course_code,
            course_description = course_description
        )
        
        db.session.add(course)
        db.session.commit()
        
        course = Course.query.filter(Course.course_code == course_code).one()
        
        return course,201
        

class StudentAPI(Resource):
    @marshal_with(student_fields)
    def get(self, student_id):        
        # Get the student details from the database
        student = Student.query.filter(Student.student_id == student_id).scalar()
        
        if student:
            # student exists in database, hence return the student object which will be marshalled to json
            return student
        else:
            # Return 404 Error
            raise NotFoundError(status_code = 404)
    
    @marshal_with(student_fields)
    def put(self, student_id): # Update        
        student = Student.query.filter(Student.student_id == student_id).scalar()
        
        if student is None:
            raise NotFoundError(status_code= 404)
        
        # Get the data from request body
        args = update_student_parser.parse_args()
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        roll_number = args.get("roll_number", None)
        
        if (first_name is None) or (first_name.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "STUDENT002",
                error_message= "First Name is required and should be string."                
            )
        
        if (roll_number is None) or (roll_number.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "STUDENT001",
                error_message= "Roll Number is required and should be string."                
            )
            
        if (last_name is not None) and (last_name.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "STUDENT003",
                error_message= "Last Name should be string."
            )
            
        
        student.first_name = first_name
        student.last_name = last_name
        student.roll_number = roll_number
        db.session.commit()
        return student
        
    
    def delete(self, student_id):        
        # check if student exists
        student = Student.query.filter(Student.student_id == student_id).scalar()
        
        if student is None:
            raise NotFoundError(status_code= 404)
        
        enrolls = Enrollment.query.filter(Enrollment.student_id == student_id).all()
        
        for enroll in enrolls:
            db.session.delete(enroll)
        db.session.commit()
        
        db.session.delete(student)
        db.session.commit()
        return "",200
    
    @marshal_with(student_fields)
    def post(self):
        # Get the data from request body
        args = update_student_parser.parse_args()
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        roll_number = args.get("roll_number", None)
        
        student = Student.query.filter(Student.roll_number == roll_number).scalar()
        
        if student is not None:
            return "",409
        
        if (first_name is None) or (first_name.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "STUDENT002",
                error_message= "First Name is required and should be string."                
            )
        
        if (roll_number is None) or (roll_number.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "STUDENT001",
                error_message= "Roll Number is required and should be string."                
            )
            
        if (last_name is not None) and (last_name.isnumeric()):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "STUDENT003",
                error_message= "Last Name should be string."
            )
            
        student = Student(
            first_name = first_name,
            last_name = last_name,
            roll_number = roll_number
        )
        
        db.session.add(student)
        db.session.commit()
        
        student = Student.query.filter(Student.roll_number == roll_number).one()        
        return student,201

class EnrollmentAPI(Resource):
    def get(self,student_id):
        student = Student.query.filter(Student.student_id == student_id).scalar()
        
        if student is None:
            raise BusinessValidationError(
                status_code= 400,
                error_code= "ENROLLMENT002",
                error_message= "Student does not exist"
            )
        enrolls = Enrollment.query.filter(Enrollment.student_id == student_id).all()
        
        if enrolls == []:
            raise NotFoundError(status_code= 404)
        
        l = []
        
        for enroll in enrolls:
            msg = {
                "enrollment_id": enroll.enrollment_id,
                "student_id": enroll.student_id,
                "course_id": enroll.course_id
            }
            l.append(msg)
            
        return l,200
    
    def post(self, student_id):
        args = create_enroll_parser.parse_args()
        course_id = args.get("course_id", None)
        
        student = Student.query.filter(Student.student_id == student_id).scalar()
        
        if student is None:
            raise BusinessValidationError(
                status_code= 400,
                error_code= "ENROLLMENT002",
                error_message= "Student does not exist"
            )
            
        course = Course.query.filter(Course.course_id == course_id).scalar()
        
        if course is None:
            raise BusinessValidationError(
                status_code= 400,
                error_code= "ENROLLMENT001",
                error_message= "Course does not exist"
            )
            
        enroll = Enrollment(
            student_id = student_id,
            course_id = course_id
        )
        
        db.session.add(enroll)
        db.session.commit()
        
        enrolls = Enrollment.query.filter(Enrollment.student_id == student_id).all()
        
        if enrolls == []:
            raise NotFoundError(status_code= 404)
        
        l = []
        
        for enroll in enrolls:
            msg = {
                "enrollment_id": enroll.enrollment_id,
                "student_id": enroll.student_id,
                "course_id": enroll.course_id
            }
            l.append(msg)
            
        return l,201
    
    def delete(self, course_id, student_id):
        student = Student.query.filter(Student.student_id == student_id).scalar()
        
        if student is None:
            raise BusinessValidationError(
                status_code= 400,
                error_code= "ENROLLMENT002",
                error_message= "Student does not exist"
            )
            
        course = Course.query.filter(Course.course_id == course_id).scalar()
        
        if course is None:
            raise BusinessValidationError(
                status_code= 400,
                error_code= "ENROLLMENT001",
                error_message= "Course does not exist"
            )
            
        enrolls = Enrollment.query.filter(
            Enrollment.student_id == student_id and Enrollment.course_id == course_id
        ).all()
        
        if enrolls == []:
            raise NotFoundError(status_code= 404)
        
        for enroll in enrolls:
            db.session.delete(enroll)
        db.session.commit()
        
        return "",200
        


# Adding the resources to the API
api.add_resource(CourseAPI, "/api/course", "/api/course/<int:course_id>")
api.add_resource(StudentAPI, "/api/student", "/api/student/<int:student_id>")
api.add_resource(EnrollmentAPI, "/api/student/<int:student_id>/course", "/api/student/<int:student_id>/course/<int:course_id>")


app.run(
    debug= True,
    port= 5000
)