from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import UserManager
from django.core.validators import RegexValidator



class UploadFileForm(forms.Form):
    file_upload = forms.FileField()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}))
    phone_number = forms.CharField(required=True, validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be in the format '+999999999'. Up to 15 digits allowed.")
    ])



class Meta:
    mode = UserCreationFormfields = ["first_name","last_name", "name","email", "address", "phone_number", "password1", "password2"]

