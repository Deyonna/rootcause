from django import forms
from .models import Comment, WriteUp

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})
        }


class WriteUpForm(forms.ModelForm):
    class Meta:
        model = WriteUp
        fields = ['title', 'body', 'category', 'is_premium', 'coin_cost']