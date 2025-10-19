from .models import Profile
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from .models import User
from .models import Donation
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import ContactForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.urls import reverse
from .models import Branch, Appointment


from .models import Profile, DonorDetail, PatientDetail, HospitalDetail, User, ContactMessage
from .forms import LoginForm, UserForm, ContactForm, DonorDetailForm, PatientDetailForm, HospitalDetailForm,EligibilityForm


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
                # Check if the user already filled details
                role = user.profile.role
                if role == 'donor':
                    if hasattr(user, 'donordetail'):
                        return redirect('donor_dashboard')
                    else:
                        return redirect('donor_detail_form')
                elif role == 'patient':
                    if hasattr(user, 'patientdetail'):
                        return redirect('patient_dashboard')
                    else:
                        return redirect('patient_detail_form')
                elif role == 'hospital':
                    if hasattr(user, 'hospitaldetail'):
                        return redirect('hospital_dashboard')
                    else:
                        return redirect('hospital_detail_form')
                elif role == 'admin':
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
@login_required
def donor_dashboard(request):
    donor = DonorDetail.objects.filter(user=request.user).first()  # get latest donor details
    return render(request, 'donor_dashboard.html', {'donor': donor})
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



from django.shortcuts import redirect, render, get_object_or_404

@login_required
def donor_detail_form_view(request):
    # Get the donor detail instance for logged-in user
    donor_instance, created = DonorDetail.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = DonorDetailForm(request.POST, request.FILES, instance=donor_instance)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user  # ensure the user is set
            donor.save()  # save model including file
            messages.success(request, "Your details have been updated successfully!")
            return redirect('donor_detail_form')  # reload the form with updated data
        else:
            messages.error(request, "Please fix the errors below.")
            print(form.errors)  # debug: check for validation errors
    else:
        form = DonorDetailForm(instance=donor_instance)

    return render(request, 'donor_detail_form.html', {'form': form})

@login_required
def update_donor_detail_view(request):
    donor_instance = get_object_or_404(DonorDetail, user=request.user)

    if request.method == 'POST':
        form = DonorDetailForm(request.POST, request.FILES, instance=donor_instance)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user  # make sure it's linked
            donor.save()
            messages.success(request, "✅ Your details have been updated successfully!")
            return redirect('update_donor_detail')  # stay on same page
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
            print("Form errors:", form.errors)
    else:
        form = DonorDetailForm(instance=donor_instance)

    return render(request, 'donor/update_donor_detail.html', {'form': form})





def view_donation_history(request):
    donations = Donation.objects.filter(donor=request.user).order_by('-date')
    return render(request,'donor/view_donation_history.html',{'donations':donations})




@login_required
def check_eligibility(request):
    form = EligibilityForm(request.POST or None)
    result = None
    status = None

    if request.method == 'POST':
        if form.is_valid():
            age = form.cleaned_data['age']
            weight = form.cleaned_data['weight']
            last_donation = form.cleaned_data['last_donation_date']
            hemoglobin = form.cleaned_data['hemoglobin']

            # --- Eligibility Logic ---
            if age < 18 or age > 65:
                result = "❌ You are not eligible due to age restrictions."
                status = "danger"
            elif weight < 50:
                result = "⚠️ You are not eligible due to low weight."
                status = "warning"
            elif last_donation and (date.today() - last_donation).days < 90:
                next_date = last_donation + timedelta(days=90)
                result = f"🕒 You can donate again after {next_date.strftime('%d %B %Y')}."
                status = "warning"
            else:
                # ✅ Eligible: redirect to Request Appointments
                message = "✅ You are eligible to donate blood! Proceed to request an appointment."
                return redirect(f"{reverse('donor_dashboard')}?section=request_appoiments&msg={message}")
        else:
            result = "⚠️ Please correct the errors and try again."
            status = "warning"

    return render(request, 'donor/check_eligibility.html', {
        'form': form,
        'result': result,
        'status': status
    })
    
@login_required
def request_appoiments(request):
    branches = Branch.objects.all()
    success_message = None

    if request.method == 'POST':
        date = request.POST.get('appointment_date')
        time = request.POST.get('appointment_time')
        branch_id = request.POST.get('branch')
        notes = request.POST.get('notes')

        if date and time and branch_id:
            Appointment.objects.create(
                donor=request.user,
                branch_id=branch_id,
                appointment_date=date,
                appointment_time=time,
                notes=notes
            )
            # ✅ Use redirect to avoid duplicate submissions
            success_message = "✅ Your appointment request has been submitted successfully!"
            return redirect(f"{reverse('request_appoiments')}?msg={success_message}")

    # Check if there's a success message in GET params
    if 'msg' in request.GET:
        success_message = request.GET['msg']

    return render(request, 'donor/request_appoiment.html', {
        'branches': branches,
        'success_message': success_message
    })




@login_required
def patient_detail_form_view(request):
    form = PatientDetailForm(request.POST or None, request.FILES or None, instance=getattr(request.user, 'patientdetail', None))
    if form.is_valid():
        patient = form.save(commit=False)
        patient.user = request.user
        patient.save()
        return redirect('patient_dashboard')
    return render(request, 'patient_detail_form.html', {'form': form})

@login_required
def hospital_detail_form_view(request):
    form = HospitalDetailForm(request.POST or None, request.FILES or None, instance=getattr(request.user, 'hospitaldetail', None))
    if form.is_valid():
        hospital = form.save(commit=False)
        hospital.user = request.user
        hospital.save()
        return redirect('hospital_dashboard')
    return render(request, 'hospital_detail_form.html', {'form': form})
