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

def add_subject(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    
    # Get batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod.fk_department_id)
    
    # Get unique semesters for each batch (by semester number, not by academic year)
    semesters = []
    for batch in batches:
        academic_years = models.AcademicYears.objects.filter(fk_batch_id=batch.batch_id)
        batch_semesters = models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True))
        
        # Get unique semester numbers for this batch
        unique_semesters = {}
        for semester in batch_semesters:
            if semester.semester_number not in unique_semesters:
                unique_semesters[semester.semester_number] = semester
        
        # Add unique semesters to the list
        for semester_number, semester in unique_semesters.items():
            semesters.append({
                'semester': semester,
                'batch_id': batch.batch_id
            })
    
    if request.method == "POST":
        batch_id = request.POST.get('batch')
        semester_id = request.POST.get('semester')
        subjects = request.POST.getlist('subjects[]')
        
        # Filter out empty subject names
        subjects = [subject.strip() for subject in subjects if subject.strip()]
        
        if batch_id and semester_id and subjects:
            for subject_name in subjects:
                # Check if subject already exists for this semester
                if not models.Subjects.objects.filter(
                    subject_name=subject_name, 
                    fk_semester_id=semester_id,
                    fk_batch_id=batch_id
                ).exists():
                    
                    # Create new subject
                    subject = models.Subjects(
                        subject_name=subject_name,
                        fk_batch_id=batch_id,
                        fk_semester_id=semester_id
                    )
                    subject.save()
        
        return redirect('list_subject')
    
    return render(request, 'hod/add_subject.html', {
        'batches': batches,
        'semesters': semesters
    })

def list_subject(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    batches = models.Batches.objects.filter(fk_department_id=hod.fk_department_id)
    
    # Get all semesters for template
    semesters = []
    for batch in batches:
        academic_years = models.AcademicYears.objects.filter(fk_batch_id=batch.batch_id)
        batch_semesters = models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True))
        
        # Get unique semester numbers for this batch
        unique_semesters = {}
        for semester in batch_semesters:
            if semester.semester_number not in unique_semesters:
                unique_semesters[semester.semester_number] = semester
        
        # Add unique semesters to list
        for semester_number, semester in unique_semesters.items():
            semesters.append({
                'semester': semester,
                'batch_id': batch.batch_id
            })
    
    # Handle filtering
    selected_batch = request.POST.get('batch', '')
    selected_semester = request.POST.get('semester', '')
    
    # Get subjects for HOD's department
    subjects = models.Subjects.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    # Filter subjects based on selections
    if selected_batch and selected_semester:
        subjects = subjects.filter(fk_batch_id=selected_batch, fk_semester_id=selected_semester)
    elif selected_batch:
        subjects = subjects.filter(fk_batch_id=selected_batch)
    elif selected_semester:
        subjects = subjects.filter(fk_semester_id=selected_semester)
    
    data = []
    for subject in subjects:
        batch = models.Batches.objects.get(batch_id=subject.fk_batch_id)
        semester = models.Semesters.objects.get(semester_id=subject.fk_semester_id)
        
        data.append({
            'subject': subject,
            'batch': batch,
            'semester': semester
        })
    
    context = {
        'data': data,
        'batches': batches,
        'semesters': semesters,
        'selected_batch': selected_batch,
        'selected_semester': selected_semester
    }
    
    return render(request, 'hod/list_subject.html', context)

def delete_subject(request, subject_id):
    subject = models.Subjects.objects.get(subject_id=subject_id)
    subject.delete()
    return redirect('list_subject')


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

