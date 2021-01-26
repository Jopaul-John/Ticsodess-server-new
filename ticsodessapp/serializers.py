from rest_framework import serializers
from ticsodessapp.models import User, GameRoom, Game_Model

""" 
    serialzes different model classes
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','id','username','won','lost','played', 'points', 'level','usernameUpdated', "imageUrl"]

class GameRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRoom
        exclude = []
        
class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email","username","is_online","is_busy","imageUrl", "id"]

class GameModelSerializer(serializers.ModelSerializer):
    player1 = FriendSerializer(read_only=True)
    player2 = FriendSerializer(read_only=True)
    class Meta:
        model = Game_Model
        fields = ["room","player1","player2","first_player"]