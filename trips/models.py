from django.db import models

from routes.models import Route
from users.models import User
from vehicles.models import Vehicle


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(null=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('CREATED', 'Created'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ], default='CREATED')

class PassengerTrip(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    validated = models.BooleanField(default=False)
    validation_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('trip', 'passenger')
        db_table = 'passenger_trip'