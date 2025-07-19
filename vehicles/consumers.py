import time

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from django.conf import settings

from vehicles.models import VehicleLocation

class VehicleLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]
        self.group_name = f"ride_{self.ride_id}"

        # Initialize redis client
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding = 'utf-8',
            decode_responses = True
        )

        # Subscribe the socket to the ride's group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        lat = data.get('lat')
        lng = data.get('lng')

        if lat is None or lng is None:
            return

        # Save location in redis
        timestamp = time.time()
        key       = f"ride:{self.ride_id}:locations"
        member = json.dumps({
            "lat":       lat,
            "lng":       lng,
            "timestamp": timestamp
        })

        await self.redis.zadd(key, {member: timestamp})
        await self.redis.expire(key, 60*60*24)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type":      "send_location",
                "lat":       lat,
                "lng":       lng,
                "timestamp": timestamp
            }
        )

    async def send_location(self, event):
        await self.send(text_data=json.dumps({
            "lat":        event["lat"],
            "lng":        event["lng"],
            "timestamp":  event["timestamp"]
        }))