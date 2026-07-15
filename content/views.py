from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import models
from .models import WriteUp, Category, ReadLog, Unlock, Rating
from .forms import CommentForm

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

    if writeup.is_premium:
        unlocked = Unlock.objects.filter(user=request.user, writeup=writeup).exists()
        context = {
            'writeup': writeup, 'unlocked': unlocked, 'recommended': recommended,
            'comments': comments, 'comment_form': comment_form,
        }
        return render(request, 'content/writeup_detail.html', context)

    _, created = ReadLog.objects.get_or_create(user=request.user, writeup=writeup)
    if created:
        profile.coins += READ_REWARD
        profile.save()

    context = {
        'writeup': writeup, 'recommended': recommended,
        'comments': comments, 'comment_form': comment_form,
    }
    return render(request, 'content/writeup_detail.html', context)

@login_required
def writeup_unlock(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk, is_premium=True)
    profile = request.user.profile

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

    if writeup.is_premium and not Unlock.objects.filter(user=request.user, writeup=writeup).exists():
        return redirect('writeup_detail', pk=pk)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.writeup = writeup
        comment.user = request.user
        comment.save()

    return redirect('writeup_detail', pk=pk)