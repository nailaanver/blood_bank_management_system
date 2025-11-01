from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .models import ContactMessage
from .models import DonorDetail, PatientDetail, HospitalDetail,HospitalBloodRequest,Appointment


class UserForm(forms.ModelForm):
    full_name = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    class Meta:
        model = User
        fields = ['full_name','username', 'email', 'password']
        help_texts = {
            'username': None,   # removes "Required. 150 characters..." text
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message', 'class': 'form-control', 'rows': 5}),
        }
        
class DonorDetailForm(forms.ModelForm):
    class Meta:
        model = DonorDetail
        fields = ['blood_group', 'gender', 'date_of_birth', 'age', 'weight', 'address', 'phone_number', 'profile_photo']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}

class PatientDetailForm(forms.ModelForm):
    class Meta:
        model = PatientDetail
        fields = ['blood_group', 'gender', 'date_of_birth', 'age', 'medical_condition', 'address', 'phone_number', 'profile_photo']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}

class HospitalDetailForm(forms.ModelForm):
    class Meta:
        model = HospitalDetail
        fields = ['hospital_name', 'address', 'phone_number', 'hospital_code']
        
class EligibilityForm(forms.Form):
    age = forms.IntegerField(min_value=18, max_value=65, label='Age')
    weight = forms.FloatField(min_value=40, label='weight (kg)')
    last_donation_date = forms.DateField(label = 'Last Donation Date',required=False,widget=forms.DateInput(attrs={'type':'date'}))
    hemoglobin = forms.FloatField(min_value=12.0, max_value=18.0, label="Hemoglobin Level (g/dL)", required=False)

from .models import BloodRequest

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'blood_group', 'units_required',
            'hospital_name',  'required_date',
            'urgency', 'reason'
        ]
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units_required': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hospital name'}),
            'required_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter reason (optional)'}),
        }

# forms.py
from django import forms
from .models import BloodStock

class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = [ 'blood_group', 'units_available']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure all hospitals are included

class HospitalBloodRequestForm(forms.ModelForm):
    class Meta:
        model = HospitalBloodRequest
        fields = [ 'hospital_name','blood_group', 'units_required', 'required_date', 'urgency']

class UserEditForm(forms.ModelForm):
    # first_name = forms.CharField(required=False)
    # last_name = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = [  'username', 'email']
        
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['hospital', 'appointment_date', 'appointment_time', 'notes']