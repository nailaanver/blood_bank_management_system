from .models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


from blood_bank_app.forms import LoginForm,UserForm

# Create your views here.
def login_View(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.profile.role == 'patient':
                    return redirect('patient_dashboard')
                elif user.profile.role == 'donor':
                    return redirect('donor_dashboard')
                elif user.profile.role == 'hospital':
                    return redirect('hospital_dashboard')
                elif user.profile.role == 'admin':
                    return redirect('admin_dashboard')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# register
def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # hash password
            user.save()
            # Save profile (role)
            role = request.POST.get('role')
            Profile.objects.create(user=user, role=role)
            return redirect('login')
    else:
        form = UserForm()
    return render(request, 'register.html', {'form': form})
def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')
def hospital_dashboard(request):
    return render(request, 'patient_dashboard.html')
def admin_dashboard(request):
    return render(request, 'patient_dashboard.html')
def donor_dashboard(request):
    return render(request, 'patient_dashboard.html')
def index(request):
    return render(request,'index.html', Name='index')
