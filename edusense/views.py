from datetime import datetime
from email import message
from django.contrib import messages
from django.shortcuts import redirect, render
from edusense import models
import re

from django.contrib.sessions.models import Session

def home(request):
    return render(request,'home/index.html')

def login(request):
    departments = models.Departments.objects.all()
    
    academic_years = models.AcademicYears.objects.values('academic_year', 'fk_department_id').distinct()
    semesters = models.Semesters.objects.all()
    return render(request, 'login/login.html', {
        'department': departments,
        'academic_years': academic_years,
        'semesters': semesters
    })

def check_login(request):
    username = request.POST['username']
    password = request.POST['password']
    info_log = models.Login.objects.filter(username=username,password=password)
    for info in info_log:
        if info.username == username and info.password == password:
            # Get user's full name from Users table
            try:
                user = models.Users.objects.get(email=username)
                full_name = user.full_name
            except models.Users.DoesNotExist:
                full_name = username  # Fallback to username if user not found
            
            if info.usertype =='admin':
                request.session['email']=info.username
                request.session['usertype']=info.usertype
                request.session['full_name']=full_name
                return redirect("../admin_dashboard/administrator")
            elif info.usertype == 'student':
                request.session['email']=info.username
                request.session['usertype']=info.usertype
                request.session['full_name']=full_name
                return redirect("../student_dashboard/student")
            elif info.usertype == 'hod':
                request.session['email']=info.username
                request.session['usertype']=info.usertype
                request.session['full_name']=full_name
                return redirect("../hod_dashboard/hod")
            elif info.usertype == 'attendanceofficer':
                request.session['email']=info.username
                request.session['usertype']=info.usertype
                request.session['full_name']=full_name
                return redirect("../attendanceofficer_dashboard/attendanceofficer")
            elif info.usertype == 'faculty':
                request.session['email']=info.username
                request.session['usertype']=info.usertype
                request.session['full_name']=full_name
                return redirect("../faculty_dashboard/faculty")
        else:
            messages.error(request,"Invalid Data")
    messages.error(request,"Eror Data")
    return redirect('login')
    
def register(request):
    departments = models.Departments.objects.all()
    academic_years = models.AcademicYears.objects.values('academic_year', 'fk_department_id').distinct()
    semesters = models.Semesters.objects.all()
    
    if request.method == "POST":
        fullname = request.POST['fullname']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        role = request.POST['role']
        department_id = request.POST['dept']
        academic_year = request.POST.get('academic_year', '')
        semester_id = request.POST.get('semester', '')
        
        # Set academic and semester IDs (0 for non-students)
        fk_academic_id = 0
        fk_semester_id = 0
        
        if role == 'student' and academic_year:
            academic_obj = models.AcademicYears.objects.filter(
                academic_year=academic_year, 
                fk_department_id=department_id
            ).first()
            fk_academic_id = academic_obj.academic_id if academic_obj else 0
            fk_semester_id = int(semester_id) if semester_id else 0
        
        if models.Login.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists!")
        else:
            try:
                models.Login(username=email, password=password, usertype=role, status="Active").save()
                models.Users(full_name=fullname, email=email, phone=phone, role=role,
                    fk_department_id=department_id, status="Active", 
                    created_at=datetime.now().date(),
                    fk_academic_id=fk_academic_id, fk_semester_id=fk_semester_id
                ).save()
                messages.success(request, "Registration successful!")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'login/login.html', {
        'department': departments,
        'academic_years': academic_years,
        'semesters': semesters
    })






