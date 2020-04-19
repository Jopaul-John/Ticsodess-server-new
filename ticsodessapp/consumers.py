from channels.generic.websocket import AsyncWebsocketConsumer
import json
from ticsodessapp.models import GameRoom, User, Game_Model
from ticsodessapp.AI import getAIMove
import numpy as np

class TicsodessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting to gameroom ")
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
        print("text data = ",(text_data_json))
        if text_data_json.get("firstPlayer"):
            message = text_data_json
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'firstPlayer',
                'message': message
            }
        )
        elif text_data_json.get("movement"):
            message = text_data_json["movement"]
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'makeMove',
                'message': message
            }
        )
        elif text_data_json.get("GameOver"):
            message = text_data_json["GameOver"]
            message["winner"] = text_data_json["Winner"]
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'gameOver',
                'message': message
            }
        )
        elif text_data_json.get("startgame"):
            message = text_data_json["startgame"]
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'startGame',
                'message': message
            }
        )
        elif text_data_json.get("player") == "botmon":
            message = text_data_json
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'aiMove',
                'message': message
            }
        )
        elif text_data_json.get("MultiplayerStatus") == "true":
            message = text_data_json
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'multiplayerConnection',
                'message': message
            }
        )
        elif text_data_json.get("killGame") == "true":
            message = text_data_json
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'killGame',
                'message': message
            }
        )
            await self.disconnect(0)    

    async def firstPlayer(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'firstPlayer': message["firstPlayer"],
            "gamename": message["gamename"]
        }))

    async def makeMove(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'movement': message
        }))
    
    async def gameOver(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'gameOver': message
        }))

    async def startGame(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'startGame': message
        }))

    async def aiMove(self, event):
        message = event['message']
        # print(message)
        move = getAIMove(np.array(message["board"]),np.array(message["boardList"]),int(message["lastMove"]),int(message["playerMark"]))
        await self.send(text_data=json.dumps({
            'aimove': str(move)
        }))
    
    async def multiplayerConnection(self, event):
        message = event['message']
        # print(message)
        await self.send(text_data=json.dumps({
            'MultiplayerStatus': message
        }))

    async def killGame(self, event):
        message = event['message']
        # print(message)
        await self.send(text_data=json.dumps({
            'killgame': message
        }))


