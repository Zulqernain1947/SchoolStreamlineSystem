import json

from django.db import models
from django.http import HttpResponse
# from db_connection import db
#
# user = db['user']
from mongoengine import Document, fields, SequenceField, EmbeddedDocumentField
from django.contrib.sessions.models import Session
class User(Document):
    userName = fields.StringField()
    password = fields.StringField()
    email = fields.StringField()
    userType = fields.StringField()

class Teacher(Document):
    teacher_id = fields.SequenceField(primary_key=True)
    name = fields.StringField(required=True)
    email = fields.StringField(required=True)
    password = fields.StringField(required=True)
    phone_no = fields.StringField(required=True)
    joining_date = fields.DateTimeField(required=True)
    salary = fields.FloatField(required=True)

class Student(Document):
    student_id = fields.SequenceField(primary_key=True)
    name = fields.StringField(required=True)
    email = fields.StringField(required=True)
    password = fields.StringField(required=True)
    dob = fields.DateField(required=True)
    phone_no = fields.StringField(required=True)
    admission_date = fields.DateField(required=True)
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)

class Diary(Document):
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    course_id = fields.IntField(required=True)
    description = fields.StringField(required=True)
    date = fields.DateTimeField(required=True)


class Announcement(Document):
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    course_id = fields.IntField(required=True)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    date = fields.DateTimeField(required=True)

class Section(fields.EmbeddedDocument):
    section_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    course_ids = fields.ListField(fields.IntField(), required=True)
    teacher_ids = fields.ListField(fields.IntField(), required=True)
    std_counts = fields.IntField(required=True)


class Classroom(Document):
    classroom_id = SequenceField(primary_key=True)
    sections = fields.ListField(EmbeddedDocumentField(Section), required=True)
    total_students = fields.IntField(required=True)

class Course(Document):
    course_id = fields.SequenceField(primary_key=True)
    name = fields.StringField(required=True)


class Exam(Document):
    exam_id = fields.SequenceField(primary_key=True)
    course_id = fields.IntField(required=True)
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    exam_name = fields.StringField(required=True)
    exam = fields.FileField(required=True)


class Attendance(Document):
    student_id = fields.IntField(required=True)
    classroom_id = fields.IntField(required=True)
    course_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    date = fields.DateTimeField(required=True)
    status = fields.StringField(required=True)


class Quiz(fields.EmbeddedDocument):
    quiz_id = fields.SequenceField(primary_key=True)
    quiz_topic = fields.StringField(required=True)
    obtained_marks = fields.FloatField(required=True)
    total_marks = fields.FloatField(required=True)
    percentage = fields.FloatField(required=True)

class Assignment(fields.EmbeddedDocument):
    assignment_id = fields.SequenceField(primary_key=True)
    assignment_topic = fields.StringField(required=True)
    obtained_marks = fields.FloatField(required=True)
    total_marks = fields.FloatField(required=True)
    percentage = fields.FloatField(required=True)

class Marks(Document):
    student_id = fields.IntField(required=True)
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    course_id = fields.IntField(required=True)
    quizzes = fields.ListField(fields.EmbeddedDocumentField(Quiz), required=True)
    assignments = fields.ListField(fields.EmbeddedDocumentField(Assignment), required=True)
    totalMarks = fields.FloatField(required=True)

class MarksSheet(Document):
    student_id = fields.IntField(required=True)
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    course_id = fields.IntField(required=True)
    first_term_marks = fields.FloatField(required=True)
    first_term_total_marks= fields.FloatField(required=True)
    second_term_marks = fields.FloatField(required=True)
    second_term_total_marks = fields.FloatField(required=True)
    third_term_marks = fields.FloatField(required=True)
    third_term_total_marks = fields.FloatField(required=True)

class Challan_form(Document):
    student_id = fields.IntField(required=True)
    classroom_id = fields.IntField(required=True)
    section_id = fields.StringField(required=True)
    uploaded_file = fields.FileField(required= True)
    received_file = fields.FileField()
