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
    path('donor/request_appoiments/',views.request_appoiments,name = 'request_appoiments'),
    path('donor/update_donor_detail/', views.update_donor_detail_view, name='update_donor_detail'),


]
# ✅ Add this at the end to serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)