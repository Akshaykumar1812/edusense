from django.shortcuts import render,redirect
from django.contrib.auth import logout
from edusense import models
from datetime import datetime

def student(request):
    return render(request,'student/student.html')

def logout_view_student(request):
    logout(request)
    return redirect('login')

def change_password_std(request):
    return render(request,'student/change_password_std.html')

def stud_update_password(request):
    username = request.session['email']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']
    if new_password==confirm_password:
        log = models.Login.objects.filter(username=username)
        log.update(password=new_password)
        return render(request,'login/login.html')
    else:
        return render(request,'student/change_password_std.html')
    
def apply_leave(request):
    return render(request,'student/apply_leave.html')

# def add_leave(request):
#     user_id = models.Users.objects.get('user_id')
#     if request.method == "POST":
#         leave_type = request.POST['leave_type']
#         start_date = request.POST['start_date']
#         end_date = request.POST['end_date']
#         reason = request.POST['reason']
#         status = "Active"
#         applied_on = datetime.now().date()

        
#         leave_info = models.LeaveRequests(fk_user_id=user_id,leave_type=leave_type,start_date=start_date,end_date=end_date,reason=reason,status=status,applied_on=applied_on)
#         leave_info.save()
#     return redirect('apply_leave')

def add_leave(request):
    username=request.session['email']
    user=models.Users.objects.get(email=username)

    leave_type = request.POST['leave_type']
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    reason = request.POST['reason']
    status = "Pending" 
    applied_on = datetime.now().date()

    leave = models.LeaveRequests(fk_user_id=user.user_id,leave_type=leave_type,start_date=start_date,end_date=end_date,reason=reason,status=status,applied_on=applied_on)
    leave.save()
    return redirect('leave_status')

def leave_status(request):
    return render(request,'student/leave_status.html')

def history(request):
    return render(request,'student/history.html')

def student_profile(request):
    username = request.session['email']
    user = models.Users.objects.get(email=username)
    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()
    
    # Get batch and semester information
    user_batch = None
    user_semester = None
    batches = models.Batches.objects.filter(fk_department_id=user.fk_department_id)
    
    try:
        user_batch = models.Batches.objects.get(batch_id=user.fk_batch_id)
        # Get semesters for the user's batch
        academic_years = models.AcademicYears.objects.filter(fk_batch_id=user.fk_batch_id)
        semesters = []
        for semester in models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True)):
            try:
                academic_year = models.AcademicYears.objects.get(academic_id=semester.fk_academic_id)
                semesters.append({
                    'semester': semester,
                    'batch_id': academic_year.fk_batch_id
                })
            except models.AcademicYears.DoesNotExist:
                continue
        user_semester = models.Semesters.objects.get(semester_id=user.fk_semester_id)
    except (models.Batches.DoesNotExist, models.AcademicYears.DoesNotExist, models.Semesters.DoesNotExist):
        semesters = []
    
    return render(request,'student/student_profile.html',{
        'user': user,
        'user_department': user_department, 
        'departments': departments,
        'user_batch': user_batch,
        'user_semester': user_semester,
        'batches': batches,
        'semesters': semesters
    })

def update_student_profile(request):
    username=request.session['email']
    user=models.Users.objects.get(email=username)
    user.full_name = request.POST['full_name']
    user.phone = request.POST['phone']
    
    # Handle department update (may not be present if disabled)
    if 'department' in request.POST and request.POST['department']:
        user.fk_department_id = request.POST['department']
    
    # Update batch and semester if provided
    if 'batch' in request.POST and request.POST['batch']:
        user.fk_batch_id = request.POST['batch']
    if 'semester' in request.POST and request.POST['semester']:
        user.fk_semester_id = request.POST['semester']
    
    user.save()

    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()
    
    # Get updated batch and semester information
    user_batch = None
    user_semester = None
    batches = models.Batches.objects.filter(fk_department_id=user.fk_department_id)
    
    try:
        user_batch = models.Batches.objects.get(batch_id=user.fk_batch_id)
        # Get semesters for the user's batch
        academic_years = models.AcademicYears.objects.filter(fk_batch_id=user.fk_batch_id)
        semesters = []
        for semester in models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True)):
            try:
                academic_year = models.AcademicYears.objects.get(academic_id=semester.fk_academic_id)
                semesters.append({
                    'semester': semester,
                    'batch_id': academic_year.fk_batch_id
                })
            except models.AcademicYears.DoesNotExist:
                continue
        user_semester = models.Semesters.objects.get(semester_id=user.fk_semester_id)
    except (models.Batches.DoesNotExist, models.AcademicYears.DoesNotExist, models.Semesters.DoesNotExist):
        semesters = []

    return render(request, 'student/student_profile.html', {
        'user': user,
        'user_department': user_department, 
        'departments': departments,
        'user_batch': user_batch,
        'user_semester': user_semester,
        'batches': batches,
        'semesters': semesters
    })

def leave_status(request):
    username=request.session['email']
    user=models.Users.objects.get(email=username)

    leaves = models.LeaveRequests.objects.filter(fk_user_id=user.user_id)
    return render(request, 'student/leave_status.html', {'leaves': leaves})





