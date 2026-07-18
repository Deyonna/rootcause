from django import forms
from core.mixins import BootstrapFormMixin
from .models import Comment, WriteUp, ContactMessage

class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})
        }


class WriteUpForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = WriteUp
        fields = ['title', 'body', 'category', 'image', 'is_premium', 'coin_cost']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 15, 'id': 'id_body'})
        }


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    # Honeypot: real users never see or fill this field (hidden off-screen in the
    # template); bots that auto-fill every input will, so a non-empty value here
    # marks the submission as spam without telling the bot it was caught.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5})
        }