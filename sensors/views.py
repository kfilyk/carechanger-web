from django.shortcuts import render, redirect
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
from datetime import datetime
logger = logging.getLogger(__name__)

# This does nothing right now. Oops.
# TODO: actually do this
def handler403(request, *args, **argv):
    response = render('errors/403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response

def index(request, *args, **kwargs):
    return render(request, "index/index.html", {})

# TEMPORARY
def get_data(request, *args, **kwargs):
    return render(request, 'charts.html', {})

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

# returns patient temperature, humidity data from table in postgres
# used by get_patient_data function in sensors.js
#

def ajax_get_patient_data(request):
    print("FLAG0")
    patient_id = request.GET.get('patient_id', False) # get patient id for lookup of values in sensors_data table
    #print("PATIENT ID:")  # debug check patient
    #print(patient_id)
    patient_data = Data.objects.filter(patient_id=patient_id).order_by('-time')[:180] # Contains a list of 'Data' Django objects.. order by descending timestamp vals to ensure the most recent rows are used
    patient_data = serializers.serialize('json', patient_data) # import Django rest framework to allow serialization of django objects to JSON

    return HttpResponse(patient_data, content_type="application/json")


def ajax_get_patient(request):
    print("FLAG0")
    patient_id = request.GET.get('patient_id', False) # get patient id for lookup of values in sensors_data table
    #print("PATIENT ID:")  # debug check patient
    #print(patient_id)
    patient = Patient.objects.filter(id=patient_id) # Contains a list of 'Patient' Django objects
    patient = serializers.serialize('json', patient) # import Django rest framework to allow serialization of django objects to JSON

    return HttpResponse(patient, content_type="application/json")

# I have no idea what this does currently... cant find its originating class function. Note to document this when I do figure it out
def ajax_update_patient_status(request):
    device_id = 1 # Hardcoded for now since we only have 1 device
    data = Data.objects.order_by('time').filter(device_id=device_id)
    data = serializers.serialize('json', data)

    return HttpResponse(data, content_type="application/json")

def ajax_set_patient_status_clean(request):
    patient_id = request.GET.get('patient_id', False) # get patient id for lookup of values in sensors_data table
    patient = Patient.objects.get(id=patient_id)
    #print("FLAG!")
    #print(patient.status)
    patient.status='c'
    patient.save()

# TODO: make this work properly, currently doesn't seem to actually get used at all.
# I think the problem is that the default Django login stuff is getting used instead, but I'm not really sure how
# to fix that. Supposed to set cookie to expire after browser close if remember me isn't checked.
#class LoginUser(LoginView):
   # form_class = LoginForm

    '''
    def get_success_url(self):
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
    user = request.user
    patients=Patient.objects.none()
    if(user.active_caregroup != None):
        patients = Patient.objects.filter(caregroup = user.active_caregroup)

    if request.method == 'POST':
        user = request.user
        caregroup = user.active_caregroup
        form = DeviceCreationForm(request.POST) # Form bound to POST data
        form.caregroup = caregroup
        print('FORM: ', form)
        if form.is_valid():  # If the form passes all validation rules
            p = form.cleaned_data.get('patient')
            print("PATIENT ID: ", p.id)
            patient = patients.filter(id = p.id) # get first (and only) object in queryset
            device = form.save() # save form to database
            device.caregroup = caregroup
            device.save()
            patient = patient[0]
            patient.device = device
            patient.save()
            #device.save() # call save function for DeviceCreationForm
            return(redirect('dashboard'))  # Redirect to the dashboard (TODO: change redirect location?)
        else:
            print(form.cleaned_data)

            print("INVALID DEVICE")
    else:
        form = DeviceCreationForm() # Unbound form
    return render(request, 'registration/adddevice.html', { 'form': form, 'patients':patients} )

def add_care_group(request):
    if request.method == 'POST':
        form = CareGroupCreationForm(request.POST)
        if form.is_valid():
            validate_password(form.cleaned_data.get('password'))  # Ensure password is strong enough
            form.validate()  # Ensure password matches password_confirmation
            caregroup = form.save()  # Save the form
            user = request.user # get current user
            caregroup.users.add(user) # add user to caregroup internal list
            caregroup.admin = user
            caregroup.save()
            user.active_caregroup = caregroup
            user.caregroups.add(caregroup)
            user.save()
            return redirect('dashboard')  # Redirect to the dashboard TODO: Add confirmation that group was added
    else:
        form = CareGroupCreationForm()
    return render(request, 'registration/addcaregroup.html', {'form': form})


def signup(request):
    print("FLAG")
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("FORM SUBMISSION: ", form.cleaned_data)
            print("Signup Form Valid")
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return(redirect('dashboard'))  
        else:
            print("FORM SUBMISSION: ", form.cleaned_data)
            print("Signup Form Invalid")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# this function is called whenever the incoming data form is completed by the microcontroller (roughly every 30 seconds)
def receive_data(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            # Update the patient's status here
            event = data.get('event')
            time = datetime.fromtimestamp(int(data.get('time')))
            event = int(event)
            device_id = data.get('device')
            patient = Patient.objects.get(device_id=device_id)
            # event status of 2 == event has occurred. status of 1 == patient clean. Require user to reset flag on their own
            if event == 2:
                patient.status = 'd'
                patient.last_event = time
                patient.save()
            patient.save()  # Save the modified patient object
            form.save()
            return HttpResponse("We got your data!")
    else:
        form = DataForm()
    #print("FLAG!!!")
    #print(request)
    return render(request, 'data/data.html', {'form': form})
