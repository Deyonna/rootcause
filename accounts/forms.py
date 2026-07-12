from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import AuthorApplication

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AuthorApplicationForm(forms.ModelForm):
    class Meta:
        model = AuthorApplication
        fields = ['sample_text']