from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student, name="student"),
    path('change_password_std/',views.change_password_std,name="change_password_std"),
    path('stud_update_password/',views.stud_update_password,name="stud_update_password"),
    path('apply_leave/',views.apply_leave,name="apply_leave"),
    path('add_leave/',views.add_leave,name="add_leave"),
    path('leave_status/',views.leave_status,name="leave_status"),
    path('history/',views.history,name="history"),
    path('student_profile/',views.student_profile,name="student_profile"),
    path('student_profile/update/',views.update_student_profile,name='update_student_profile'),
    
]