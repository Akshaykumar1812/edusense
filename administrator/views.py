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
    batches = models.Batches.objects.all()
    academic_years = None
    selected_batch = None
    
    if request.method == "POST":
        batch_name = request.POST.get('batch')
        academic_id = request.POST.get('department')
        semester_number = request.POST.get('semester')
        
        if batch_name and not academic_id and not semester_number:
            # Batch selected - show academic years for this batch
            selected_batch = batch_name
            academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=models.Batches.objects.filter(batch_name=batch_name).values_list('batch_id', flat=True))
        elif batch_name and academic_id and semester_number:
            # All fields selected - save semester
            sem_info = models.Semesters(
                semester_number=semester_number,
                fk_academic_id=academic_id,
                status='Active'
            )
            sem_info.save()
            return redirect('semester')
        elif academic_id:
            # Academic year selected - preserve batch selection
            selected_batch = batch_name
            academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=models.Batches.objects.filter(batch_name=batch_name).values_list('batch_id', flat=True))
    
    data = []
    for semester in semesters:
        try:
            academic_year = models.AcademicYears.objects.get(academic_id=semester.fk_academic_id)
            batch = models.Batches.objects.get(batch_id=academic_year.fk_batch_id)
            department = models.Departments.objects.get(department_id=batch.fk_department_id)
            data.append({'semester': semester, 'academic': academic_year, 'batch': batch, 'department': department})
        except (models.AcademicYears.DoesNotExist, models.Batches.DoesNotExist, models.Departments.DoesNotExist):
            data.append({'semester': semester, 'academic': None, 'batch': None, 'department': None})
    
    return render(request,'admin/semester.html',{'data': data,'departments': academic_years,'batches': batches, 'selected_batch': selected_batch})

def add_semester(request):
    if request.method == "POST":
        semester_number = request.POST.get('semester')
        academic_id = request.POST.get('department')
        status = "Active"
        
        if semester_number and academic_id:
            sem_info = models.Semesters(
                semester_number=semester_number,
                fk_academic_id=academic_id,
                status=status
            )
            sem_info.save()
            return redirect('semester')
    
def delete_semester(request, semester_id):
    semester =models.Semesters.objects.get(semester_id=semester_id)
    semester.delete()
    return redirect('semester')

def edit_semester(request,semester_id):
    semester = models.Semesters.objects.get(semester_id=semester_id)
    academic_years = models.AcademicYears.objects.all()
    batches = models.Batches.objects.all()
    error_message = None
    
    if request.method == "POST":
        semester_number = request.POST.get('semester')
        academic_id = request.POST.get('department')
        batch_id = request.POST.get('batch')
        
        print(f"POST data: semester={semester_number}, academic_id={academic_id}, batch_id={batch_id}")
        
        if semester_number and academic_id and batch_id:
            # Validate that the selected academic year belongs to the selected batch
            try:
                academic_year = models.AcademicYears.objects.get(academic_id=academic_id)
                print(f"Academic year found: {academic_year.academic_year}, fk_batch_id={academic_year.fk_batch_id}")
                print(f"Selected batch_id: {batch_id}")
                
                if academic_year.fk_batch_id == int(batch_id):
                    print("Validation passed - saving semester")
                    semester.semester_number = semester_number
                    semester.fk_academic_id = academic_id
                    semester.save()
                    return redirect('semester')
                else:
                    print("Validation failed - academic year doesn't belong to batch")
                    error_message = "Selected academic year doesn't belong to the selected batch"
            except models.AcademicYears.DoesNotExist:
                print("Academic year not found")
                error_message = "Academic year not found"
        else:
            print("Missing required fields")
            error_message = "All fields are required"
    
    # Get current academic year and batch for display
    try:
        current_academic = models.AcademicYears.objects.get(academic_id=semester.fk_academic_id)
        current_batch = models.Batches.objects.get(batch_id=current_academic.fk_batch_id)
    except (models.AcademicYears.DoesNotExist, models.Batches.DoesNotExist):
        current_academic = None
        current_batch = None
    
    context = {
        'semester': semester,
        'academic_years': academic_years,
        'batches': batches,
        'current_academic': current_academic,
        'current_batch': current_batch,
        'error_message': error_message
    }
    return render(request, 'admin/edit_semester.html', context)

def academic_year(request):
    batches = models.Batches.objects.all()
    
    if request.method == "POST":
        batch_id = request.POST.get('batch')
        academic_year = request.POST.get('academic_year')
        
        if batch_id and academic_year:
            # Check if this academic year already exists for this batch
            if not models.AcademicYears.objects.filter(
                academic_year=academic_year,
                fk_batch_id=batch_id
            ).exists():
                year_info = models.AcademicYears(
                    academic_year=academic_year,
                    fk_batch_id=batch_id
                )
                year_info.save()
            return redirect('academic_year')
    
    # Get all academic years with their related batch info
    data = []
    for ay in models.AcademicYears.objects.all():
        try:
            batch = models.Batches.objects.get(batch_id=ay.fk_batch_id)
            data.append({
                'academic': ay,
                'batch': batch
            })
        except models.Batches.DoesNotExist:
            # Handle academic years with deleted batches
            data.append({
                'academic': ay,
                'batch': None
            })

    return render(request,'admin/academic_year.html',{'batches': batches, 'data': data})

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
        
        # Get academic years for batches in this department
        academic_years = models.AcademicYears.objects.filter(
            fk_batch_id__in=models.Batches.objects.filter(fk_department_id=department_id).values_list('batch_id', flat=True)
        ).values('academic_year').distinct()
        
        # Get semesters for academic years in this department
        semesters = models.Semesters.objects.filter(
            fk_academic_id__in=models.AcademicYears.objects.filter(
                fk_batch_id__in=models.Batches.objects.filter(fk_department_id=department_id).values_list('batch_id', flat=True)
            ).values_list('academic_id', flat=True)
        )
        
        if academic_year and semester_id:
            # selected semester object for display
            selected_semester_obj = models.Semesters.objects.get(semester_id=semester_id)
            
            # students matching with criteria
            students = models.Users.objects.filter(role='student',fk_department_id=department_id,
                fk_academic_id__in=models.AcademicYears.objects.filter(
                    academic_year=academic_year,
                    fk_batch_id__in=models.Batches.objects.filter(fk_department_id=department_id).values_list('batch_id', flat=True)
                ).values_list('academic_id', flat=True),fk_semester_id=semester_id).order_by('full_name')
            
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

def batch_management(request):
    departments = models.Departments.objects.all()
    
    selected_department = None
    batch_name_value = None
    
    if request.method == "POST":
        batch_name = request.POST.get('batch_name')
        department_id = request.POST.get('department')
        
        if batch_name and department_id:
            # Create new batch
            batch = models.Batches(
                batch_name=batch_name,
                fk_department_id=int(department_id),
                status='Active'
            )
            batch.save()
            return redirect('batch_management')
        elif department_id:
            # Department selected for filtering
            selected_department = int(department_id)
            # Preserve batch name from form
            batch_name_value = batch_name if batch_name else ""
    
    # Get all batches with their related department info
    data = []
    for batch in models.Batches.objects.all():
        try:
            department = models.Departments.objects.get(department_id=batch.fk_department_id)
            data.append({
                'batch': batch,
                'department': department
            })
        except models.Departments.DoesNotExist:
            # Handle orphaned records
            data.append({
                'batch': batch,
                'department': None
            })
    
    context = {
        'departments': departments,
        'selected_department': selected_department,
        'data': data,
        'batch_name_value': batch_name_value
    }
    return render(request, 'admin/batch_management.html', context)

def delete_batch(request, batch_id):
    batch = models.Batches.objects.get(batch_id=batch_id)
    batch.delete()
    return redirect('batch_management')


def edit_batch(request, batch_id):
    batch = models.Batches.objects.get(batch_id=batch_id)
    departments = models.Departments.objects.all()
    
    if request.method == "POST":
        batch_name = request.POST.get('batch_name')
        department_id = request.POST.get('department')
        
        if batch_name and department_id:
            batch.batch_name = batch_name
            batch.fk_department_id = int(department_id)
            batch.save()
            return redirect('batch_management')
    
    # Get current department for display
    try:
        current_department = models.Departments.objects.get(department_id=batch.fk_department_id)
    except models.Departments.DoesNotExist:
        current_department = None
    
    context = {
        'batch': batch,
        'departments': departments,
        'current_department': current_department
    }
    return render(request, 'admin/edit_batch.html', context)