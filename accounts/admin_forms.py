from django import forms
from core.mixins import BootstrapFormMixin
from content.models import Category
from billing.models import SubscriptionPlan


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # a category can't be parented to itself or one of its own descendants,
            # or get_descendant_ids()/sort_hierarchically() would recurse in a cycle
            excluded_ids = self.instance.get_descendant_ids()
            self.fields['parent'].queryset = Category.objects.exclude(pk__in=excluded_ids)


class SubscriptionPlanForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'duration_days', 'price']
