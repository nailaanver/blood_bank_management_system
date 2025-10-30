from django.urls import path
from . import views
from blood_bank_app import views

# For serving media files in development
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.login_View, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/',views.register, name='register'),
    path('patient_dashboard/',views.patient_dashboard, name='patient_dashboard'),
    path('hospital_dashboard/',views.hospital_dashboard, name='hospital_dashboard'),
    path('donor_dashboard/',views.donor_dashboard, name='donor_dashboard'),
    path('admin_dashboard/',views.admin_dashboard, name='admin_dashboard'),
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:username>/', views.reset_password, name='reset_password'),
    path('contact/', views.contact_view, name='contact'),
    path('admin_dashboard_content/', views.admin_dashboard_content, name='admin_dashboard_content'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage_bloodstock/', views.manage_bloodstock, name='manage_bloodstock'),
    path('manage_requests/', views.manage_requests, name='manage_requests'),
    path('view_reports/', views.view_reports, name='view_reports'),
    
    path('donor_detail_form/',views.donor_detail_form_view,name='donor_detail_form'),
    path('patient_detail_form/',views.patient_detail_form_view,name='patient_detail_form'),
    path('hospital_detail_form/',views.hospital_detail_form_view,name='hospital_detail_form'),
    
    path('donor/view_donation_history/',views.view_donation_history,name = 'view_donation_history'),
    path('donor/check_eligibility/',views.check_eligibility,name = 'check_eligibility'),
    path('donor/request_appoiments/',views.request_appointment,name = 'request_appoiments'),
    path('donor/update_donor_detail/', views.update_donor_detail_view, name='update_donor_detail'),
    path('request_blood/', views.request_blood, name='request_blood'),
    path('request_status/', views.request_status, name='request_status'),
    path('received_history/', views.received_history, name='received_history'),
    path('search_blood/', views.search_blood, name='search_blood'),
    path('edit_patient_profile/', views.edit_patient_profile, name='edit_patient_profile'),
    path('partials/update_request_status/<int:request_id>/<str:action>/', views.update_request_status, name='update_request_status'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('view_notifications/', views.view_notifications_donor, name='view_notifications_donor'),
    path('profile/', views.view_profile, name='view_profile'),
    path('add-blood-stock/', views.add_blood_stock, name='add_blood_stock'),
    
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),  # 👈 this line is required
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    path('hospital_request_blood/',views.hospital_request_blood, name='hospital_request_blood'),
    path('hospital_request_history/',views.hospital_request_history, name='hospital_request_history'),
    path('hospital_dashboard_content/',views.hospital_dashboard_content, name='hospital_dashboard_content'),
    path('reports/', views.reports, name='reports'),
    path('update_appointment_status/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('update_patient_status/<int:request_id>/<str:status>/', views.update_patient_status, name='update_patient_status'),
    path('update_hospital_status/<int:request_id>/<str:status>/', views.update_hospital_status, name='update_hospital_status'),

    path('approve_appointment/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('reject_appointment/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('manage_hospital_requests/', views.manage_hospital_requests, name='manage_hospital_requests'),
    
    path('approve_appointment/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('respond_to_donation_date/<int:appointment_id>/', views.respond_to_donation_date, name='respond_to_donation_date'),
    path('mark_donation_completed/<int:appointment_id>/', views.mark_donation_completed, name='mark_donation_completed'),
    path('assign_donation_date/<int:request_id>/', views.assign_donation_date, name='assign_donation_date'),
    path('approve_request/<int:request_id>/', views.approve_request, name='approve_request'),

]
# ✅ Add this at the end to serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)