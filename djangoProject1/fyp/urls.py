from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('',views.index),
    # path('get',views.get_All),
    # path('get_data',views.get_Data,name="hi"),
    # path('about', views.aboutus),
    # path('course/<str:id>', views.courses),
    # path('home', views.home),
    # path('form', views.userform),
    # path('submit', views.submitform,name="submit"),
    path('teacher/<str:teacher_id>/', views.teacher_data, name="teacher_data"),

]