from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .models import ContactMessage
from .models import DonorDetail, PatientDetail, HospitalDetail


class UserForm(forms.ModelForm):
    full_name = forms.CharField()
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
        
        

