from .models import Profile
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from .models import User
from .models import Donation
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import ContactForm,BloodRequest
from .forms import BloodRequestForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.urls import reverse
from .models import Branch, Appointment


from .models import Profile, DonorDetail, PatientDetail, HospitalDetail, User, ContactMessage,Notification,BloodStock,Donation,HospitalBloodRequest
from .forms import LoginForm, UserForm, ContactForm, DonorDetailForm, PatientDetailForm, HospitalDetailForm,EligibilityForm,BloodStockForm,HospitalBloodRequestForm


from blood_bank_app.forms import LoginForm,UserForm
from django.contrib.auth.decorators import user_passes_test


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

    context = {
        'hospital': hospital,
        'blood_stocks': blood_stocks,
        'requests': requests,
        'total_requests': requests.count(),
        'pending_requests': requests.filter(status='Pending').count(),
        'approved_requests': requests.filter(status='Approved').count(),
    }

    return render(request, 'hospital_dashboard.html', context)



@login_required
def admin_dashboard(request):
    # Get all appointment requests
    appointments = Appointment.objects.all().order_by('-created_at')

    # Get other dashboard details (optional)
    total_donors = DonorDetail.objects.count()
    total_patients = PatientDetail.objects.count()
    total_hospital = HospitalDetail.objects.count()
    total_requests = appointments.count()

    context = {
        'appointments': appointments,
        'total_donors': total_donors,
        'total_patients': total_patients,
        'total_hospital': total_hospital,
        'total_requests': total_requests,
    }

    return render(request, 'admin_dashboard.html', context)

    

@login_required
def donor_dashboard(request):
    donor = DonorDetail.objects.filter(user=request.user).first()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'donor_dashboard.html', {
        'donor': donor,
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

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'
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






def view_donation_history(request):
    donations = Donation.objects.filter(donor=request.user).order_by('-date')
    return render(request,'donor/view_donation_history.html',{'donations':donations})




from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from .forms import EligibilityForm

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
                # ✅ Eligible → Redirect to Donor Dashboard with success message
                messages.success(request, "✅ You are eligible to donate blood! Proceed to request an appointment.")
                return redirect(reverse('donor_dashboard') + "?section=request_appoiments")

        else:
            result = "⚠️ Please correct the errors and try again."
            status = "warning"

    return render(request, 'donor/check_eligibility.html', {
        'form': form,
        'result': result,
        'status': status
    })

    
@login_required
def request_appointment(request):
    hospitals = HospitalDetail.objects.all()

    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        hospital_id = request.POST.get('hospital')
        notes = request.POST.get('notes')

        if not hospital_id:
            messages.error(request, "Please select a hospital.")
            return redirect('request_appointment')

        hospital = HospitalDetail.objects.get(id=hospital_id)

        Appointment.objects.create(
            donor=request.user,
            hospital=hospital,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            status='Pending'
        )

        messages.success(request, "Appointment request sent successfully! Waiting for admin approval.")
        return redirect('donor_dashboard')

    return render(request, 'donor/request_appoiment.html', {'hospitals': hospitals})



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

def request_blood(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.user = request.user  # ✅ assign logged-in user here
            blood_request.save()
            messages.success(request, 'Your blood request has been submitted successfully!')
            return redirect('request_status')  # redirect to status page
    else:
        form = BloodRequestForm()

    return render(request, 'patient/blood_request.html', {'form': form})
@login_required
def request_status(request):
    # Fetch blood requests of the logged-in user
    blood_requests = BloodRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'patient/request_status.html', {'blood_requests': blood_requests})

def received_history(request):
    # For now, a placeholder template
    return render(request, 'patient/received_history.html')
def search_blood(request):
    # Placeholder page for now
    return render(request, 'patient/search_blood.html')
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


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

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
            user=blood_request.user,
            message=f"✅ Your blood request (for {blood_request.blood_group}) has been approved."
        )
        messages.success(request, "Request approved successfully.")

    elif action == 'reject':
        blood_request.status = 'Rejected'
        blood_request.save()

        Notification.objects.create(
            user=blood_request.user,
            message=f"❌ Your blood request (for {blood_request.blood_group}) has been rejected."
        )
        messages.error(request, "Request rejected successfully.")

    return redirect('manage_requests')


@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # mark all as read when opened
    notifications.update(is_read=True)

    return render(request, 'patient/notification.html', {'notifications': notifications})

@login_required
def view_notifications_donor(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
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



# views.py
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
@login_required
def hospital_dashboard_content(request):
    hospital = HospitalDetail.objects.get(user=request.user)
    return render(request, 'hopital/hospital_dashboard_content.html', {'hospital': hospital})

from .forms import UserEditForm
from django.http import HttpResponse,JsonResponse
from django.template.loader import render_to_string

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

from .models import Notification

@login_required
def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = status
    appointment.save()

    # ✅ When accepted, create donation record and update stock
    if status == "Accepted":
        # 1️⃣ Create a new Donation record
        Donation.objects.create(
            donor=appointment.donor,
            hospital=appointment.hospital,
            date=appointment.appointment_date,
            blood_group=appointment.donor.donordetail.blood_group,
            units=1  # assuming 1 unit donated; adjust if needed
        )

        # 2️⃣ Update hospital's blood stock
        blood_stock, created = BloodStock.objects.get_or_create(
            hospital=appointment.hospital,
            blood_group=appointment.donor.donordetail.blood_group,
            defaults={'units_available': 0}
        )
        blood_stock.units_available += 1
        blood_stock.save()

        # 3️⃣ Notify donor
        Notification.objects.create(
            user=appointment.donor,
            message=f"✅ Your appointment with {appointment.hospital.hospital_name} "
                    f"on {appointment.appointment_date} has been accepted. "
                    f"Thank you for donating blood!"
        )

        messages.success(request, "Appointment accepted and donation recorded successfully.")

    elif status == "Rejected":
        Notification.objects.create(
            user=appointment.donor,
            message=f"❌ Your appointment with {appointment.hospital.hospital_name} has been rejected."
        )
        messages.error(request, "Appointment rejected.")

    return redirect('manage_requests')



def update_patient_status(request, request_id, status):
    req = get_object_or_404(BloodRequest, id=request_id)
    req.status = status
    req.save()
    messages.success(request, f"Patient request marked as {status}.")
    return redirect('manage_requests')

def update_hospital_status(request, request_id, status):
    req = get_object_or_404(HospitalBloodRequest, id=request_id)
    req.status = status
    req.save()
    messages.success(request, f"Hospital request marked as {status}.")
    return redirect('manage_requests')


from .models import Appointment, Notification

def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Approved'
    appointment.save()

    # ✅ Create notification for donor
    Notification.objects.create(
        user=appointment.donor,
        message=f"✅ Your appointment at {appointment.hospital.hospital_name} on {appointment.appointment_date} has been approved by the admin."
    )

    return redirect('manage_requests')


def reject_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    appointment.status = 'Rejected'
    appointment.save()

    Notification.objects.create(
        user=appointment.donor,
        message=f"❌ Your appointment at {appointment.hospital.hospital_name} has been rejected."
    )
    



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
