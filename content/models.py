from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class WriteUp(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writeups')
    is_premium = models.BooleanField(default=False)
    coin_cost = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'WriteUps'

    def __str__(self):
        return self.title


class Rating(models.Model):
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('writeup', 'user')


class ReadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'writeup')


class Unlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'writeup')