from django.core.validators import EmailValidator
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, login
from django.urls import reverse
from .models import Credentials, Staff_Member, Roles, Staff_Member_Roles, Staff_Member_With_Assignments_By_Unit
from organization.models import Facility, Units, Facility_Rooms
from patient.models import Patients_Location
from validate_email import validate_email
from django.contrib.auth.hashers import make_password
import os
from telegraph import utility as main_utility
from django.db.models  import Q
from . import utility as user_utility

class Roles_Summary():

    def __init__(self):
        self.role=''
        self.unit=''
        self.facility = ''


def view_my_patients(request):
    this_user = Staff_Member.objects.get(username=request.user.username)
    the_roles = Staff_Member_Roles.objects.filter(staff_member=this_user)
    
    if len(the_roles)==0:
        return render(request, 'user/view_my_patients.html', {'Error_Message':'No Patients Assigned'})

    the_units = []
    for one_role in the_roles:
        this_roles_units = one_role.unit.all()
        for one_unit in this_roles_units:
            if not (one_unit in the_units):
                the_units.append(one_unit)

    # Have to believe this can be done in one line
    the_rooms = Facility_Rooms.objects.filter(unit__in=this_roles_units)
    the_patients = Patients_Location.objects.filter(room__in=the_rooms) 

    if request.method=="POST":
        if 'cancel' in request.POST:
            return redirect('/')
        elif 'patient_select' in request.POST:
            print('patient selected')

    return render(request, 'user/view_my_patients.html', {'the_patients':the_patients})

def choose_role(request):
    FacilityList = Facility.objects.all()
    UnitList = Units.objects.all()
    
    this_user = Staff_Member.objects.get(username=request.user.username)
    this_user_current_roles_db = Staff_Member_Roles.objects.filter(staff_member=this_user)

    this_user_current_roles=[]

    for one_role in this_user_current_roles_db:
        this_roles_units = one_role.unit.all()
        for one_unit in this_roles_units:
            this_role_unit=Roles_Summary()
            this_role_unit.role=one_role.role
            this_role_unit.unit = one_unit.unit_name
            this_role_unit.facility = one_unit.facility
        this_user_current_roles.append(this_role_unit)

    RolesList = Roles.objects.filter(
        Q(credential=this_user.credential) | Q(credential=None))

    Error_Message=''

    if request.method=="POST":
        if 'cancel' in request.POST:
            return redirect('/')

        which_roles = []
        for one_role in RolesList:
            if request.POST.get('role' + str(one_role.id))=='True':
                which_roles.append(one_role)

        if len(which_roles)==0:
            Error_Message = 'You need to select at least one role'
        else:
            Error_Message = 'You need to select at least one unit or facility'

        for one_role in which_roles:
            this_user_roles = Staff_Member_Roles.objects.filter(
                staff_member=this_user,
                role=one_role
            ).first()

            if this_user_roles==None:
                this_user_roles=Staff_Member_Roles(
                    staff_member=this_user,
                    role=one_role
                )
                this_user_roles.save()
            

            for this_unit in UnitList:
                if request.POST.get(str(this_unit.id)+'-'+str(this_unit.facility.id)) == 'True' or\
                    request.POST.get(str(this_unit.facility.id) + '-all'):

                    if not(this_unit in this_user_roles.unit.all()):
                        this_user_roles.unit.add(this_unit)

                    Error_Message=''
            this_user_roles.save()
        
        if Error_Message=='':
            return render(request, 'user/success.html', {})

    
    context = {'FacilityList': FacilityList,
                'UnitList': UnitList,
                'RolesList': RolesList,
                'this_user_current_roles': this_user_current_roles,
                'Error_Message': Error_Message}

    return render(request, 'user/choose_role.html', context)

def login_here(request):
    print('here')

    if(request.method=="POST"):

        the_username = request.POST.get('username').lower()
        the_password = request.POST.get('password')
        request.user = authenticate(username=the_username, password=the_password)

        if request.user is not None:
            login(request, request.user)
            if the_password=='password':
                return redirect('/user/change_password')
                
            else:
                return redirect('/')
        else:
            return render(request, 'user/login.html',{'failed_login':True})    

    else:
        return render(request, 'user/login.html',{})


def logout_here(request):
    if request.user is not None:
        logout(request)
        return redirect('/')
    else:
        return render(request, 'userapp/login.html',{})

def upload_staff_csv(request):

    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'staff_upload.csv')
    f=open(file_path,'r')

    the_lines = f.readlines()


    for one_line in the_lines:
        one_line = one_line.partition(',')
        this_username = one_line[0]
        one_line = one_line[2].partition(',')
        this_firstname = one_line[0]
        one_line = one_line[2].partition(',')
        this_lastname = one_line[0]
        one_line = one_line[2].partition(',')
        this_email = one_line[0]
        one_line = one_line[2].partition(',')
        this_credential_temp = one_line[0]
        try:
            this_credential = Credentials.objects.filter(credentials=this_credential_temp)[0]
        except IndexError:
            this_credential=None

        one_line = one_line[2].partition(',')
        this_phone_number = one_line[0]        
        one_line = one_line[2].partition(',')
        this_is_superuser_temp = one_line[0]   
        this_is_superuser = (this_is_superuser_temp.replace('\n','')=='Yes')

        the_staff_member = Staff_Member(
            username = this_username.lower(),
            first_name = this_firstname,
            last_name = this_lastname,
            email = this_email,
            credential = this_credential,
            phone_number = this_phone_number,
            is_superuser = this_is_superuser,
            password = make_password("password"),
        )
        if (len(Staff_Member.objects.filter(email=this_email))==0) and (len(Staff_Member.objects.filter(username=this_username))==0):
            the_staff_member.save()

    f.close()

    return render(request, 'user/success.html', {}) 


def register_one(request):
    credential_list = Credentials.objects.order_by('credentials')       

    for x in credential_list:
        if x.credentials==None: 
            x.credentials=''
        
    if(request.method=="POST"):
        this_user = user_utility.build_user_context(request, credential_list)    
        
        this_user['new_user']=True

        if this_user['bad_email'] or this_user['duplicate_username'] or this_user['duplicate_email']:
            return render(request, 'user/edit_profiles.html', {'this_user':this_user})
        else:
            the_staff_member = Staff_Member(
                username = this_user['username'],
                first_name = this_user['fname'],
                last_name = this_user['lname'],
                email = this_user['email'],
                credential = this_user['credential'],
                phone_number = this_user['phonenumber'],
                is_superuser = this_user['is_superuser'],
                password = make_password("password"),
            )
            the_staff_member.save()
            return render(request, 'user/success.html', {})
    else:
        

        return render(request, 'user/edit_profiles.html', {'this_user':user_utility.build_user_context_blank(credential_list)})


def add_credentials(request):
    if(request.method=="POST"):
        credentials_text = request.POST.get("credentials")
        if credentials_text.strip()=='':
            return render(request, 'user/success.html',{})

        credential_list = main_utility.break_up_text_box(credentials_text)

        for one_credential in credential_list:
            
            if len(Credentials.objects.filter(credentials=one_credential))==0:

                one_credential_DB_entry = Credentials(credentials=one_credential)
                print(one_credential_DB_entry.credentials)
                one_credential_DB_entry.save()

        return render(request, 'user/success.html',{})    
    else:
        return render(request, 'user/add_credentials.html',{})    

def view_all(request):
    all_members = Staff_Member.objects.order_by('last_name')
    credential_list = Credentials.objects.order_by('credentials') 
    FacilityList = Facility.objects.all()

    if request.method=='POST':

    #     if request.POST.get('filter')=='True':

    #         which_credentials=[]
    #         for one_credential in credential_list:
    #             if request.POST.get('c'+one_credential.credentials):   
    #                 which_credentials.append(one_credential)

    #         some_members = Staff_Member.objects.filter(credential__in=which_credentials).order_by('last_name')    
    #         return render(request, 'userapp/all_staff.html',{'all_members':some_members,
    #             'credential_list':credential_list,})    

        which_members = []
        for one_member in all_members:
            if(request.POST.get('c'+one_member.username)):           
                which_members.append(one_member)        

        what_to_do = request.POST.get('what_to_do')
        
        if what_to_do=='delete':
            for one_member in which_members:
                Staff_Member.objects.get(username=one_member.username).delete()
    #     elif what_to_do=='role_selected':
    #         selected_member = request.POST.get('staff_drop_down')
    #         num_members = request.POST.get('num_members')
    #         the_roles = Roles.objects.values('role').distinct()                       
    #         facility_name = request.POST.get('facility_dropdown')   

    #         facility = FacilityTable.objects.get(Facility_Name=facility_name)

    #         selected_member=request.POST.get('staff_drop_down')
    #         this_user = build_user_context_from_DB(
    #             Staff_Member.objects.filter(username=selected_member)[0], 
    #             credential_list)
            
    #         the_units = FacilityUnits.objects.filter(Facility_Name=facility).values('unit').distinct()



    #         which_units=[]
    #         if request.POST.get('select_all_units'):
    #             for one_unit in the_units:
    #                 which_units.append(one_unit['unit'])       
    #         else:
    #             for one_unit in the_units:
    #                 if request.POST.get('unit'+one_unit['unit']):
    #                     which_units.append(one_unit['unit'])   

    #         the_roles = Roles.objects.filter(Q(credential=this_user['credential']) | Q(credential=None))
    #         which_roles=[]
 #           for one_role in the_roles:
 #               if(request.POST.get('role'+one_role.role)):           
 #                   which_roles.append(one_role.role)   
        elif  what_to_do=='add_roles' or what_to_do=='add_roles_change_staff_member' or what_to_do=='add_roles_change_facility':
            return Add_Roles_To_Staff_Setup(request)
            

        elif what_to_do=='edit':
            if len(which_members)==0:
                return render(request, 'user/all_staff.html',
                {
                    'all_members':all_members,
                    'credential_list':credential_list,
                    })   

            selected_member = which_members[0]

        #    if not(request.POST.get('selected_member')==None):
        #        selected_member=request.POST.get('selected_member')

            this_user = user_utility.build_user_context_from_DB(
                 selected_member, 
                 credential_list)

            context = {
                 'which_members':which_members,
                 'num_members': len(which_members),
                 'this_user':this_user,
                 }

            return render(request, 'user/edit_profiles.html', context)  
    #     elif what_to_do=='change_user':
    #         selected_member = request.POST.get('staff_drop_down')
    #         num_members = request.POST.get('num_members')
    #         which_members=[]  #this is different from the other which_members variable
    #         for n in range(int(num_members)):    
    #             which_members.append(request.POST.get('username'+str(n+1)))

    #         this_user = build_user_context_from_DB(
    #             Staff_Member.objects.filter(username=selected_member)[0], 
    #             credential_list)


    #         if request.POST.get('from_where')=='add_roles':
    #             facility_name = request.POST.get('facility_dropdown')
    #             facility = FacilityTable.objects.get(Facility_Name=facility_name)

    #             context = {
    #                 'which_members':which_members,
    #                 'num_members': len(which_members),
    #                 'this_user':this_user,
    #                 'FacilityList':FacilityList,
    #                 'facility':facility,                
    #                 }                
    #             return render(request, 'userapp/add_roles_to_user.html', context)  
    #         else:
    #             context = {
    #                 'which_members':which_members,
    #                 'num_members': len(which_members),
    #                 'this_user':this_user,               
    #                 }     
    #             return render(request, 'userapp/edit_profiles.html', context) 
    #     elif what_to_do=='update_user':
    #         selected_member = request.POST.get('staff_drop_down')
    #         num_members = request.POST.get('num_members')
    #         which_members=[] #this is different from the other which_members variable
    #         for n in range(int(num_members)):    
    #             which_members.append(request.POST.get('username'+str(n+1)))
    #         this_user = build_user_context(request, credential_list)

    #         context = {
    #             'which_members':which_members,
    #             'num_members': len(which_members),
    #             'this_user':this_user,
    #             }

    #         if not(this_user['bad_email'] or this_user['duplicate_email']):
    #             return render(request, 'userapp/edit_profiles.html', context)
    #         else:

    #             this_staff_member = Staff_Member.objects.get(username=this_user['username'])
    #             this_staff_member.first_name=this_user['fname']
                
    #             this_staff_member.last_name=this_user['lname']
    #             this_staff_member.email=this_user['email']
    #             this_staff_member.credential=this_user['credential']
    #             this_staff_member.phonenumber=this_user['phonenumber']
    #             this_staff_member.is_superuser=this_user['is_superuser']
    #             this_staff_member.save()
 
    #             return render(request, 'userapp/success.html', {})
    #     else:
    #         this_user = ({
    #             'username': '',
    #             'phonenumber': '',
    #             'fname': '',
    #             'lname': '',
    #             'credential': '',
    #             'is_superuser': 'No',
    #             'credential_list': credential_list,
    #             'bad_email': False,            
    #             'duplicate_username': False,
    #             'duplicate_email': False,
    #             })
                    
    return render(request, 'user/all_staff.html',{'all_members':all_members,
    'credential_list':credential_list,})    


def change_password(request):


    if request.method=='POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not password1==password2:
            return render(request, 'user/change_password.html',{'Error_Message': 'Passwords do not match'})        
        elif len(password1)<8:
            return render(request, 'user/change_password.html',{'Error_Message': 'Password is not long enough'})     
        else:
            user=request.user
            user.set_password(password1)
            user.save()
            return redirect('/')
    else:
        return render(request, 'user/change_password.html')    

def edit_profile(request):
    
    credential_list = Credentials.objects.order_by('credentials') 

    selected_member = request.POST.get('staff_drop_down')

    which_members=[] 
    n=1
    while not(request.POST.get('username'+str(n+1))==None):
        which_members.append(request.POST.get('username'+str(n+1)))
        n=n+1

    this_user = user_utility.build_user_context(request, credential_list)
    context = {
        'which_members':which_members,
        'num_members': len(which_members),
        'this_user':this_user,
        'update_status':'Fail'
        }

    if not(this_user['bad_email'] or this_user['duplicate_email']):
        this_staff_member = Staff_Member.objects.get(username=this_user['username'])
        this_staff_member.first_name=this_user['fname']
    
        this_staff_member.last_name=this_user['lname']
        this_staff_member.email=this_user['email']
        this_staff_member.credential=this_user['credential']
        this_staff_member.phonenumber=this_user['phonenumber']
        this_staff_member.is_superuser=this_user['is_superuser']
        this_staff_member.save()

        context['update_status']='success'

    return render(request, 'user/edit_profiles.html', context)

def change_user_edit_profile(request):
    FacilityList = Facility.objects.all()
   
    credential_list = Credentials.objects.order_by('credentials') 

    selected_member = request.POST.get('staff_drop_down')
    print(selected_member)
    which_members=[] 
    n=0
    while not(request.POST.get('username'+str(n+1))==None):
        which_members.append(Staff_Member.objects.get(username=request.POST.get('username'+str(n+1))))
        n=n+1

    this_user = user_utility.build_user_context_from_DB(
        Staff_Member.objects.get(username=selected_member), 
        credential_list)

    if request.POST.get('from_where')=='add_roles':
        print('here')
        pass
        # facility_name = request.POST.get('facility_dropdown')
        # facility = Facility.objects.get(name=facility_name)
        # context = {
        #     'which_members':which_members,
        #     'num_members': len(which_members),
        #     'this_user':this_user,
        #     'FacilityList':FacilityList,
        #     'facility':facility,                
        #     }                
        # return render(request, 'user/add_roles_to_user.html', context)  
    else:
        context = {
            'which_members':which_members,
            'num_members': len(which_members),
            'this_user':this_user,               
            }     
        return render(request, 'user/edit_profiles.html', context) 

def add_roles(request):
    credential_list = Credentials.objects.all().exclude(credentials=None).order_by('credentials')

    if(request.method=="POST"):
        role_text = request.POST.get("role")
        Roles.objects.filter(role=role_text).delete()
        which_credentials=[]
        for this_credential in credential_list:
            # print(this_credential.id)
            # print(this_credential.credentials)
            if request.POST.get('credential'+str(this_credential.id)):
                which_credentials.append(this_credential)
        
        if len(which_credentials)==0:
            # print(role_text)
            Roles(role=role_text).save()
        else:
            for this_credential in which_credentials:
                Roles(role=role_text, credential=this_credential).save()

        return render(request, 'user/success.html', {}) 
    else:
        return render(request, 'user/add_roles.html',{'credential_list':credential_list})        


def print_staff(request):
    all_members = Staff_Member.objects.order_by('last_name')
    f=open('staff.csv','w')
    for one_member in all_members:
        
        f.write(
            one_member.username + ',' +
            one_member.first_name + ',' +
            one_member.last_name + ',' +
            one_member.email + ',' +
            one_member.phone_number + ',' +
            one_member.credentials.credential + ','
        )
        if one_member.is_superuser:
            f.write('Yes\n')
        else:
            f.write('No\n')

    f.close()
    return render(request, 'user/success.html', {}) 

def Add_Roles_To_Staff_Setup(request):

    credential_list = Credentials.objects.order_by('credentials') 
    FacilityList = Facility.objects.all()

    all_members = Staff_Member.objects.order_by('last_name')

    which_members = []
    for one_member in all_members:
        if(request.POST.get('c'+one_member.username)):           
            which_members.append(one_member)   

    

    # if not(num_members==None):  #if we are coming from all_staff don't go through here.
    #     which_members=[]  #this is different from the other which_members variable
    #     for n in range(int(num_members)):    
    #         which_members.append(request.POST.get('username'+str(n+1)))

    selected_member = request.POST.get('staff_drop_down')

    if selected_member==None:
        selected_member=which_members[0].username


    this_user = Staff_Member.objects.get(username=selected_member)
    the_roles = Roles.objects.values('role').distinct()

    if len(which_members)==0:
        return render(request, 'user/all_staff.html',{'all_members':all_members,
        'credential_list':credential_list,})   

    facility_name = request.POST.get('facility_dropdown')
    if facility_name==None:
        facility_name=FacilityList[0].name

    this_facility = Facility.objects.get(name=facility_name)

    the_units = Units.objects.filter(facility=this_facility).values('unit_name').distinct()
    the_roles = Roles.objects.filter(Q(credential=this_user.credential) | Q(credential=None))
 
    context = {
        'which_members':which_members,
        'num_members': len(which_members),
        'which_user':this_user,
        'FacilityList':FacilityList,
        'this_facility':this_facility,
        'the_units':the_units,
        'the_roles':the_roles,
        }

    return render(request, 'user/add_roles_to_user.html', context)          


def Add_Roles_To_Staff(request):
    credential_list = Credentials.objects.order_by('credentials') 
    FacilityList = Facility.objects.all()

    all_members = Staff_Member.objects.order_by('last_name')

    which_members = []
    for one_member in all_members:
        if(request.POST.get('c'+one_member.username)):           
            which_members.append(one_member)   
    
    selected_member = request.POST.get('staff_drop_down')
    this_user = Staff_Member.objects.get(username=selected_member)    
    the_roles = Roles.objects.values('role').distinct()

    facility_name = request.POST.get('facility_dropdown')

    this_facility = Facility.objects.get(name=facility_name)

    the_units = Units.objects.filter(facility=this_facility)
    the_roles = Roles.objects.filter(Q(credential=this_user.credential) | Q(credential=None))

    which_roles = []
    for one_role in the_roles:
        if(request.POST.get('c'+one_role.role)):           
            which_roles.append(one_role)      
 
    which_units = []

    for one_unit in the_units:
        if(request.POST.get('c'+one_unit.unit_name) or request.POST.get('select_all')):           
            which_units.append(one_unit)      

    for one_unit in which_units:
        for one_role in which_roles:
            one_entry = Staff_Member_With_Assignments_By_Unit(staff_member=this_user, role=one_role, unit=one_unit)
            one_entry.save()

    the_units = the_units.values('unit_name').distinct()
    
    context = {
        'which_members':which_members,
        'num_members': len(which_members),
        'which_user':this_user,
        'FacilityList':FacilityList,
        'this_facility':this_facility,
        'the_units':the_units,
        'the_roles':the_roles,
        }
    return render(request, 'user/add_roles_to_user.html', context)          
