from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/patient/', views.register_patient_view, name='register_patient'),
    path('register/doctor/', views.register_doctor_view, name='register_doctor'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('patient/dashboard/', views.patient_dashboard_view, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Actions
    path('admin/approve-doctor/<int:doctor_id>/', views.admin_approve_doctor, name='admin_approve_doctor'),
    path('admin/reject-doctor/<int:doctor_id>/', views.admin_reject_doctor, name='admin_reject_doctor'),
    path('doctor/request-consent/<int:patient_id>/', views.doctor_request_consent, name='doctor_request_consent'),
    path('doctor/patient/<int:patient_id>/', views.doctor_patient_record_view, name='doctor_patient_record'),
    path('doctor/settings/', views.doctor_settings_view, name='doctor_settings'),
    path('patient/consent-action/<int:request_id>/<str:action>/', views.patient_consent_action, name='patient_consent_action'),
    path('patient/upload-record/', views.patient_upload_record, name='patient_upload_record'),
    path('patient/settings/', views.patient_settings_view, name='patient_settings'),
]
