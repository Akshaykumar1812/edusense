from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib import messages
from edusense import models
from datetime import datetime

def faculty(request):
    return render(request,'faculty/faculty.html')

def logout_view_faculty(request):
    logout(request)
    return redirect('login')

def change_password(request):
    return render(request,'faculty/change_password.html')

def faculty_update_password(request):
    username = request.session['email']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if not new_password:
            return render(request, 'faculty/change_password.html',{
            'error': 'Please enter new password'})

    if not confirm_password:
            return render(request, 'faculty/change_password.html',{
            'error': 'Please confirm your password'})
    
    if new_password==confirm_password:
        log = models.Login.objects.filter(username=username)
        log.update(password=new_password)
        return render(request,'login/login.html')
    else:
        return render(request,'faculty/change_password.html',{
            'error': 'Passwords do not match'
        })
    
def faculty_profile(request):
    username = request.session['email']
    user = models.Users.objects.get(email=username)
    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()
    return render(request,'faculty/faculty_profile.html',{'user': user,'user_department': user_department,'departments': departments})

def update_faculty_profile(request):
    username=request.session['email']
    user=models.Users.objects.get(email=username)
    user.full_name = request.POST['full_name']
    user.phone = request.POST['phone']
    user.fk_department_id = request.POST['department']
    user.save()

    user_department = models.Departments.objects.get(department_id=user.fk_department_id)
    departments = models.Departments.objects.all()

    return render(request, 'faculty/faculty_profile.html', {'user': user,'user_department': user_department,'departments': departments})

def faculty_list_semester(request):
    semesters = models.Semesters.objects.all()
    departments = models.Departments.objects.all()
    data = []
    for semester in semesters:
        department = models.Departments.objects.get(department_id=semester.fk_department_id)
        data.append({'semester': semester,'department': department})

    return render(request,'faculty/faculty_list_semester.html',{'data': data,'departments': departments})

def list_sub_sem(request):
    departments = models.Departments.objects.all()
    semesters = []
    subjects = []

    selected_department = None
    selected_semester = None
    show_table = False
    

    if request.method == "POST":
        if 'department' in request.POST and 'semester' not in request.POST:
            selected_department = int(request.POST['department'])
            semesters = models.Semesters.objects.filter(fk_department_id=selected_department)
        elif 'department' in request.POST and 'semester' in request.POST:
            selected_department = int(request.POST['department'])
            selected_semester = int(request.POST['semester'])

            semesters = models.Semesters.objects.filter(fk_department_id=selected_department)
            subjects = models.Subjects.objects.filter(fk_department_id=selected_department,fk_semester_id=selected_semester)

            show_table = True 

    context = {
        'department': departments,
        'semesters': semesters,
        'subjects': subjects,
        'selected_department': selected_department,
        'selected_semester': selected_semester,
        'show_table': show_table
    }

    return render(request, 'faculty/list_sub_sem.html', context)


def mark_attendance(request):
    username = request.session['email']
    faculty = models.Users.objects.get(email=username)
    faculty_department_id = faculty.fk_department_id
    faculty_department = models.Departments.objects.get(department_id=faculty_department_id)
    
    # Get data for dropdowns
    academic_years = models.AcademicYears.objects.filter(fk_department_id=faculty_department_id).values('academic_year').distinct()
    semesters = models.Semesters.objects.filter(fk_department_id=faculty_department_id)
    
    students = None
    selected_date = None
    selected_semester_obj = None
    
    if request.method == "POST":
        academic_year = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        
        # Get selected semester object for display
        if semester_id:
            selected_semester_obj = models.Semesters.objects.get(semester_id=semester_id)
        
        # Filter students by department, academic year, and semester (sorted alphabetically)
        students = models.Users.objects.filter(
            role='student',
            fk_department_id=faculty_department_id,
            fk_academic_id__in=models.AcademicYears.objects.filter(
                academic_year=academic_year,
                fk_department_id=faculty_department_id
            ).values_list('academic_id', flat=True),
            fk_semester_id=semester_id
        ).order_by('full_name')
        
        # Handle attendance submission
        if 'submit_attendance' in request.POST:
            selected_date = request.POST.get('attendance_date')
            duplicate_count = 0
            
            for student in students:
                # Check if attendance already exists for this student on this date
                existing_attendance = models.AttendanceRecords.objects.filter(
                    fk_user_id=student.user_id,
                    decision_date=selected_date
                ).first()
                
                if existing_attendance:
                    duplicate_count += 1
                else:
                    attendance_status = request.POST.get(f'attendance_{student.user_id}')
                    remarks = request.POST.get(f'remarks_{student.user_id}', '')
                    
                    # Create attendance record
                    models.AttendanceRecords.objects.create(
                        fk_user_id=student.user_id,
                        fk_leave_id=0,  # 0 for daily attendance (not leave)
                        decision=attendance_status,
                        decision_date=selected_date,
                        remarks=remarks
                    )
                    
                    # Update attendance summary for this student
                    update_attendance_summary(student.user_id, semester_id)
            
            if duplicate_count > 0:
                messages.warning(request, f'Attendance already exists for {duplicate_count} student(s) on {selected_date}. Only new records were saved.')
            else:
                messages.success(request, 'Attendance marked successfully!')
            return redirect('mark_attendance')
    
    context = {
        'students': students,
        'academic_years': academic_years,
        'semesters': semesters,
        'selected_date': selected_date,
        'faculty_department_id': faculty_department_id,
        'faculty_department': faculty_department,
        'selected_semester_obj': selected_semester_obj
    }
    return render(request, 'faculty/mark_attendance.html', context)

def show_attendance(request):
    username = request.session['email']
    faculty = models.Users.objects.get(email=username)
    faculty_department_id = faculty.fk_department_id
    faculty_department = models.Departments.objects.get(department_id=faculty_department_id)
    
    # Get data for dropdowns
    academic_years = models.AcademicYears.objects.filter(fk_department_id=faculty_department_id).values('academic_year').distinct()
    semesters = models.Semesters.objects.filter(fk_department_id=faculty_department_id)
    
    attendance_records = None
    selected_date = None
    selected_semester_obj = None
    
    if request.method == "POST":
        academic_year = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        selected_date = request.POST.get('attendance_date')
        
        # Get selected semester object for display
        if semester_id:
            selected_semester_obj = models.Semesters.objects.get(semester_id=semester_id)
        
        # Get students matching the criteria
        students = models.Users.objects.filter(
            role='student',
            fk_department_id=faculty_department_id,
            fk_academic_id__in=models.AcademicYears.objects.filter(
                academic_year=academic_year,
                fk_department_id=faculty_department_id
            ).values_list('academic_id', flat=True),
            fk_semester_id=semester_id
        ).order_by('full_name')
        
        # Get attendance records for these students on the selected date
        attendance_records = []
        for student in students:
            attendance = models.AttendanceRecords.objects.filter(
                fk_user_id=student.user_id,
                decision_date=selected_date
            ).first()
            
            attendance_records.append({
                'student': student,
                'attendance': attendance,
                'attendance_id': attendance.attendance_id if attendance else None
            })
    
    context = {
        'attendance_records': attendance_records,
        'academic_years': academic_years,
        'semesters': semesters,
        'selected_date': selected_date,
        'faculty_department': faculty_department,
        'selected_semester_obj': selected_semester_obj
    }
    return render(request, 'faculty/show_attendance.html', context)

def edit_attendance(request, attendance_id):
    attendance = models.AttendanceRecords.objects.get(attendance_id=attendance_id)
    student = models.Users.objects.get(user_id=attendance.fk_user_id)
    
    if request.method == "POST":
        attendance.decision = request.POST.get('attendance')
        attendance.remarks = request.POST.get('remarks', '')
        attendance.save()
        
        messages.success(request, 'Attendance updated successfully!')
        return redirect('edit_attendance', attendance_id=attendance_id)
    
    context = {'attendance': attendance,'student': student}
    return render(request, 'faculty/edit_attendance.html', context)


def update_attendance_summary(student_id, semester_id):
    attendance_records = models.AttendanceRecords.objects.filter(fk_user_id=student_id,fk_leave_id=0)
    
    student = models.Users.objects.get(user_id=student_id)
    semester = models.Semesters.objects.get(semester_id=semester_id)
    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(decision='Present').count()
    
    if total_classes > 0:
        percentage = (attended_classes / total_classes) * 100
    else:
        percentage = 0.0
    
    summary = models.AttendanceSummary.objects.filter(fk_student_id=student_id).first()
    if summary:
        # Update existing record
        summary.total_classes = total_classes
        summary.attended_classes = attended_classes
        summary.total_percentage = percentage
        summary.save()
    else:
        # Create new record
        summary = models.AttendanceSummary(
            fk_student_id=student_id,
            total_classes=total_classes,
            attended_classes=attended_classes,
            total_percentage=percentage
        )
        summary.save()