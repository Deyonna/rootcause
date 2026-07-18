from django import forms
from core.mixins import BootstrapFormMixin
from content.models import Category
from billing.models import SubscriptionPlan


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']


class SubscriptionPlanForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'duration_days', 'price']
