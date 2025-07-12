from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Location
from asgiref.sync import async_to_sync
class VehicleLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vehicle_id = self.scope['url_route']['kwargs']['vehicle_id']
        self.group_name = f'vehicle_{self.vehicle_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print("ENTRO AL RECEIVE")
        data = json.loads(text_data)

        await sync_to_async(Location.objects.create)(
            vehicle_id=self.vehicle_id,
            latitude=data['latitude'],
            longitude=data['longitude']
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'location_update',
                'latitude': data['latitude'],
                'longitude': data['longitude'],
            }
        )

    async def location_update(self, event):
        await self.send(text_data=json.dumps({
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))