from channels.generic.websocket import AsyncWebsocketConsumer
import json

from vehicles.models import Location

class VehicleLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            "message": "Ubicación recibida correctamente"
        }))

    async def location_update(self, event):
        await self.send(text_data=json.dumps({
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))