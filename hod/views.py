from django.shortcuts import render,redirect
from django.contrib.auth import logout
from edusense import models
from datetime import datetime

def hod(request):
    return render(request,'hod/hod.html')

def logout_view_hod(request):
    logout(request)
    return redirect('login')

def change_password_hod(request):
    return render(request,'hod/change_password_hod.html')

def hod_update_password(request):
    username = request.session['email']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if not new_password:
            return render(request, 'hod/change_password_hod.html',{
            'error': 'Please enter new password'})

    if not confirm_password:
            return render(request, 'hod/change_password_hod.html',{
            'error': 'Please confirm your password'})
    
    if new_password==confirm_password:
        log = models.Login.objects.filter(username=username)
        log.update(password=new_password)
        return render(request,'login/login.html')
    else:
        return render(request,'hod/change_password_hod.html',{
            'error': 'Passwords do not match'
        })
    
def hod_profile(request):
    username = request.session['email']
    user = models.Users.objects.get(email=username)
    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()
    return render(request,'hod/hod_profile.html',{'user': user,'user_department': user_department,'departments': departments})

def update_hod_profile(request):
    username=request.session['email']
    user=models.Users.objects.get(email=username)
    user.full_name = request.POST['full_name']
    user.phone = request.POST['phone']
    user.fk_department_id = request.POST['department']
    user.save()

    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()

    return render(request, 'hod/hod_profile.html', {'user': user,'user_department': user_department,'departments': departments})

def hod_list_semester(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    
    # Get all batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod.fk_department_id)
    
    # Get all academic years for HOD's department
    academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    semesters = models.Semesters.objects.all()
    departments = models.Departments.objects.all()
    
    # Handle filtering
    selected_batch = request.POST.get('batch', '')
    selected_year = request.POST.get('academic_year', '')
    
    # Filter semesters based on selections
    if selected_batch and selected_year:
        semesters = semesters.filter(
            fk_academic_id__in=academic_years.filter(
                fk_batch_id=selected_batch,
                academic_year=selected_year
            ).values_list('academic_id', flat=True)
        )
    elif selected_batch:
        semesters = semesters.filter(
            fk_academic_id__in=academic_years.filter(
                fk_batch_id=selected_batch
            ).values_list('academic_id', flat=True)
        )
    elif selected_year:
        semesters = semesters.filter(
            fk_academic_id__in=academic_years.filter(
                academic_year=selected_year
            ).values_list('academic_id', flat=True)
        )
    
    # Order by batch and semester
    semesters = semesters.order_by('fk_academic_id', 'semester_number')
    
    data = []
    for semester in semesters:
        try:
            academic_year = models.AcademicYears.objects.get(academic_id=semester.fk_academic_id)
            batch = models.Batches.objects.get(batch_id=academic_year.fk_batch_id)
            department = models.Departments.objects.get(department_id=batch.fk_department_id)
            data.append({'semester': semester, 'academic': academic_year, 'batch': batch, 'department': department})
        except (models.AcademicYears.DoesNotExist, models.Batches.DoesNotExist, models.Departments.DoesNotExist):
            data.append({'semester': semester, 'academic': None, 'batch': None, 'department': None})
    
    # Sort data by batch name and semester number
    data.sort(key=lambda x: (x['batch'].batch_name if x['batch'] else '', x['semester'].semester_number if x['semester'] else 0))

    context = {
        'data': data, 
        'departments': departments,
        'batches': batches,
        'academic_years': academic_years,
        'selected_batch': selected_batch,
        'selected_year': selected_year
    }
    
    return render(request,'hod/hod_list_semester.html', context)

def list_assign_subject(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)

    subjects = models.Subjects.objects.filter(fk_department_id=hod.fk_department_id)
    
    data = []
    for subject in subjects:
        faculty = models.Users.objects.get(user_id=subject.fk_faculty_id)
        department = models.Departments.objects.get(department_id=subject.fk_department_id)
        semester = models.Semesters.objects.get(semester_id=subject.fk_semester_id)
        batch = models.Batches.objects.get(batch_id=subject.fk_batch_id)

        data.append({'subject': subject,'faculty': faculty,'department': department,'semester': semester, 'batch': batch})

    return render(request,'hod/list_assign_subject.html',{'data': data})


def add_assign_subject(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    
    # Get batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod.fk_department_id)
    faculty = models.Users.objects.filter(role='faculty', fk_department_id=hod.fk_department_id)

    selected_batch = None
    semesters = []

    if request.method == "POST":
        if 'batch' in request.POST and 'semester' not in request.POST:
            selected_batch = int(request.POST['batch'])
            # Get semesters for selected batch
            academic_years = models.AcademicYears.objects.filter(fk_batch_id=selected_batch)
            semesters = models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True))
        elif 'semester' in request.POST and 'assign_faculty' in request.POST and 'subject_name' in request.POST:
            subject_name = request.POST['subject_name']
            batch_id = int(request.POST['batch'])
            semester_id = int(request.POST['semester'])
            assign_faculty_id = int(request.POST['assign_faculty'])

            if not models.Subjects.objects.filter(subject_name=subject_name, fk_semester_id=semester_id, fk_faculty_id=assign_faculty_id).exists():
                sub_info = models.Subjects(
                    subject_name=subject_name,
                    fk_department_id=hod.fk_department_id,
                    fk_batch_id=batch_id,
                    fk_semester_id=semester_id,
                    fk_faculty_id=assign_faculty_id
                )
                sub_info.save()
            return redirect('list_assign_subject')

    return render(request, 'hod/add_assign_subject.html', {
        'batches': batches,
        'faculty': faculty,
        'semesters': semesters,
        'selected_batch': selected_batch
    })


def edit_assign_subject(request,subject_id):
    subject = models.Subjects.objects.get(subject_id=subject_id)
    faculty = models.Users.objects.filter(role='faculty')
    department = models.Departments.objects.all()
    

    if request.method == "POST":
        subject.subject_name = request.POST['subject_name']
        subject.fk_department_id = request.POST['department']
        subject.fk_faculty_id = request.POST['assign_faculty']
        subject.fk_semester_id = request.POST['semester']
        subject.save()

    sub_faculty = models.Users.objects.get(user_id=subject.fk_faculty_id)
    sub_department = models.Departments.objects.get(department_id=subject.fk_department_id)
    sub_semester = models.Semesters.objects.get(semester_id=subject.fk_semester_id)

    semesters = models.Semesters.objects.filter(fk_department_id=sub_department.department_id)

    return render(request,'hod/edit_assign_subject.html',{
        'subject':subject,
        'sub_faculty':sub_faculty,
        'faculty':faculty,
        'sub_department':sub_department,
        'department':department,
        'sub_semester': sub_semester,
        'semesters': semesters})

def delete_assign_subject(request, subject_id):
    subject = models.Subjects.objects.get(subject_id=subject_id)
    subject.delete()
    return redirect('list_assign_subject')


def student_attendance(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    hod_department_id = hod.fk_department_id
    hod_department = models.Departments.objects.get(department_id=hod_department_id)
    
    # Get data for dropdowns
    academic_years = models.AcademicYears.objects.filter(fk_department_id=hod_department_id).values('academic_year').distinct()
    semesters = models.Semesters.objects.filter(fk_department_id=hod_department_id)
    
    attendance_summaries = None
    selected_semester_obj = None
    
    if request.method == "POST":
        academic_year = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        
        # Get selected semester object for display
        if semester_id:
            selected_semester_obj = models.Semesters.objects.get(semester_id=semester_id)
        
        # Get students matching the criteria
        students = models.Users.objects.filter(
            role='student',
            fk_department_id=hod_department_id,
            fk_academic_id__in=models.AcademicYears.objects.filter(
                academic_year=academic_year,
                fk_department_id=hod_department_id
            ).values_list('academic_id', flat=True),
            fk_semester_id=semester_id
        ).order_by('full_name')
        
        # Get attendance summaries for these students
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
        'attendance_summaries': attendance_summaries,
        'academic_years': academic_years,
        'semesters': semesters,
        'hod_department': hod_department,
        'selected_semester_obj': selected_semester_obj
    }
    return render(request, 'hod/student_attendance.html', context)

