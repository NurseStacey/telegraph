from django.db import models
from django.contrib.auth.models import AbstractUser
from organization.models import Units, Facility_Rooms

class Credentials(models.Model):
    credentials = models.CharField(max_length=10, null=True)
    # do I need other elements to the record?
    def __str__(self):
        return '%s ' % (self.credentials)
    

class Roles(models.Model):
    role = models.CharField(max_length=20)
    credential = models.ForeignKey(Credentials, on_delete=models.SET_DEFAULT, default=None, null=True)
    # do I need other elements to the record?   

    def __str__(self):
        return '%s ' % (self.role)
    
class Staff_Member(AbstractUser):
    credential = models.ForeignKey(Credentials, on_delete=models.SET_DEFAULT, default=None, null=True, related_name='this_credential')
    phone_number = models.CharField(max_length=15)
    
    def __str__(self):
        return '%s %s ' % (self.first_name, self.last_name)
    

class Staff_Member_Roles(models.Model):
    staff_member = models.ForeignKey(Staff_Member, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, null=True)
    unit = models.ManyToManyField(Units)
    
# we will be removing this eventually
class Staff_Member_With_Assignments_By_Unit(models.Model):
    staff_member = models.ForeignKey(Staff_Member, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, null=True)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '%s %s %s' % (self.staff_member.__str__(), self.role.__str__(), self.unit.__str__())


class Staff_Member_With_Assignments_By_Room(models.Model):
    staff_member = models.ForeignKey(Staff_Member, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Facility_Rooms, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '%s %s %s' % (self.staff_member.__str__(), self.role.__str__(), self.unit.__str__())
        Facility_Rooms
