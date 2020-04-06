from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ticsodessapp.models import Game_Model, User, GameRoom
from ticsodessapp.serializers import FriendSerializer, GameRoomSerializer, UserSerializer, GameModelSerializer
from rest_framework.permissions import IsAuthenticated
import random
import uuid
from ticsodessapp.AI import getAIMove
import base64
import requests
from django.db import transaction
import time

class UserImageView(APIView):
    def post(self, request):
        print("creating image", request.data)
        user = User.objects.get(email=request.user)
        user.imageUrl = request.data["imageUrl"]
        user.save()
        return Response({}, status=status.HTTP_201_CREATED)


class UserFriends(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        friends = FriendSerializer(user.friends.all(), many=True)
        for friendData, friend in zip(friends.data, user.friends.all()):
            friendData["image"] = str(base64.b64encode(
                requests.get(friend.imageUrl).content))
        return Response({"data": friends.data}, status=200)


class UserProfileView(APIView):
    serializer_class = UserSerializer

    def get(self, request, format=None):
        print(request.user)
        user = User.objects.get(email=request.user)
        user = UserSerializer([user], many=True)
        if user:
            return Response({"data": user.data}, status=200)
        else:
            return Response(False, status=200)

    def post(self, request, format=None):
        print("User = ", request.user)
        user, created = User.objects.get_or_create(email=request.user)
        if not created:
            user.country = request.data['country_name']
            user.place = request.data['place_name']
            user.save()
            user = UserSerializer([user], many=True)
            print(user.data)
            return Response({"data": user.data}, status=status.HTTP_201_CREATED)


class GameRoomView(APIView):
    serializer_class = GameRoomSerializer

    def get(self, request, format=None):
        _is_friend = False if request.query_params.get(
            "is_friend_game") == "false" else True
        if _is_friend:
            player1 = request.query_params.get("player1")
            player2 = request.query_params.get("player2")
            print(player1, player2)
            player1 = User.objects.get(email=player1)
            player2 = User.objects.get(email=player2)
            player1.is_busy = True
            player1.save()
            player2.is_busy = True
            player2.save()
            gameRoom = GameRoom.objects.create(room_name=str(
                uuid.uuid4()), is_friend=True, is_full=True)
            gameModel = Game_Model.objects.create(
                room=gameRoom, player1=player1, player2=player2)
            gameRoom = GameRoomSerializer([gameRoom], many=True)
            return Response({"data": gameRoom.data}, status=status.HTTP_200_OK)
        else:
            user = User.objects.get(email=request.user)
            gameRoom, gameModel = multiFriend(user)
            print(gameRoom.data[0]["is_full"])
            return Response({"data": gameRoom.data},status=status.HTTP_200_OK)
            # if gameRoom.data[0]["is_full"]:
            #     return Response({"data": gameRoom.data})
            # else:
            #     gameRoom, gameModel = checkNewOnlinePlayer(user,gameRoom,gameModel,0)
                # return Response({"data": gameRoom.data})

    def post(self, request):
        print("request data = ", request.data)
        username = request.data["username"]
        roomname = request.data["roomname"]
        gameModel = Game_Model.objects.get(room__room_name=roomname)
        if gameModel.first_player == "":
            gameModel.first_player = username
            gameModel.save()
            gameModel = GameModelSerializer([gameModel], many=True)
            return Response({"data": gameModel.data}, status=status.HTTP_200_OK)
        else:
            return Response({"data": "First Player is already choosed"}, status=status.HTTP_200_OK)


class FriendView(APIView):

    def get(self, request, format=None):
        friend = request.query_params.get("friend")
        print("friend = ",friend)
        try:
            friendmodel = User.objects.get(username=friend)
            print("username = ",friendmodel.email)
            friendmodelserializer = FriendSerializer([friendmodel],many=True)
            friendmodelserializer.data[0]["image"] = str(base64.b64encode(
                requests.get(friendmodel.imageUrl).content))
            return Response({"data": friendmodelserializer.data}, status=200)
        except Exception as e:
            print(e)
            friendmodel = None
            return Response({'response': "Username not found"}, status=status.HTTP_200_OK)


class GameModelView(APIView):
    def post(self, request, format=None):
        game_model = Game_Model.objects.get(room__room_name=request.room)
        game_model.score_o = int(request.oscore)
        game_model.score_x = int(request.xscore)
        game_model.save()


class AiView(APIView):
    def get(self, request, format=None):
        board = request.query_params.get("board")
        move = request.query_params.get("move")
        next_move = alphabetaPrune(board, "x", -1000, 1000, 0)[1]
        return Response({'next_move': next_move}, status=status.HTTP_200_OK)

class UserStatusView(APIView):
    def post(self,request):
        user = User.objects.get(email=request.user)
        if request.data["status"] == "true":
            user.is_online = True
            user.save()
            return Response({"user":"user is online now"})
        else:
            user.is_online = False
            user.save()
            return Response({"user":"user is offline now"})

class BusyStatus(APIView):
    def post(self,request):
        user = User.objects.get(email=request.user)
        if request.data["status"] == "true":
            user.is_busy = True
            user.save()
            return Response({"user":"user is busy now"})
        else:
            user.is_busy = False
            user.save()
            return Response({"user":"user is not busy now"})

class LogoutView(APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class AiHandOver(APIView):
    def get(self,request):
        room = request.query_params.get("room")
        model = Game_Model.objects.get(room__room_name=room)
        model.player1 = User.objects.get(username="botmon")
        model.save()
        return Response({})

class ReleaseResource(APIView):
    def get(self,request):
        room = request.query_params.get("room")
        room = GameRoom.objects.get(room_name=room)
        room.delete()
        return Response({})
        
class Winner(APIView):
    def post(self,request):
        winner = request.data["player1"]
        loser = request.data["player2"]
        user = User.objects.get(email=winner)
        user.won += 1
        user.save()
        user = User.objects.get(email=loser)
        loser.lost += 1
        user.save()
        return Response({"status:true"})
def multiFriend(user):
    gameRoom = None
    try:
        with transaction.atomic():
            user.is_busy = True
            user.save()
            gameRoom = GameRoom.objects.select_for_update().filter(is_full=False, is_friend=False).earliest('id')
            gameRoom.is_full = True
            gameRoom.save()
            gameModel = Game_Model.objects.get(room=gameRoom)
            gameModel.player2 = user
            gameModel.save()
            gameRoom = GameRoomSerializer([gameRoom], many=True)
            gameRoom.data[0]["creator"] = gameModel.player1.username
            return gameRoom, gameModel
    except:
        gameRoom = GameRoom.objects.create(room_name=str(
            uuid.uuid4()), is_friend=False, is_full=False)
        bot = User.objects.get(username="botmon")
        gameModel = Game_Model.objects.create(
            room=gameRoom, player1=user, player2=bot)
        gameModel.save()
        gameRoom = GameRoomSerializer([gameRoom], many=True)
        gameRoom.data[0]["creator"] = gameModel.player1.username
    return gameRoom, gameModel
        

def checkNewOnlinePlayer(user,gameRoom,gameModel,i):
    try:
        if i >4 :
            print("checking number",i)
            bot = User.objects.get(username="botmon")
            gameRoom = GameRoom.objects.get(room_name=gameRoom.data[0]["room_name"])
            gameRoom.is_full = True
            gameRoom.save()
            gameRoom = GameRoomSerializer([gameRoom], many=True)
            gameRoom.data[0]["creator"] = gameModel.player1.username
            print(gameRoom.data,gameModel.room.room_name)
            return gameRoom, gameModel
        else:
            time.sleep(0.5)
            i += 1
            print("incrementing i",i)
            return checkNewOnlinePlayer(user,gameRoom,gameModel,i)
    except Exception as e:
        print(e)

