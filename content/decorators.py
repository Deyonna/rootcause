from django.contrib.auth.decorators import user_passes_test

def author_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.profile.role == 'author')(view_func)