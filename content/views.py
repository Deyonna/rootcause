from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import models
from .models import WriteUp, Category, ReadLog, Unlock, Rating
from .forms import CommentForm, WriteUpForm, ContactForm
from .utils import has_access
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from billing.models import SubscriptionPlan, Subscription
from .decorators import author_required

READ_REWARD = 10  # coins earned per free writeup, first read only

def writeup_list(request):
    writeups = WriteUp.objects.all().order_by('-created_at')

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_coins = request.GET.get('min_coins', '')
    max_coins = request.GET.get('max_coins', '')
    premium_only = request.GET.get('premium_only', '')

    if query:
        writeups = writeups.filter(title__icontains=query)

    if category_id:
        writeups = writeups.filter(category_id=category_id)

    if min_coins:
        writeups = writeups.filter(coin_cost__gte=min_coins)

    if max_coins:
        writeups = writeups.filter(coin_cost__lte=max_coins)

    if premium_only == 'on':
        writeups = writeups.filter(is_premium=True)

    categories = Category.objects.all()

    context = {
        'writeups': writeups,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'min_coins': min_coins,
        'max_coins': max_coins,
        'premium_only': premium_only,
    }
    return render(request, 'content/writeup_list.html', context)

@login_required
def writeup_detail(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    profile = request.user.profile
    recommended = WriteUp.objects.filter(category=writeup.category).exclude(pk=writeup.pk)[:4]
    comments = writeup.comments.all()
    comment_form = CommentForm()
    unlocked = has_access(request.user, writeup)

    if writeup.is_premium and not unlocked:
        context = {'writeup': writeup, 'unlocked': unlocked, 'recommended': recommended,
                   'comments': comments, 'comment_form': comment_form}
        return render(request, 'content/writeup_detail.html', context)

    _, created = ReadLog.objects.get_or_create(user=request.user, writeup=writeup)
    if created:
        profile.coins += READ_REWARD
        profile.save()

    context = {'writeup': writeup, 'unlocked': unlocked, 'recommended': recommended,
               'comments': comments, 'comment_form': comment_form}
    return render(request, 'content/writeup_detail.html', context)

@login_required
def writeup_unlock(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk, is_premium=True)
    profile = request.user.profile

    if has_access(request.user, writeup):
        return redirect('writeup_detail', pk=pk)

    already_unlocked = Unlock.objects.filter(user=request.user, writeup=writeup).exists()
    if already_unlocked:
        return redirect('writeup_detail', pk=pk)

    if request.method == 'POST':
        if profile.coins >= writeup.coin_cost:
            profile.coins -= writeup.coin_cost
            profile.save()
            Unlock.objects.create(user=request.user, writeup=writeup)
            messages.success(request, f'Unlocked "{writeup.title}"!')
        else:
            messages.error(request, 'Not enough coins to unlock this.')
        return redirect('writeup_detail', pk=pk)

    return redirect('writeup_detail', pk=pk)

@login_required
@require_POST
def rate_writeup(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    if not has_access(request.user, writeup):
        return JsonResponse({'error': 'You must unlock this writeup before rating it'}, status=403)
    score = request.POST.get('score')

    if score not in ['1', '2', '3', '4', '5']:
        return JsonResponse({'error': 'Invalid score'}, status=400)

    Rating.objects.update_or_create(
        writeup=writeup, user=request.user,
        defaults={'score': int(score)}
    )

    avg = writeup.ratings.aggregate(models.Avg('score'))['score__avg'] or 0
    count = writeup.ratings.count()

    return JsonResponse({'average': round(avg, 1), 'count': count})

@login_required
@require_POST
def add_comment(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    if not has_access(request.user, writeup):
        return redirect('writeup_detail', pk=pk)

    if writeup.is_premium and not Unlock.objects.filter(user=request.user, writeup=writeup).exists():
        return redirect('writeup_detail', pk=pk)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.writeup = writeup
        comment.user = request.user
        comment.save()

    return redirect('writeup_detail', pk=pk)

@login_required
@require_POST
def add_subscription_to_cart(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    item = {'type': 'subscription', 'plan_id': plan.pk}

    if request.POST.get('is_gift'):
        recipient_email = request.POST.get('recipient_email', '').strip()
        if not recipient_email:
            messages.error(request, 'Enter the recipient\'s email to gift this subscription.')
            return redirect('subscription_plans')
        item['is_gift'] = True
        item['recipient_email'] = recipient_email

    cart = request.session.get('cart', [])
    cart.append(item)
    request.session['cart'] = cart
    messages.success(request, f'Added "{plan.name}" to your cart.')
    return redirect('subscription_plans')


@login_required
def view_cart(request):
    cart = request.session.get('cart', [])
    display_items = []
    money_total = 0

    for idx, item in enumerate(cart):
        plan = SubscriptionPlan.objects.filter(pk=item['plan_id']).first()
        if plan:
            label = plan.name
            if item.get('is_gift'):
                label += f" (gift for {item.get('recipient_email')})"
            display_items.append({'index': idx, 'label': label, 'cost': f"${plan.price}"})
            money_total += plan.price

    return render(request, 'content/cart.html', {
        'items': display_items, 'money_total': money_total,
    })


@login_required
@require_POST
def remove_from_cart(request, index):
    cart = request.session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
    request.session['cart'] = cart
    return redirect('view_cart')


@login_required
@require_POST
def checkout(request):
    cart = request.session.get('cart', [])
    unlocked_titles, skipped_titles = [], []

    for item in cart:
        plan = SubscriptionPlan.objects.filter(pk=item['plan_id']).first()
        if not plan:
            continue

        is_gift = item.get('is_gift')
        if is_gift:
            recipient = User.objects.filter(email__iexact=item.get('recipient_email')).first()
            if not recipient:
                skipped_titles.append(f"{plan.name} (no account with that email)")
                continue
        else:
            recipient = request.user

        # simulated payment: no real charge, no coin deduction - just "goes through"
        Subscription.objects.create(
            user=recipient,
            plan=plan,
            expires_at=timezone.now() + timedelta(days=plan.duration_days),
            gifted_by=request.user if is_gift else None,
        )
        unlocked_titles.append(f"{plan.name} (${plan.price})")

    request.session['cart'] = []

    if unlocked_titles:
        messages.success(request, f'Purchased: {", ".join(unlocked_titles)}')
    if skipped_titles:
        messages.error(request, f'Could not complete: {", ".join(skipped_titles)}')
    return redirect('dashboard')

def subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    return render(request, 'content/subscriptions.html', {'plans': plans})

@author_required
def my_writeups(request):
    writeups = WriteUp.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'content/my_writeups.html', {'writeups': writeups})


@author_required
def writeup_create(request):
    if request.method == 'POST':
        form = WriteUpForm(request.POST, request.FILES)
        if form.is_valid():
            writeup = form.save(commit=False)
            writeup.author = request.user
            writeup.save()
            messages.success(request, f'Published "{writeup.title}".')
            return redirect('my_writeups')
    else:
        form = WriteUpForm()
    return render(request, 'content/writeup_form.html', {'form': form})


@author_required
def writeup_edit(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk, author=request.user)
    if request.method == 'POST':
        form = WriteUpForm(request.POST, request.FILES, instance=writeup)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{writeup.title}".')
            return redirect('my_writeups')
    else:
        form = WriteUpForm(instance=writeup)
    return render(request, 'content/writeup_form.html', {'form': form})


@author_required
def writeup_delete(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk, author=request.user)
    if request.method == 'POST':
        writeup.delete()
        messages.success(request, f'Deleted "{writeup.title}".')
    return redirect('my_writeups')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data.get('website'):
                form.save()
            messages.success(request, "Thanks - your message has been received.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'content/contact.html', {'form': form})


def about(request):
    return render(request, 'content/about.html')