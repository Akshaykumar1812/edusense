from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
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
    
    # Get all batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
    
    # Get all academic years for HOD's department
    academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    # Get all semesters for HOD's department
    semesters = models.Semesters.objects.all()
    
    # Handle filtering
    selected_batch = request.POST.get('batch', '')
    selected_academic = request.POST.get('academic_year', '')
    
    # Filter semesters based on selections
    if selected_batch and selected_academic:
        semesters = semesters.filter(
            fk_academic_id__in=academic_years.filter(
                fk_batch_id=selected_batch,
                academic_year=selected_academic
            ).values_list('academic_id', flat=True)
        )
    elif selected_batch:
        semesters = semesters.filter(
            fk_academic_id__in=academic_years.filter(
                fk_batch_id=selected_batch
            ).values_list('academic_id', flat=True)
        )
    elif selected_academic:
        semesters = semesters.filter(
            fk_academic_id__in=academic_years.filter(
                academic_year=selected_academic
            ).values_list('academic_id', flat=True)
        )
    
    # Order by academic year and semester
    semesters = semesters.order_by('fk_academic_id', 'semester_number')
    
    attendance_summaries = None
    selected_semester_obj = None
    selected_batch_obj = None
    
    if request.method == "POST":
        batch_id = request.POST.get('batch')
        academic_year = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        
        # Get selected batch object for display
        selected_batch_obj = None
        if batch_id:
            try:
                selected_batch_obj = models.Batches.objects.get(batch_id=batch_id)
            except models.Batches.DoesNotExist:
                selected_batch_obj = None
        
        # Get selected semester object for display
        if semester_id:
            selected_semester_obj = models.Semesters.objects.get(semester_id=semester_id)
        
        # Get students matching criteria
        students = models.Users.objects.filter(
            role='student',
            fk_department_id=hod_department_id,
            fk_batch_id=batch_id,
            fk_academic_id__in=models.AcademicYears.objects.filter(
                academic_year=academic_year,
                fk_batch_id=batch_id
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
        'batches': batches,
        'hod_department': hod_department,
        'selected_semester_obj': selected_semester_obj,
        'selected_batch_obj': selected_batch_obj
    }
    return render(request, 'hod/student_attendance.html', context)

def add_timetable(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    hod_department_id = hod.fk_department_id
    
    if request.method == 'POST':
        try:
            # Get form data
            batch_id = request.POST.get('batch')
            academic_id = request.POST.get('academic_year')
            semester_id = request.POST.get('semester')
            
            # Get dynamic form arrays
            days_of_week = request.POST.getlist('day_of_week[]')
            hours = request.POST.getlist('hour[]')
            subjects = request.POST.getlist('subject[]')
            faculties = request.POST.getlist('faculty[]')
            
            # Validate required fields
            if not all([batch_id, academic_id, semester_id]):
                messages.error(request, 'Please select batch, academic year, and semester')
                return redirect('add_timetable')
            
            # Save each timetable entry with proper day-hour mapping
            timetable_entries = []
            
            # The form structure: each day block has multiple hours
            # We need to map hours to their corresponding day blocks
            # Since all form data comes as flat arrays, we need to reconstruct the grouping
            
            if len(days_of_week) > 0 and len(hours) > 0:
                # Calculate how many hours each day should have
                total_hours = len(hours)
                total_days = len(days_of_week)
                
                # Distribute hours as evenly as possible across days
                # First day gets first set of hours, second day gets next set, etc.
                hours_per_day = total_hours // total_days
                remaining_hours = total_hours % total_days
                
                hour_index = 0
                for day_idx, current_day in enumerate(days_of_week):
                    # Calculate how many hours this day should get
                    hours_for_this_day = hours_per_day
                    if day_idx < remaining_hours:
                        hours_for_this_day += 1
                    
                    # Assign the appropriate number of hours to this day
                    for h in range(hours_for_this_day):
                        if hour_index < len(hours) and hour_index < len(subjects) and hour_index < len(faculties):
                            if hours[hour_index] and subjects[hour_index] and faculties[hour_index]:
                                timetable_entry = models.Timetable(
                                    fk_department_id=hod_department_id,
                                    fk_batch_id=batch_id,
                                    fk_academic_id=academic_id,
                                    fk_semester_id=semester_id,
                                    fk_subject_id=subjects[hour_index],
                                    fk_faculty_id=faculties[hour_index],
                                    day_of_week=current_day,
                                    hours=hours[hour_index],
                                    created_at=timezone.now()
                                )
                                timetable_entries.append(timetable_entry)
                            hour_index += 1
            
            # Bulk create timetable entries
            if timetable_entries:
                models.Timetable.objects.bulk_create(timetable_entries)
                messages.success(request, f'Successfully saved {len(timetable_entries)} timetable entries')
                return redirect('list_timetable')
            else:
                messages.error(request, 'No valid timetable entries to save')
                return redirect('add_timetable')
                
        except Exception as e:
            messages.error(request, f'Error saving timetable: {str(e)}')
            return redirect('add_timetable')
    
    # GET request - display form
    # Get batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
    
    # Get academic years for HOD's department
    academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    # Get all semesters for HOD's department
    semesters = models.Semesters.objects.filter(
        fk_academic_id__in=academic_years.values_list('academic_id', flat=True)
    ).order_by('fk_academic_id', 'semester_number')
    
    # Get subjects for HOD's department
    subjects = models.Subjects.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    # Get faculty for HOD's department
    faculty_list = models.Users.objects.filter(fk_department_id=hod_department_id, role='faculty')
    
    context = {
        'batches': batches,
        'semesters': semesters,
        'academic_years': academic_years,
        'subjects': subjects,
        'faculty_list': faculty_list
    }
    return render(request,'hod/add_timetable.html', context)


def list_timetable(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    hod_department_id = hod.fk_department_id
    
    # Handle filtering
    selected_batch = request.POST.get('batch', '')
    selected_academic = request.POST.get('academic_year', '')
    selected_semester = request.POST.get('semester', '')
    
    # Get batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
    
    # Get academic years - filtered by selected batch if available, otherwise all for department
    if selected_batch:
        academic_years = models.AcademicYears.objects.filter(fk_batch_id=selected_batch)
    else:
        academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    # Get all semesters for template with batch and academic year mapping
    semesters = []
    for batch in batches:
        batch_academic_years = models.AcademicYears.objects.filter(fk_batch_id=batch.batch_id)
        batch_semesters = models.Semesters.objects.filter(fk_academic_id__in=batch_academic_years.values_list('academic_id', flat=True))
        
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
    
    # Only process timetable data if filters are applied
    timetable_flat = []
    has_data = False
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = range(1, 8)  # Default hours
    
    if selected_batch and selected_academic and selected_semester:
        # Filter timetable entries
        timetable_entries = models.Timetable.objects.filter(fk_department_id=hod_department_id)
        
        if selected_batch:
            timetable_entries = timetable_entries.filter(fk_batch_id=selected_batch)
        if selected_academic:
            timetable_entries = timetable_entries.filter(fk_academic_id=selected_academic)
        if selected_semester:
            timetable_entries = timetable_entries.filter(fk_semester_id=selected_semester)
        
        # Get unique days and hours that have timetable entries
        days_with_data = set()
        hours_with_data = set()
        for entry in timetable_entries:
            if entry.day_of_week:
                days_with_data.add(entry.day_of_week)
            if entry.hours:
                hours_with_data.add(entry.hours)
        
        # Sort days in proper order (Monday to Sunday)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days_of_week = [day for day in day_order if day in days_with_data]
        
        # Sort hours in numerical order (1st to 8th)
        hours = sorted(hours_with_data)
        
        # If no days or hours have data, show all as fallback
        if not days_of_week:
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if not hours:
            hours = range(1, 8)  # 1st to 7th hour
        
        # Initialize empty grid
        timetable_grid = {}
        for day in days_of_week:
            timetable_grid[day] = {}
            for hour in hours:
                timetable_grid[day][hour] = None
        
        # Fill grid with timetable data
        for entry in timetable_entries:
            try:
                subject = models.Subjects.objects.get(subject_id=entry.fk_subject_id)
                faculty = models.Users.objects.get(user_id=entry.fk_faculty_id)
                
                if entry.day_of_week in timetable_grid and entry.hours in timetable_grid[entry.day_of_week]:
                    timetable_grid[entry.day_of_week][entry.hours] = {
                        'subject': subject,
                        'faculty': faculty,
                        'entry': entry
                    }
            except (models.Subjects.DoesNotExist, models.Users.DoesNotExist):
                continue
        
        # Create a flat list for easier template access
        for day in days_of_week:
            row_data = {'day': day, 'hours': []}
            for hour in hours:
                cell_data = timetable_grid[day][hour]
                if cell_data:
                    row_data['hours'].append({
                        'hour': hour,
                        'subject': cell_data['subject'].subject_name,
                        'faculty': cell_data['faculty'].full_name
                    })
                else:
                    row_data['hours'].append({
                        'hour': hour,
                        'subject': None,
                        'faculty': None
                    })
            timetable_flat.append(row_data)
        
        has_data = timetable_entries.exists()
    
    context = {
        'timetable_flat': timetable_flat,
        'days_of_week': days_of_week,
        'hours': hours,
        'batches': batches,
        'academic_years': academic_years,
        'semesters': semesters,
        'selected_batch': selected_batch,
        'selected_academic': selected_academic,
        'selected_semester': selected_semester,
        'has_data': has_data,
        'filters_applied': bool(selected_batch and selected_academic and selected_semester)
    }
    
    return render(request,'hod/list_timetable.html', context)


def faculty_students(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    hod_department_id = hod.fk_department_id
    
    # Get batches for HOD's department
    batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
    
    # Get academic years for HOD's department
    academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    
    # Get all semesters for HOD's department through academic years
    semesters = models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True))
    
    selected_role = request.POST.get('role', '')
    selected_batch = request.POST.get('batch', '')
    selected_academic = request.POST.get('academic_year', '')
    
    faculty_list = []
    student_list = []
    
    if request.method == 'POST' and selected_role:
        if selected_role == 'faculty':
            # Get faculty for HOD's department
            faculty_list = models.Users.objects.filter(
                fk_department_id=hod_department_id,
                role='faculty'
            ).order_by('full_name')
            
        elif selected_role == 'student':
            # Base student query for HOD's department
            student_query = models.Users.objects.filter(
                fk_department_id=hod_department_id,
                role='student'
            )
            
            # Apply batch filter if selected
            if selected_batch:
                student_query = student_query.filter(fk_batch_id=selected_batch)
            
            # Apply academic year filter if selected
            if selected_academic:
                student_query = student_query.filter(fk_academic_id=selected_academic)
            
            student_list = student_query.order_by('full_name')
    
    context = {
        'faculty_list': faculty_list,
        'student_list': student_list,
        'batches': batches,
        'academic_years': academic_years,
        'semesters': semesters,
        'selected_role': selected_role,
        'selected_batch': selected_batch,
        'selected_academic': selected_academic
    }
    
    return render(request, 'hod/faculty_students.html', context)


def delete_faculty(request, user_id):
    try:
        # Get faculty user from Users table
        faculty_user = models.Users.objects.get(user_id=user_id)
        
        # Get the HOD's department
        username = request.session['email']
        hod = models.Users.objects.get(email=username)
        hod_department_id = hod.fk_department_id
        
        # Get email to delete from Login table
        faculty_email = faculty_user.email
        
        # Delete from Login table (username is email)
        models.Login.objects.filter(username=faculty_email).delete()
        
        # Delete from Users table
        faculty_user.delete()
        
        messages.success(request, 'Faculty deleted successfully')
        
        # Get updated faculty list
        faculty_list = models.Users.objects.filter(
            fk_department_id=hod_department_id,
            role='faculty'
        ).order_by('full_name')
        
        # Get batches for context
        batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
        academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
        semesters = models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True))
        
        context = {
            'faculty_list': faculty_list,
            'student_list': [],
            'batches': batches,
            'academic_years': academic_years,
            'semesters': semesters,
            'selected_role': 'faculty',
            'selected_batch': '',
            'selected_academic': ''
        }
        
    except models.Users.DoesNotExist:
        messages.error(request, 'Faculty not found')
        return redirect('faculty_students')
    except Exception as e:
        messages.error(request, f'Error deleting faculty: {str(e)}')
        return redirect('faculty_students')
    
    return render(request, 'hod/faculty_students.html', context)


def delete_student(request, user_id):
    try:
        # Get student user from Users table
        student_user = models.Users.objects.get(user_id=user_id)
        
        # Get the HOD's department
        username = request.session['email']
        hod = models.Users.objects.get(email=username)
        hod_department_id = hod.fk_department_id
        
        # Get email to delete from Login table
        student_email = student_user.email
        
        # Delete from Login table (username is email)
        models.Login.objects.filter(username=student_email).delete()
        
        # Delete from Users table
        student_user.delete()
        
        messages.success(request, 'Student deleted successfully')
        
        # Get updated student list
        student_list = models.Users.objects.filter(
            fk_department_id=hod_department_id,
            role='student'
        ).order_by('full_name')
        
        # Get batches for context
        batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
        academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
        semesters = models.Semesters.objects.filter(fk_academic_id__in=academic_years.values_list('academic_id', flat=True))
        
        context = {
            'faculty_list': [],
            'student_list': student_list,
            'batches': batches,
            'academic_years': academic_years,
            'semesters': semesters,
            'selected_role': 'student',
            'selected_batch': '',
            'selected_academic': ''
        }
        
    except models.Users.DoesNotExist:
        messages.error(request, 'Student not found')
        return redirect('faculty_students')
    except Exception as e:
        messages.error(request, f'Error deleting student: {str(e)}')
        return redirect('faculty_students')
    
    return render(request, 'hod/faculty_students.html', context)

def update_semester(request):
    username = request.session['email']
    hod = models.Users.objects.get(email=username)
    hod_department_id = hod.fk_department_id
    
    # Get base data for dropdowns
    batches = models.Batches.objects.filter(fk_department_id=hod_department_id)
    academic_years = models.AcademicYears.objects.filter(fk_batch_id__in=batches.values_list('batch_id', flat=True))
    semesters = models.Semesters.objects.filter(
        fk_academic_id__in=academic_years.values_list('academic_id', flat=True)
    ).order_by('fk_academic_id', 'semester_number')
    
    students = None
    current_semester = None
    selected_batch = ''
    selected_academic = ''
    selected_semester = ''
    available_semesters = []
    selected_batch_obj = None
    selected_academic_obj = None
    
    if request.method == 'POST':
        action = request.POST.get('action', 'filter')
        batch_id = request.POST.get('batch')
        academic_id = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')
        new_semester_id = request.POST.get('new_semester')
        
        # Handle update operation
        if action == 'update' and new_semester_id:
            try:
                # Get all students matching the criteria
                students_to_update = models.Users.objects.filter(
                    role='student',
                    fk_department_id=hod_department_id,
                    fk_batch_id=batch_id,
                    fk_academic_id=academic_id,
                    fk_semester_id=semester_id
                )
                
                # Update all students to new semester
                updated_count = students_to_update.update(fk_semester_id=new_semester_id)
                
                messages.success(request, f'Successfully updated semester for {updated_count} students!')
                
                # Show students in their NEW semester after update
                students = models.Users.objects.filter(
                    role='student',
                    fk_department_id=hod_department_id,
                    fk_batch_id=batch_id,
                    fk_academic_id=academic_id,
                    fk_semester_id=new_semester_id
                ).order_by('full_name')
                
                # Update display variables
                current_semester = models.Semesters.objects.get(semester_id=new_semester_id)
                selected_batch = batch_id
                selected_academic = academic_id
                selected_semester = new_semester_id
                
                # Get batch and academic year objects for display
                selected_batch_obj = models.Batches.objects.get(batch_id=batch_id)
                selected_academic_obj = models.AcademicYears.objects.get(academic_id=academic_id)
                
                # Get available semesters for the same academic year only
                available_semesters = models.Semesters.objects.filter(
                    fk_academic_id=academic_id
                ).order_by('semester_number')
                
            except Exception as e:
                messages.error(request, f'Error updating students: {str(e)}')
        
        # Handle show students operation
        elif batch_id and academic_id and semester_id:
            students = models.Users.objects.filter(
                role='student',
                fk_department_id=hod_department_id,
                fk_batch_id=batch_id,
                fk_academic_id=academic_id,
                fk_semester_id=semester_id
            ).order_by('full_name')
            
            if students.exists():
                current_semester = models.Semesters.objects.get(semester_id=semester_id)
                selected_batch = batch_id
                selected_academic = academic_id
                selected_semester = semester_id
                
                # Get batch and academic year objects for display
                selected_batch_obj = models.Batches.objects.get(batch_id=batch_id)
                selected_academic_obj = models.AcademicYears.objects.get(academic_id=academic_id)
                
                # Get available semesters for the same academic year only
                available_semesters = models.Semesters.objects.filter(
                    fk_academic_id=academic_id
                ).order_by('semester_number')
            else:
                messages.warning(request, 'No students found matching the selected criteria.')
                selected_batch_obj = None
                selected_academic_obj = None
    
    context = {
        'batches': batches,
        'academic_years': academic_years,
        'semesters': semesters,
        'students': students,
        'current_semester': current_semester,
        'selected_batch': selected_batch,
        'selected_academic': selected_academic,
        'selected_semester': selected_semester,
        'selected_batch_obj': selected_batch_obj,
        'selected_academic_obj': selected_academic_obj,
        'available_semesters': available_semesters
    }
    return render(request,'hod/update_semester.html', context)