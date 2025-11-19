from flask import Flask, jsonify, request, make_response, abort
from flask_restful import Api, Resource
from config import Config
from flask_migrate import Migrate
from models import db, Student, Profile, Instructor, Course, Enrollment
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config.from_object(Config)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Home(Resource):
    def get(self):
        response_body = {"message": "Course enrollment backend API"}

        response = make_response(response_body, 200)
        return response

api.add_resource(Home, '/')

class Courses(Resource):
    # Api to return all the courses present
    def get(self):
        courses = [c.to_dict() for c in Course.query.all()]

        if courses:
            response = make_response(courses, 200)
            return response
        else:
            abort(404, description="Could not fetch the courses")
    # Handles addition of new course to the system    
    def post(self):
        data = request.get_json()

        new_course = Course(
            title=data.get('title'),
            instructor_id=data.get('instructor_id')
        )
        db.session.add(new_course)
        db.session.commit()

        new_course_dict = new_course.to_dict()
        response = make_response(new_course_dict, 201)

        return response
    

api.add_resource(Courses, '/course')

class CourseByID(Resource):
    # Hanldes the fetching of a course
    def get(self, id):
        course_dict = Course.query.filter_by(id=id).first()

        if not course_dict:
            abort(404, description='Course cannot be found')
        
        response = make_response(course_dict.to_dict(), 200)
        return response

    # Handles the updating of a course     
    def put(self, id):
        course = Course.query.filter_by(id=id).first()

        if not course:
            abort(404, description='Course not found')

        data = request.get_json()

        for attr, value in data.items():
            setattr(course, attr, value)

        db.session.commit()
        response = make_response(course.to_dict(), 200)
        return response

    # Handles the deletion of a course
    def delete(self, id):
        course = Course.query.filter_by(id=id).first()

        if not course:
            abort(404, description='Course not found')

        db.session.delete(course)
        db.session.commit()

        response = {"message": "Course deleted successfully"}
        return response


api.add_resource(CourseByID, '/course/<int:id>')


class Students(Resource):
    # handling the fetching of students from the database
    def get(self):
        student_list_dict = [s.to_dict() for s in Student.query.all()]

        if student_list_dict:
            response = make_response(student_list_dict, 200)
            return response
        
        else:
            error_response = {"message": "Error fetching students"}
            response = make_response(error_response, 404)
            return response
        
    def post(self):
        data = request.get_json()
        new_student = Student(
            name=data["name"],
            email=data["email"]
        )

        db.session.add(new_student)
        db.session.commit()

        return make_response(new_student.to_dict(), 201)
    
api.add_resource(Students, '/student')

class StudentByID(Resource):
    # Fetching a specific student
    def get(self, id):
        student_dict = Student.query.filter_by(id=id).first()

        if student_dict:
            response = make_response(student_dict.to_dict(), 200)
            return response
        else:
            error_response = {"message": "Error fetching student"}
            response = make_response(error_response, 404)
            return response
        
    def put(self, id):
        data = request.get_json()

        student = Student.query.filter_by(id=id).first()

        if not student:
            abort(404, description="Student not found")

        for attr, value in data.items():
            setattr(student, attr, value)


        db.session.commit()

        response = make_response(student.to_dict(), 200)
        return response


api.add_resource(StudentByID, '/student/<int:id>')


class StudentsCount(Resource):
    # Api to return the total number of students
    def get(self):
        students_list = Student.query.count()

        if students_list:

            res = {"count": students_list}

            response = make_response(res, 200)
            return response
        
        else:
            error_response = {"message": "Error fetching item"}
            response = make_response(error_response, 404)
            return response

api.add_resource(StudentsCount, '/student_count')

class Instructors(Resource):
    def get(self):
        instructors_list_dict = [i.to_dict() for i in Instructor.query.all()]

        if instructors_list_dict:
            response = make_response(instructors_list_dict, 200)
            return response
        
        else:
            error_response = {"message": "Error fetching instructors"}
            response = make_response(error_response, 404)
            return response
    
    def post(self):
        data = request.get_json()
        new_instructor = Instructor(name=data["name"])

        db.session.add(new_instructor)
        db.session.commit()

        response = make_response(new_instructor.to_dict(), 201)
        return response

api.add_resource(Instructors, '/instructor')

class InstructorsByID(Resource):
    def get(self, id):
        instructor_dict = Instructor.query.filter_by(id=id).first()

        if instructor_dict:
            response = make_response(instructor_dict.to_dict(), 200)
            return response
        else:
            error_response = {"message": "Error fetching instructor"}
            response = make_response(error_response, 404)
            return response
        
    
    def delete(self, id):
        instructor = Instructor.query.filter_by(id=id).first()

        if not instructor:
            abort(404, description="Instructor not found")

        db.session.delete(instructor)
        db.session.commit()

        response = make_response({"message": "Instructor deleted successfully"}, 200)
        return response

    def put(self, id):
        instructor = Instructor.query.filter_by(id=id).first()

        if not instructor:
            abort(404, description="Could not find instructor")

        data = request.get_json()

        for attr, value in data.items():
            setattr(instructor, attr, value)
        
        db.session.commit()

        response = make_response(instructor.to_dict(), 200)
        return response

api.add_resource(InstructorsByID, '/instructor/<int:id>')

class Enrollments(Resource):
    def post(self):
        data = request.get_json()
        # Validate missing fields
        if not data.get("student_id") or not data.get('course_id'):
            abort(400, description='student_id and course_id are required')

        # Prevent double enrollment
        existing = Enrollment.query.filter_by(student_id=data['student_id'], course_id=data['course_id']).first()
        if existing:
            abort(409, description="Student is already enrolled in this course")

        grade = data.get('grade', 'N/A')
        new_enrollment = Enrollment(
            grade=grade,
            course_id=data.get('course_id'),
            student_id=data.get('student_id'),
            date_enrolled=datetime.utcnow()
        )

        student = Student.query.get(data.get('student_id'))
        course = Course.query.get(data.get('course_id'))

        if not student or not course:
            abort(404, description='Invalid student_id or course_id')

        db.session.add(new_enrollment)
        db.session.commit()

        response = make_response(new_enrollment.to_dict(), 201)
        return response
    
    def get(self):
        all_enrollments = [e.to_dict() for e in Enrollment.query.all()]

        if not all_enrollments:
            abort(404, description="Could not fetch enrollments from the database")
        
        return make_response(all_enrollments, 200)

api.add_resource(Enrollments, '/enrollment')


class EnrollmentByID(Resource):
    def get(self, id):
        enrollment = Enrollment.query.filter_by(id=id).first()

        if not enrollment:
            error_response = {"message": "Could not find enrollment"}
            response = make_response(error_response, 404)
            return response
        
        response = make_response(enrollment.to_dict(), 200)
        return response

    def delete(self, id):
        enrollment = Enrollment.query.filter_by(id=id).first()
        
        if not enrollment:
            error_response = {"message": "Could not find enrollment"}
            response = make_response(error_response, 404)
            return response

        db.session.delete(enrollment)
        db.session.commit()

        response = {"message": "Deleted successfully"}
        return response

api.add_resource(EnrollmentByID, '/enrollment/<int:id>')

class ProfileByID(Resource):
    def get(self, id):
        profile = Profile.query.filter_by(id=id).first()

        if not profile:
            abort(404, description='Could not find profile')
    
        response = make_response(profile.to_dict(), 200)
        return response
    
    def put(self, id):
        profile = Profile.query.filter_by(id=id).first()

        if not profile:
            abort(404, description='Profile not found')

        data = request.get_json()

        for attr, value in data.items():
            setattr(profile, attr, value)
        
        db.session.commit()

        response = make_response(profile.to_dict(), 200)
        return response

api.add_resource(ProfileByID, '/profile/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)