from django.utils import timezone
from billing.models import Subscription
from .models import Unlock

def has_access(user, writeup):
    if not writeup.is_premium:
        return True
    if writeup.author_id == user.id:
        return True  # authors always have access to their own writeups, premium or not
    if Unlock.objects.filter(user=user, writeup=writeup).exists():
        return True
    if Subscription.objects.filter(user=user, expires_at__gte=timezone.now()).exists():
        return True
    return False