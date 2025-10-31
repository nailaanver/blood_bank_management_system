from django.db import models
from PIL import Image

from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_future_date(value):
    """Allow only today or future dates."""
    if value < timezone.localdate():
        raise ValidationError("Date cannot be in the past.")

# Create your models here.
from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('patient', 'Patient'),
        ('hospital','Hospital'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='donor')

    def __str__(self):
        return f"{self.user} ({self.role})"
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
    
class DonorDetail(models.Model):
    BLOOD_GROUPS = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]
    GENDER_CHOICES = [('Male','Male'),('Female','Female'),('Other','Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='donor_photos/', default='donor_photos/default.jpg')

    # ✅ New field to track eligibility
    is_eligible = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


            
            
class PatientDetail(models.Model):
    BLOOD_GROUPS = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]
    GENDER_CHOICES = [('Male','Male'),('Female','Female'),('Other','Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField()
    medical_condition = models.TextField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='patient_photos/', default='default.jpg')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.profile_photo.path)
        if img.height > 400 or img.width > 400:
            output_size = (400, 400)
            img.thumbnail(output_size)
            img.save(self.profile_photo.path)

class HospitalDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    hospital_code = models.CharField(max_length=50)

    def __str__(self):
        return self.hospital_name

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     img = Image.open(self.hospital_photo.path)
    #     if img.height > 400 or img.width > 400:
    #         output_size = (400, 400)
    #         img.thumbnail(output_size)
    #         img.save(self.hospital_photo.path)
    
class Donation(models.Model):
    donor =  models.ForeignKey(User,on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=255)
    date = models.DateField()
    units = models.DecimalField(max_digits=3,decimal_places=1)
    status = models.CharField(max_length=50,choices=[('Pending','Pending'),('Approved','Approved')])
    certificate = models.FileField(upload_to='certificates/',null=True,blank=True) 
    
class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(HospitalDetail, on_delete=models.CASCADE, null=True)
    appointment_date = models.DateField(null=True, validators=[validate_future_date])
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', null=True)

    donor_response = models.CharField(
        max_length=20,
        choices=[('Accepted', 'Accepted'), ('Reschedule', 'Reschedule'), ('No Response', 'No Response')],
        default='No Response', null=True
    )

    blood_units = models.IntegerField(default=0, null=True)  # Units donated by donor

    created_at = models.DateTimeField(auto_now_add=True,null=True)  # Add created_at field
    donation_date = models.DateField(null=True, blank=True,validators=[validate_future_date])  # Optional: Date when donation happens


    def __str__(self):
        return f"{self.donor.username} - {self.hospital.hospital_name}"
    
class BloodRequest(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    URGENCY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Emergency', 'Emergency'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_required = models.PositiveIntegerField()
    hospital_name = models.CharField(max_length=150)
    hospital_address = models.TextField()
    required_date = models.DateField(validators=[validate_future_date])
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.blood_group}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


# models.py
class BloodStock(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    hospital = models.ForeignKey('HospitalDetail', on_delete=models.CASCADE, null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_available = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_group} - {self.hospital.hospital_name if self.hospital else 'No Hospital'}"


class HospitalBloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    URGENCY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    hospital_name = models.ForeignKey(HospitalDetail, on_delete=models.CASCADE, null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True)
    units_required = models.IntegerField(null=True)
    required_date = models.DateField(null=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='Medium', null=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending',
        null=True
    )
    requested_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        if self.hospital_name:
            return f"{self.hospital_name.hospital_name} - {self.blood_group}"
        else:
            return f"Hospital Blood Request - {self.blood_group}"

class DonationRequest(models.Model):
    donor = models.ForeignKey('DonorDetail', on_delete=models.CASCADE,null=True)
    hospital = models.ForeignKey('HospitalDetail', on_delete=models.CASCADE,null=True)
    donation_date = models.DateField(null=True, blank=True, validators=[validate_future_date])
    status = models.CharField(max_length=20, default='Pending')



