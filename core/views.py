from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from core.models import Login, UserInfo, DoctorProfile, AuditLog, ConsentRequest, MedicalRecord, Prescription
from core.forms import LoginForm, PatientRegisterForm, DoctorRegisterForm, AddPrescriptionForm
from core.decorators import role_required
from django.utils import timezone
from django.db.models import Q
from itertools import chain
from operator import attrgetter
import uuid

def index_view(request):
    """Public landing page. Logged-in users are sent straight to their dashboard."""
    if request.session.get('user_id'):
        role = request.session.get('role')
        if role == 'patient':
            return redirect('patient_dashboard')
        elif role == 'doctor':
            return redirect('doctor_dashboard')
        elif role == 'admin':
            return redirect('admin_dashboard')
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                user = Login.objects.get(email=email)
                if check_password(password, user.password):
                    if not user.is_active:
                        messages.error(request, "Your account is deactivated.")
                        return render(request, 'auth/login.html', {'form': form})
                    
                    if user.role == 'doctor' and not hasattr(user.user_info, 'doctor_profile'):
                        messages.error(request, "Doctor profile missing.")
                        return render(request, 'auth/login.html', {'form': form})
                        
                    if user.role == 'doctor' and not user.user_info.doctor_profile.is_approved:
                        messages.warning(request, "Your account is pending admin approval.")
                        return render(request, 'auth/login.html', {'form': form})
                    
                    # Cycle session key for security
                    request.session.cycle_key()
                    
                    # Store session details
                    request.session['user_id'] = user.id
                    request.session['role'] = user.role
                    
                    # Log audit event
                    AuditLog.objects.create(
                        actor=user,
                        action_type='LOGIN',
                        details='User logged in successfully',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    
                    messages.success(request, f"Welcome back, {user.email}!")
                    
                    if user.role == 'patient':
                        return redirect('patient_dashboard') # To be implemented
                    elif user.role == 'doctor':
                        return redirect('doctor_dashboard') # To be implemented
                    elif user.role == 'admin':
                        return redirect('admin_dashboard') # To be implemented
                else:
                    messages.error(request, "Invalid credentials.")
            except Login.DoesNotExist:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
        
    return render(request, 'auth/login.html', {'form': form})


def register_patient_view(request):
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            if Login.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email is already registered.")
                return render(request, 'auth/register_patient.html', {'form': form})
                
            login_user = Login.objects.create(
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password']),
                role='patient',
                is_active=True
            )
            
            # Generate Global Health ID (e.g. GHID-XXXX-XXXX)
            unique_id = f"GHID-{uuid.uuid4().hex[:8].upper()}"
            
            UserInfo.objects.create(
                login=login_user,
                name=form.cleaned_data['name'],
                dob=form.cleaned_data['dob'],
                gender=form.cleaned_data['gender'],
                contact_number=form.cleaned_data['contact_number'],
                global_health_id=unique_id
            )
            
            AuditLog.objects.create(
                actor=login_user,
                action_type='REGISTER',
                details=f'Patient registered with ID {unique_id}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f"Registration successful! Your Global Health ID is {unique_id}. Please login.")
            return redirect('login')
    else:
        form = PatientRegisterForm()
        
    return render(request, 'auth/register_patient.html', {'form': form})


def register_doctor_view(request):
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            if Login.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email is already registered.")
                return render(request, 'auth/register_doctor.html', {'form': form})
                
            if DoctorProfile.objects.filter(registration_number=form.cleaned_data['registration_number']).exists():
                messages.error(request, "Registration number already in use.")
                return render(request, 'auth/register_doctor.html', {'form': form})
                
            login_user = Login.objects.create(
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password']),
                role='doctor',
                is_active=True
            )
            
            user_info = UserInfo.objects.create(
                login=login_user,
                name=form.cleaned_data['name']
                # Contact info etc can be added to form if needed
            )
            
            DoctorProfile.objects.create(
                user_info=user_info,
                specialization=form.cleaned_data['specialization'],
                registration_number=form.cleaned_data['registration_number'],
                is_approved=False
            )
            
            AuditLog.objects.create(
                actor=login_user,
                action_type='REGISTER',
                details='Doctor registered, pending approval',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, "Registration successful! Your account is pending admin approval.")
            return redirect('login')
    else:
        form = DoctorRegisterForm()
        
    return render(request, 'auth/register_doctor.html', {'form': form})


def logout_view(request):
    if 'user_id' in request.session:
        try:
            user = Login.objects.get(id=request.session['user_id'])
            AuditLog.objects.create(
                actor=user,
                action_type='LOGOUT',
                details='User logged out',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        except Login.DoesNotExist:
            pass
            
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('login')

@role_required(['patient'])
def patient_dashboard_view(request):
    user = request.custom_user
    user_info = user.user_info
    
    # Stats
    total_records = MedicalRecord.objects.filter(patient=user_info).count() + Prescription.objects.filter(patient=user_info).count()
    # Consents
    active_consents_list = ConsentRequest.objects.filter(patient=user_info, status='approved')
    pending_requests_list = ConsentRequest.objects.filter(patient=user_info, status='pending')
    
    active_consents = active_consents_list.count()
    pending_requests = pending_requests_list.count()
    
    # Unified Timeline
    med_records = MedicalRecord.objects.filter(patient=user_info)
    prescriptions = Prescription.objects.filter(patient=user_info)
    
    # Combine and sort by created_at descending
    timeline = sorted(
        chain(med_records, prescriptions),
        key=attrgetter('created_at'),
        reverse=True
    )
    
    context = {
        'user_info': user_info,
        'total_records': total_records,
        'active_consents': active_consents,
        'pending_requests': pending_requests,
        'active_consents_list': active_consents_list,
        'pending_requests_list': pending_requests_list,
        'timeline': timeline,
    }
    return render(request, 'patient/dashboard.html', context)

@role_required(['doctor'])
def doctor_dashboard_view(request):
    user = request.custom_user
    doctor_profile = user.user_info.doctor_profile
    
    now = timezone.now()
    active_consents = ConsentRequest.objects.filter(
        doctor=user.user_info, 
        status='approved'
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    )
    
    pending_requests = ConsentRequest.objects.filter(doctor=user.user_info, status='pending')
    
    search_query = request.GET.get('search', '')
    search_results = None
    if search_query:
        search_results = UserInfo.objects.filter(global_health_id=search_query, login__role='patient')
        
    context = {
        'doctor_profile': doctor_profile,
        'active_consents': active_consents,
        'pending_requests': pending_requests,
        'search_query': search_query,
        'search_results': search_results,
    }
    return render(request, 'doctor/dashboard.html', context)

@role_required(['admin'])
def admin_dashboard_view(request):
    pending_doctors = DoctorProfile.objects.filter(is_approved=False)
    recent_logs = AuditLog.objects.all().order_by('-timestamp')[:50]
    
    # Stats
    stats = {
        'total_patients': Login.objects.filter(role='patient').count(),
        'total_doctors': Login.objects.filter(role='doctor').count(),
        'total_records': MedicalRecord.objects.count() + Prescription.objects.count(),
        'active_consents': ConsentRequest.objects.filter(status='approved').count()
    }
    
    context = {
        'pending_doctors': pending_doctors,
        'stats': stats,
        'recent_logs': recent_logs,
    }
    return render(request, 'admin/dashboard.html', context)

@role_required(['admin'])
def admin_approve_doctor(request, doctor_id):
    doctor = DoctorProfile.objects.get(id=doctor_id)
    doctor.is_approved = True
    doctor.save()
    
    AuditLog.objects.create(
        actor=request.custom_user,
        action_type='APPROVE_DOCTOR',
        details=f'Approved doctor {doctor.user_info.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f"Dr. {doctor.user_info.name} has been approved.")
    return redirect('admin_dashboard')

@role_required(['admin'])
def admin_reject_doctor(request, doctor_id):
    doctor = DoctorProfile.objects.get(id=doctor_id)
    name = doctor.user_info.name
    # Delete the profile and login
    doctor.user_info.login.delete() # Cascade deletes UserInfo and DoctorProfile
    
    AuditLog.objects.create(
        actor=request.custom_user,
        action_type='REJECT_DOCTOR',
        details=f'Rejected doctor {name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f"Dr. {name}'s registration has been rejected and removed.")
    return redirect('admin_dashboard')

@role_required(['doctor'])
def doctor_request_consent(request, patient_id):
    patient = UserInfo.objects.get(id=patient_id)
    # Check if request already exists
    existing = ConsentRequest.objects.filter(patient=patient, doctor=request.custom_user.user_info).first()
    if existing:
        if existing.status == 'approved':
            messages.info(request, "You already have access to this patient.")
        elif existing.status == 'pending':
            messages.info(request, "A consent request is already pending.")
        else:
            # Re-request if revoked/denied
            existing.status = 'pending'
            existing.requested_at = timezone.now()
            existing.save()
            messages.success(request, "Consent request re-submitted.")
    else:
        ConsentRequest.objects.create(
            patient=patient,
            doctor=request.custom_user.user_info,
            status='pending'
        )
        messages.success(request, "Consent request submitted to patient.")
    
    AuditLog.objects.create(
        actor=request.custom_user,
        action_type='REQUEST_CONSENT',
        target_patient=patient,
        details=f'Requested consent from {patient.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    return redirect('doctor_dashboard')

@role_required(['patient'])
def patient_consent_action(request, request_id, action):
    consent = ConsentRequest.objects.get(id=request_id, patient=request.custom_user.user_info)
    
    if action == 'approve':
        consent.status = 'approved'
        consent.expires_at = timezone.now() + timezone.timedelta(days=30)
    elif action == 'deny':
        consent.status = 'denied'
    elif action == 'revoke':
        consent.status = 'revoked'
        
    consent.decided_at = timezone.now()
    consent.save()
    
    AuditLog.objects.create(
        actor=request.custom_user,
        action_type=f'CONSENT_{action.upper()}',
        details=f'{action.capitalize()} consent for Dr. {consent.doctor.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    messages.success(request, f"Consent {action}d successfully.")
    return redirect('patient_dashboard')

@role_required(['doctor'])
def doctor_patient_record_view(request, patient_id):
    patient = UserInfo.objects.get(id=patient_id)
    doctor_info = request.custom_user.user_info
    
    now = timezone.now()
    has_consent = ConsentRequest.objects.filter(
        patient=patient,
        doctor=doctor_info,
        status='approved'
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).exists()
    
    if not has_consent:
        messages.error(request, "You do not have active consent to view this patient's records.")
        return redirect('doctor_dashboard')
        
    if request.method == 'POST':
        form = AddPrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.patient = patient
            prescription.doctor = doctor_info
            prescription.save()
            
            AuditLog.objects.create(
                actor=request.custom_user,
                action_type='ADD_PRESCRIPTION',
                target_patient=patient,
                details=f'Added prescription for {patient.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Prescription added successfully.")
            return redirect('doctor_patient_record', patient_id=patient.id)
    else:
        form = AddPrescriptionForm()
        
    med_records = MedicalRecord.objects.filter(patient=patient)
    prescriptions = Prescription.objects.filter(patient=patient)
    timeline = sorted(chain(med_records, prescriptions), key=attrgetter('created_at'), reverse=True)
    
    context = {
        'patient': patient,
        'timeline': timeline,
        'form': form,
    }
    return render(request, 'doctor/patient_record.html', context)

@role_required(['patient'])
def patient_upload_record(request):
    if request.method == 'POST':
        from core.forms import UploadMedicalRecordForm
        form = UploadMedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = request.custom_user.user_info
            record.uploaded_by = request.custom_user.user_info
            record.save()
            
            AuditLog.objects.create(
                actor=request.custom_user,
                action_type='UPLOAD_RECORD',
                target_record_info=f"{record.get_record_type_display()} - {record.title}",
                details=f'Patient uploaded {record.get_record_type_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Document uploaded successfully.")
            return redirect('patient_dashboard')
    else:
        from core.forms import UploadMedicalRecordForm
        form = UploadMedicalRecordForm()
        
    return render(request, 'patient/upload_record.html', {'form': form})

@role_required(['patient'])
def patient_settings_view(request):
    user_info = request.custom_user.user_info
    
    if request.method == 'POST':
        from core.forms import PatientProfileForm
        form = PatientProfileForm(request.POST, request.FILES, instance=user_info)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                actor=request.custom_user,
                action_type='UPDATE_PROFILE',
                details='Patient updated their profile settings',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Profile updated successfully.")
            return redirect('patient_dashboard')
    else:
        from core.forms import PatientProfileForm
        form = PatientProfileForm(instance=user_info)
        
    return render(request, 'patient/settings.html', {'form': form, 'user_info': user_info})

@role_required(['doctor'])
def doctor_settings_view(request):
    user_info = request.custom_user.user_info
    
    if request.method == 'POST':
        from core.forms import DoctorSettingsForm
        form = DoctorSettingsForm(request.POST, request.FILES, instance=user_info)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                actor=request.custom_user,
                action_type='UPDATE_PROFILE',
                details='Doctor updated their profile settings',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Profile updated successfully.")
            return redirect('doctor_dashboard')
    else:
        from core.forms import DoctorSettingsForm
        form = DoctorSettingsForm(instance=user_info)
        
    return render(request, 'doctor/settings.html', {'form': form, 'user_info': user_info})
