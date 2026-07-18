
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from core.mixins import BootstrapFormMixin
from .models import AuthorApplication, Profile

class RegisterForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

class AuthorApplicationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AuthorApplication
        fields = ['sample_text']

class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']


class StyledLoginForm(BootstrapFormMixin, AuthenticationForm):
    pass