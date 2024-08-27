from django.db import models
# from db_connection import db
#
# user = db['user']
from mongoengine import Document, fields,EmbeddedDocument,EmbeddedDocumentField
class User(Document):
    userName = fields.StringField()
    password = fields.StringField()
    email = fields.StringField()
    userType = fields.StringField()

class Exam(Document):
    exam_id = fields.StringField(required=True)
    course_id = fields.StringField(required=True)
    classroom_id = fields.StringField(required=True)
    section_id = fields.StringField(required=True)
    exam_name = fields.StringField(required=True)
class Teacher(Document):
    teacher_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    email = fields.StringField(required=True)
    password = fields.StringField(required=True)
    phone_no = fields.StringField(required=True)
    joining_date = fields.DateTimeField(required=True)
    salary = fields.FloatField(required=True)

class Student(Document):
    student_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    email = fields.StringField(required=True)
    password = fields.StringField(required=True)
    dob = fields.DateTimeField(required=True)
    phone_no = fields.StringField(required=True)
    admission_date = fields.DateTimeField(required=True)
    section_id = fields.StringField(required=True)
    classroom_id = fields.StringField(required=True)

class Section(EmbeddedDocument):
    section_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    course_ids = fields.ListField(fields.StringField(), required=True)
    teacher_ids = fields.ListField(fields.StringField(), required=True)
    std_counts = fields.IntField(required=True)

class Classroom(Document):
    classroom_id = fields.StringField(required=True)
    sections = fields.ListField(fields.EmbeddedDocumentField(Section), required=True)
    total_students = fields.IntField(required=True)
class Course(Document):
    course_id = fields.StringField(required=True)
    name = fields.StringField(required=True)

class Attendance(Document):
    student_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    date = fields.StringField(required=True)
    status = fields.StringField(required=True)







