from django.db import models
from django.utils import timezone

def patient_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/patient_<id>/<filename>
    return f'patient_{instance.patient.id}/{filename}'

class Login(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.email} ({self.role})"

class UserInfo(models.Model):
    login = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='user_info')
    name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    emergency_contact = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    global_health_id = models.CharField(max_length=50, unique=True, null=True, blank=True) # Only for patients
    
    def __str__(self):
        return self.name

class DoctorProfile(models.Model):
    user_info = models.OneToOneField(UserInfo, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Dr. {self.user_info.name} - {self.specialization}"

class ConsentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('revoked', 'Revoked'),
    ]
    patient = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='received_consents')
    doctor = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='requested_consents')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ('prescription', 'Prescription'),
        ('lab_report', 'Lab Report'),
        ('diagnosis', 'Diagnosis'),
        ('discharge_summary', 'Discharge Summary'),
        ('scan', 'Scan'),
        ('other', 'Other')
    ]
    patient = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='medical_records')
    uploaded_by = models.ForeignKey(UserInfo, on_delete=models.SET_NULL, null=True, related_name='uploaded_records')
    record_type = models.CharField(max_length=50, choices=RECORD_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=patient_directory_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Prescription(models.Model):
    patient = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='issued_prescriptions')
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    actor = models.ForeignKey(Login, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=100)
    target_patient = models.ForeignKey(UserInfo, on_delete=models.SET_NULL, null=True, blank=True)
    target_record_info = models.CharField(max_length=255, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
