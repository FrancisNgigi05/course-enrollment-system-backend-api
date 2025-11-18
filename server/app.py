from flask import Flask, jsonify, request, make_response, abort
from flask_restful import Api, Resource
from config import Config
from flask_migrate import Migrate
from models import db, Student, Profile, Instructor, Course, Enrollment
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
        course_dict = [c.to_dict() for c in Course.query.all()]

        if course_dict:
            response = make_response(course_dict, 200)
            return response
        else:
            error_response = {"message": "No item was found"}
            response = make_response(error_response, 404)
            return response
        
api.add_resource(Courses, '/course')

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
    
api.add_resource(Students, '/student')

class StudentByID(Resource):
    # Fetching a specific student
    def get(self, id):
        student_dict = Student.query.filter_by(id=id).first().to_dict()

        if student_dict:
            response = make_response(student_dict, 200)
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
        students_list = [s.to_dict for s in Student.query.all()]

        if students_list:
            student_count = len(students_list)

            res = {"count": student_count}

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

api.add_resource(Instructors, '/instructor')

class InstructorsByID(Resource):
    def get(self, id):
        instructor_dict = Instructor.query.filter_by(id=id).first().to_dict()

        if instructor_dict:
            response = make_response(instructor_dict, 200)
            return response
        else:
            error_response = {"message": "Error fetching instructor"}
            response = make_response(error_response, 404)
            return response

api.add_resource(InstructorsByID, '/instructor/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)