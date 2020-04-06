from rest_framework import serializers
from ticsodessapp.models import User, GameRoom, Game_Model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','id','username','won','lost','played']
        extra_kwargs = {"password":{"write_only":True}}

class GameRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRoom
        exclude = []
        
class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email","username","is_online","is_busy","imageUrl"]

class GameModelSerializer(serializers.ModelSerializer):
    player1 = serializers.CharField(read_only=True)
    player2 = serializers.CharField(read_only=True)
    class Meta:
        model = Game_Model
        fields = ["room","player1","player2","first_player"]