from django.urls import path

from . import views


app_name='organization'
urlpatterns = [
    path('create_facility/', views.create_facility, name='create_facility'),
    path('printout_facilities/', views.printout_facilities, name='printout_facilities'),
    path('create_facility_units/', views.create_facility_units, name='create_facility_units'),
    path('view_facility_beds/', views.view_facility_beds, name='view_facility_beds'),
    path('edit_facility/', views.edit_facility, name='edit_facility'),
]