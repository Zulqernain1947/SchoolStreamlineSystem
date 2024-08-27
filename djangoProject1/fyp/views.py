from django.shortcuts import render,redirect,HttpResponseRedirect
from .models import User,Teacher,Student,Section,Course,Classroom,Attendance,Exam
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as django_login

# Create your views here.

def teacher_data(request, teacher_id):
    teacher = Teacher.objects.get(teacher_id=teacher_id)

    classrooms = {}

    for classroom in Classroom.objects.filter(sections__teacher_ids=teacher.teacher_id):
        if classroom.classroom_id not in classrooms:
            classrooms[classroom.classroom_id] = {
                'sections': [],
            }

        for section in classroom.sections:
            if teacher.teacher_id in section.teacher_ids:
                students = Student.objects.filter(section_id=section.section_id, classroom_id=classroom.classroom_id)
                student_data = [{
                    'name': student.name,
                    'email': student.email,
                } for student in students]

                teacher_courses = Course.objects.filter(course_id__in=section.course_ids)
                course_data = [{
                    'course_name': course.name,
                    'course_id': course.course_id,
                } for course in teacher_courses]

                classrooms[classroom.classroom_id]['sections'].append({
                    'section_id': section.section_id,
                    'name': section.name,
                    'courses': course_data,
                    'std_counts': section.std_counts,
                    'students': student_data,
                })

    context = {
        'teacher': teacher,
        'classrooms': classrooms,
    }

    return render(request, "teacher_data.html", context)














def index(request):
    exam_data = {
        "exam_id": "your_exam_id",
        "course_id": "your_course_id",
        "classroom_id": "your_classroom_id",
        "section_id": "your_section_id",
        "exam_name": "your_exam_name",
    }
    exam_instance = Exam(**exam_data)
    exam_instance.save()
    return HttpResponse("Hello")

#     # records={
#     #     "userName":"Mirha",
#     #     "password":"123",
#     #     "email":"Mirha@gmail.com",
#     #     "userType":"Teacher"
#     # }
#     # user=User(**records)
#     # user.save()
#     # classroom_data = {
#     #     "classroom_id": "C001",
#     #     "sections": [
#     #         {
#     #             "section_id": "S001",
#     #             "name": "A",
#     #             "course_ids": ["1", "2"],
#     #             "teacher_ids": ["T001", "T002"],
#     #             "std_counts": 30
#     #         }
#     #     ],
#     #     "total_students": 30
#     # }
#     #
#     # classroom = Classroom(**classroom_data)
#     # classroom.save()
#
#
#     # records1 = {
#     #     "student_id": "10",
#     #     "name": "minsa",
#     #     "email": "ml@gmail.com",
#     #     "password": "123",
#     #     "dob": datetime.strptime("2002-04-26", "%Y-%m-%d"),
#     #     "phone_no": "234556",
#     #     "admission_date": datetime.strptime("2023-05-06", "%Y-%m-%d"),
#     #     "section_id": "1"
#     # }
#     # user1 = Student(**records1)
#     # user1.save()
#     # records1 = {
#     #     "icon": "this",
#     #     "title": "minsa",
#     #     "desc": "hello!!!!! and welcome"
#     # }
#     # users = service(**records1)
#     # users.save()
#     #
#     # classroom_data = {
#     #     "classroom_id": "C002",
#     #     "sections": [
#     #         Section(
#     #             section_id="S003",
#     #             name="Arts Section2",
#     #             course_ids=["3", "2"],
#     #             teacher_ids=["T001"],
#     #             std_counts=20
#     #         )
#     #     ],
#     #     "total_students": 20
#     # }
#     #
#     # # Save the Classroom object
#     # classroom = Classroom(**classroom_data)
#     # classroom.save()
#     #
#     # student_data = {
#     #     "student_id": "ST002",
#     #     "name": "mirha",
#     #     "email": "mirha@example.com",
#     #     "password": "12",
#     #     "dob": datetime(2003, 11, 1),
#     #     "phone_no": "1567890",
#     #     "admission_date": datetime(2022, 11, 1),
#     #     "section_id": "S001",
#     #     "classroom_id": "C001",
#     # }
#     #
#     # student = Student(**student_data)
#     # student.save()
#     return HttpResponse("Hello")
#
# def get_All(request):
#     # record= User.objects(userName='zohan')
#     # return HttpResponse(record[0]["userName"])
#     sdata=User.objects.all()
#     dt={
#         'sdt':sdata
#     }
#     return render(request, "teacher_data.html", dt)
#
# def get_Data(request):
#     n1=""
#     context={}
#     try:
#         if request.method =="POST":
#             n1=request.POST.get('name')
#             n2=request.POST.get('cgpa')
#             n3=request.POST.get('class')
#             print(n1)
#             u=User(userName=n1,email=n2,password="123",userType=n3).save()
#             context={'data':n1}
#     except Exception as e:
#         print("ERROR",e)
#     return render(request,"index.html",context)
#
#
#
#
#
# def aboutus(request):
#     return HttpResponse("hello i'm mirha")
#
# def courses(request,id):
#     return HttpResponse(id)
#
# def home(request):
#     data={
#         'title':'my page',
#         'dt':'welcome to my page',
#         'clist':['django','flask','python'],
#         'num':[10,20,30,40],
#         'std_details':[
#             {'name':'minahil','phone':'233647'},
#             {'name': 'minha', 'phone': '2312364547'}
#         ]
#     }
#     return render(request,"hello.html",data)
# def userform(request):
#     res=""
#     dict={}
#     try:
#         if request.method == "POST":
#             n1=request.POST['un']
#             n2=request.POST['em']
#             res=n1+n2
#             dict={
#                 'var1':res
#             }
#             return HttpResponseRedirect('home')
#     except:
#         pass
#     return render(request,"form.html",dict)
#
# def submitform(request):
#     return HttpResponse("submitted")



