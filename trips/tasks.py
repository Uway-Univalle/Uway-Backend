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
    """
    Analyzes a specific trip to detect two types of events:
    1. Deviations: identifies locations where the vehicle was more than 150 meters away from the planned route.
    2. Incidents: detects prolonged stops (at least 4 minutes) within a 20-meter radius.

    Args:
        trip_id (int): The ID of the trip to analyze.
    """
    trip = Trip.objects.get(id=trip_id)
    route = trip.route  # Assuming it has a 'route' field with a LineString
    locations = VehicleLocation.objects.filter(trip=trip).order_by('date')

    # Detect deviations
    trajectory = route.trajectory.clone()
    trajectory.transform(3857)
    deviations = []
    for location in locations:
        point = location.position.clone()
        point.transform(3857)
        if point.distance(trajectory) > 150:
            deviations.append(location)

    # Detect incidents (stopped >= 4 min within a 20 m radius)
    incidents = []
    i = 0
    n = len(locations)
    while i < n:
        loc_i = locations[i]
        pt_i = loc_i.position.clone()
        pt_i.transform(3857)

        # Move k forward while still within 20 m
        k = i
        for j in range(i + 1, n):
            pt_j = locations[j].position.clone()
            pt_j.transform(3857)
            if pt_i.distance(pt_j) < 20:
                k = j
            else:
                break

        # If the duration between i and k is >= 4 min, it's an incident
        if locations[k].date - loc_i.date >= timedelta(minutes=4):
            incidents.append(loc_i)
            # Skip all points up to k to avoid marking again
            i = k + 1
        else:
            i += 1
    print(f"deviations = {len(deviations)}, incidents = {len(incidents)}")

def transform_to_3857(location):
    """
    Transforms a location to the Web Mercator projection (EPSG:3857).
    """
    pt = location.clone()
    pt.transform(3857)
    return pt