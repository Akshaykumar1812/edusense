from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/',views.login,name="login"),
    path('checklogin/',views.check_login,name="check_login"),
    path('register/',views.register,name="register"),
    path('admin_dashboard/',include('administrator.urls')),
    path('student_dashboard/',include('student.urls')),
    path('hod_dashboard/',include('hod.urls')),
    path('attendanceofficer_dashboard/',include('attendanceofficer.urls')),
    path('faculty_dashboard/',include('faculty.urls')),


]
