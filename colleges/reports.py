from collections import Counter
from django.db.models import Count, Sum
from trips.models import Trip, PassengerTrip, Rate, TripReport
from users.models import User
from vehicles.models import Vehicle
from django.db import models
from routes.models import Route

def get_mobility_report(college, start_date, end_date):
    # Filter trips by institution and dates
    students = User.objects.filter(college=college)
    vehicles = Vehicle.objects.filter(user_id__college=college)
    drivers = User.objects.filter(college=college)
    trips = Trip.objects.filter(
        driver__in=drivers,
        vehicle__in=vehicles,
        date__range=(start_date, end_date)
    )

    # Usage frequency per student
    student_trip_counts = PassengerTrip.objects.filter(
        passenger__in=students,
        trip__in=trips
    ).values('passenger', 'passenger__username').annotate(count=Count('id'))

    # Usage frequency per driver
    driver_trip_counts = trips.values('driver', 'driver__username').annotate(count=Count('id'))

    # Usage frequency per vehicle
    vehicle_trip_counts = trips.values('vehicle').annotate(count=Count('id'))

    # Most demanded time slots (by start hour)
    hour_counts = trips.exclude(start_time=None).values_list('start_time', flat=True)
    hour_counter = Counter([t.hour for t in hour_counts])
    top_hours = hour_counter.most_common(3)

    # Most demanded routes
    route_counts = trips.values('route', 'route__name').annotate(count=Count('id')).order_by('-count')[:3]

    return {
        'student_trip_counts': list(student_trip_counts),
        'driver_trip_counts': list(driver_trip_counts),
        'vehicle_trip_counts': list(vehicle_trip_counts),
        'top_hours': top_hours,
        'top_routes': list(route_counts),
    }

def get_performance_report(college, start_date, end_date):
    # Filter institution drivers
    drivers = User.objects.filter(college=college)
    # Filter trips of those drivers in the date range
    trips = Trip.objects.filter(
        driver__in=drivers,
        date__range=(start_date, end_date)
    )
    # Filter ratings for those trips
    rates = Rate.objects.filter(trip__in=trips)

    # Passenger ratings and comments
    passenger_feedback = rates.values('passenger', 'comment')

    # Average rating per driver
    avg_ratings = rates.values('trip__driver', 'trip__driver__username').annotate(
        avg_ratting=models.Avg('ratting'),
        total=models.Count('id')
    )
    # Security report: incidents and total trips
    trip_reports = TripReport.objects.filter(trip__in=trips)
    total_incidents = trip_reports.aggregate(total=Sum('incidents'))['total'] or 0
    total_deviations = trip_reports.aggregate(total=Sum('deviations'))['total'] or 0
    total_trips = trips.count()

    return {
        'passenger_feedback': list(passenger_feedback),
        'driver_avg_ratings': list(avg_ratings),
        'total_incidents': total_incidents,
        'total_deviations': total_deviations,
        'total_trips': total_trips,
    }
