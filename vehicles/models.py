from django.db import models

class VehicleType(models.Model):
    vehicle_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField()

    class Meta:
        db_table = 'vehicle_type'

class VehicleCategory(models.Model):
    vehicle_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField()

    class Meta:
        db_table = 'vehicle_category'

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    date = models.DateTimeField()

    class Meta:
        db_table = 'location'

class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True)
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.SET_NULL, null=True)
    vehicle_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20)
    brand = models.CharField(max_length=30)
    tecnicomecanica_date = models.DateField()
    soat_date = models.DateField()
    is_verified = models.BooleanField(default=False)
    plate = models.CharField(max_length=7, unique=True)

    class Meta:
        db_table = 'vehicle'