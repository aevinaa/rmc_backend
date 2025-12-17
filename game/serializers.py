from rest_framework import serializers
from .models import Player, Room, RoomPlayer

class PlayerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "username", "display_name")

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "status", "round", "created_at")

class RoomPlayerSerializer(serializers.Serializer):
    player_id = serializers.UUIDField()
    username = serializers.CharField()
    display_name = serializers.CharField(allow_blank=True)
