from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from sensors.forms import PatientCreationForm, CareGroupCreationForm, SignUpForm, DataForm, DeviceCreationForm, LoginForm
from django.contrib.auth.password_validation import validate_password
from django.template import RequestContext
from sensors.models import CareGroup, Patient, User, Data, Device # import custom user model
from django.core import serializers
import logging
from django.contrib.auth.views import LoginView
logger = logging.getLogger(__name__)

# This does nothing right now. Oops.
# TODO: actually do this
def handler403(request, *args, **argv):
    response = render_to_response('errors/403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response


def index(request, *args, **kwargs):
    return render(request, "index/index.html", {})

# TEMPORARY
def get_data(request, *args, **kwargs):
    return render(request, 'charts.html', {});

def dashboard(request, *args, **kwargs):
    user = request.user
    patients=Patient.objects.none()
    active_caregroup={}
    caregroups = user.caregroups.all()
    #print("DASHBOARD CAREGROUPS:")
    #print(caregroups)
    if(user.active_caregroup != None):
        patients = Patient.objects.filter(caregroup = user.active_caregroup)
        active_caregroup = user.active_caregroup

    return render(request, "dashboard/dashboard.html", {'patients':patients, 'user':user, 'active_caregroup':active_caregroup, 'caregroups':caregroups})

# used to retrieve caregroup data for changing dashboard view between caregroups for signed in user
def ajax_change_caregroup(request):
    print("CAREGROUP ID:") # new caregroup
    print(request.GET.get('caregroup', False))
    caregroup_id = request.GET.get('caregroup', False) # access caregroup
    user = request.user
    user.active_caregroup=CareGroup.objects.get(id=caregroup_id) # switch user active caregroup
    user.save()
    try:
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False})
    return JsonResponse(data)

# returns patient temperature, humidity data from table in postgres
def ajax_get_patient_data(request):
    print("FLAG0")
    patient_id = request.GET.get('patient_id', False) # get patient id for lookup of values in sensors_data table
    #print("PATIENT ID:")  # debug check patient
    #print(patient_id)
    patient_data = Data.objects.order_by('time').filter(patient_id=patient_id)[:180] # Contains a list of 'Data' Django objects
    patient_data = serializers.serialize('json', patient_data) # import Django rest framework to allow serialization of django objects to JSON

    return HttpResponse(patient_data, content_type="application/json")


def ajax_update_patient_status(request):
    device_id = 1 # Hardcoded for now since we only have 1 device
    data = Data.objects.order_by('time').filter(device_id=device_id)
    data = serializers.serialize('json', data)

    return HttpResponse(data, content_type="application/json")


# TODO: make this work properly, currently doesn't seem to actually get used at all.
# I think the problem is that the default Django login stuff is getting used instead, but I'm not really sure how
# to fix that. Supposed to set cookie to expire after browser close if remember me isn't checked.
#class LoginUser(LoginView):
   # form_class = LoginForm

    '''def get_success_url(self):
        request = self.request.GET
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)
        url = self.get_redirect_url()
        return url
        '''


def add_patient(request, *args, **kwargs):
    # If the form has been submitted
    if request.method == 'POST':
        user = request.user
        caregroup = user.active_caregroup
        form = PatientCreationForm(request.POST) # Form bound to POST data
        if form.is_valid(): # If the form passes all validation rules
            print("Patient Form Valid")
            patient = form.save()
            patient.caregroup = caregroup
            patient.save()
            return(redirect('dashboard')) # Redirect to the dashboard (TODO: change redirect location?)
    else:
        form = PatientCreationForm() # Unbound form
    return render(request, 'registration/addpatient.html', { 'form': form })


def add_device(request):
    if request.method == 'POST':
        user = request.user
        caregroup = user.active_caregroup
        form = DeviceCreationForm(request.POST) # Form bound to POST data
        if form.is_valid():  # If the form passes all validation rules
            device = form.save()
            device.caregroup=caregroup
            device.save()
            return(redirect('dashboard'))  # Redirect to the dashboard (TODO: change redirect location?)
    else:
        form = DeviceCreationForm() # Unbound form
    return render(request, 'registration/adddevice.html', { 'form': form })


def add_care_group(request):
    if request.method == 'POST':
        form = CareGroupCreationForm(request.POST)
        if form.is_valid():
            validate_password(form.cleaned_data.get('password'))  # Ensure password is strong enough
            form.validate()  # Ensure password matches password_confirmation
            caregroup=form.save()  # Save the form
            user = request.user # get current user
            caregroup.users.add(user) # add user to caregroup internal list
            user.active_caregroup = caregroup
            user.caregroups.add(caregroup)
            user.save()
            return redirect('dashboard')  # Redirect to the dashboard TODO: Add confirmation that group was added
    else:
        form = CareGroupCreationForm()
    return render(request, 'registration/addcaregroup.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("Signup Form Valid")
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        print("Signup Form Invalid")
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def receive_data(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            form.save()
            # Update the patient's status
            event = data.get('event')
            event = int(event)
            device_id = data.get('device')
            patient = Patient.objects.get(device_id=device_id)
            if event == 2:
                patient.status = 'd'
                patient.save()
            else:
                patient.status = 'c'
                patient.save()
            return HttpResponse("We got your data!")
    else:
        form = DataForm()
    print("FLAG!!!")
    print(request)
    return render(request, 'data/data.html', {'form': form})
