from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ticsodessapp.models import Game_Model, User, GameRoom, SocialLogin
from ticsodessapp.serializers import FriendSerializer, GameRoomSerializer, UserSerializer, GameModelSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
import random
import uuid
from ticsodessapp.AI import getAIMove
import base64
import requests
from django.db import transaction
import time
import requests
import os
from rest_framework.authtoken.models import Token
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from io import BytesIO

UnProhibitedNames = ["fuck", "suck", "dick", "cunt", "boob", "vagina", "ass", "anal", "sex", "bikini", "penis", "rectum", "nipple", "69", "whore", "bitch", "horny"]
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
            return Response({"data": gameRoom.data}, status=status.HTTP_200_OK)

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
        print("friend = ", friend)
        try:
            friendmodel = User.objects.get(username=friend)
            print("username = ", friendmodel.email)
            friendmodelserializer = FriendSerializer([friendmodel], many=True)
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
    def post(self, request):
        user = User.objects.get(email=request.user)
        if request.data["status"] == "true":
            user.is_online = True
            user.save()
            return Response({"user": "user is online now"})
        else:
            user.is_online = False
            user.save()
            return Response({"user": "user is offline now"})


class BusyStatus(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        if request.data["status"] == "true":
            user.is_busy = True
            user.save()
            return Response({"user": "user is busy now"})
        else:
            user.is_busy = False
            user.save()
            return Response({"user": "user is not busy now"})


class LogoutView(APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class AiHandOver(APIView):
    def get(self, request):
        room = request.query_params.get("room")
        model = Game_Model.objects.get(room__room_name=room)
        model.player1 = User.objects.get(username="botmon")
        model.save()
        return Response({})


class ReleaseResource(APIView):
    def post(self, request):
        room = request.data["room"]
        print("releasing room = ", room)
        try:
            room = GameRoom.objects.get(room_name=room)
            room.delete()
        except:
            pass
        return Response({})


class Winner(APIView):
    def post(self, request):
        winner = request.data["player1"]
        loser = request.data["player2"]
        user = User.objects.get(email=winner)
        user.won += 1
        user.played += 1
        user.save()
        user = User.objects.get(email=loser)
        loser.lost += 1
        user.played += 1
        user.save()
        return Response({"status:true"})


def multiFriend(user):
    gameRoom = None
    try:
        with transaction.atomic():
            user.is_busy = True
            user.save()
            gameRoom = GameRoom.objects.select_for_update().filter(
                is_full=False, is_friend=False).earliest('id')
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


def checkNewOnlinePlayer(user, gameRoom, gameModel, i):
    try:
        if i > 4:
            print("checking number", i)
            bot = User.objects.get(username="botmon")
            gameRoom = GameRoom.objects.get(
                room_name=gameRoom.data[0]["room_name"])
            gameRoom.is_full = True
            gameRoom.save()
            gameRoom = GameRoomSerializer([gameRoom], many=True)
            gameRoom.data[0]["creator"] = gameModel.player1.username
            print(gameRoom.data, gameModel.room.room_name)
            return gameRoom, gameModel
        else:
            time.sleep(0.5)
            i += 1
            print("incrementing i", i)
            return checkNewOnlinePlayer(user, gameRoom, gameModel, i)
    except Exception as e:
        print(e)


@authentication_classes([])
@permission_classes([])
class TempUser(APIView):

    def get(self, request):
        userName = str(uuid.uuid4())
        email = userName + "@ticsodess.com"
        password = str(uuid.uuid4())
        userObject = User.objects.create(
            email=email, username=userName, password=password)
        token = Token.objects.create(user=userObject)
        print(token)
        user = UserSerializer(instance=userObject)
        return Response({"data": user.data, "token": token.key})

# here starts the new code


class ArtificialIntelligence(APIView):

    def get(self, request):
        board = np.fromstring(request.query_params.get(
            "board"), dtype="int", sep=",")
        boardList = np.fromstring(request.query_params.get(
            "boardList"), dtype="int", sep=",")
        lastMove = int(request.query_params.get("lastMove"))
        marker = int(request.query_params.get("marker"))
        move = getAIMove(board, boardList, lastMove, marker)
        return Response({"move": move})


class GameRoomViewNew(APIView):

    def post(self, request):
        player = request.data["username"]
        isFriend = request.data["isfriend"]
        user = User.objects.get(username=player)
        gameRoom = GameRoom.objects.filter(is_full=False, is_friend=isFriend)
        print("Gameroom = ", gameRoom)
        if len(gameRoom) == 0:
            botUser = User.objects.filter(email__contains="botmon@bot")[0]
            gameRoom = GameRoom.objects.create(
                room_name=str(uuid.uuid4()), is_friend=isFriend)
            gameModel = Game_Model.objects.create(
                room=gameRoom, player1=user, player2=botUser)
        else:
            gameRoom = gameRoom[0]
            gameRoom.is_full = True
            gameRoom.save()
            gameModel = Game_Model.objects.get(room=gameRoom)
            gameModel.player2 = user
            gameModel.save()
        gameRoomSerialzed = GameRoomSerializer(gameRoom)
        gameModelSer = GameModelSerializer(gameModel)
        return Response({"data": gameRoomSerialzed.data, "gameModel": gameModelSer.data})


class SwitchToBotPlayer(APIView):
    def post(self, request):
        confirmation = False
        roomName = request.data["gameRoom"]
        gameRoom = GameRoom.objects.get(room_name=roomName)
        if not gameRoom.is_full:
            gameRoom.is_full = True
            gameRoom.save()
            confirmation = True
        gameRoom = GameRoomSerializer(gameRoom)
        return Response({"data": gameRoom.data, "confirmation": confirmation})


class TemperoryUser(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data["ipaddress"]
        user = User.objects.get_or_create(email=email + "@ticsodess.com",
                                          username=email, is_online=True)
        token = Token.objects.create(user=user[0])
        userserialized = UserSerializer(instance=user[0])
        return Response({"data": userserialized.data, "token": token.key})


class Friends(APIView):
    def get(self, request):
        userMail = request.query_params.get("userMail")
        user = User.objects.get(username=userMail)
        friends = list(user.friends.all())
        print(friends)
        friendsSerilaized = FriendSerializer(friends, many=True)
        return Response({"data": friendsSerilaized.data})


class FriendSearch(APIView):
    def get(self, request):
        userMail = request.query_params.get("userMail")
        try:
            user = User.objects.get(username=userMail)
            if not user.is_online:
                return Response({"error": "User is not online"})
            elif user.is_busy:
                return Response({"error": "User is busy"})
            else:
                friendsSerilaized = FriendSerializer(user)
                return Response({"data": friendsSerilaized.data})
        except:
            return Response({"error": "No user exists"})


class FriendRoom(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        gameRoom = GameRoom.objects.create(
            room_name=str(uuid.uuid4()), is_friend=True)
        gameObject = Game_Model.objects.create(
            room=gameRoom, player1=user, player2=user)
        gameRoomSerialzed = GameRoomSerializer(gameRoom)
        return Response({"data": gameRoomSerialzed.data})


class JoinFriend(APIView):
    def get(self, request):
        userMail = request.query_params.get("username")  # mail name actually
        roomName = request.query_params.get("roomName")
        user = User.objects.get(username=userMail)
        room = GameRoom.objects.get(room_name=roomName)
        room.is_full = True
        room.save()
        gameModel = Game_Model.objects.get(room=room)
        gameModel.player2 = user
        gameModel.save()
        gameModelSerialized = GameModelSerializer(gameModel)
        return Response({"startGame": True, "data": gameModelSerialized.data})


class UserDetails(APIView):

    def get(self, request):
        print(request.user)
        user = User.objects.get(email=request.user)
        userserialized = UserSerializer(user)
        return Response({"data": userserialized.data})


class SocialLoginView(APIView):
    
    def post(self, request):
        userMail = None
        userImage = None
        accessToken = request.data.get("acesstoken")
        print(request.data)
        userid = request.data["userID"]
        if not accessToken:
            return Response({"data" : "No access token were found!"})
        if request.data["backend"] == "facebook":
            userMail = request.user
            data = requests.get("https://graph.facebook.com/v8.0/" + userid + "/picture")
            userImage = data.url
        elif request.data["backend"] == "google":
            userMail = request.data["email"]
            userImage = request.data["imageurl"]
        if request.user:
            user = User.objects.get(email=request.user)
        else:
            user = User.objects.create(email=userMail)
        
        user.usernameUpdated = False
        user.imageUrl = userImage
        user.email = userMail
        user.save()
        try:
            socialUser = SocialLogin.objects.get(email=userMail)
        except:
            socialUser = SocialLogin.objects.create(user=user)
        socialUser.userID = userid
        socialUser.socialmedia = request.data["backend"]
        socialUser.accessToken = accessToken
        socialUser.save()
        userserialized = UserSerializer(user)
        return Response({'data':userserialized.data})

class BusyView(APIView):
    def get(self, request):
        print("in busy view", request.query_params.get("isbusy"))
        user = User.objects.get(email=request.user)
        if request.query_params.get("isbusy") == "true":
            user.is_busy = True
        else:
            user.is_busy = False
        user.save()
        return Response({"user": "user is not busy now"})

class UpdateStatsAndRelease(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        try:
            opponent = User.objects.get(email=request.data["opponent"])
            user.friends.add(opponent)
        except:
            print("No user with email ", request.data["opponent"])
        user.points += int(request.data["points"])
        user.played += 1 
        user.won += int(request.data["won"])
        user.lost += int(request.data["lost"])
        user.is_busy = False
        user.save()
        userserialized = UserSerializer(user)
        return Response({"data": userserialized.data})

class UpdateUserName(APIView):
    def post(self, request):
        username = request.data["username"]
        user = None
        if any(name in username.lower() for name in UnProhibitedNames):
            return Response({"error": "Please choose a good name"})
        try:
            user = User.objects.get(username=username)
        except:
            pass
        if user:
            return Response({"error": "Username already taken. Please select a new name"})
        user = User.objects.get(email=request.user)
        user.username = username
        user.usernameUpdated = True
        user.save()
        userserializer = UserSerializer(user)
        return Response({"data": userserializer.data})

class UserStats(APIView):
    def post (self, request):
        username = request.user
        points = request.data.get("points")
        isWin = request.data["isWin"]
        print(request.data)
        opponentName = request.data.get("opponent")
        if isWin == "true":
            isWin = True
        else:
            isWin = False
        isDraw = request.data["isDraw"]
        if isDraw == "true":
            isDraw = True
        else:
            isDraw = False
        user = User.objects.get(email=username)
        try:
            opponentuser = User.objects.get(username=opponentName)
        except:
            pass
        user.friends.add(opponentuser)
        user.played += 1
        user.is_busy = False
        if not points:
            if isWin:
                user.won += 1
                user.points += 10
            elif not isWin and not isDraw:
                user.lost += 1
                user.points += -10
        else:
            if isWin:
                user.won += 1
                user.points += points 
            elif not isWin and not isDraw:
                user.lost += 1
                user.points += points
            else:
                user.points += points
        user.save()
        return Response({"message" : "Userdata updated"})

class ShareImage(APIView):
    def get(self, request):
        username = request.data["Username"]
        level = request.data["level"]
        img = Image.open("../white.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("../agengsans.ttf", 72)
        draw.text((900, 20),username + " have reached level " + level + " !!!",(200,200,200),font=font)
        buffered = BytesIO()
        img.save(buffered, format="png")
        img_str = base64.b64encode(buffered.getvalue())
        return Response({"image": img_str})