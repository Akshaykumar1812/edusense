from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import render,redirect
from edusense import models

def admin(request):
    return render(request,'admin/admin.html')

def change_pswd(request):
    return render(request,'admin/change_pswd.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def update_password(request):
    username = request.session['email']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if not new_password:
            return render(request, 'admin/change_pswd.html',{'error': 'Please enter new password'})

    if not confirm_password:
            return render(request, 'admin/change_pswd.html',{'error': 'Please confirm your password'})

    if new_password==confirm_password:
        log = models.Login.objects.filter(username=username)
        log.update(password=new_password)
        return render(request,'login/login.html')
    else:
        return render(request,'admin/change_pswd.html',{'error': 'Passwords do not match'})

def department(request):
    departments = models.Departments.objects.all()
    return render(request,'admin/department.html',{'departments': departments})


def add_department(request):
    dept_name = request.POST['dept_name']
    dept_info = models.Departments(department_name=dept_name)
    dept_info.save()
    return redirect('department')

def edit_department(request, id):
    department = models.Departments.objects.get(department_id=id)
    if request.method == "POST":
        department.department_name = request.POST['dept_name']
        department.save()
        return redirect('department')

    return render(request, 'admin/edit_department.html', {'department': department})

def delete_department(request, id):
    department =models.Departments.objects.get(department_id=id)
    department.delete()
    return redirect('department')

def leave_request(request):
    leaves = models.LeaveRequests.objects.all()

    data = []
    for leave in leaves:
        try:
            user = models.Users.objects.get(user_id=leave.fk_user_id)
            department = models.Departments.objects.get(department_id=user.fk_department_id)
            data.append({'leave': leave,'user': user,'department': department})
        except models.Users.DoesNotExist:
            # Skip leave requests for deleted users
            continue
        except models.Departments.DoesNotExist:
            # Handle case where department doesn't exist
            data.append({'leave': leave,'user': None,'department': None})
    return render(request, 'admin/leave_request.html', {'data': data})

def delete_leave(request, leave_id):
    leave = models.LeaveRequests.objects.get(leave_id=leave_id)
    leave.delete()
    return redirect('leave_request')

def ai_analysis(request,leave_id):
    leave = models.LeaveRequests.objects.get(leave_id=leave_id)
    try:
        user = models.Users.objects.get(user_id=leave.fk_user_id)
        return render(request,'admin/ai_analysis.html',{'leave':leave,'user':user})
    except models.Users.DoesNotExist:
        # Handle case where user doesn't exist
        return render(request,'admin/ai_analysis.html',{'leave':leave,'user':None})

def reason(request, leave_id):
    leave = models.LeaveRequests.objects.get(leave_id=leave_id)
    if request.method == "POST":
        decision = request.POST['decision']
        reason = request.POST['reason']
        decision_time = datetime.now().date()

        log_entry = models.LeaveDecisionLogs(fk_leave_id=leave.leave_id,reason=reason,decision=decision,decision_time=decision_time)
        log_entry.save()

        leave.status = decision  # Approve/Reject
        leave.save()
        return redirect('leave_request')
    return render(request,'admin/reason.html',{'leave': leave})


def semester(request):
    semesters = models.Semesters.objects.all()
    departments = models.Departments.objects.all()
    data = []
    for semester in semesters:
        department = models.Departments.objects.get(department_id=semester.fk_department_id)
        data.append({'semester': semester,'department': department})

    return render(request,'admin/semester.html',{'data': data,'departments': departments})

def add_semester(request):
    if request.method == "POST":
        semester = request.POST['semester']
        department_id = request.POST['department']
        status = "Active"
        sem_info = models.Semesters(semester_number=semester,fk_department_id=department_id,status=status)
        sem_info.save()
        return redirect('semester')
    
def delete_semester(request, semester_id):
    semester =models.Semesters.objects.get(semester_id=semester_id)
    semester.delete()
    return redirect('semester')

def edit_semester(request,semester_id):
    semester = models.Semesters.objects.get(semester_id=semester_id)
    department = models.Departments.objects.all()
    if request.method == "POST":
        semester.semester_number = request.POST['semester']
        semester.fk_department_id = request.POST['department']
        semester.save()
        
    sem_department = models.Departments.objects.get(department_id=semester.fk_department_id)
    
    return render(request, 'admin/edit_semester.html', {'semester': semester,'sem_department': sem_department,'department': department})



def academic_year(request):
    departments = models.Departments.objects.all()

    selected_department = None
    semesters = []

    if request.method == "POST":
        if 'department' in request.POST and 'semester' not in request.POST:
            selected_department = int(request.POST['department'])
            semesters = models.Semesters.objects.filter(fk_department_id=selected_department)
        elif 'department' in request.POST and 'semester' in request.POST and 'academic_year' in request.POST:
            academic_year = request.POST['academic_year']
            department_id = int(request.POST['department'])
            semester_id = int(request.POST['semester'])

            if academic_year:
                if not models.AcademicYears.objects.filter(academic_year=academic_year,fk_department_id=department_id,fk_semester_id=semester_id).exists():

                    year_info = models.AcademicYears(
                        academic_year=academic_year,
                        fk_department_id=department_id,
                        fk_semester_id=semester_id,
                
                    )
                    year_info.save()
                return redirect('academic_year')
        
    data = []
    for ay in models.AcademicYears.objects.all():
        department = models.Departments.objects.get(department_id=ay.fk_department_id)
        semester = models.Semesters.objects.get(semester_id=ay.fk_semester_id)
        data.append({
            'academic': ay,
            'department': department,
            'semester': semester
        })


    return render(request,'admin/academic_year.html',{'department': departments,'semesters': semesters,'selected_department': selected_department,'data': data})

def delete_academic_year(request, academic_id):
    ay = models.AcademicYears.objects.get(academic_id=academic_id)
    ay.delete()
    return redirect('academic_year')

def show_student_attendance(request):
    departments = models.Departments.objects.all()
    
    academic_years = None
    semesters = None
    attendance_summaries = None
    selected_department = None
    selected_semester_obj = None
    hod_name = None
    
    if request.method == "POST":
        department_id = request.POST.get('department')
        academic_year = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        
        # selected dept
        selected_department = models.Departments.objects.get(department_id=department_id)
        
        #  HOD under selected department
        hod = models.Users.objects.filter(role='hod',fk_department_id=department_id).first()
        hod_name = hod.full_name if hod else "No HOD Assigned"
        
        academic_years = models.AcademicYears.objects.filter(fk_department_id=department_id).values('academic_year').distinct()
        semesters = models.Semesters.objects.filter(fk_department_id=department_id)
        
        if academic_year and semester_id:
            # selected semester object for display
            selected_semester_obj = models.Semesters.objects.get(semester_id=semester_id)
            
            # students matching with criteria
            students = models.Users.objects.filter(role='student',fk_department_id=department_id,
                fk_academic_id__in=models.AcademicYears.objects.filter(
                    academic_year=academic_year,
                    fk_department_id=department_id).values_list('academic_id', flat=True),fk_semester_id=semester_id).order_by('full_name')
            
            #attendance summaries
            attendance_summaries = []
            for student in students:
                summary = models.AttendanceSummary.objects.filter(fk_student_id=student.user_id).first()
                
                attendance_summaries.append({
                    'student': student,
                    'total_classes': summary.total_classes if summary else 0,
                    'attended_classes': summary.attended_classes if summary else 0,
                    'percentage': summary.total_percentage if summary else 0.0
                })
    
    context = {
        'departments': departments,
        'academic_years': academic_years,
        'semesters': semesters,
        'attendance_summaries': attendance_summaries,
        'selected_department': selected_department,
        'selected_semester_obj': selected_semester_obj,
        'hod_name': hod_name
    }
    return render(request, 'admin/show_student_attendance.html', context)