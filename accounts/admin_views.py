from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from django.views.decorators.http import require_POST

from content.models import WriteUp, Category, ContactMessage
from content.forms import WriteUpForm
from billing.models import Subscription, SubscriptionPlan
from .decorators import admin_required
from .models import AuthorApplication, Profile
from .admin_forms import CategoryForm, SubscriptionPlanForm


def _ctx(active_tab, **extra):
    return {'active_tab': active_tab, **extra}


@admin_required
def admin_dashboard(request):
    total_revenue = Subscription.objects.aggregate(total=Sum('plan__price'))['total'] or 0
    total_coins = Profile.objects.aggregate(total=Sum('coins'))['total'] or 0
    pending_applications = (AuthorApplication.objects
                             .filter(status='pending')
                             .select_related('user')
                             .order_by('submitted_at'))

    context = _ctx('overview',
        total_users=User.objects.count(),
        total_writeups=WriteUp.objects.count(),
        premium_writeup_count=WriteUp.objects.filter(is_premium=True).count(),
        total_revenue=total_revenue,
        total_coins=total_coins,
        pending_applications=pending_applications,
    )
    return render(request, 'accounts/admin/dashboard.html', context)


@admin_required
def admin_users(request):
    query = request.GET.get('q', '')
    users = (User.objects
             .select_related('profile')
             .annotate(writeup_count=Count('writeups', distinct=True))
             .order_by('-date_joined'))
    if query:
        users = users.filter(username__icontains=query)
    return render(request, 'accounts/admin/users.html', _ctx('users', users=users, query=query))


@admin_required
def admin_user_detail(request, pk):
    profile_user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    writeups = WriteUp.objects.filter(author=profile_user).select_related('category').order_by('-created_at')
    subscriptions = Subscription.objects.filter(user=profile_user).select_related('plan').order_by('-started_at')
    context = _ctx('users', profile_user=profile_user, writeups=writeups, subscriptions=subscriptions)
    return render(request, 'accounts/admin/user_detail.html', context)


@admin_required
@require_POST
def admin_user_toggle_role(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile
    profile.role = 'reader' if profile.role == 'author' else 'author'
    profile.save()
    messages.success(request, f'{user.username} is now {profile.get_role_display()}.')
    return redirect('admin_user_detail', pk=pk)


@admin_required
@require_POST
def admin_user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, "You can't deactivate a superuser account.")
        return redirect('admin_user_detail', pk=pk)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'{user.username} is now {"active" if user.is_active else "deactivated"}.')
    return redirect('admin_user_detail', pk=pk)


@admin_required
@require_POST
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, "You can't delete a superuser account.")
        return redirect('admin_user_detail', pk=pk)
    username = user.username
    user.delete()
    messages.success(request, f'Deleted user {username}.')
    return redirect('admin_users')


@admin_required
def admin_writeups(request):
    query = request.GET.get('q', '')
    writeups = (WriteUp.objects
                .select_related('author', 'category')
                .annotate(avg_rating=Avg('ratings__score'))
                .order_by('-created_at'))
    if query:
        writeups = writeups.filter(title__icontains=query)
    return render(request, 'accounts/admin/writeups.html', _ctx('writeups', writeups=writeups, query=query))


@admin_required
def admin_writeup_edit(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    if request.method == 'POST':
        form = WriteUpForm(request.POST, request.FILES, instance=writeup)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{writeup.title}".')
            return redirect('admin_writeups')
    else:
        form = WriteUpForm(instance=writeup)
    return render(request, 'accounts/admin/writeup_form.html', _ctx('writeups', form=form, writeup=writeup))


@admin_required
@require_POST
def admin_writeup_delete(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    title = writeup.title
    writeup.delete()
    messages.success(request, f'Deleted "{title}".')
    return redirect('admin_writeups')


@admin_required
def admin_categories(request):
    categories = Category.sort_hierarchically(
        Category.objects.select_related('parent').annotate(writeup_count=Count('writeup', distinct=True))
    )
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'accounts/admin/categories.html', _ctx('categories', categories=categories, form=form))


@admin_required
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{category.name}".')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    context = _ctx('categories', form=form, entity_label='Category', object_name=category.name,
                    back_url='admin_categories', back_label='categories')
    return render(request, 'accounts/admin/edit_form.html', context)


@admin_required
@require_POST
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.success(request, f'Deleted "{name}".')
    return redirect('admin_categories')


@admin_required
def admin_plans(request):
    plans = SubscriptionPlan.objects.annotate(subscriber_count=Count('subscription', distinct=True)).order_by('duration_days')
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan added.')
            return redirect('admin_plans')
    else:
        form = SubscriptionPlanForm()
    return render(request, 'accounts/admin/plans.html', _ctx('plans', plans=plans, form=form))


@admin_required
def admin_plan_edit(request, pk):
    plan = get_object_or_404(SubscriptionPlan, pk=pk)
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{plan.name}".')
            return redirect('admin_plans')
    else:
        form = SubscriptionPlanForm(instance=plan)
    context = _ctx('plans', form=form, entity_label='Plan', object_name=plan.name,
                    back_url='admin_plans', back_label='plans')
    return render(request, 'accounts/admin/edit_form.html', context)


@admin_required
@require_POST
def admin_plan_delete(request, pk):
    plan = get_object_or_404(SubscriptionPlan, pk=pk)
    name = plan.name
    plan.delete()
    messages.success(request, f'Deleted "{name}".')
    return redirect('admin_plans')


@admin_required
def admin_subscriptions(request):
    subscriptions = Subscription.objects.select_related('user', 'plan', 'gifted_by').order_by('-started_at')
    total_revenue = subscriptions.aggregate(total=Sum('plan__price'))['total'] or 0
    context = _ctx('subscriptions', subscriptions=subscriptions, total_revenue=total_revenue)
    return render(request, 'accounts/admin/subscriptions.html', context)


@admin_required
def admin_applications(request):
    applications = AuthorApplication.objects.select_related('user').order_by('-submitted_at')
    return render(request, 'accounts/admin/applications.html', _ctx('applications', applications=applications))


@admin_required
def admin_application_detail(request, pk):
    application = get_object_or_404(AuthorApplication.objects.select_related('user'), pk=pk)
    return render(request, 'accounts/admin/application_detail.html', _ctx('applications', application=application))


@admin_required
@require_POST
def admin_review_application(request, pk, decision):
    application = get_object_or_404(AuthorApplication, pk=pk, status='pending')
    if decision not in ('approved', 'rejected'):
        messages.error(request, 'Invalid decision.')
        return redirect('admin_applications')

    application.status = decision
    application.save()
    messages.success(request, f'Application from {application.user.username} {decision}.')
    return redirect('admin_applications')


@admin_required
def admin_messages(request):
    contact_messages = ContactMessage.objects.order_by('-created_at')
    return render(request, 'accounts/admin/messages.html', _ctx('messages', contact_messages=contact_messages))


@admin_required
@require_POST
def admin_message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, 'Message deleted.')
    return redirect('admin_messages')
