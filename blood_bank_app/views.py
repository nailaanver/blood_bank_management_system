from .models import Profile
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import ContactForm



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
    return render(request, 'hospital_dashboard.html')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')
def donor_dashboard(request):
    return render(request, 'donor_dashboard.html')
def index(request):
    return render(request,'index.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # ✅ Redirect to reset-password page with username
            return redirect('reset_password', username=user.username)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
    return render(request, 'forgot_password.html')


def reset_password(request, username):
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user.password = make_password(password)
            user.save()
            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'reset_password.html', {'username': username})

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
def admin_dashboard_content(request):
    # total_users = User.objects.count()
    # total_contacts = Contact.objects.count()

    # context = {
    #     'total_users': total_users,
    #     'total_contacts': total_contacts
    # }
    return render(request, 'partials/admin_dashboard_content.html')
def manage_users(request):
    return render(request, 'partials/manage_users.html')
def manage_bloodstock(request):
    return render(request, 'partials/manage_bloodstock.html')
def manage_requests(request):
    return render(request, 'partials/manage_requests.html')
def view_reports(request):
    return render(request, 'partials/view_reports.html')