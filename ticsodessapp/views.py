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
from django.utils.crypto import get_random_string

""" 
    Since kids are targeted, certain names are prohibited
"""
UnProhibitedNames = ["fuck", "suck", "dick", "cunt", "boob", "vagina", "ass", "anal",
                     "sex", "bikini", "penis", "rectum", "nipple", "69", "whore", "bitch", "horny"]


class ArtificialIntelligence(APIView):
    """ 
        get API calls from the client with lastmove, marker, board and boardlist(subboard list)
        returns the best move with these params
    """

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
    """ 
        user requests for a game room.
        if there are free rooms, then a room is returned
        else a room is created
        parameter includes, isfriend and is full
        returns gameroom data and game model
     """

    def post(self, request):
        player = request.data["username"]
        isFriend = request.data["isfriend"]
        user = User.objects.get(username=player)
        gameRoom = GameRoom.objects.filter(is_full=False, is_friend=isFriend)
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
    """ 
        switches opponent player to bot
        there are cases where online players are less, hence user should not wait long enough
        10 seconds waiting time is given, if there are no new users, the opponent swtiches to AI
        Not mentioned to the user for better user experience  
        returns game room data and a confirmation
    """

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
    """ 
        creates a temporary authentication for user 
        returns user serialized data with a token
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = get_random_string(15)
        user = User.objects.get_or_create(email=email + "@ticsodess.com",
                                          username=email, is_online=True)
        token = Token.objects.create(user=user[0])
        userserialized = UserSerializer(instance=user[0])
        return Response({"data": userserialized.data, "token": token.key})


class Friends(APIView):
    """ 
        finds and returns the current user friends
    """

    def get(self, request):
        userMail = request.query_params.get("userMail")
        user = User.objects.get(username=userMail)
        friends = list(user.friends.all())
        friendsSerilaized = FriendSerializer(friends, many=True)
        return Response({"data": friendsSerilaized.data})


class FriendSearch(APIView):
    """ 
        search for a specific friend for "friend game"
        returns the user / error messages
    """

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
    """ 
        creates a room specfic for friend game
        so that room is not used for random/ ai games
        returns room data
    """

    def get(self, request):
        user = User.objects.get(email=request.user)
        gameRoom = GameRoom.objects.create(
            room_name=str(uuid.uuid4()), is_friend=True)
        gameObject = Game_Model.objects.create(
            room=gameRoom, player1=user, player2=user)
        gameRoomSerialzed = GameRoomSerializer(gameRoom)
        return Response({"data": gameRoomSerialzed.data})


class JoinFriend(APIView):
    """ 
        friend is joined in the current room
        room is marked as full, so noone else joins the room
        returns a message to start the game and game model data
    """

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
    """
        returns the user stats
    """

    def get(self, request):
        user = User.objects.get(email=request.user)
        userserialized = UserSerializer(user)
        return Response({"data": userserialized.data})


class SocialLoginView(APIView):
    """ 
       social authentication method
       google and fb are used RN.
       gets the user profile pic and email
       saves in the social user model
       returns the new user model containing the new DP and email  
    """

    def post(self, request):
        userMail = None
        userImage = None
        accessToken = request.data.get("acesstoken")
        userid = request.data["userID"]
        if not accessToken:
            return Response({"data": "No access token were found!"})
        if request.data["backend"] == "facebook":
            userMail = request.user
            data = requests.get(
                "https://graph.facebook.com/v8.0/" + userid + "/picture")
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
        return Response({'data': userserialized.data})


class BusyView(APIView):
    """ 
        checks if the user is busy, blocks the game request
    """

    def get(self, request):
        user = User.objects.get(email=request.user)
        if request.query_params.get("isbusy") == "true":
            user.is_busy = True
        else:
            user.is_busy = False
        user.save()
        return Response({"user": "user is not busy now"})


class UpdateStatsAndRelease(APIView):
    """ 
        update the user stats and busy stats are negated
    """

    def post(self, request):
        user = User.objects.get(email=request.user)
        try:
            opponent = User.objects.get(email=request.data["opponent"])
            user.friends.add(opponent)
        except:
            return Response({"No user name"})
        user.points += int(request.data["points"])
        user.played += 1
        user.won += int(request.data["won"])
        user.lost += int(request.data["lost"])
        user.is_busy = False
        user.save()
        userserialized = UserSerializer(user)
        return Response({"data": userserialized.data})


class UpdateUserName(APIView):
    """
        User name is updated, just once
    """
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
    """ 
        updates user stats to boost points
        adds the opponent to recently played
    """
    def post(self, request):
        username = request.user
        points = request.data.get("points")
        isWin = request.data["isWin"]
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
            user.friends.add(opponentuser)
        except:
            pass
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
        return Response({"message": "Userdata updated"})


class ShareImage(APIView):
    """ 
        creates an image so user can share it in fb/social networks
    """
    def get(self, request):
        username = request.data["Username"]
        level = request.data["level"]
        img = Image.open("../white.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("../agengsans.ttf", 72)
        draw.text((900, 20), username + " have reached level " +
                  level + " !!!", (200, 200, 200), font=font)
        buffered = BytesIO()
        img.save(buffered, format="png")
        img_str = base64.b64encode(buffered.getvalue())
        return Response({"image": img_str})


# privacy policy 
def privacyPolicy(request):
    return render(request, "ticsodessapp/privacy.html")
