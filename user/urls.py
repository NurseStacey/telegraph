from django.urls import path

from . import views

app_name='user'
urlpatterns = [
    path('login/', views.login_here, name='login_here'),
    path('logout/', views.logout_here, name='logout_here'),
    path('register_one/', views.register_one, name='register_one'),
    path('add_credentials/', views.add_credentials, name='add_credentials'),
    path('add_roles/', views.add_roles, name='add_roles'),
    path('view_all_staff_members/', views.view_all, name='view_all'),
    path('change_password/', views.change_password, name='change_Password'),
    path('print_staff/', views.print_staff, name='print_staff'),
    path('upload_staff_csv/', views.upload_staff_csv, name='upload_staff_csv'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('update_add_roles_to_user/', views.Add_Roles_To_Staff_Setup, name='Add_Roles_To_Staff_Setup'),
    path('add_roles_to_user/', views.Add_Roles_To_Staff, name='Add_Roles_To_Staff'),
    path('choose_role/', views.choose_role, name='choose_role'),
    path('view_my_patients/', views.view_my_patients, name='view_my_patients'),

     
#  #   path('assign_role/', views.assign_role, name='assign_role'),
]
