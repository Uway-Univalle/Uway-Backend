import datetime
import json
import time

from celery import shared_task
from django.conf import settings
from django.contrib.gis.geos import Point
from redis import Redis

from trips.models import Trip
from vehicles.models import VehicleLocation


@shared_task
def flush_locations_to_db():
    """
    Flushes vehicle locations from Redis to the database for all active trips.
    This task retrieves all vehicle locations stored in Redis for trips that are currently in progress,
    converts them into `VehicleLocation` objects, and saves them in the database. After saving, it removes
    the processed locations from Redis.
    """
    now_ts = time.time()
    redis = Redis.from_url(settings.REDIS_URL, encoding='utf-8', decode_responses=True)
    active = Trip.objects.filter(status='IN_PROGRESS').values_list('id', flat=True)
    for trip_id in active:
        key = f"ride:{trip_id}:locations"
        raws = redis.zrangebyscore(key, 0, now_ts)
        objs = []
        for entry in raws:
            d = json.loads(entry)
            objs.append(
                VehicleLocation(
                    trip_id = trip_id,
                    vehicle = Trip.objects.get(id=trip_id).vehicle,
                    position = Point(d['lng'], d['lat'], srid=4326),
                    date = datetime.datetime.fromtimestamp(d['timestamp'], tz=datetime.UTC)
                )
            )

        VehicleLocation.objects.bulk_create(objs)
        redis.zremrangebyscore(key, 0, now_ts)