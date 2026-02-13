from django.urls import path
from . import views

urlpatterns = [
    path('administrator/', views.admin, name="admin"),
    path('change/',views.change_pswd,name="change_pswd"),
    path('update_password/',views.update_password,name="update_password"),
    
    path('logout/', views.logout_view, name='logout'),

    path('department/',views.department,name="department"),
    path('add_department/',views.add_department,name="add_department"),
    path('update/<int:id>/', views.edit_department, name='edit_department'),
    path('delete/<int:id>/', views.delete_department, name='delete_department'),
    path('leave_request/',views.leave_request,name="leave_request"),
    path('delete_leave/<int:leave_id>/', views.delete_leave, name='delete_leave'),
    path('ai_analysis/<int:leave_id>/', views.ai_analysis, name='ai_analysis'),
    path('reason/<int:leave_id>/', views.reason, name="reason"),
    path('semester/',views.semester,name="semester"),
    path('add_semester/',views.add_semester,name="add_semester"),
    path('delete_semester/<int:semester_id>/', views.delete_semester, name='delete_semester'),
    path('edit_semester/<int:semester_id>/',views.edit_semester,name="edit_semester"),

    path('academic_year/',views.academic_year,name="academic_year"),
    path('delete_academic_year/<int:academic_id>/', views.delete_academic_year, name='delete_academic_year'),

    path('show_student_attendance/', views.show_student_attendance, name='show_student_attendance'),


    



    
]