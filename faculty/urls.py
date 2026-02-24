from django.urls import path
from . import views

urlpatterns = [
    path('faculty/', views.faculty, name="faculty"),
    path('logout/', views.logout_view_faculty, name="logout_view_faculty"),
    path('change_pass/',views.change_password,name="change_password"),
    path('faculty_update_password/',views.faculty_update_password,name="faculty_update_password"),
    path('faculty_profile/',views.faculty_profile,name="faculty_profile"),
    path('faculty_profile/update/',views.update_faculty_profile,name='update_faculty_profile'),
    path('faculty_list_semester/',views.faculty_list_semester,name="faculty_list_semester"),
    path('list_sub_sem/',views.list_sub_sem,name="list_sub_sem"),
    path('mark_attendance/',views.mark_attendance,name="mark_attendance"),
    path('show_attendance/',views.show_attendance,name="show_attendance"),
    path('edit_attendance/<int:attendance_id>/',views.edit_attendance,name="edit_attendance"),
]