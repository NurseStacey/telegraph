from . import utility as main_utility
from .models import Facility, Facility_Rooms, Units
from telegraph import utility as main_utility

def add_rooms_to_DB(rooms_text, unit, this_facility, number_beds):

    this_unit = Units.objects.get(facility=this_facility, unit_name=unit)
    room_list=main_utility.break_up_text_box(rooms_text)

    duplicate_rooms=[]

    for room in room_list: 
        if len(Facility_Rooms.objects.filter(unit=this_unit).filter(room_number=room))>0:
            duplicate_rooms.append(room)                   
        else: 
            for bed in range(number_beds):
                if not(room.strip()==''):
                    this_room=Facility_Rooms(unit=this_unit, room_number=room, bed_number=str(bed+1))
                    this_room.save()
    
    return duplicate_rooms