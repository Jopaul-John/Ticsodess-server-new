from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
from ticsodessapp.models import User
from asgiref.sync import sync_to_async
from urllib.parse import urlparse

class InvitationConsumerNew(AsyncWebsocketConsumer):
    """  
        sends the player movements and game updates
        checks for the win/lose
        send the board positions
    """
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
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
        canStartGame = text_data_json.get("startGame")
        isMove = text_data_json.get("isMove")
        isExit = text_data_json.get("isexit")
        if canStartGame:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'startGame',
                    'message': text_data_json,
                }
            )
        elif isMove:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'sendMove',
                    'message': text_data_json,
                }
            )
        elif isExit:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'userExited',
                    'message': text_data_json,
                }
            )
       
    async def startGame(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'startGame': message["startGame"],
            "player1" : message["player1"],
            "player2": message["player2"]
        }))

    async def sendMove(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'player': message["player"],
            'move': message["move"],
            'playerValue' : message["value"],
            "isMove" : True
        }))
    async def userExited(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'player': message["player"],
            'isexit': True
        }))

def setUserOnline(userMail):
    user = User.objects.get(id=userMail)
    user.is_online = True
    user.save()

def setUserOffline(userMail):
    user = User.objects.get(id=userMail)
    user.is_online = False
    user.is_busy = False
    user.save()

class InvitationConsumerFriend(AsyncWebsocketConsumer):
    """  
        invites the user for invitations/rejections etc
    """
    async def connect(self):
        user = self.scope["query_string"].decode("utf-8") 
        import threading
        # async to synch requires threading !
        t = threading.Thread(target=setUserOnline, args=[user])
        t.setDaemon(True)
        t.start()
        self.room_group_name = "invitation"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        user = self.scope["query_string"].decode("utf-8") 
        import threading
        t = threading.Thread(target=setUserOffline, args=[user])
        t.setDaemon(True)
        t.start()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        isInvitation = text_data_json.get("isinvitation")
        isStartGame = text_data_json.get("startGame")
        isrejected = text_data_json.get("invitationRejected")
        if isInvitation:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'sendInvitation',
                    'message': text_data_json,
                }
            )
        elif isStartGame:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'startGame',
                    'message': text_data_json,
                }
            )
        elif isrejected:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'rejectInvitation',
                    'message': text_data_json,
                }
            )
       
    async def sendInvitation(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            "sender": message["sendingUserName"],
            "target": message["targetUserName"],
            "gameTime": message["gameType"],
            "isinvitation": True,
            "roomName": message["gameRoom"],
            "sendername": message["sendername"]
        }))

    async def startGame(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            "startGame" : True,
            "player1": message["user1"],
            "player2": message["user2"]
        }))

    async def rejectInvitation(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            "invitationRejected" : True,
            "sender": message["sender"]
        }))
