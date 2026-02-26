# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AcademicYears(models.Model):
    academic_id = models.AutoField(primary_key=True)
    academic_year = models.CharField(max_length=30)
    fk_batch_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'academic_years'


class AttendanceRecords(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    fk_user_id = models.IntegerField()
    fk_leave_id = models.IntegerField()
    decision = models.CharField(max_length=50)
    decision_date = models.DateField()
    remarks = models.TextField()

    class Meta:
        managed = False
        db_table = 'attendance_records'


class AttendanceSummary(models.Model):
    summary_id = models.AutoField(primary_key=True)
    fk_student_id = models.IntegerField()
    total_classes = models.IntegerField()
    attended_classes = models.IntegerField()
    total_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'attendance_summary'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Batches(models.Model):
    batch_id = models.AutoField(primary_key=True)
    batch_name = models.CharField(max_length=50)
    fk_department_id = models.IntegerField()
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'batches'


class Classes(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=50)
    fk_department_id = models.IntegerField()
    academic_year = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'classes'


class Departments(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'departments'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class LeaveAiAnalysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    fk_leave_id = models.IntegerField()
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    past_leave_count = models.IntegerField()
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=2)
    academic_risk_level = models.CharField(max_length=20)
    approve_probabilty = models.DecimalField(max_digits=5, decimal_places=2)
    recommendation = models.CharField(max_length=50)
    analyzed_on = models.DateField()

    class Meta:
        managed = False
        db_table = 'leave_ai_analysis'


class LeaveDecisionLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    fk_leave_id = models.IntegerField()
    reason = models.CharField(max_length=50)
    decision = models.CharField(max_length=50)
    decision_time = models.DateField()

    class Meta:
        managed = False
        db_table = 'leave_decision_logs'


class LeaveHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    fk_leave_id = models.IntegerField()
    status = models.CharField(max_length=50)
    updated_by = models.IntegerField()
    updated_on = models.DateField()
    remarks = models.TextField()

    class Meta:
        managed = False
        db_table = 'leave_history'


class LeaveRequests(models.Model):
    leave_id = models.AutoField(primary_key=True)
    fk_user_id = models.IntegerField()
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=50)
    applied_on = models.DateField()

    class Meta:
        managed = False
        db_table = 'leave_requests'


class Login(models.Model):
    username = models.CharField(primary_key=True, max_length=50)
    password = models.CharField(max_length=20)
    usertype = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'login'


class MlModels(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=50)
    algorithm = models.CharField(max_length=50)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2)
    precision_score = models.DecimalField(max_digits=5, decimal_places=2)
    recall_score = models.DecimalField(max_digits=5, decimal_places=2)
    fl_score = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.IntegerField()
    trained_on = models.DateField()

    class Meta:
        managed = False
        db_table = 'ml_models'


class Semesters(models.Model):
    semester_id = models.AutoField(primary_key=True)
    fk_academic_id = models.IntegerField()
    status = models.CharField(max_length=50)
    semester_number = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'semesters'


class Subjects(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=50)
    fk_batch_id = models.IntegerField()
    fk_semester_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'subjects'


class Timetable(models.Model):
    timetable_id = models.AutoField(primary_key=True)
    fk_department_id = models.IntegerField()
    fk_semester_id = models.IntegerField()
    fk_subject_id = models.IntegerField()
    fk_faculty_id = models.IntegerField()
    day_of_week = models.CharField(max_length=20)
    hours = models.IntegerField()
    created_at = models.DateTimeField()
    fk_batch_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'timetable'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=50)
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)
    role = models.CharField(max_length=50)
    fk_department_id = models.IntegerField()
    status = models.CharField(max_length=50)
    created_at = models.DateField()
    fk_batch_id = models.IntegerField()
    fk_academic_id = models.IntegerField()
    fk_semester_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'
