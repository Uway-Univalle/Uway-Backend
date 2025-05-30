from django.contrib.auth.models import AbstractUser
from django.db import models

from colleges.models import College


class UserType(models.Model):
    user_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.TextField()

    class Meta:
        db_table = 'user_type'

class PassengerType(models.Model):
    passenger_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.TextField()

    class Meta:
        db_table = 'passenger_type'

class User(AbstractUser):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)
    passenger_type = models.ForeignKey(PassengerType, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=50, unique=True)
    personal_id = models.CharField(max_length=40)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    code = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'


class UserDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    url = models.CharField(max_length=255)

    class Meta:
        db_table: 'user_document'