from django.contrib import admin
from .models import Category, WriteUp, Rating, ReadLog, Unlock, Comment, ContactMessage

admin.site.register(Category)
admin.site.register(WriteUp)
admin.site.register(Rating)
admin.site.register(ReadLog)
admin.site.register(Unlock)
admin.site.register(Comment)
admin.site.register(ContactMessage)