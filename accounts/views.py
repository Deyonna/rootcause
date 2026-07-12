from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, AuthorApplicationForm
from .models import AuthorApplication


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
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'author':
        return render(request, 'accounts/author_dashboard.html', {'profile': profile})
    return render(request, 'accounts/reader_dashboard.html', {'profile': profile})
    
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