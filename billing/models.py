from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    gifted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gifts_sent')

    def is_active(self):
        return self.expires_at >= timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
