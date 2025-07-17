from django.db import models
from django.conf import settings

class VehicleType(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()

    class Meta:
        db_table = 'vehicle_type'

class VehicleCategory(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()

    class Meta:
        db_table = 'vehicle_category'

class Location(models.Model):
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    date = models.DateTimeField()

    class Meta:
        db_table = 'location'

class Vehicle(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True)
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.SET_NULL, null=True)
    vehicle_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    capacity = models.IntegerField(null=False, default=5)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user')
    state = models.CharField(max_length=20, choices=[
        ('AVAILABLE', 'Available'),
        ('MAINTENANCE', 'Maintenance'),
        ('IN_USE', 'In Use')
    ])
    brand = models.CharField(max_length=30)
    tecnicomecanica_date = models.DateField()
    soat_date = models.DateField()
    is_verified = models.BooleanField(default=False)
    plate = models.CharField(max_length=7, unique=True)

    class Meta:
        db_table = 'vehicle'