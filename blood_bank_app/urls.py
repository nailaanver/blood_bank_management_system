from django.urls import path
from . import views
from blood_bank_app import views


urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.login_View, name='login'),
    path('register/',views.register, name='register'),
    path('patient_dashboard/',views.patient_dashboard, name='patient_dashboard'),
    path('hospital_dashboard/',views.hospital_dashboard, name='hospital_dashboard'),
    path('donor_dashboard/',views.donor_dashboard, name='donor_dashboard'),
    path('admin_dashboard/',views.admin_dashboard, name='admin_dashboard'),
    

]