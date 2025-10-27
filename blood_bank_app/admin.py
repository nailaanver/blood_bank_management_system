from django.contrib import admin
from .models import Profile,ContactMessage,DonorDetail,PatientDetail,HospitalDetail,Donation,Branch,Appointment,BloodRequest,Notification,BloodStock,HospitalBloodRequest
# Register your models here.
admin.site.register(Profile)
admin.site.register(ContactMessage)
admin.site.register(DonorDetail)
admin.site.register(PatientDetail)
admin.site.register(HospitalDetail)
admin.site.register(Branch)
admin.site.register(Donation)
admin.site.register(Appointment)
admin.site.register(BloodRequest)
admin.site.register(Notification)
admin.site.register(BloodStock)
admin.site.register(HospitalBloodRequest)

