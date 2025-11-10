from .models import Profile
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import ContactForm,BloodRequest
from .forms import BloodRequestForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.urls import reverse
from .models import Branch, Appointment,DonationRequest
from .models import Profile, DonorDetail, PatientDetail, HospitalDetail, User, ContactMessage,Notification,BloodStock,Donation,HospitalBloodRequest
from .forms import LoginForm, UserForm, ContactForm, DonorDetailForm, PatientDetailForm, HospitalDetailForm,EligibilityForm,BloodStockForm,HospitalBloodRequestForm,AppointmentForm,HospitalBloodStockForm
from blood_bank_app.forms import LoginForm,UserForm
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError

from pyecharts.charts import Pie
from pyecharts import options as opts
from .models import HospitalDetail, HospitalBloodStock
from .models import update_completed_donations  # ✅ import this at the top of your views file


# ✅ Check if logged-in user is a hospital
def is_hospital(user):
    return hasattr(user, 'profile') and user.profile.role == 'hospital'

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

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

@login_required
def patient_dashboard(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'patient_dashboard.html', {'unread_count': unread_count})

@login_required
def hospital_dashboard(request):
    hospital = HospitalDetail.objects.get(user=request.user)
    blood_stocks = BloodStock.objects.filter(hospital=hospital)
    requests = BloodRequest.objects.filter(hospital_name=hospital.hospital_name)

    # ✅ Get unread notifications count
    from .models import Notification
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'hospital': hospital,
        'blood_stocks': blood_stocks,
        'requests': requests,
        'total_requests': requests.count(),
        'pending_requests': requests.filter(status='Pending').count(),
        'approved_requests': requests.filter(status='Approved').count(),
        'unread_count': unread_count,  # ✅ add this
    }

    return render(request, 'hospital_dashboard.html', context)

@login_required
def update_hospital_status(request, request_id, status):
    blood_request = HospitalBloodRequest.objects.get(id=request_id)
    blood_request.status = status
    blood_request.save()

    # ✅ Only send notification when Approved or Rejected
    if status in ['Approved', 'Rejected']:
        message = f"Your hospital blood request for {blood_request.blood_group} has been {status.lower()}."
        Notification.objects.create(
            user=blood_request.user,   # hospital user (receiver)
            sender=request.user,       # admin user (sender)
            message=message
        )

    return redirect('manage_hospital_requests')
@login_required
def hospital_notifications(request):
    from .models import Notification

    # ✅ Filter only notifications related to blood requests
    notifications = Notification.objects.filter(
        user=request.user,
        message__icontains='blood request'  # only messages mentioning “blood request”
    ).order_by('-created_at')

    # Mark all as read when hospital views them
    notifications.update(is_read=True)

    return render(request, 'hopital/hospital_notifications.html', {'notifications': notifications})

from django.http import JsonResponse

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})



@login_required
def admin_dashboard(request):
    # Get all appointment requests
    appointments = Appointment.objects.all().order_by('-created_at')
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Get other dashboard details (optional)
    total_donors = DonorDetail.objects.count()
    total_patients = PatientDetail.objects.count()
    total_hospital = HospitalDetail.objects.count()
    total_requests = appointments.count()

    context = {
        'unread_count': unread_count,
        'total_donors': total_donors,
        'total_patients': total_patients,
        'total_hospital': total_hospital,
        'total_requests': total_requests,
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
def donor_dashboard(request):
    check_and_add_blood_to_stock()
    donor = DonorDetail.objects.filter(user=request.user).first()
    donor_requests = DonationRequest.objects.filter(donor=donor)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    unread_count = unread_notifications.count()

    return render(request, 'donor_dashboard.html', {
        'donor': donor,
        'donor_requests': donor_requests,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count
    })

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
    # ✅ Step 1: Update completed donations before fetching totals
    update_completed_donations()

    # ✅ Step 2: Calculate statistics for dashboard
    total_donors = DonorDetail.objects.count()
    total_patients = PatientDetail.objects.count()
    total_hospital = HospitalDetail.objects.count()
    total_stock_data = BloodStock.objects.aggregate(total_units=Sum('units_available'))
    total_stock = total_stock_data['total_units'] or 0  # handle None case
    total_requests = BloodRequest.objects.all().count()
    pending_count = BloodRequest.objects.filter(status='Pending').count()

    context = {
        'total_donors': total_donors,
        'total_stock': total_stock,
        'total_requests': total_requests,
        'total_patients': total_patients,
        'total_hospital': total_hospital,
        'pending_count': pending_count,
    }

    return render(request, 'partials/admin_dashboard_content.html', context)

def manage_users(request):
    users = User.objects.all().select_related('profile')  # if you have a Profile model linked to User
    return render(request, 'partials/manage_users.html', {'users': users})



from django.db.models import Sum, Q
@login_required
@user_passes_test(is_admin)
def manage_bloodstock(request):
    stock = BloodStock.objects.all()

    blood_group = request.GET.get('blood_group')
    if blood_group:
        stock = stock.filter(blood_group=blood_group)

    hospital = request.GET.get('hospital')
    if hospital:
        stock = stock.filter(hospital_id=hospital)

    hospitals = HospitalDetail.objects.all()

    total_units = stock.values('blood_group').annotate(total=Sum('units_available'))

    return render(request, 'partials/manage_bloodstock.html', {
        'blood_stock': stock,
        'hospitals': hospitals,
        'blood_groups': BloodStock.BLOOD_GROUPS,  # pass this for filter dropdown
        'total_units': total_units
    })

@login_required
def manage_requests(request):
    from .models import Appointment, BloodRequest, HospitalBloodRequest

    # Fetch all donor appointment requests
    appointment_requests = Appointment.objects.all().order_by('-created_at')

    # Fetch all patient blood requests
    patient_requests = BloodRequest.objects.all().order_by('-created_at')

    # Fetch all hospital blood requests
    hospital_requests = HospitalBloodRequest.objects.all().order_by('-required_date')

    return render(request, 'partials/manage_requests.html', {
        'appointment_requests': appointment_requests,
        'patient_requests': patient_requests,
        'hospital_requests': hospital_requests,
    })

import io
import base64
from matplotlib import pyplot as plt
from django.shortcuts import render
from django.db.models import Sum
from .models import BloodStock

def view_reports(request):
    # Normalize blood_group values (trim spaces + uppercase)
    blood_data = (
        BloodStock.objects
        .values_list('blood_group', 'units_available')
    )

    normalized_data = {}
    for bg, units in blood_data:
        clean_bg = bg.strip().upper()  # remove spaces and make uppercase
        normalized_data[clean_bg] = normalized_data.get(clean_bg, 0) + (units or 0)

    # Prepare data for chart
    labels = list(normalized_data.keys())
    sizes = list(normalized_data.values())

    # Create pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        shadow=True
    )
    plt.title('Total Blood Stock by Blood Group')

    # Save chart as image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    plt.close()

    return render(request, 'partials/view_reports.html', {'chart': graphic})

@login_required
def donor_detail_form_view(request):
    try:
        donor_instance = DonorDetail.objects.get(user=request.user)
    except DonorDetail.DoesNotExist:
        donor_instance = None  # Don’t create yet

    if request.method == 'POST':
        form = DonorDetailForm(request.POST, request.FILES, instance=donor_instance)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user  # ensure user is set
            donor.save()
            messages.success(request, "Your details have been updated successfully!")
            return redirect('donor_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
            print(form.errors)  # debug
    else:
        form = DonorDetailForm(instance=donor_instance)

    return render(request, 'donor_detail_form.html', {'form': form})

@login_required
def update_donor_detail_view(request):
    donor_detail, created = DonorDetail.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = DonorDetailForm(request.POST, request.FILES, instance=donor_detail)
        if form.is_valid():
            form.save()
            messages.success(request, "Your donor details have been updated successfully!")
            return redirect('donor_dashboard')  # 👈 Redirect to dashboard after success
    else:
        form = DonorDetailForm(instance=donor_detail)

    return render(request, 'donor/update_donor_detail.html', {'form': form})

from datetime import date

from datetime import timedelta

@login_required
def view_donation_history(request):
    # ✅ Update completed donations automatically
    update_completed_donations()

    donations = Appointment.objects.filter(
        donor=request.user
    ).order_by('-appointment_date')

    for d in donations:
        if d.appointment_date:
            d.next_eligible_date = d.appointment_date + timedelta(days=90)
        else:
            d.next_eligible_date = None

    return render(request, 'donor/view_donation_history.html', {'donations': donations})

@login_required
def check_eligibility(request):
    donor = get_object_or_404(DonorDetail, user=request.user)
    result = None
    status = None

    # Prefill form data
    initial_data = {}
    if donor.age:
        initial_data['age'] = donor.age
    if donor.weight:
        initial_data['weight'] = donor.weight

    last_donation = (
        Appointment.objects.filter(donor=request.user, status='Completed')
        .order_by('-appointment_date')
        .first()
    )

    if last_donation:
        initial_data['first_donation'] = 'no'
        initial_data['last_donation_date'] = last_donation.appointment_date
    else:
        initial_data['first_donation'] = 'yes'

    form = EligibilityForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        age = form.cleaned_data['age']
        weight = form.cleaned_data['weight']
        first_donation = form.cleaned_data['first_donation']
        last_donation_date = form.cleaned_data['last_donation_date']

        # --- Default: Not eligible ---
        donor.is_eligible = False  

        # Age check
        if age < 18 or age > 65:
            result = "❌ You are not eligible due to age restrictions."
            status = "danger"

        # Weight check
        elif weight < 50:
            result = "⚠️ You are not eligible due to low weight."
            status = "warning"

        # Donation gap check
        elif first_donation == 'no' and last_donation_date:
            days_since_last = (date.today() - last_donation_date).days
            if days_since_last < 90:
                next_date = last_donation_date + timedelta(days=90)
                result = f"🕒 You can donate again after {next_date.strftime('%d %B %Y')}."
                status = "warning"
            else:
                donor.is_eligible = True
                donor.save()
                messages.success(request, "✅ You are eligible! You can now request an appointment.")
                return redirect('request_appoiments')

        # First-time donors
        elif first_donation == 'yes':
            donor.is_eligible = True
            donor.save()
            messages.success(
                request,
                "🎉 You are eligible! This is your first donation — thank you for saving lives!"
            )
            return redirect('request_appoiments')

        else:
            result = "⚠️ Please provide valid information to check eligibility."
            status = "warning"

        # Save updated data
        donor.age = age
        donor.weight = weight
        donor.save()

    return render(
        request,
        'donor/check_eligibility.html',
        {'form': form, 'result': result, 'status': status, 'donor': donor}
    )


from datetime import date, datetime
from datetime import date, timedelta

# Eligibility check function
def is_donor_eligible(donor):
    """
    Returns True if donor is eligible based on last completed donation.
    """
    last_donation = Appointment.objects.filter(donor=donor, status='Completed').order_by('-donation_date').first()
    if not last_donation:
        return True  # First-time donor → eligible

    required_gap = 90  # days
    next_eligible_date = last_donation.donation_date + timedelta(days=required_gap)
    return date.today() >= next_eligible_date


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

from .models import PatientDetail

@login_required
def request_blood(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.user = request.user
            patient = PatientDetail.objects.get(user=request.user)
            blood_request.full_name = request.user.get_full_name() or request.user.username
            blood_request.blood_group = patient.blood_group
            blood_request.status = "Pending"
            blood_request.save()

            # Notify all admins/staff
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    message=f"🩸 New blood request from {request.user.username}."
                )

            messages.success(request, "Your blood request has been submitted successfully!")
            return redirect('patient_dashboard')
    else:
        form = BloodRequestForm()

    return render(request, 'patient/blood_request.html', {'form': form})

@login_required
def request_status(request):
    # Fetch blood requests of the logged-in user
    blood_requests = BloodRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'patient/request_status.html', {'blood_requests': blood_requests})

@login_required
def edit_patient_profile(request):
    # Get existing patient details if they exist
    patient_instance = getattr(request.user, 'patientdetail', None)

    if request.method == 'POST':
        form = PatientDetailForm(request.POST, request.FILES, instance=patient_instance)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientDetailForm(instance=patient_instance)

    return render(request, 'patient/edit_patient_profile.html', {'form': form})


@user_passes_test(is_admin)
def admin_manage_requests(request):
    blood_requests = BloodRequest.objects.all().order_by('-created_at')
    return render(request, 'admin/manage_requests.html', {'blood_requests': blood_requests})

@login_required
@user_passes_test(is_admin)
def update_request_status(request, request_id, action):
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if action == 'approve':
        blood_request.status = 'Approved'
        blood_request.save()

        Notification.objects.create(
            sender=request.user,  # Admin who approves
            user=blood_request.user,  # Patient who receives notification
            message=f"✅ Your blood request (for {blood_request.blood_group}) has been approved."
        )
        messages.success(request, "Request approved successfully.")

    elif action == 'reject':
        blood_request.status = 'Rejected'
        blood_request.save()

        Notification.objects.create(
            sender=request.user,  # Admin
            user=blood_request.user,  # Patient
            message=f"❌ Your blood request (for {blood_request.blood_group}) has been rejected."
        )
        messages.error(request, "Request rejected successfully.")

    return redirect('manage_requests')


@login_required
def view_notifications(request):
    user = request.user
    print("🔍 Logged in as:", request.user.username)
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    
    

    # Mark unread notifications as read
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'patient/notification.html', {'notifications': notifications})


@login_required
def view_notifications_donor(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # 🔴 Mark all unread notifications as read
    unread_notifications = notifications.filter(is_read=False)
    if unread_notifications.exists():
        unread_notifications.update(is_read=True)

    return render(request, 'donor/view_notifications.html', {'notifications': notifications})


@login_required
def view_profile(request):
    user = request.user
    try:
        donor = user.donordetail  # For donors
    except:
        donor = None

    context = {
        'user': user,
        'donor': donor,
    }
    return render(request, 'view_profile.html', context)

@login_required
@user_passes_test(is_admin)
def add_blood_stock(request):
    if request.method == "POST":
        form = BloodStockForm(request.POST)
        if form.is_valid():
            blood_stock = form.save(commit=False)
            
            # Automatically assign hospital if the admin is linked to one
            if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'hospital'):
                blood_stock.hospital = request.user.profile.hospital
            else:
                blood_stock.hospital = None  # optional, depends on your model
            
            blood_stock.save()
            messages.success(request, "Blood stock added successfully!")
            return redirect('manage_bloodstock')
    else:
        form = BloodStockForm()
    
    return render(request, 'partials/add_blood_stock.html', {'form': form})

def is_hospital(user):
    return hasattr(user, 'profile') and user.profile.role == 'hospital'

@login_required
@user_passes_test(is_hospital)
def hospital_bloodstock(request):
    if request.method == "POST":
        form = HospitalBloodStockForm(request.POST)
        print("🩸 POST data:", request.POST)

        if form.is_valid():
            blood_stock = form.save(commit=False)
            try:
                hospital = HospitalDetail.objects.get(user=request.user)
                blood_stock.hospital = hospital  # ✅ set hospital automatically
                blood_stock.save()
                messages.success(request, "✅ Blood stock added successfully!")
                return redirect('hospital_dashboard')
            except HospitalDetail.DoesNotExist:
                messages.error(request, "⚠️ No hospital profile found for this user.")
        else:
            print("🩸 Form errors:", form.errors)
            messages.error(request, "❌ Invalid form data.")
    else:
        form = HospitalBloodStockForm()

    return render(request, 'hopital/hospital_bloodstock.html', {'form': form})



@login_required
def view_blood_stock(request):
    stocks = BloodStock.objects.all()
    return render(request, 'hopital/view_blood_stock.html', {'stocks': stocks})

@login_required
def hospital_request_blood(request):
    try:
        hospital = HospitalDetail.objects.get(user=request.user)
    except HospitalDetail.DoesNotExist:
        messages.error(request, "Hospital details not found for this user.")
        return redirect('hospital_detail_form')

    if request.method == 'POST':
        form = HospitalBloodRequestForm(request.POST)
        if form.is_valid():
            hospital_request = form.save(commit=False)
            hospital_request.hospital_name = hospital
            hospital_request.user = request.user  # ✅ link user too
            hospital_request.save()
            messages.success(request, "Blood request sent successfully!")
            return redirect('hospital_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = HospitalBloodRequestForm()

    return render(request, 'hopital/hospital_request_blood.html', {'form': form})

@login_required
def hospital_request_history(request):
    try:
        hospital = HospitalDetail.objects.get(user=request.user)
    except HospitalDetail.DoesNotExist:
        messages.error(request, "Hospital details not found for this user.")
        return redirect('hospital_dashboard')

    requests = HospitalBloodRequest.objects.filter(hospital_name=hospital).order_by('-requested_at')
    return render(request, 'hopital/hospital_request_history.html', {'requests': requests})

@login_required
def reports(request):
    return render(request, 'reports.html')

def is_hospital(user):
    return hasattr(user, 'profile') and user.profile.role == 'hospital'
# from pyecharts.charts import Pie
# from pyecharts import options as opts
# from pyecharts.globals import CurrentConfig


@login_required
def hospital_dashboard_content(request):
    hospital = HospitalDetail.objects.filter(user=request.user).first()
    blood_stocks = HospitalBloodStock.objects.filter(hospital=hospital)

    labels = [stock.blood_group for stock in blood_stocks]
    values = [stock.units_available for stock in blood_stocks]

    chart_uri = None

    if labels and values:
        # Create a matplotlib figure
        plt.figure(figsize=(6, 4))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"{hospital.hospital_name} - Blood Stock Distribution")

        # Save the chart to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode the image to base64
        chart_uri = base64.b64encode(image_png).decode('utf-8')
        plt.close()
    else:
        chart_uri = None

    return render(request, "hopital/hospital_dashboard_content.html", {
        "hospital": hospital,
        "chart_uri": chart_uri,
        "blood_stocks": blood_stocks,
    })


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            # Save user info
            form.save()
            
            # Save profile info
            profile.full_name = form.cleaned_data['full_name']
            profile.role = form.cleaned_data['role']
            profile.save()

            messages.success(request, "User updated successfully!")
            return redirect('/admin_dashboard/?section=manage_users&msg=User+updated+successfully!')
    else:
        form = UserForm(
            instance=user,
            initial={
                'full_name': profile.full_name,
                'role': profile.role
            }
        )

    return render(request, 'partials/edit_user.html', {'form': form})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('manage_users')

@login_required
def received_history(request):
    received_requests = BloodRequest.objects.filter(
        user=request.user, status='Approved'
    ).order_by('-created_at')

    context = {
        'received_requests': received_requests
    }
    return render(request, 'patient/received_history.html', context)

@login_required
def search_blood(request):
    blood_group = request.GET.get('blood_group')
    location = request.GET.get('location')

    results = BloodStock.objects.select_related('hospital')

    if blood_group:
        results = results.filter(blood_group=blood_group)
    if location:
        results = results.filter(hospital__address__icontains=location)

    context = {
        'results': results,
        'blood_group': blood_group,
        'location': location,
    }
    return render(request, 'patient/search_blood.html', context)

def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = status
    appointment.save()

    # ✅ If admin accepts, send notification to donor
    if status == "Accepted":
        message = (
            f"Your blood donation appointment has been accepted by "
            f"{appointment.hospital.hospital_name}. "
            f"Please donate blood on {appointment.appointment_date} at {appointment.appointment_time}."
        )
    elif status == "Rejected":
        message = (
            f"Your blood donation appointment request at "
            f"{appointment.hospital.hospital_name} has been rejected."
        )
    else:
        message = f"Your appointment request status changed to {status}."

    # ✅ Create Notification for donor
    Notification.objects.create(
        user=appointment.donor,
        message=message
    )

    messages.success(request, f"Appointment status updated to {status}.")
    return redirect('manage_requests')

@login_required
@user_passes_test(is_admin)
def update_patient_status(request, request_id, status):
    req = get_object_or_404(BloodRequest, id=request_id)
    req.status = status
    req.save()

    # ✅ Create notification for the patient
    if status == 'Accepted':
        Notification.objects.create(
            sender=request.user,  # admin who approved
            user=req.user,        # patient who made the request
            message=f"✅ Your blood request (for {req.blood_group}) has been approved."
        )
    elif status == 'Rejected':
        Notification.objects.create(
            sender=request.user,
            user=req.user,
            message=f"❌ Your blood request (for {req.blood_group}) has been rejected."
        )

    messages.success(request, f"Patient request marked as {status}.")
    return redirect('manage_requests')


def update_hospital_status(request, request_id, status):
    req = get_object_or_404(HospitalBloodRequest, id=request_id)
    req.status = status
    req.save()
    messages.success(request, f"Hospital request marked as {status}.")
    return redirect('manage_requests')

@login_required
@user_passes_test(is_admin)
def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        donation_date = request.POST.get('donation_date')
        donation_time = request.POST.get('donation_time')

        # Set appointment status to 'Date Sent' and save the donation date and time
        appointment.appointment_date = donation_date
        appointment.appointment_time = donation_time
        appointment.status = 'Approved'
        appointment.save()

        # Create a notification for the donor about the scheduled donation date
        Notification.objects.create(
            user=appointment.donor,
            message=f"🩸 Your donation is scheduled on {donation_date} at {appointment.hospital.hospital_name}. Please confirm your availability."
        )

        messages.success(request, "Donation date sent to donor successfully!")
        
        # Redirect to the manage requests page after successful operation
        return redirect('manage_requests')

    # If the request method is GET, show the form for setting the donation date
    return render(request, 'partials/approve_appointment.html', {'appointment': appointment})

from django.http import HttpResponse


@login_required
def respond_to_appointment(request, appointment_id, response):
    # Fetch the appointment associated with the current user
    appointment = get_object_or_404(Appointment, id=appointment_id, donor=request.user)

    # Handle donor's response (accept or reschedule)
    if response == 'accept':  # Donor accepts the scheduled date
        appointment.donor_response = 'Accepted'
        appointment.status = 'Confirmed'  # Appointment status is set to Confirmed
        appointment.save()

        # Notify the admin about the acceptance
        Notification.objects.create(
            user=appointment.hospital.user,
            message=f"✅ Donor {request.user.username} confirmed the donation on {appointment.appointment_date}."
        )
        messages.success(request, "You have confirmed the donation date.")
    
    elif response == 'reschedule':  # Donor requests to reschedule the appointment
        appointment.donor_response = 'Reschedule'
        appointment.status = 'Pending'  # Back to 'Pending' status
        appointment.save()

        # Notify the admin about the request for another date
        Notification.objects.create(
            user=appointment.hospital.user,
            message=f"🔄 Donor {request.user.username} requested to reschedule the donation date."
        )
        messages.warning(request, "You requested a new date. Admin will update soon.")
    
    # Redirect back to donor dashboard after response
    return redirect('donor_dashboard')

@login_required
@user_passes_test(is_admin)
def mark_donation_completed(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # ✅ Allow completion only if Approved and scheduled time has passed
    if appointment.status == 'Approved':
        now = timezone.localtime()
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )
        appointment_datetime = timezone.make_aware(appointment_datetime)

        # ⚠️ Check both date and time
        if now >= appointment_datetime:
            donor = appointment.donor
            hospital = appointment.hospital
            donor_detail = donor.donordetail

            # ✅ Update or create blood stock record
            blood_stock, _ = BloodStock.objects.get_or_create(
                hospital=hospital,
                blood_group=donor_detail.blood_group,
                defaults={'units_available': 0}
            )

            # Convert blood_units (ml) to stock units (1 unit ≈ 350 ml)
            donated_units = round(appointment.blood_units / 350, 2)
            blood_stock.units_available += donated_units
            blood_stock.save()

            # ✅ Update appointment
            appointment.status = 'Completed'
            appointment.donation_date = timezone.now().date()
            appointment.save()

            # ✅ Notify donor
            Notification.objects.create(
                user=donor,
                message=(
                    f"🎉 Thank you for donating {appointment.blood_units} ml of blood "
                    f"on {appointment.appointment_date}! Your donation has been recorded."
                )
            )

            messages.success(request, "✅ Donation marked as completed and added to blood stock.")
        else:
            # If the appointment time hasn't passed yet
            messages.warning(
                request,
                f"⏰ You can only mark this as completed after "
                f"{appointment.appointment_date} {appointment.appointment_time.strftime('%I:%M %p')}."
            )
    else:
        messages.error(request, "⚠️ You can only mark as completed if the status is 'Approved'.")

    return redirect('manage_requests')

    
@login_required
def manage_hospital_requests(request):
    requests = HospitalBloodRequest.objects.all().order_by('-requested_at')
    return render(request, 'partials/manage_hospital_requests.html', {'requests': requests})

@login_required
def update_hospital_status(request, request_id, status):
    blood_request = HospitalBloodRequest.objects.get(id=request_id)
    blood_request.status = status
    blood_request.save()

    # ✅ Create notification for hospital
    from .models import Notification
    message = f"Your hospital blood request for {blood_request.blood_group} has been {status.lower()}."
    Notification.objects.create(user=blood_request.user, message=message)

    return redirect('manage_hospital_requests')


def donor_accept_date(request, request_id):
    donor_request = get_object_or_404(DonationRequest, id=request_id)
    donor_request.status = "donor_confirmed"
    donor_request.save()
    messages.success(request, "You have confirmed your donation date.")
    return redirect('donor_dashboard')

def donor_reject_date(request, request_id):
    donor_request = get_object_or_404(DonationRequest, id=request_id)
    donor_request.status = "date_rejected"
    donor_request.save()
    messages.warning(request, "You have requested another date. Admin will update soon.")
    return redirect('donor_dashboard')

def approve_request(request, request_id):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        blood_request.status = 'Approved'
        blood_request.save()
        return redirect(request.META.get('HTTP_REFERER', 'manage_requests'))
    
def approve_donation_request(request, request_id):
    donor_request = DonationRequest.objects.get(id=request_id)
    if request.method == 'POST':
        donation_date = request.POST.get('donation_date')
        donor_request.status = 'approved'
        donor_request.donation_date = donation_date
        donor_request.save()
        messages.success(request, "Donation date assigned successfully.")
        return redirect('manage_donor_requests')

    return render(request, 'admin/assign_donation_date.html', {'donor_request': donor_request})

from django.utils import timezone
def check_and_add_blood_to_stock():
    # Fetch appointments where the donation date has passed and the status is 'Date Sent'
    appointments = Appointment.objects.filter(donation_date__lte=timezone.now().date(), status="Date Sent")
    
    for appointment in appointments:
        # If the donation date is passed and the appointment status is "Date Sent"
        if appointment.donation_date <= timezone.now().date() and appointment.status == "Date Sent":
            # Update the appointment status to "Completed"
            appointment.status = "Completed"
            appointment.save()

            # Add blood to the blood stock for the hospital
            blood_stock, created = BloodStock.objects.get_or_create(
                hospital=appointment.hospital, 
                blood_group=appointment.donor.donordetail.blood_group,
                defaults={'units_available': 0}  # Default value if stock doesn't exist
            )

            # Increase the units available in the blood stock
            blood_stock.units_available += 1
            blood_stock.save()

            # Optional: Create a notification for the donor about the successful donation
            Notification.objects.create(
                user=appointment.donor,
                message=f"🎉 Thank you for donating blood on {appointment.donation_date}! Your donation has been recorded."
            )

    return redirect('donor_dashboard')  # Redirect to donor dashboard or any other page

from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_admin(request):
    admin_user = request.user
    notifications = Notification.objects.filter(user=admin_user).order_by('-created_at')

    # ✅ Mark all unread notifications as read
    notifications.filter(is_read=False).update(is_read=True)

    unread_count = 0  # Since we just marked them all read

    return render(
        request,
        'partials/notification_admin.html',
        {
            'notifications': notifications,
            'unread_count': unread_count,
        },
    )





@login_required
def create_appointment(request):
    if request.method == 'POST':
        # assume form handling here
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = request.user
            appointment.save()

            # Create notification for admin
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    message=f"New blood request from {request.user.username}."
                )


            messages.success(request, "Appointment request submitted successfully!")
            return redirect('donor_dashboard')
    else:
        form = AppointmentForm()

    return render(request, 'appointment_form.html', {'form': form})

# hospital blood stock
@login_required
def hospital_edit_profile(request):
    hospital = HospitalDetail.objects.get(user=request.user)
    if request.method == 'POST':
        form = HospitalDetailForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('hospital_dashboard')
    else:
        form = HospitalDetailForm(instance=hospital)
    
    return render(request, 'hospital_detail_form.html', {'form': form})

# new       new            new               new

@login_required
def request_appointment(request):
    hospitals = HospitalDetail.objects.all()
    today = date.today().isoformat()

    donor = DonorDetail.objects.filter(user=request.user).first()
    eligible = donor.is_eligible if donor else False

    # 🚫 Restrict if next eligible date is in the future
    if donor and donor.next_eligible_date and donor.next_eligible_date > date.today():
        messages.warning(
            request,
            f"⏳ You can donate again only after {donor.next_eligible_date}."
        )
        return redirect('donor_dashboard')

    # Fetch last completed donation
    last_donation = (
        Appointment.objects.filter(donor=request.user, status='Completed')
        .order_by('-appointment_date')
        .first()
    )

    first_time_donor = not bool(last_donation)
    last_donation_date = last_donation.appointment_date if last_donation else None

    if request.method == "POST":
        if not eligible:
            messages.error(request, "❌ You must check your eligibility before requesting an appointment.")
            return redirect('check_eligibility')

        hospital_id = request.POST.get("hospital")
        preferred_date = request.POST.get("appointment_date")
        preferred_time = request.POST.get("appointment_time")
        blood_units = int(request.POST.get("blood_units"))
        notes = request.POST.get("notes")

        if blood_units < 350 or blood_units > 470:
            messages.error(request, "❌ Blood volume must be between 350ml and 470ml.")
            return redirect('request_appoiments')

        Appointment.objects.create(
            donor=request.user,
            hospital_id=hospital_id,
            appointment_date=preferred_date,
            appointment_time=preferred_time,
            blood_units=blood_units,
            notes=notes,
            status='Pending'
        )

        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            Notification.objects.create(
                sender=request.user,
                user=admin_user,
                message=f"🩸 New donation appointment request from {request.user.username}."
            )

        messages.success(request, "✅ Appointment request sent to admin successfully!")
        return redirect('donor_dashboard')

    return render(request, 'donor/request_appoiment.html', {
        'hospitals': hospitals,
        'today': today,
        'eligible': eligible,
        'first_time_donor': first_time_donor,
        'last_donation_date': last_donation_date,
    })
@login_required
@user_passes_test(is_admin)
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Rejected'
    appointment.save()

    Notification.objects.create(
        user=appointment.donor,
        message=f"❌ Your appointment at {appointment.hospital.hospital_name} has been rejected by admin."
    )

    messages.warning(request, "Appointment rejected successfully.")
    return redirect('manage_requests')

@login_required
def assign_donation_date(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    today = timezone.localdate().strftime('%Y-%m-%d')

    if request.method == 'POST':
        date_str = request.POST.get('donation_date')
        time_str = request.POST.get('donation_time')

        # 🕓 Combine date + time
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            selected_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('assign_donation_date', appointment_id)

        selected_datetime = datetime.combine(selected_date, selected_time)
        selected_datetime = timezone.make_aware(selected_datetime)
        now = timezone.localtime()

        print("DEBUG: selected =", selected_datetime, "now =", now)  # 🧠 check what Django sees

        # 🚫 Validate future datetime
        if selected_datetime <= now:
            messages.error(request, "You cannot assign a past date or time.")
            return redirect('assign_donation_date', appointment_id)

        # ✅ Save valid appointment
        appointment.appointment_date = selected_date
        appointment.appointment_time = selected_time
        appointment.status = 'Date Sent'
        appointment.donor_response = 'No Response'
        appointment.save()

        # 🩸 Send notification
        Notification.objects.create(
            sender=request.user,
            user=appointment.donor,
            appointment=appointment,
            message=f"🩸 {appointment.hospital.hospital_name} assigned a donation date: {date_str} at {time_str}."
        )

        messages.success(request, "Donation date and time assigned successfully.")
        return redirect('manage_requests')

    return render(request, 'partials/assign_donation_date.html', {
        'appointment': appointment,
        'today': today
    })
    
@login_required
def respond_to_donation_date(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, donor=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            appointment.status = 'Approved'
            appointment.donor_response = 'Accepted'
            appointment.save()

            Notification.objects.create(
                user=appointment.hospital.user,
                message=f"✅ {appointment.donor.username} accepted the donation date."
            )

        elif action == 'reschedule':
            appointment.status = 'Pending'
            appointment.donor_response = 'Reschedule Requested'
            appointment.save()

            Notification.objects.create(
                user=appointment.hospital.user,
                message=f"🔄 {appointment.donor.username} requested to reschedule the donation."
            )

    return redirect('donor_dashboard')

from datetime import timedelta

def update_completed_donations():
    now = timezone.localtime()

    past_appointments = []
    for app in Appointment.objects.filter(status='Approved'):
        if not app.appointment_date or not app.appointment_time:
            continue

        appointment_datetime = timezone.make_aware(datetime.combine(
            app.appointment_date,
            app.appointment_time
        ))

        if appointment_datetime <= now:
            past_appointments.append(app)

    for app in past_appointments:
        donor_detail = DonorDetail.objects.filter(user=app.donor).first()
        if not donor_detail:
            continue

        stock, _ = BloodStock.objects.get_or_create(
            hospital=None,
            blood_group=donor_detail.blood_group,
            defaults={'units_available': 0}
        )

        donated_units = max(1, app.blood_units // 350)
        stock.units_available += donated_units
        stock.save()

        app.status = 'Completed'
        app.save()

        # ✅ Set next eligible date = 90 days after this donation
        donor_detail.next_eligible_date = app.appointment_date + timedelta(days=90)
        donor_detail.save()

        Notification.objects.create(
            user=app.donor,
            message=(
                f"🎉 Thank you for donating {app.blood_units} ml on {app.appointment_date} at {app.appointment_time}! "
                f"You can donate again after {donor_detail.next_eligible_date}."
            )
        )

