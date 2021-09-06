from datetime import datetime
from django.shortcuts import redirect, render
from django.db.models import Q
from patient.models import Patients, Patients_Location
from organization.models import Facility, Facility_Rooms, Units
import datetime
import re
import os

def batch_patient_load(request):
    
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, '100patients.csv')
    f=open(file_path,'r')

    the_lines = f.readlines()


    for one_line in the_lines:
        one_line = one_line.partition(',')
        first_name = one_line[0]
        one_line = one_line[2].partition(',')
        last_name = one_line[0]
        one_line = one_line[2].partition(',')
        dob_str = one_line[0].replace('\n','')
        print(dob_str)
        datetime_object = datetime.datetime.strptime(dob_str, '%m/%d/%Y')

        the_patient = Patients(
            First_Name=first_name,
            Last_Name=last_name,
            Date_of_Birth=datetime_object,
        )

        the_patient.save()

    f.close()

    return redirect('/')

def add_patient(request):

    if request.method == "POST":
        if 'cancel' in request.POST:
            return redirect('/')
            
    if(request.method=="POST"):
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        dob_str =re.sub('[^0-9]','/',request.POST.get('dob'))

        return_error='no_error'
        try:
            
            dob = datetime.datetime.strptime(dob_str, '%m/%d/%Y').date()
        except ValueError:
            return_error='Bad_Date'
     
        if len(Patients.objects.filter(First_Name__iexact = first_name).filter(Last_Name__iexact = last_name).filter(Date_of_Birth=dob))>0:
            return_error='Duplicate'
        else:
            print('there')
            new_patient = Patients(First_Name=first_name, Last_Name=last_name, Date_of_Birth=dob)
            new_patient.save()
            print('here')
            return render (request,'patient/patient_added_successfully.html', {
                'patient_id':new_patient.pk,})
            
        return render (request,'patient/add_one_patient.html', {
            'fname':first_name,
            'lname':last_name,
            'dob':dob_str,
            'return_error':return_error
            })
    else:
        return render (request,'patient/add_one_patient.html', {})

def assign_patient_to_room(request):

    # assigned_patients = Patients_Location.objects.all().patients_set  don't need this
    unassigned_patients = \
        Patients.objects.filter(~Q(patients_location__pk__in=Patients_Location.objects.values('pk'))).order_by('Last_Name')

    this_patient = unassigned_patients[0]

    FacilityList = Facility.objects.all().order_by('name')

    error_message=''
    if request.method=='POST':

        new_patient=request.POST.get('new_patient')

        patient_selected='False'
        if new_patient=='True':
            patient_selected='True'
        
        facility_name=request.POST.get('facility_dropdown')
        if facility_name in {'',None}:
            facility_name = FacilityList[0].name

        this_facility = Facility.objects.get(name=facility_name)    
        UnitList = Units.objects.filter(facility=this_facility)
        what_to_do=request.POST.get('what_to_do')
        this_patient_id = int(request.POST.get('patient_dropdown'))
        this_patient = Patients.objects.get(pk=this_patient_id)
        if not(this_patient==None):
            patient_selected='True'

        this_unit = None

        this_unit_id = request.POST.get('unit_dropdown')
        if this_unit_id==None:
            this_unit_id=''

        if this_unit_id.isnumeric():
            this_unit = Units.objects.get(pk=int(this_unit_id))
        else:
            this_unit = UnitList[0]
            

        the_beds=None
        unit_chosen='False'
        if what_to_do == 'choose_patient':
            pass         
        if what_to_do == 'choose_facility':
            pass  #don't really need to do anything
        elif what_to_do == 'assign_to_facility':
            this_patient_location = Patients_Location(patient=this_patient, facility=this_facility)
            this_patient_location.save()
        elif what_to_do == 'choose_unit':
            the_beds = Facility_Rooms.objects.filter(unit=this_unit).filter(~Q(patients_location__pk__in=Patients_Location.objects.values('pk')))
            unit_chosen='True'
        elif what_to_do=='bed_selected':
            the_beds = Facility_Rooms.objects.filter(unit=this_unit).filter(~Q(patients_location__pk__in=Patients_Location.objects.values('pk')))
            which_bed = None
            for one_bed in the_beds:
                if request.POST.get('bed'+str(one_bed.id)):
                    which_bed = one_bed
                    break
            
            
            if not(which_bed==None):
                this_patient_location = Patients_Location(patient=this_patient, room=which_bed)
                this_patient_location.save()    
                
                UnitList = Units.objects.filter(facility=FacilityList[0])
                this_unit=UnitList[0]
                request.method=''
                if new_patient=='True':
                    redirect('/patient_added/successfully_assigned.html')
                else:
                    assign_patient_to_room(request)  #start the whole process over
            else:
                error_message='choose_bed'

        return render (request,'patient/assign_patient.html', 
                {'FacilityList':FacilityList,
                'this_facility':this_facility,
                'unassigned_patients':unassigned_patients,
                'this_patient': this_patient,
                'UnitList':UnitList,
                'this_unit':this_unit,
                'patient_selected':patient_selected,
                'unit_chosen':unit_chosen,
                'the_beds':the_beds,
                'new_patient': new_patient})
    else:
        UnitList = Units.objects.filter(facility=FacilityList[0])
        this_unit=UnitList[0]
        the_beds = Facility_Rooms.objects.filter(unit=this_unit).filter(
            ~Q(patients_location__pk__in=Patients_Location.objects.values('pk')))
            
        return render (request,'patient/assign_patient.html', 
                {'FacilityList':FacilityList,
                'this_facility':FacilityList[0],
                'this_unit':this_unit,
                'UnitList': UnitList,
                'unassigned_patients':unassigned_patients,
                'this_patient': this_patient,
                 'the_beds': the_beds, })

def view_patients(request):

    FacilityList = Facility.objects.all().order_by('name')    
    this_facility = FacilityList[0]
    assigned_patients = Patients_Location.objects.all()
    unassigned_patients = \
        Patients.objects.filter(~Q(patients_location__pk__in=Patients_Location.objects.values('pk')))
    this_patient = unassigned_patients[0]

    if request.method=='POST':
        what_to_do=request.POST.get('what_to_do')

        facility_name=request.POST.get('facility_dropdown')
        if facility_name in {'',None}:
            facility_name = FacilityList[0].name

        this_facility = Facility.objects.get(name=facility_name)    
        return render (request,'patient/view_patients.html', 
            {'FacilityList':FacilityList,
            'this_facility':this_facility,})

    else:
        return render (request,'patient/view_patients.html', 
            {'FacilityList':FacilityList,
            'this_facility':this_facility,
            'assigned_patients':assigned_patients,
            'unassigned_patients':unassigned_patients,
            })

def edit_patient(request):
    pass
