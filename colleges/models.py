from django.db import models

class College(models.Model):
    college_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=255)
    address = models.CharField(max_length=150)
    email = models.EmailField(max_length=320, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

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