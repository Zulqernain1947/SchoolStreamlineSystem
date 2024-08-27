from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from . import views
from .views import change_password, password_change_error, show_challan_form, student_announcements, student_diary

urlpatterns = [
    path('home',views.home),
    path('home2', views.home2),
    path('home3', views.home3),
    path('classes', views.classes),
    path('teachers', views.teachers),
    path('students', views.students),
    path('show_teachers', views.show_teachers),
    path('show_students', views.show_students),
    path('logout', views.logout,name='logout'),
    path('', views.login, name='login'),
    path('courses', views.courses),
    path('show_courses', views.show_courses),
    path('teacher_data', views.teacher_data,name='teacher_data'),
    path('add', views.add_exam, name='add_exam'),
    path('get1',views.get1),
    path('show_courses1' , views.show_courses1),
    path('get_data',views.get_Data),
    path('ins', views.ins),
    path('getMarks/<str:course_id>/', views.get_marks),
    path('markAttendence/<slug:section_id>/<int:classroom_id>/<int:course_id>',views.markAttendence,name='markAttendence'),
    path('student/<int:course_id>/', views.student, name='student_attendance'),
    path('get_Exam',views.get_Exam),
    path('add/', views.add_exam, name='add_exam'),
    path('download/<int:exam_id>/', views.download_exam, name='download_exam'),
    path('show_Exam',views.show_Exam),
    path('change_password/', change_password, name='change_password'),
    path('password_change_error/', password_change_error, name='password_change_error'),
    path('upload_chalan/',views.upload_chalan, name='upload_chalan'),
    path('addStd/', views.addStudents, name='addStd'),
    path('addTech/', views.addTeachers, name='addTech'),
    path('addCourse/', views.addCourses, name='addCourse'),
    path('updStd/<int:st_id>', views.updateStudent, name='updStd'),
    path('updTech/<int:tec_id>', views.updateTeacher , name='updTech'),
    path('updCrs/<int:cour_id>', views.updateCourse , name ="updCrs"),
    path('remStd/<int:st_id>', views.removeStudent,name="remStd"),
    path('remTech/<int:tec_id>', views.removeTeacher,name="remTech"),
    path('remCrs/<int:crs_id>', views.removeCourse,name="remCrs"),
    path('download_challan/<int:challan_id>/<slug:section_id>/<int:classroom_id>/', views.download_challan, name='download_challan'),
    path('show_challan_form/', show_challan_form , name='show_challan_form'),
    path('diary/<slug:section_id>/<int:classroom_id>/<int:course_id>/', views.add_diary, name='diary'),
    path('announcement/<slug:section_id>/<int:classroom_id>/<int:course_id>/', views.add_announcement, name='addAnnouncement'),
    path('student/announcements/', student_announcements, name='student_announcements'),
    path('student_diary/', student_diary, name='student_diary'),
    path('marks/<slug:section_id>/<int:classroom_id>/<int:course_id>/', views.marks, name='addMarks'),
    path('chatbot/',views.chatbot_model,name="chatbot"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('previous_diaries/', views.previous_diaries, name='previous_diaries'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)