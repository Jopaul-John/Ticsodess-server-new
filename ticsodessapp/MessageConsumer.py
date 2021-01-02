from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting to friends ")
        self.room_group_name = "friends"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("text data = ",(text_data_json))
        user = text_data_json.get("user")
        if text_data_json.get("status") == "online":
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'sendBusyStatus',
                'user': user
            }
        )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'sendOnlineStatus',
                    'user': user
                }
            )
       

    async def sendOnlineStatus(self, event):
        user = event["user"]
        await self.send(text_data=json.dumps({
            'refreshData': "true",
            'user':user
        }))

    async def sendBusyStatus(self, event):
        user = event["user"]
        await self.send(text_data=json.dumps({
            'busystatus': "yes",
            'user':user
        }))
