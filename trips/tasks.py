from celery import shared_task
from datetime import timedelta

from vehicles.models import VehicleLocation
from .models import Trip, TripReport


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

    deviations = count_deviations(locations, trajectory)
    incidents = count_incidents(locations)

    TripReport.objects.create(
        trip=trip,
        incidents=incidents,
        deviations=deviations
    )

def count_incidents(locations):
    """
    Counts the number of incidents in a list of vehicle locations.
    An incident is defined as a stop of at least 4 minutes within a 20-meter radius.
    :param locations: List of VehicleLocation objects ordered by date.
    :return: Number of incidents found.
    """
    incidents = 0
    n = len(locations)
    i = 0
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
            incidents += 1
            # Skip all points up to k to avoid marking again
            i = k + 1
        else:
            i += 1

    return incidents

def count_deviations(locations, trajectory):
    """
    Counts the number of deviations in a list of vehicle locations.
    A deviation is defined as a location that is more than 150 meters away from the planned route.
    :param locations: List of VehicleLocation objects ordered by date.
    :param trajectory: The planned route as a LineString in EPSG:3857 projection.
    :return: Number of deviations found.
    """
    i = 0
    n = len(locations)
    deviations = 0

    while i < n:
        # If the current location is within 150 meters of the route, skip it, not a deviation
        if distance_to_route(locations[i], trajectory) <= 150:
            i += 1
            continue

        # We found a deviation, now find the segment of deviation
        start = locations[i]
        k = i

        # Move k forward while still deviating
        for j in range(i + 1, n):
            if distance_to_route(locations[j], trajectory) > 150:
                k = j
            else:
                break

        # We have a segment from i to k that is a deviation
        deviations += 1

        # Skip all points up to k to avoid counting them again
        i = k + 1

    return deviations

def transform_to_3857(location):
    """
    Transforms a location to the Web Mercator projection (EPSG:3857).
    """
    pt = location.clone()
    pt.transform(3857)
    return pt

def distance_to_route(location, route):
    """
    Calculates the distance from a location to a route.
    """
    point = location.position.clone()
    point.transform(3857)
    return point.distance(route)