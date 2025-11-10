from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .models import ContactMessage
from .models import DonorDetail, PatientDetail, HospitalDetail,HospitalBloodRequest,Appointment,HospitalBloodStock


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
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'readonly': 'readonly'}),  # 👈 prevents manual editing
        }


class PatientDetailForm(forms.ModelForm):
    class Meta:
        model = PatientDetail
        fields = ['full_name','blood_group', 'gender', 'date_of_birth', 'age', 'medical_condition', 'address', 'phone_number', 'profile_photo']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'})}

class HospitalDetailForm(forms.ModelForm):
    class Meta:
        model = HospitalDetail
        fields = ['hospital_name', 'address', 'phone_number', 'hospital_code']
        
from django import forms
from datetime import date

class EligibilityForm(forms.Form):
    age = forms.IntegerField(label="Age", min_value=18, max_value=65)
    weight = forms.FloatField(label="Weight (kg)", min_value=0)
    first_donation = forms.ChoiceField(
        label="Is this your first donation?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.RadioSelect
    )
    last_donation_date = forms.DateField(
    label="Last Donation Date",
    required=False,
    widget=forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'})
)


    # (Hemoglobin field removed as per your earlier request)


from .models import BloodRequest
from django.utils import timezone

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['hospital_name', 'units_required', 'urgency', 'required_date', 'medical_condition']
        widgets = {
            'hospital_name': forms.TextInput(attrs={
                'placeholder': 'Enter hospital name',
                'class': 'form-control'
            }),
            'units_required': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control',
                'placeholder': 'Number of blood units required'
            }),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'required_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': timezone.localdate().isoformat(),  # prevent past dates
                    'class': 'form-control'
                }
            ),
            'medical_condition': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g., Surgery, Accident, Anemia...',
                'class': 'form-control'
            }),
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
        
class HospitalBloodStockForm(forms.ModelForm):
    class Meta:
        model = HospitalBloodStock
        fields = ['blood_group', 'units_available']

        # Make sure all hospitals are included

from datetime import date
class HospitalBloodRequestForm(forms.ModelForm):
    class Meta:
        model = HospitalBloodRequest
        fields = ['blood_group', 'units_required', 'required_date', 'urgency']
        widgets = {
            'required_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d')
            }),
        }


class UserEditForm(forms.ModelForm):
    # first_name = forms.CharField(required=False)
    # last_name = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = [  'username', 'email']
        
class AppointmentForm(forms.ModelForm):
    blood_units = forms.IntegerField(
        label="Blood Volume (ml)",
        min_value=350,
        max_value=470,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter between 350 and 470 ml',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Appointment
        fields = ['hospital', 'appointment_date', 'appointment_time', 'blood_units', 'notes']