from django.urls import path
from . import views

urlpatterns = [
    path('attendanceofficer/', views.attendanceofficer, name="attendanceofficer"),
    path('logout/', views.logout_view_attendanceofficer, name="logout_view_attendanceofficer"),
    path('change_password_ato/',views.change_password_ato,name="change_password_ato"),
    path('attendanceofficer_update_password/',views.attendanceofficer_update_password,name="attendanceofficer_update_password"),
     path('attendanceofficer_profile/',views.attendanceofficer_profile,name="attendanceofficer_profile"),
     path('attendanceofficer_profile/update/',views.update_attendanceofficer_profile,name='update_attendanceofficer_profile'),
    
    
    
]