from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from content.models import ReadLog, Unlock, Rating
from .models import AuthorApplication
from .forms import RegisterForm, AuthorApplicationForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def apply_author(request):
    profile = request.user.profile

    if profile.role == 'author':
        return redirect('dashboard')

    existing = AuthorApplication.objects.filter(user=request.user, status='pending').first()
    if existing:
        return render(request, 'accounts/apply_author.html', {'already_applied': True})

    if request.method == 'POST':
        form = AuthorApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('dashboard')
    else:
        form = AuthorApplicationForm()
    return render(request, 'accounts/apply_author.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def dashboard(request):
    profile = request.user.profile
    recent_reads = ReadLog.objects.filter(user=request.user).select_related('writeup').order_by('-timestamp')[:5]
    recent_unlocks = Unlock.objects.filter(user=request.user).select_related('writeup').order_by('-timestamp')[:5]
    recent_ratings = Rating.objects.filter(user=request.user).select_related('writeup').order_by('-created_at')[:5]
    free_count = ReadLog.objects.filter(user=request.user).count()
    unlocked_count = Unlock.objects.filter(user=request.user).count()

    context = {
        'profile': profile,
        'recent_reads': recent_reads,
        'recent_unlocks': recent_unlocks,
        'recent_ratings': recent_ratings,
        'free_count': free_count,
        'unlocked_count': unlocked_count,
    }
    if profile.role == 'author':
        return render(request, 'accounts/author_dashboard.html', context)
    return render(request, 'accounts/reader_dashboard.html', context)
