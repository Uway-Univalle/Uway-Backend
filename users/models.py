from django.contrib.auth.models import AbstractUser
from django.db import models

class College(models.Model):
    college_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=255)
    address = models.CharField(max_length=150)

    class Meta:
        db_table = 'college'

class Color(models.Model):
    hex_code = models.CharField(max_length=7, primary_key=True)

    class Meta:
        db_table = 'color'

class CollegeColor(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'college_color'
        unique_together = ('college', 'color')

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
    user_id = models.AutoField(primary_key=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)
    passenger_type = models.ForeignKey(PassengerType, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=50, unique=True)
    personal_id = models.CharField(max_length=40)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    code = models.CharField(max_length=15)

    class Meta:
        db_table = 'user'