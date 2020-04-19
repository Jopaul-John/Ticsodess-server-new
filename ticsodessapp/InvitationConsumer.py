from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid

class InvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting to invitation ")
        self.room_name = self.scope['url_route']['kwargs']['username']
        print("room_name = ",self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("text data = ",(text_data_json))
        
        message = "true" if text_data_json.get("connect") == "true" else "false"
        user = text_data_json.get("user")
        if not user == None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'invitationSetup',
                    'message': message,
                    'user': user
                }
            )
        elif text_data_json.get("room_name"):
            print(text_data)
            print("Hoyyare hoyya")
            message = text_data_json["room_name"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'invitationStatus',
                    'message': message
                }
            ) 
        elif text_data_json.get("invitation_accept") == "false":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'invitationReject',
                    'message': "false"
                }
            )
        else:
            print("No matching case for ",text_data_json.keys())
       

    async def invitationSetup(self, event):
        message = event['message']
        user = event["user"]
        await self.send(text_data=json.dumps({
            'connection_status': message,
            'user':user
        }))

    async def invitationStatus(self,event):
        message = event["message"]
        print("Message invitationstatus = ",message)
        await self.send(text_data=json.dumps({
            'room_name': message,
        }))

    async def invitationReject(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            'invitationStatus': message,
        }))

