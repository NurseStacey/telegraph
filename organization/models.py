from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    address_1 = models.CharField(max_length=30, null=False, default='')
    address_2 = models.CharField(max_length=30, null=False, default='')
    address_3 = models.CharField(max_length=30, null=False, default='')
    city = models.CharField(max_length=30, null=False, default='')
    state = models.CharField(max_length=2, null=False, default='')
    zip_code = models.CharField(max_length=12, null=False, default='')
    phone_number = models.CharField(max_length=15, null=False, default='')
    fax_number = models.CharField(max_length=15, null=False, default='')

    def __str__(self):
        return '%s ' % (self.name)

    class Meta:
        order_with_respect_to = 'name'

class Units(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, default=None, null=True)
    unit_name = models.CharField(max_length=30, null=False)  

    def __str__(self):
        return '%s %s' % (self.facility.__str__(), self.unit_name)

    class Meta:
        order_with_respect_to = 'facility'

class Facility_Rooms(models.Model):
    unit =  models.ForeignKey(Units, on_delete=models.CASCADE, default=None, null=True)
    room_number = models.CharField(max_length=30, null=False)
    bed_number = models.CharField(max_length=30, null=False)

    def __str__(self):
        return '%s %s %s' % (self.unit.__str__(), self.room_number, self.bed_number)