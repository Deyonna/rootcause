from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @staticmethod
    def sort_hierarchically(categories):
        children_by_parent = {}
        for cat in categories:
            children_by_parent.setdefault(cat.parent_id, []).append(cat)
        for group in children_by_parent.values():
            group.sort(key=lambda c: c.name.lower())

        ordered = []

        def add_children(parent_id, depth):
            for cat in children_by_parent.get(parent_id, []):
                cat.depth = depth
                indent = '    ' * depth
                prefix = '- ' if depth else ''
                cat.display_name = indent + prefix + cat.name
                ordered.append(cat)
                add_children(cat.pk, depth + 1)

        add_children(None, 0)
        return ordered

    def get_descendant_ids(self):
        ids = [self.pk]
        for child in self.subcategories.all():
            ids.extend(child.get_descendant_ids())
        return ids


class WriteUp(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=40000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writeups')
    image = models.ImageField(upload_to='writeups/', blank=True, null=True)
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

    def __str__(self):
        return f"{self.user.username} rated {self.writeup.title}: {self.score}"


class ReadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'writeup')

    def __str__(self):
        return f"{self.user.username} read {self.writeup.title}"


class Unlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'writeup')

    def __str__(self):
        return f"{self.user.username} unlocked {self.writeup.title}"

class Comment(models.Model):
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.writeup.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.name}"
