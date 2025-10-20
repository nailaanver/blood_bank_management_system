from django.db import models
from PIL import Image


# Create your models here.
from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
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

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.profile_photo.path)
            if img.height > 400 or img.width > 400:
                output_size = (400, 400)
                img.thumbnail(output_size)
                img.save(self.profile_photo.path)
        except Exception as e:
            print("Image processing error:", e)

            
            
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
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} - {self.appointment_date}"
    

