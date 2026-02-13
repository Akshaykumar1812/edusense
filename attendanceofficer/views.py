from django.shortcuts import render,redirect
from edusense import models
from datetime import datetime

def attendanceofficer(request):
    return render(request,'attendanceofficer/attendanceofficer.html')

def change_password_ato(request):
    return render(request,'attendanceofficer/change_password_ato.html')

def attendanceofficer_update_password(request):
    username = request.session['email']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if not new_password:
            return render(request, 'attendanceofficer/change_password_ato.html',{
            'error': 'Please enter new password'})

    if not confirm_password:
            return render(request, 'attendanceofficer/change_password_ato.html',{
            'error': 'Please confirm your password'})

    if new_password==confirm_password:
        log = models.Login.objects.filter(username=username)
        log.update(password=new_password)
        return render(request,'login/login.html')
    else:
        return render(request,'attendanceofficer/change_password_ato.html',{
            'error': 'Passwords do not match'
        })
    
def attendanceofficer_profile(request):
    username = request.session['email']
    user = models.Users.objects.get(email=username)
    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()
    return render(request,'attendanceofficer/attendanceofficer_profile.html',{'user': user,'user_department': user_department,'departments': departments})

def update_attendanceofficer_profile(request):
    username=request.session['email']
    user=models.Users.objects.get(email=username)
    user.full_name = request.POST['full_name']
    user.phone = request.POST['phone']
    user.fk_department_id = request.POST['department']
    user.save()

    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()

    return render(request, 'attendanceofficer/attendanceofficer_profile.html', {'user': user,'user_department': user_department,'departments': departments})
