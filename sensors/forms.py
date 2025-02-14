from django import forms
from django.contrib.auth.forms import UserCreationForm, authenticate
from sensors.models import Patient, CareGroup, Data, User, Device
from django.contrib.auth.hashers import make_password
import logging
logger = logging.getLogger('app_api')

# Form for adding a new patient to the database
class PatientCreationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = (
            'first_name',
            'last_name',
            'age',
        )


# Custom login form that also sends the remember me setting.
class LoginForm(forms.ModelForm):
    remember_me = forms.BooleanField()

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'remember_me',
        )


# Form for adding a new device to the database
class DeviceCreationForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = (
            'patient',
        )

# Form for user creation TODO: Send a confirmation email to the provided address
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Requires a valid email address.')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)

    def validate(self):
        print("RUNNING SIGNUP FORM VALIDATION FUNCTION")

        # Get the cleaned data for password and password_confirmation
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        # Throws an error if the passwords don't match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

# Form for care group creation
# TODO: Send a confirmation email to the provided admin address
class CareGroupCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = CareGroup
        fields = (
            'name',
            'password',
            'password_confirmation',
        )

    # Save creates a DATABASE INSTANCE
    def save(self, commit=True):
        instance = super(CareGroupCreationForm, self).save(commit=False)
        instance.password = make_password(self.cleaned_data['password'])  # Make the password hashed before saving
        if commit:
            instance.save()  # Save the form
        return instance

    # Validates that password and password_confirmation match
    def validate(self):
        # Get the cleaned data for password and password_confirmation
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")
        # Throws an error if the passwords don't match
        if password and password_confirmation and password_confirmation != password:
            raise forms.ValidationError("Passwords do not match.")
        return password_confirmation


# Form for receiving data
class DataForm(forms.ModelForm):

    class Meta:
        model = Data
        fields = (
            'temperature',
            'humidity',
            'event',
            'device',
            'time',
        )

    # Save creates a DATABASE INSTANCE
    def save(self, commit=True):
        instance = super(DataForm, self).save(commit=False)  # Create an instance of the data form
        device = self.cleaned_data.get('device')  # Get the device ID from the data packet
        patient = Patient.objects.get(device=device)  # Get the patient object corresponding to the device
        instance.patient_id = patient.pk  # Send the patient's primary key to the database along with the form
        if commit:
            instance.save()  # Save the form
        return instance
