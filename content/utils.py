from django.utils import timezone
from billing.models import Subscription
from .models import Unlock

def has_access(user, writeup):
    if not writeup.is_premium:
        return True
    if Unlock.objects.filter(user=user, writeup=writeup).exists():
        return True
    if Subscription.objects.filter(user=user, expires_at__gte=timezone.now()).exists():
        return True
    return False