from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WriteUp, ReadLog, Unlock

READ_REWARD = 10  # coins earned per free writeup, first read only

def writeup_list(request):
    writeups = WriteUp.objects.all().order_by('-created_at')
    return render(request, 'content/writeup_list.html', {'writeups': writeups})

@login_required
def writeup_detail(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    profile = request.user.profile

    if writeup.is_premium:
        unlocked = Unlock.objects.filter(user=request.user, writeup=writeup).exists()
        context = {'writeup': writeup, 'unlocked': unlocked}
        return render(request, 'content/writeup_detail.html', context)

    # free writeup: log the read, award coins only the first time
    _, created = ReadLog.objects.get_or_create(user=request.user, writeup=writeup)
    if created:
        profile.coins += READ_REWARD
        profile.save()

    context = {'writeup': writeup}
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