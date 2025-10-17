from django.urls import path
from . import views
from blood_bank_app import views


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


    

]