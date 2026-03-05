from django.urls import path
from . import views

urlpatterns = [
    path('hod/', views.hod, name="hod"),
    path('logout/', views.logout_view_hod, name="logout_view_hod"),
    path('change_password_hod/',views.change_password_hod,name="change_password_hod"),
    path('hod_update_password/',views.hod_update_password,name="hod_update_password"),

    path('hod_profile/',views.hod_profile,name="hod_profile"),
    path('hod_profile/update/',views.update_hod_profile,name='update_hod_profile'),

    path('hod_list_semester/',views.hod_list_semester,name="hod_list_semester"),
    
    path('add_subject/',views.add_subject,name="add_subject"),
    path('list_subject/',views.list_subject,name="list_subject"),
    path('delete_subject/<int:subject_id>/',views.delete_subject,name="delete_subject"),

    path('student_attendance/',views.student_attendance,name="student_attendance"),

    path('add_timetable/',views.add_timetable,name="add_timetable"),
    path('list_timetable/',views.list_timetable,name="list_timetable"),

    path('faculty_students/',views.faculty_students,name="faculty_students"),
    path('delete_faculty/<int:user_id>/',views.delete_faculty,name="delete_faculty"),
    path('delete_student/<int:user_id>/',views.delete_student,name="delete_student"),

    path('update_semester/',views.update_semester,name="update_semester"),
]