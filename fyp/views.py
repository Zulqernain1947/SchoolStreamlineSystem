import json
import mimetypes
from bson import ObjectId
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from mongoengine import DoesNotExist
from djangoProject1 import settings
from .models import User, Teacher, Student, Classroom, Section, Course, Exam, Attendance, Marks, Quiz, Assignment, \
    Challan_form, \
    Diary, Announcement, MarksSheet
from django.http import JsonResponse, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseRedirect
from datetime import datetime, date
import google.generativeai as genai
import os
os.environ['API_KEY'] = ''
api_key = os.environ.get('API_KEY')
if api_key:
    genai.configure(api_key=api_key)
else:
    print("API_KEY environment variable is not set.")


username = ""
usertype = ""
useremail = ""


def logout(request):
    try:
        username = ""
        usertype = ""
        useremail = ""
        return redirect('login')
    except Exception as e:
        return redirect('login')


def login(request):


    global usertype, useremail, username
    if request.method == "POST":
        uname = request.POST.get("uname")
        pwd = request.POST.get("pwd")
        username = uname
        try:
            user = User.objects.get(userName=uname,password=pwd)
            useremail = user['email']
            utype = ""
            for mydata in User.objects.all():
                if uname == mydata.userName:
                    utype = mydata.userType
                    break

            usertype = utype

            if utype == "Admin":
                return render(request, "Admin/Dashboard1.html", {"name": uname})
            elif utype == "Student":
                return render(request, "Student/Dashboard2.html", {"name": uname})
            elif utype == "Teacher":
                return render(request, "Teacher/Dashboard3.html", {"name": uname})

        except DoesNotExist:
            # User not found or password incorrect
            return render(request, 'login.html', {'error': 'Invalid username or password'})


    return render(request, "Login.html")


def change_password(request):
    form = None

    if request.method == 'POST':
        uname = username
        email = useremail
        user = User.objects.filter(userName=uname, email=email).first()

        if user:
            old_password = request.POST.get('old_password')
            if old_password == user.password:
                # Passwords match, proceed with the form validation
                new_password = request.POST.get('new_password1')
                confirm_password = request.POST.get('new_password2')

                if new_password == confirm_password:
                    user.password = new_password
                    user.save()

                    user_type = usertype
                    if user_type == 'Student':
                        student = Student.objects.filter(email=email).first()
                        if student:
                            student.password = new_password
                            student.save()

                            messages.success(request, 'Your password was successfully updated!')
                            return redirect('login')
                    elif user_type == 'Teacher':
                        teacher = Teacher.objects.filter(email=email).first()
                        if teacher:
                            # Update teacher's password (if needed)
                            teacher.password = new_password
                            teacher.save()

                            messages.success(request, 'Your password was successfully updated!')
                            return redirect('login')

                else:
                    messages.error(request, 'New passwords do not match.')
                    # Redirect to error page with a specific URL name
                    return redirect('password_change_error')
            else:
                messages.error(request, 'Old password is incorrect.')
                # Redirect to error page with a specific URL name
                return redirect('password_change_error')
        else:
            messages.error(request, 'User not found.')
            # Redirect to error page with a specific URL name
            return redirect('password_change_error')
    else:
        # Use the built-in PasswordChangeForm
        form = PasswordChangeForm(request.user)
    if usertype == "Student":
        return render(request, 'Student/change_password.html', {'form': form})
    elif usertype == "Teacher":
        return render(request, 'Teacher/change_password.html', {'form': form})



def password_change_error(request):
    if usertype == "Student":
        return render(request, 'Student/password_change_error.html')
    elif usertype == "Teacher":
        return render(request, 'Teacher/password_change_error.html')

# admin request method
def classes(request):
    classrooms = []

    try:
        for classroom in Classroom.objects.all():
            class_info = {
                'class_id': classroom.id,
                'total_students': classroom.total_students,
                'sections': []
            }

            for section in classroom.sections:
                section_info = {
                    'section_id': section.section_id,
                    'name': section.name,
                    'course_ids': section.course_ids,
                    'teacher_ids': section.teacher_ids,
                    'std_counts': section.std_counts,
                    'students': [],
                    'teachers': [],
                    'courses': [],
                }

                courses_info = []
                for course_id in section.course_ids:
                    try:
                        course = Course.objects.get(course_id=course_id)
                        course_info = {
                            'course_id': course.course_id,
                            'course_name': course.name,
                        }
                        courses_info.append(course_info)
                    except Exception as e:
                        return HttpResponseServerError(f"An error occurred!! Course not found: {str(e)}")

                section_info['courses'] = courses_info

                teachers_info = []
                for teacher_id in section.teacher_ids:
                    try:
                        teacher = Teacher.objects.get(teacher_id=teacher_id)
                        teacher_info = {
                            'teacher_id': teacher.teacher_id,
                            'name': teacher.name,
                            'email': teacher.email,
                        }
                        teachers_info.append(teacher_info)
                    except Exception as e:
                        return HttpResponseServerError(f"An error occurred!! Teacher not found: {str(e)}")

                section_info['teachers'] = teachers_info

                students = Student.objects.filter(classroom_id=classroom.id, section_id=section.section_id)
                for student in students:
                    student_info = {
                        'name': student.name,
                        'email': student.email,
                    }
                    section_info['students'].append(student_info)

                class_info['sections'].append(section_info)

            classrooms.append(class_info)

        context = {
            'classrooms': classrooms,
        }

        return render(request, "Admin/Classes.html", context)

    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {str(e)}")


def students(request):
    return render(request, "Admin/Student.html")


def show_students(request):
    try:
        student = Student.objects.all()
        student_data = []

        for item in student:
            try:
                data_dict = item.to_mongo().to_dict()
                data_dict['_id'] = str(data_dict['_id'])
                data_dict['dob'] = data_dict['dob'].strftime('%Y-%m-%d')
                data_dict['admission_date'] = data_dict['admission_date'].strftime('%Y-%m-%d')
                student_data.append(data_dict)
            except Exception as e:
                print(f"Error processing student data: {e}")

        return JsonResponse({'data': student_data}, safe=False)

    except Exception as e:
        print(f"Error retrieving student data: {e}")
        return JsonResponse({'error': 'An error occurred while retrieving student data.'}, status=500)


def show_Exam(request):
    return render(request, 'Admin/ShowExam.html')


def get_Exam(request):
    try:
        exam = Exam.objects.all()
        exam_data = []

        for item in exam:
            try:
                data_dict = item.to_mongo().to_dict()
                data_dict['_id'] = str(data_dict['_id'])
                data_dict['exam'] = str(data_dict['exam'])
                exam_data.append(data_dict)
            except Exception as e:
                print(f"Error processing teacher data: {e}")

        return JsonResponse({'data': exam_data}, safe=False)

    except Exception as e:
        print(f"Error retrieving teacher data: {e}")
        return JsonResponse({'error': 'An error occurred while retrieving teacher data.'}, status=500)


def download_exam(request, exam_id):
    exam = Exam.objects.get(exam_id=exam_id)

    response = HttpResponse(exam.exam.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{exam.exam_name}.pdf"'

    return response


def teachers(request):
    return render(request, 'Admin/Teacher.html')

def show_teachers(request):
    try:
        teachers = Teacher.objects.all()
        teachers_data = []

        for item in teachers:
            try:
                data_dict = item.to_mongo().to_dict()
                data_dict['_id'] = str(data_dict['_id'])
                data_dict['joining_date'] = data_dict['joining_date'].strftime('%Y-%m-%d')
                teachers_data.append(data_dict)
            except Exception as e:
                print(f"Error processing teacher data: {e}")

        return JsonResponse({'data': teachers_data}, safe=False)

    except Exception as e:
        print(f"Error retrieving teacher data: {e}")
        return JsonResponse({'error': 'An error occurred while retrieving teacher data.'}, status=500)


def home(request):
    return render(request, "Admin/Dashboard1.html")


def home2(request):
    return render(request, "Student/Dashboard2.html")


def home3(request):
    return render(request, "Teacher/Dashboard3.html")


def courses(request):
    return render(request, 'Admin/Courses.html')


def show_courses(request):
    try:
        courses = Course.objects.all()
        courses_data = []

        for course in courses:
            classrooms = Classroom.objects.filter(sections__course_ids=course.course_id)
            for classroom in classrooms:
                for section in classroom.sections:
                    if course.course_id in section.course_ids:
                        try:
                            teacher = Teacher.objects.filter(teacher_id=section.teacher_ids[0]).first()

                            course_info = {
                                'course_id': str(course.course_id),
                                'course_name': course.name,
                                'class_id': str(classroom.classroom_id),
                                'section_id': section.section_id,
                                'teacher_id': str(teacher.teacher_id) if teacher else None,
                                'teacher_name': teacher.name if teacher else None,
                                'teacher_email': teacher.email if teacher else None,
                            }
                            courses_data.append(course_info)
                        except Exception as e:
                            print(f"Error processing teacher data: {e}")
            if not classrooms:
                # If the course is not taught in any classroom, include it once with default values
                course_info = {
                    'course_id': str(course.course_id),
                    'course_name': course.name,
                    'class_id': "-----",
                    'section_id': "-----",
                    'teacher_id': "-----",
                    'teacher_name': "-------",
                    'teacher_email': "--------",
                }
                courses_data.append(course_info)

        return JsonResponse({'data': courses_data}, safe=False)

    except Exception as e:
        print(f"Error retrieving course data: {e}")
        return JsonResponse({'error': 'An error occurred while retrieving course data.'}, status=500)


def send_Email( st):
    try:
        subject = "Challan Form"
        recipent_list = [st]
        from_email = settings.EMAIL_HOST_USER
        message = "Assalam o Alaikum \n Kindly find or download your challan form from student portal"
        send_mail(subject, message, from_email, recipent_list)
        return HttpResponse('Email sent successfully!')
    except ValidationError as e:
        return HttpResponse(f'Error: {e}')



def addStudents(request):
    if request.method == 'POST':
        try:
            count = int(request.POST.get('count'))
            print('Count:', count)

            for i in range(1, count + 1):
                name = request.POST.get(f'name{i}')
                email = request.POST.get(f'email{i}')
                password = request.POST.get(f'password{i}')
                dob = request.POST.get(f'dob{i}')
                phone = request.POST.get(f'phone_no{i}')
                adm_date = request.POST.get(f'admission_date{i}')
                classroom_id = request.POST.get(f'classroom_id{i}')
                section_id = request.POST.get(f'section_id{i}')

                print(f'Processing Student {i}:')
                print('Name:', name)
                print('Email:', email)
                print('Classroom ID:', classroom_id)
                print('Section ID:', section_id)

                cls = Classroom.objects(classroom_id=classroom_id).first()
                if cls:
                    print('Classroom Found:', cls)

                    chk = False
                    for section in cls.sections:
                        if section_id == section.section_id:
                            chk = True
                            stdCount = section.std_counts + 1
                            print('Section Found:', section)
                            print('Updated Student Count:', stdCount)
                            break  # Exit the loop after finding the section

                    if chk:
                        student = Student(
                            name=name,
                            email=email,
                            password=password,
                            dob=dob,
                            phone_no=phone,
                            admission_date=adm_date,
                            classroom_id=classroom_id,
                            section_id=section_id
                        )
                        student.save()
                        print('Student Saved:', student)

                        user = User(
                            userName=name,
                            password=password,
                            email=email,
                            userType="Student"
                        )
                        user.save()
                        print('User Saved:', user)

                        totalCount = cls.total_students + 1
                        Classroom.objects(classroom_id=classroom_id).update(total_students=totalCount)
                        Classroom.objects(classroom_id=classroom_id, sections__section_id=section_id).update(
                            set__sections__S__std_counts=stdCount
                        )
                        print('Classroom Updated:', cls)
                    else:
                        print('Section Not Found for ID:', section_id)
                else:
                    print('Classroom Not Found for ID:', classroom_id)

            return render(request, "Admin/Student.html")

        except Exception as e:
            # Log the error for debugging purposes
            print('Error:', str(e))
            return render(request, "Admin/Student.html", {"error": str(e)})

    # If not a POST request, render the form page
    return render(request, "Admin/Student.html")


def addTeachers(request):
    uname = username
    utype = usertype

    if request.method == 'POST':
        try:
            uname = username
            count = int(request.POST.get('count'))

            for i in range(1, count + 1):
                name = request.POST.get(f'name{i}')
                email = request.POST.get(f'email{i}')
                password = request.POST.get(f'password{i}')
                phone = request.POST.get(f'phone_no{i}')
                joining_date = request.POST.get(f'joiningDate{i}')
                salary = float(request.POST.get(f'salary{i}'))

                Teacher(
                    name=name,
                    email=email,
                    password=password,
                    phone_no=phone,
                    joining_date=joining_date,
                    salary=salary
                ).save()
                User(userName=name, password=password, email=email, userType="Teacher").save()

            return render(request, "Admin/Teacher.html", {"name": uname})
        except Exception as e:
            return render(request, "Admin/Teacher.html", {"error": str(e)})
    return render(request, "Admin/Teacher.html")


def addCourses(request):
    uname = username
    utype = usertype

    if request.method == 'POST':
        try:
            print("post")
            count = int(request.POST.get('count'))
            for i in range(1, count + 1):
                name = request.POST.get(f'name{i}')
                course = Course(
                    name=name
                )
                print("course")
                course.save()

            return render(request, "Admin/Courses.html")

        except Exception as e:
            print("Error", str(e))
            return render(request, "Admin/Courses.html")

    return render(request, "Admin/Courses.html")




def updateCourse(request, cour_id):
    uname = username
    utype = usertype

    if request.method == 'GET':
        if uname is not None and utype == "Admin":
            st = Course.objects.get(course_id=cour_id)
            return render(request, "Admin/UpdateCourse.html",{"data":st})
        else:
            return render(request, "Login.html", {"error": "First login to the system with Teacher credentials"})

    elif request.method == 'POST':
        try:
            course_id =int(request.POST.get('course_id'))
            updated_name = request.POST.get('name')

            if updated_name != '':
                Course.objects(course_id=course_id).update(name=updated_name)

            return render(request, "Admin/Courses.html")
        except Exception as e:
            return render(request, "Admin/UpdateCourse.html", {"error": str(e)})


def updateTeacher(request, tec_id):
    uname = username
    utype = usertype

    if request.method == 'GET':
        if uname is not None and utype == "Admin":
            st = Teacher.objects.get(teacher_id=tec_id)
            return render(request, "Admin/UpdateTeacher.html",{"data": st})
        else:
            return render(request, "Login.html", {"error": "First login to the system with Teacher credentials"})

    elif request.method == 'POST':
        try:
            teacher_id = int(request.POST.get("teacher_id"))
            updated_name = request.POST.get("name")
            updated_email = request.POST.get("email")
            updated_password = request.POST.get("password")
            updated_phone_no = request.POST.get("phone_no")
            updated_joining_date = request.POST.get("joining_date")
            updated_salary = request.POST.get("salary")

            if updated_name != '':
                Teacher.objects(teacher_id=teacher_id).update(name=updated_name)
            if updated_email != '':
                Teacher.objects(teacher_id=teacher_id).update(email=updated_email)
            if updated_password != '':
                Teacher.objects(teacher_id=teacher_id).update(password=updated_password)
            if updated_phone_no != '':
                Teacher.objects(teacher_id=teacher_id).update(phone_no=updated_phone_no)
            if updated_joining_date != '':
                Teacher.objects(teacher_id=teacher_id).update(joining_date=updated_joining_date)
            if updated_salary != '':
                Teacher.objects(teacher_id=teacher_id).update(salary=updated_salary)

            return render(request, "Admin/Teacher.html")
        except Exception as e:
            return render(request, "Admin/UpdateTeacher.html", {"error": str(e)})


def updateStudent(request,st_id):
    uname = username
    utype = usertype

    if request.method == 'GET':

        if uname is not None and utype == "Admin":
            st = Student.objects.get(student_id=st_id)
            return render(request, "Admin/UpdateStudent.html",{"data": st})
        else:
            return render(request, "Login.html", {"error": "First login to the system with Teacher credentials"})

    elif request.method == 'POST':
        try:
            id = st_id
            print(id)
            classroom_Id = int(request.POST.get('classroom_id'))
            section_Id = request.POST.get('section_id')
            updatedName = request.POST.get('name')
            updatedEmail = request.POST.get('email')
            updatedPassword = request.POST.get('password')
            updatedDob = request.POST.get('dob')
            updatedPhoneNo = request.POST.get('phone_no')
            updatedAdmissionDate = request.POST.get('admission_date')

            if updatedName != '':
                Student.objects(student_id=id, classroom_id = classroom_Id, section_id = section_Id).update(name=updatedName)
            if updatedEmail != '':
                Student.objects(student_id=id, classroom_id = classroom_Id, section_id = section_Id).update(email=updatedEmail)
            if updatedPassword != '':
                Student.objects(student_id=id, classroom_id = classroom_Id, section_id = section_Id).update(password=updatedPassword)
            if updatedDob != '':
                Student.objects(student_id=id, classroom_id = classroom_Id, section_id = section_Id).update(dob=updatedDob)
            if updatedPhoneNo != '':
                Student.objects(student_id=id, classroom_id = classroom_Id, section_id = section_Id).update(phone_no=updatedPhoneNo)
            if updatedAdmissionDate != '':
                Student.objects(student_id=id, classroom_id = classroom_Id, section_id = section_Id).update(admission_date=updatedAdmissionDate)

            return render(request, "Admin/Student.html")
        except Exception as e:
            return render(request, "Admin/UpdateStudent.html", {"error": str(e)})


def upload_chalan(request):
    if request.method == 'POST':
        student_id = int(request.POST.get('student_id'))
        classroom_id = int(request.POST.get('classroom_id'))
        section_id = request.POST.get('section_id')
        chalan_file = request.FILES['chalan']
        if not (student_id and classroom_id and section_id  and chalan_file):
            return HttpResponseBadRequest("Invalid form data. Please check your inputs.")

        chalan = Challan_form(
            student_id= student_id,
            classroom_id=classroom_id,
            section_id=section_id,
            uploaded_file=chalan_file
        )
        chalan.save()
        send_Email('bilal.visual@gmail.com')
    return render(request, "Admin/uploadChallan.html")

def removeStudent(request, st_id):
    uname = username
    utype = usertype

    try:
        if uname is None or utype != "Admin":
            return render(request, "Login.html", {"error": "First login to the system with Admin credentials"})

        if request.method == 'GET':
            st = Student.objects.get(student_id=st_id)
            return render(request, "Admin/removeStudent.html", {"data": st})

        elif request.method == 'POST':
            try:
                st = Student.objects.get(student_id=st_id)
                classroom_id = st.classroom_id
                section_id = st.section_id

                classroom = Classroom.objects.get(classroom_id=classroom_id)
                section_found = False
                for section in classroom.sections:
                    if section.section_id == section_id:
                        section_found = True
                        # Validate course_ids and teacher_ids before saving
                        if all(isinstance(course_id, int) for course_id in section.course_ids) \
                                and all(isinstance(teacher_id, int) for teacher_id in section.teacher_ids):
                            # Remove the student from the Student collection
                            st.delete()

                            # Decrement std_counts for the section
                            section.std_counts -= 1

                            # Decrement total_students for the classroom
                            classroom.total_students -= 1

                            classroom.save()  # Save the updated Classroom object
                            break
                        else:
                            return render(request, "Admin/removeStudent.html",
                                          {"error": "Invalid data in course_ids or teacher_ids"})
                if not section_found:
                    return render(request, "Admin/removeStudent.html", {"error": "Section not found in classroom"})
            except Student.DoesNotExist:
                return render(request, "Admin/removeStudent.html", {"error": "Student does not exist"})
            except Classroom.DoesNotExist:
                return render(request, "Admin/removeStudent.html", {"error": "Classroom does not exist"})
            except Exception as e:
                return render(request, "Admin/removeStudent.html", {"error": str(e)})

        return render(request,"Admin/Student.html")  # Redirect to student page after successful removal

    except Exception as e:
        return render(request, "Admin/removeStudent.html", {"error": str(e)})


def removeTeacher(request,tec_id):
    uname = username
    utype = usertype

    if request.method == 'GET':
        st = Teacher.objects.get(teacher_id=tec_id)
        if uname is not None and utype == "Admin":
            return render(request, "Admin/removeTeacher.html",{"data": st})
        else:
            return render(request, "Login.html", {"error": "First login to the system with Teacher credentials"})

    elif request.method == 'POST':
        try:
            Teacher.objects(teacher_id = tec_id).delete()
            return render(request, "Admin/Teacher.html", {"name": uname})
        except Exception as e:
            return render(request, "Admin/removeTeacher.html", {"error": str(e)})


def removeCourse(request,crs_id):
    uname = username
    utype = usertype

    if request.method == 'GET':
        st = Course.objects.get(course_id=crs_id)
        if uname is not None and utype == "Admin":
            return render(request, "Admin/removeCourse.html",{"data":st})
        else:
            return render(request, "Login.html", {"error": "First login to the system with Teacher credentials"})

    elif request.method == 'POST':
        try:
            Course.objects(course_id = crs_id).delete()
            return render(request, "Admin/Courses.html", {"name": uname})
        except Exception as e:
            return render(request, "Admin/removeCourse.html", {"error": str(e)})


# teacher Request method



def add_exam(request):
    if request.method == 'POST':
        course_id = int(request.POST.get('course_id'))
        classroom_id = int(request.POST.get('classroom_id'))
        section_id = request.POST.get('section_id')
        exam_name = request.POST.get('exam_name')
        exam_file = request.FILES['exam']
        if not (course_id and classroom_id and section_id and exam_name and exam_file):
            return HttpResponseBadRequest("Invalid form data. Please check your inputs.")

        exam = Exam(
            course_id=course_id,
            classroom_id=classroom_id,
            section_id=section_id,
            exam_name=exam_name,
            exam=exam_file
        )
        exam.save()

    return render(request, "Teacher/upload_exam.html")


def teacher_data(request):
    global useremail
    teacher = Teacher.objects.get(email=useremail)

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

    return render(request, "Teacher/teacher_data.html", context)


def marks(request, section_id, classroom_id, course_id):
    if request.method == 'POST':
        if username:
            student_data = Student.objects.filter(section_id=section_id, classroom_id=classroom_id)
            date = datetime.today().strftime('%Y-%m-%d')
            for student in student_data:
                student_id = student.student_id
                student_name = student.name

                first_term_marks = request.POST.get(f'first_term_{student_id}')
                second_term_marks = request.POST.get(f'second_term_{student_id}')
                third_term_marks = request.POST.get(f'third_term_{student_id}')

                marks_record = MarksSheet(
                    student_id=student_id,
                    classroom_id=classroom_id,
                    section_id=section_id,
                    course_id=course_id,
                    first_term_marks=first_term_marks,
                    first_term_total_marks=100,
                    second_term_marks=second_term_marks,
                    second_term_total_marks=100,
                    third_term_marks=third_term_marks,
                    third_term_total_marks=100,
                )
                marks_record.save()

            return render(request, "Teacher/mark_sheet.html", {'data': student_data})
        else:
            return render(request, "login.html", {'error': "Please login first"})

    else:
        if username:
            student_data = Student.objects.filter(section_id=section_id, classroom_id=classroom_id)
            if student_data:
                return render(request, "Teacher/mark_sheet.html", {'data': student_data})
            else:
                return render(request, "login.html", {'error': "No student found"})
        else:
            return render(request, "login.html", {'error': "Please login first"})


def add_diary(request, section_id, classroom_id, course_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        section_id_str = str(section_id)
        today_date = date.today()

        diary=Diary(
            classroom_id=classroom_id,
            section_id=section_id_str,
            course_id=course_id,
            description=description,
            date=today_date

        )
        diary.save()
    return render(request, "Teacher/add_diary.html")




def add_announcement(request, section_id, classroom_id, course_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        section_id_str = str(section_id)
        today_date = request.POST.get('date')

        announcement = Announcement(
            classroom_id=classroom_id,
            section_id=section_id_str,
            course_id=course_id,
            title=title,
            description=description,
            date=today_date

        )
        announcement.save()
    return render(request, "Teacher/teacher_announcement.html")


def markAttendence(request,section_id,classroom_id,course_id):
    if request.method == 'POST':
        if username:
            student_data = Student.objects.filter(section_id=section_id, classroom_id=classroom_id)
            date = datetime.today().strftime('%Y-%m-%d')
            for student in student_data:
                student_id = student.student_id
                student_name = student.name
                attendance_key = f'attendance_{student_id}'


                if request.POST.get(attendance_key)== 'on':
                    status = 'Present'
                else:
                    status = 'Absent'

                attendance_record = Attendance(
                    student_id=student_id,
                    name=student_name,
                    date=date,
                    status=status,
                    section_id=section_id,
                    classroom_id=classroom_id,
                    course_id=course_id
                )
                attendance_record.save()
                context = {'data': student_data, 'course_id': course_id}
            return render(request, "Teacher/MarkAttendence.html", context)
        else:
            return render(request, "login.html", {'error': "Please login first"})

    else:
        if username:
            student_data = Student.objects.filter(section_id=section_id, classroom_id=classroom_id)
            if student_data:
                context = {'data': student_data, 'course_id': course_id}

                return render(request, "Teacher/MarkAttendence.html", context)
            else:
                return render(request, "login.html", {'error': "No student found"})
        else:
            return render(request, "login.html", {'error': "Please login first"})


# student request method


def dashboard(request):
    # Retrieve the student object
    student = Student.objects.get(email=useremail)

    # Extract the classroom_id and section_id from the student object
    classroom_id = student.classroom_id
    name = student.name
    section_id = student.section_id

    # Retrieve the course_ids associated with the section
    classroom = Classroom.objects.get(classroom_id=classroom_id)
    section = next((section for section in classroom.sections if section.section_id == section_id), None)

    if section:
        course_ids = section.course_ids
        # Assuming you want the first course_id from the list
        course_id = course_ids[0] if course_ids else None
    else:
        course_id = None

    # Retrieve all attendance records for the student
    attendance_records = Attendance.objects.filter(student_id=student.student_id)

    # Calculate total, present, and absent counts for all courses
    total_attendance = attendance_records.count()
    present_attendance = attendance_records.filter(status="Present").count()
    absent_attendance = total_attendance - present_attendance

    return render(request, 'Student/dashboard.html', {'course_id': course_id, 'present_attendance': present_attendance,
                                              'absent_attendance': absent_attendance,
                                              'total_attendance': total_attendance, 'name': name})
def previous_diaries(request):
    try:
        # Get the student_id for the logged-in student
        student = Student.objects.get(email=useremail)

        # Extract classroom_id and section_id from the student object
        classroom_id = student.classroom_id
        section_id = student.section_id

        # Retrieve all diary entries for the specified classroom and section
        previous_diaries = Diary.objects.filter(
            classroom_id=classroom_id,
            section_id=section_id
        ).order_by('-date')

        # Send the relevant data to the template
        return render(request, 'Student/previous_diaries.html', {'diary_entries': previous_diaries})
    except Exception as e:
        # Handle exceptions, such as invalid input or database errors
        return render(request, 'Student/error.html', {'error': str(e)})

def chatbot_model(request):
    data = ""
    if request.method == 'POST':
        input_data = request.POST.get('data')
        section_id_str = "Tellme concise and to the point about "
        input_data = section_id_str + input_data
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input_data)
        data = response.text

    return render(request, "Student/Chatbot.html",context={'data':data})


def student_announcements(request):
    # Get the classroom_id and section_id for the logged-in student
    student = Student.objects.get(email=useremail)
    classroom_id = student.classroom_id
    section_id = student.section_id

    # Get the current date
    today = datetime.now().date()

    # Retrieve announcements for the student's classroom and section with a deadline greater than or equal to the current date
    announcements = Announcement.objects.filter(
        classroom_id=classroom_id,
        section_id=section_id,
        date__gte=today
    )

    return render(request, 'Student/student_announcements.html', {'announcements': announcements})
def student_diary(request):
    # Get the student_id for the logged-in student
    student = Student.objects.get(email=useremail)
    # Retrieve diary entries for the student's classroom and all sections
    diary_entries = Diary.objects.filter(
        classroom_id=student.classroom_id,
        section_id__in=[section.section_id for section in
                        Classroom.objects.get(classroom_id=student.classroom_id).sections]
    )

    # Extract course_ids from the sections in the student's classroom
    course_ids = [course_id for section in Classroom.objects.get(classroom_id=student.classroom_id).sections for course_id in section.course_ids]

    # Retrieve Course objects based on the extracted course_ids
    courses = Course.objects.filter(course_id__in=course_ids)

    # Send all relevant data to the template
    return render(request, 'Student/student_diary.html',
                  {'diary_entries': diary_entries, 'student': student, 'courses': courses})


def ins(request):
    # Add data to the Marks model
    marks_data = Marks(
        student_id=1,
        classroom_id=1,
        section_id='S001',
        course_id=1,
        quizzes=[
            Quiz(
                quiz_topic="Quiz 1",
                obtained_marks=8,
                total_marks=10,
                percentage=80
            ),
            Quiz(
                quiz_topic="Quiz 2",
                obtained_marks=15,
                total_marks=20,
                percentage=75
            )
        ],
        assignments=[
            Assignment(
                assignment_topic="Assignment 1",
                obtained_marks=18,
                total_marks=20,
                percentage=90
            ),
            Assignment(
                assignment_topic="Assignment 2",
                obtained_marks=25,
                total_marks=30,
                percentage=83
            )
        ],
        totalMarks=350
    )

    marks_data.save()


def get1(request):
    if username:
        student_data = Student.objects.filter(email=useremail)

        if student_data:
            student_id = student_data[0].student_id
            attendance_data = Attendance.objects.filter(student_id=student_id).to_json()

            # Parse JSON string to Python dictionary
            parsed_data = json.loads(attendance_data)

            return JsonResponse({"data": parsed_data})


def student(request, course_id):
    if username:
        student_data = Student.objects.filter(email=useremail)
        if student_data:
            student_id = student_data[0].student_id
            attendance_data = Attendance.objects.filter(
                student_id=student_id,
                course_id=course_id  # Filter by the provided course_id
            )

            # Organize attendance data by course
            courses_attendance = {}
            for record in attendance_data:
                course_id = record.course_id
                if course_id not in courses_attendance:
                    courses_attendance[course_id] = []

                courses_attendance[course_id].append({
                    "student_id": record.student_id,
                    "classroom_id": record.classroom_id,
                    "section_id": record.section_id,
                    "name": record.name,
                    "date": record.date,
                    "status": record.status,
                })

            # Extract all course_ids of this student
            course_ids = [course_id for section in
                          Classroom.objects.get(classroom_id=student_data[0].classroom_id).sections for
                          course_id in section.course_ids]

            # Retrieve Course objects based on the extracted course_ids
            courses = Course.objects.filter(course_id__in=course_ids)

            return render(request, "Student/Attendance.html", {"courses_attendance": courses_attendance, "courses": courses})
        else:
            return render(request, "login.html", {"error": "Student not found"})
    else:
        return render(request, "login.html", {"error": "Please login first"})


def show_courses1(request):
    if username is not None:
        student_data = Student.objects.filter(email=useremail)

        if student_data:
            st_name = student_data[0].name
            st_classroom_id = student_data[0].classroom_id
            section_id = student_data[0].section_id
            classroom_data = Classroom.objects.filter(classroom_id=st_classroom_id)

            if classroom_data:
                dic = {}
                for section in classroom_data[0].sections:
                    for course_id in section.course_ids:
                        course_data = Course.objects.filter(course_id=course_id)
                        if course_data:
                            dic[course_id] = \
                                {
                                     "name": course_data[0].name,
                                     "teacher_ids": section.teacher_ids,
                                     "exams": [],
                                     "quizzes": [],
                                     "assignments": []
                                 }

                            # Fetching exams for the course
                            exam_data = Exam.objects.filter(course_id=course_id, classroom_id=st_classroom_id)
                            for exam in exam_data:
                                dic[course_id]["exams"].append({"exam_name": exam.exam_name, "exam_id": str(exam.exam_id)})

                            # Assuming Marks is the document containing Assignment and Quiz
                            marks_data = Marks.objects.filter(student_id=student_data[0].student_id, classroom_id=st_classroom_id)
                            if marks_data:
                                for assignment in marks_data[0].assignments:
                                    dic[course_id]["assignments"].append({"assignment_topic": assignment.assignment_topic, "assignment_id": str(assignment.assignment_id)})

                                for quiz in marks_data[0].quizzes:
                                    dic[course_id]["quizzes"].append({"quiz_topic": quiz.quiz_topic, "quiz_id": str(quiz.quiz_id)})

                # Assuming there is only one teacher for simplicity, modify accordingly
                section = next((s for s in classroom_data[0].sections if s.section_id == section_id), None)
                if section:
                    st_teacher_ids = section.teacher_ids
                    teacher_data = Teacher.objects.filter(teacher_id__in=st_teacher_ids)

                    if teacher_data:
                        tech_names = [teacher.name for teacher in teacher_data]

                        return render(request, "Student/AllCourses.html", {"st_name": st_name, "cls_id": st_classroom_id,
                                                                "tec_names": tech_names, "data": dic})
                    else:
                        return HttpResponse("Teacher not found.")
                else:
                    return HttpResponse("Section not found.")
            else:
                return HttpResponse("Classroom not found.")
        else:
            return render(request, "login.html", {"error": "Student not found"})
    else:
        return render(request, "login.html", {"error": "Please login first"})



def get_Data(request):
    n1=""
    context={}
    try:
        if request.method =="POST":
            n1=request.POST.get('name')
            n2=request.POST.get('cgpa')
            n3=request.POST.get('class')
            print(n1)
            u=User(userName=n1,email=n2,password="123",userType=n3).save()
            context={'data':n1}
    except Exception as e:
        print("ERROR",e)
    return render(request,"index1.html",context)


def get_marks(request, course_id):
    if username:
        student_data = Student.objects.filter(email=useremail)

        if student_data:
            student_id = student_data[0].student_id
            class_id = student_data[0].classroom_id
            sec_id = student_data[0].section_id
            marks_data = MarksSheet.objects.filter(course_id=course_id, student_id=student_id,classroom_id=class_id,section_id=sec_id)

            if marks_data:  # Check if marks_data has any items
                st_name = student_data[0].name
                st_classroom_id = student_data[0].classroom_id
                classroom_data = Classroom.objects.filter(classroom_id=st_classroom_id)

                if classroom_data:
                    st_teacher_ids = classroom_data[0].sections[0].teacher_ids  # Assuming there is only one section
                    teacher_data = Teacher.objects.filter(teacher_id__in=st_teacher_ids)

                    if teacher_data:
                        tech_names = [teacher.name for teacher in teacher_data]
                        return render(request, "Student/Student_marks.html", {
                            'st_name': st_name,
                            'cls_id': st_classroom_id,
                            'tec_names': tech_names,
                            'data': marks_data[0],
                        })
                    else:
                        return HttpResponse("Teacher not found.")
                else:
                    return HttpResponse("Classroom not found.")
            else:
                return HttpResponse("No marks data found for this course and student.")
        else:
            return render(request, "login.html", {"error": "Student not found"})
    else:
        return render(request, "login.html", {"error": "Please login first"})


def show_challan_form(request):
    # Fetch student_id, classroom_id, and section_id from the logged-in user
    if username:
        student_data = Student.objects.filter(email=useremail)

        if student_data:
            student_id = student_data[0].student_id
            classroom_id = student_data[0].classroom_id
            section_id = student_data[0].section_id
        else:
            return HttpResponseBadRequest("Student data not found for the logged-in user.")
    else:
        return HttpResponseBadRequest("User not logged in.")

    if request.method == 'POST':
        # Handle file upload if the form is submitted
        received_file = request.FILES.get('received_file')

        if not (student_id and classroom_id and section_id and received_file):
            return HttpResponseBadRequest("Invalid form data. Please check your inputs.")

        # Update the existing challan form with the received_file
        challan = Challan_form.objects.filter(
            student_id=student_id,
            classroom_id=classroom_id,
            section_id=section_id
        ).first()

        if challan:
            challan.received_file = received_file
            challan.save()

    # Fetch the existing challan file for the user's section, student_id, and classroom_id
    challan = Challan_form.objects.filter(
        student_id=student_id,
        classroom_id=classroom_id,
        section_id=section_id
    ).first()
    print(f'{student_id} , {section_id}, {classroom_id}')
    if challan:
        return render(request, "Student/showChallanForm.html", {'challan': challan})
    else:
        return HttpResponseBadRequest("Challan not found for the specified criteria.")

def download_challan(request, challan_id,section_id,classroom_id):
    # Retrieve the Challan_form object
    challan = Challan_form.objects.get(student_id=challan_id,section_id=section_id,classroom_id=classroom_id)

    # Prepare the response with the downloaded file
    response = HttpResponse(challan.uploaded_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="RollNumber_{challan_id}.pdf"'

    return response




