from django import forms
from django.db.models import Case, When
from core.mixins import BootstrapFormMixin
from .models import Category, Comment, WriteUp, ContactMessage

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ordered = Category.sort_hierarchically(Category.objects.select_related('parent'))
        display_names = {cat.pk: cat.display_name for cat in ordered}
        pk_order = list(display_names.keys())
        if pk_order:
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_order)])
            self.fields['category'].queryset = Category.objects.filter(pk__in=pk_order).order_by(preserved_order)
        self.fields['category'].label_from_instance = lambda cat: display_names.get(cat.pk, cat.name)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('is_premium'):
            # server-side backstop for premium-toggle.js: forces coin_cost to 0 whenever
            # is_premium is off so a free writeup can never carry a lingering cost
            cleaned_data['coin_cost'] = 0
        return cleaned_data


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    # Honeypot: real users never see or fill this field (hidden off-screen in the template) bots that auto-fill every input will, so a non-empty value here marks the submission as spam.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5})
        }