from django.shortcuts import render, get_object_or_404
from .models import WriteUp


def writeup_list(request):
    writeups = WriteUp.objects.all().order_by('-created_at')
    return render(request, 'content/writeup_list.html', {'writeups': writeups})


def writeup_detail(request, pk):
    writeup = get_object_or_404(WriteUp, pk=pk)
    return render(request, 'content/writeup_detail.html', {'writeup': writeup})