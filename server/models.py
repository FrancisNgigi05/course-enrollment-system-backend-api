from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


db = SQLAlchemy(metadata=metadata)

class Student(db.Model, SerializerMixin):
    __tablename__ = "students"

    serialize_rules = ('-profile.student', '-enrollments.student',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    # Relationship between the student to the related profile
    profile = db.relationship('Profile', uselist=False, back_populates='student', cascade='all, delete-orphan')
    # Relationship between students to their related enrollments
    enrollments = db.relationship('Enrollment', back_populates='student', cascade="all, delete-orphan")

    courses = association_proxy('enrollments', 'course', creator=lambda course_obj: Enrollment(course=course_obj))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile": {
                "age": self.profile.age,
                "bio": self.profile.bio,
                "student_id": self.profile.student_id,
            },
            "enrollments": [e.to_dict() for e in self.enrollments]
        }


    def __repr__(self):
        return f"<Student {self.id} {self.name} {self.email}>"

class Profile(db.Model, SerializerMixin):
    __tablename__ = "profiles"

    serialize_rules = ('-student.profile',)

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.String, nullable=False)
    # Storing the foreign key to initialize the relationship
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True)
    # Relationship between profile to the associated student
    student = db.relationship('Student', back_populates='profile')


    def to_dict(self):
        return {
            "age": self.age,
            "bio": self.bio,
            "student_id": self.student_id
        }


    def __repr__(self):
        return f"<Profile {self.id} {self.age} {self.bio}>"

class Instructor(db.Model, SerializerMixin):
    __tablename__ = "instructors"

    serialize_rules = ('-courses.instructor',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # Relationship between instractor to their associated courses
    courses = db.relationship('Course', back_populates="instructor", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "courses": [
                {
                    "id": course.id,
                    "title": course.title,
                    "instructor_id": course.instructor_id
                } 
                for course in self.courses
            ]
        }

    def __repr__(self):
        return f"<Instructor {self.id} {self.name}>"

class Course(db.Model, SerializerMixin):
    __tablename__ = "courses"

    serialize_rules = ('-instructor.courses', '-enrollments.course',)
    # serialize_only = ('id', 'title', 'instructor_id', 'instructor', 'enrollments')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)

    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'))

    instructor = db.relationship('Instructor', back_populates="courses")

    # Relationship between course to their related enrolments
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')

    students = association_proxy('enrollments', 'student', creator=lambda student_obj: Enrollment(student=student_obj))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,

            "instructor": {
                "id": self.instructor.id,
                "name": self.instructor.name
            } if self.instructor else None,
            "student_count": len(self.students)
        }

    def __repr__(self):
        return f"<Course {self.id} {self.title}>"

class Enrollment(db.Model, SerializerMixin):
    __tablename__ = "enrollments"

    serialize_rules = ('-student.enrollments', '-course.enrollments',)

    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String, nullable=True, default="N/A")
    date_enrolled = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Foreing key to store the relationship between student and enrollment
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    # Foreign key to store the relationship between courses and enrollment 
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    student = db.relationship('Student', back_populates="enrollments")
    course = db.relationship('Course', back_populates="enrollments")

    def to_dict(self):
        return{
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "date_enrolled": self.date_enrolled,
            "grade":self.grade,
            "course": {
                "id": self.course.id,
                "title": self.course.title,
                "instructor_id": self.course.instructor_id,
                "instructor": {
                    "id": self.course.instructor.id,
                    "name": self.course.instructor.name
                }
            }if self.course else None
        }

    def __repr__(self):
        return f"<Enrollment {self.id} {self.grade} {self.date_enrolled}>"