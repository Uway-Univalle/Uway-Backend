from django.contrib.gis.db import models as gis_models
from django.db import models

from users.models import User


class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    trajectory = gis_models.LineStringField(srid=4326)