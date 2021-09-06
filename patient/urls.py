from django.urls import path

from . import views

app_name='patient'
urlpatterns = [
        path('add_patient/', views.add_patient, name='add_patient'),
        path('assign_patient_to_room/', views.assign_patient_to_room, name='assign_patient_to_room'),
        path('view_patients/', views.view_patients, name='view_patients'),
        path('edit_patient/', views.edit_patient, name='edit_patient'),
        # path('batch_patient_load/', views.batch_patient_load, name='batch_patient_load'),    
]
