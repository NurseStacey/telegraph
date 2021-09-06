from django.shortcuts import render, redirect
from .models import Facility, Facility_Rooms, Units
from django.db.models import Count
from . import utility as facility_utility

# Create your views here.

class facility_base_data():
    def __init__(self):
        self.address1 = ''
        self.address2 = ''
        self.address3 = ''
        self.city = ''
        self.state= ''
        self.zip_code= ''
        self.phone_number = ''
        self.fax_number = ''
        self.name = ''

    def pull_base_data_from_HTML(self, request):

            if not request.POST.get('facility_name')==None:
                self.name=request.POST.get('facility_name').strip()

            if not request.POST.get('address1')==None:
                self.address1=request.POST.get('address1').strip()

            if not request.POST.get('address2')==None:
                self.address2=request.POST.get('address2').strip()                
                
            if not request.POST.get('address3')==None:
                self.address3=request.POST.get('address3').strip()

            if not request.POST.get('city')==None:
                self.city=request.POST.get('city').strip()

            if not request.POST.get('state')==None:
                self.state=request.POST.get('state').strip()

            if not request.POST.get('zip_code')==None:
                self.zip_code=request.POST.get('zip_code').strip()

            if not request.POST.get('phone_number')==None:
                self.phone_number=request.POST.get('phone_number').strip()

            if not request.POST.get('fax_number')==None:
                self.fax_number=request.POST.get('fax_number') .strip()    

        
def create_facility(request):

    if(request.method=="POST"):


        temp_facility_data = facility_base_data()
        temp_facility_data.pull_base_data_from_HTML(request)

        duplicate_error = len(Facility.objects.filter(name=temp_facility_data.name))>0
        missing_facility_name = temp_facility_data.name.strip()==''
        if duplicate_error or missing_facility_name:    
            return render(request, 'organization/duplicate_facility.html', {
                'duplicate_error':duplicate_error,
                'missing_facility_name':missing_facility_name
                })        

        the_facility = Facility(
            name = temp_facility_data.name,
            address_1 = temp_facility_data.address1,
            address_2 = temp_facility_data.address2,
            address_3 = temp_facility_data.address3,
            city = temp_facility_data.city,
            state = temp_facility_data.state,
            zip_code = temp_facility_data.zip_code,
            phone_number = temp_facility_data.phone_number,
            fax_number = temp_facility_data.fax_number
            )
        
        the_facility.save()
        return redirect('/')
    else:
        return render(request, 'organization/create_facility.html',{})    

def printout_facilities(request):
    all_facilities = Facility.objects.order_by('name')
    f=open('facilities.csv','w')
    for one_facility in all_facilities:
        
        f.write(
            one_facility.name + ',' +
            one_facility.address_1 + ',' +
            one_facility.address_2 + ',' +
            one_facility.address_3 + ',' +
            one_facility.city + ',' +
            one_facility.state + ',' + 
            one_facility.zip_code + ',' +
            one_facility.phone_number + ',' +
            one_facility.fax_number + '\n'
        )

    f.close()

    return redirect('/')

def edit_facility(request):

    #this info is for all paths
    update_message=''
    FacilityList = Facility.objects.all().order_by('name')
    what_to_do = ''

    #need defaults if we aren't in POST
    if(request.method=='POST'):
        what_to_do = request.POST.get('what_to_do')
        facility_name = request.POST.get('facility_dropdown')
    else:
        facility_name = FacilityList[0].name

    #Need the facility and it's units we are working with, either default or chosen
    this_facility = Facility.objects.get(name=facility_name)
    the_units = Units.objects.filter(facility=this_facility).values('unit_name').distinct().order_by('unit_name')

    # either a default unit or one that was chosen in the drop down box
    if(request.method=='POST'):
        which_unit=request.POST.get('unit_dropdown')
    else:
        which_unit=the_units[0]['unit_name']

    
    # the rooms for the current unit, either default or selected    
    the_rooms_by_bed=[]

    duplicate_rooms = []

    if what_to_do=='edit_beds':

        this_unit=Units.objects.get(facility=this_facility, unit_name=which_unit)
        # don't know why this was the first one I did.  should have been the last.
        Facility_Rooms.objects.filter(unit=this_unit).delete()
        for index in range(8):
            this_duplicate_rooms = facility_utility.add_rooms_to_DB(
                request.POST.get('room_numbers'+str(index+1)),
                which_unit, 
                this_facility, 
                index+1)  
                
            for one in this_duplicate_rooms:
                 duplicate_rooms.append(one)

        update_message='Beds have been updated'
    elif what_to_do=='facility_chosen':
        pass    #don't think we need to do anything
    elif what_to_do=='update_base_data':
        temp_facility_data = facility_base_data()
        temp_facility_data.pull_base_data_from_HTML(request)
        this_facility.address_1      = temp_facility_data.address1
        this_facility.address_2      = temp_facility_data.address2
        this_facility.address_3      = temp_facility_data.address3
        this_facility.city           = temp_facility_data.city
        this_facility.state          = temp_facility_data.state
        this_facility.zip_code       = temp_facility_data.zip_code
        this_facility.phone_number   = temp_facility_data.phone_number
        this_facility.fax_number     = temp_facility_data.fax_number
        this_facility.save()
        update_message = 'Facility Data Updated'
    elif what_to_do=='unit_chosen':
        pass #nothing really needs to be done with how it is set up currently
            #should move stuff from below this nested if up here somehow
    elif what_to_do=='change_unit_names':
        for one_unit in the_units:
            which_unit=one_unit['unit_name']

            new_unit_name=request.POST.get('unit_' + which_unit).strip()
            if new_unit_name=='':  # if they deleted the name that means we delete the unit
                Units.objects.filter(unit_name=which_unit).filter(facility = this_facility).delete()
                the_units.delete(one_unit)
            elif not(which_unit==new_unit_name):
                this_unit=Units.objects.get(unit_name=which_unit, facility = this_facility)
                this_unit.unit_name = new_unit_name
                this_unit.save()
                update_message = 'Unit Names Updated'

        if update_message== 'Unit Names Updated':
            the_units = Units.objects.filter(facility=this_facility).values('unit_name').distinct().order_by('unit_name')

    #if we chose a facility without an units we need to leave now
    if len(the_units)==0:
        return render(request, 
            'facilityapp/edit_facility.html',
            {'FacilityList':FacilityList,
            'facility':this_facility,
            'has_units': False,
            'update_message': update_message,
            })    

    #doesn't have to be here, this is for when we update unit names
    #don't want to duplicate the bit just above incase there are now no units
    if len(Units.objects.filter(unit_name=which_unit).filter(facility=this_facility))==0:
        which_unit=the_units[0]['unit_name']
    #Need to get the rooms for the current facility/unit combo 
    # this only needs to change really if a different facility or unit was selected.
    this_unit=Units.objects.get(unit_name=which_unit, facility=this_facility)
    the_rooms = Facility_Rooms.objects.filter(unit=this_unit).values('room_number').annotate(Count('id'))
    the_rooms_by_bed=['','','','','','','','']
    max_num_rooms = 0
    for one_room in the_rooms:
        the_rooms_by_bed[one_room['id__count']-1] = the_rooms_by_bed[one_room['id__count']-1] + '\n' + str(one_room['room_number'])
        max_num_rooms=max(max_num_rooms, one_room['id__count'])

    return render(request, 
        'organization/edit_facility.html',
        {'FacilityList':FacilityList,
        'facility':this_facility,
        'has_units': True,
        'the_units':the_units,
        'the_rooms_by_bed':the_rooms_by_bed,
        'max_num_rooms':max_num_rooms+1,
        'which_unit':which_unit,
        'update_message': update_message,
        })        


def create_facility_units(request):

    FacilityList = Facility.objects.all()
    this_facility=FacilityList[0]

    if request.method=='POST':
        what_to_do = request.POST.get('what_to_do')
        facility_name = request.POST.get('facility_dropdown')
        this_unit = request.POST.get('unit_name')

        this_facility =Facility.objects.get(name=facility_name)

        if what_to_do=='add_unit':
            if len(Units.objects.filter(facility=this_facility).filter(unit_name=this_unit))>0:
                return render(request, 'organization/add_unit.html',{'FacilityList':FacilityList, 'error_message':'exists'})

            Units(facility=this_facility, unit_name=this_unit).save()

            return render(request, 
                'organization/add_rooms_to_unit.html',
                {'facility_dropdown':facility_name,
                'unit_name': this_unit,
                'number_beds':1})
        else:
            number_beds = int(request.POST.get('number_beds'))
            rooms_text = request.POST.get('room_numbers')
            facility =Facility.objects.get(name=facility_name)

            duplicate_rooms = []
            if not(rooms_text.strip()==''):
                duplicate_rooms = facility_utility.add_rooms_to_DB(rooms_text, this_unit, facility, number_beds)    


            return render(request, 
                'organization/add_rooms_to_unit.html',
                {'facility_dropdown':facility_name,
                'this_facility': this_facility,
                'unit_name': this_unit,
                'number_beds':number_beds+1,
                'duplicate_rooms':duplicate_rooms,
                'duplicate_error':len(duplicate_rooms)>0,
                })           
    else:     
        return render(request, 'organization/add_unit.html',
        {'FacilityList':FacilityList, 
        'this_facility': this_facility,
        'error_message':'none'})

def view_facility_beds(request):
    FacilityList = Facility.objects.all()
    
    if len(FacilityList)==0:
        return render(request, 
            'organization/view_units.html',
            {'error_message':'No_Facilities'})        

    no_rooms=False
    if request.method=='POST':

        no_rooms = request.POST.get('no_rooms')=='True'
        if no_rooms:
            print('no rooms')
        else:
            print('rooms')
        this_facility=''
        facility_name = request.POST.get('facility_dropdown')
        print(facility_name)
        if not(facility_name =='see_all' or facility_name == ''):
            this_facility =Facility.objects.get(name=facility_name)
            all_units = Units.objects.filter(facility=this_facility).order_by('facility')
            
        else:
            all_units = Units.objects.all().order_by('facility')
        
        BedList = Facility_Rooms.objects.filter(unit__in=all_units)

        if no_rooms:
            return render(request, 
                'organization/view_units_no_rooms.html',
                {'FacilityList':FacilityList,
                'which_facilty': this_facility,
                'all_units':all_units,
                'no_rooms':no_rooms})
        else:
            return render(request, 
                'organization/view_units.html',
                {'FacilityList':FacilityList,
                'which_facilty': this_facility,
                'BedList':BedList,
                'no_rooms':no_rooms})

    else:
        BedList = Facility_Rooms.objects.all().order_by('unit')
        this_facility=''

        return render(request, 
            'organization/view_units.html',
            {'FacilityList':FacilityList,
            'which_facilty': this_facility,
            'BedList':BedList})
