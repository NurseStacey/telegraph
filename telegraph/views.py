from django.shortcuts import render
#from .settings import STATIC_FILES_DIR, STATIC_ROOT

def home(request):
    if request.user.is_superuser:
        return render(request, 'superuser_index.html', {})
    else:
        return render(request, 'index.html', {})

