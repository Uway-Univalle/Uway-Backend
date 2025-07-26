from celery import shared_task
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.template.defaultfilters import length
from django.utils import timezone
from datetime import timedelta

from vehicles.models import VehicleLocation
from .models import Trip

@shared_task
def analyze_trip(trip_id):
    trip = Trip.objects.get(id=trip_id)
    route = trip.route  # Suponiendo que tiene un campo 'route' con un LineString
    locations = VehicleLocation.objects.filter(trip=trip).order_by('date')

    # Detectar desvíos
    desviaciones = []
    for loc in locations:
        if loc.position.distance(route.trajectory) > 0.15:  # 0.15 km = 150 m
            desviaciones.append(loc)

    # Detectar incidentes (detención >= 4 min en un radio de 20 m)
    incidentes = []
    i = 0
    while i < len(locations):
        j = i + 1
        while (j < len(locations) and
               locations[j].date - locations[i].date <= timedelta(minutes=4) and
               locations[j].position.distance(locations[i].position) < 0.02):  # 0.02 km = 20 m
            j += 1
        if j - i > 1 and locations[j-1].date - locations[i].date >= timedelta(minutes=4):
            incidentes.append(locations[i])
            i = j
        else:
            i += 1
    print(f"desviaciones = {len(desviaciones)}, incidentes = {len(incidentes)}")
