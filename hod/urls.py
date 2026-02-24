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
    
    path('list_assign_subject/',views.list_assign_subject,name="list_assign_subject"),
    path('add_assign_subject/',views.add_assign_subject,name="add_assign_subject"),
    path('edit_assign_subject/<int:subject_id>/',views.edit_assign_subject,name="edit_assign_subject"),
    path('delete_assign_subject/<int:subject_id>/',views.delete_assign_subject,name="delete_assign_subject"),

    path('student_attendance/',views.student_attendance,name="student_attendance"),

]