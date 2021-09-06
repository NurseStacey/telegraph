from django.db import models
from organization.models import Facility_Rooms, Facility

class Patients(models.Model):
    First_Name = models.CharField(max_length=50)
    Last_Name  = models.CharField(max_length=50)
    Date_of_Birth = models.DateField()


    def __str__(self):
        return '%s, %s(%d-%d-%d)' % (self.Last_Name, self.First_Name[0], self.Date_of_Birth.month, self.Date_of_Birth.day, self.Date_of_Birth.year)

class Patients_Location(models.Model):
    room = models.ForeignKey(Facility_Rooms, on_delete=models.SET_DEFAULT, default=None, null=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_DEFAULT, default=None, null=True)
    patient =  models.ForeignKey(Patients, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return '%s, %s, %s' % (self.patient, self.facility, self.room)
        




