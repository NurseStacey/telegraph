from django.urls import path

from . import views

app_name = 'message'

urlpatterns = [
    path('create_message/', views.create_message, name='create_message'),
]
