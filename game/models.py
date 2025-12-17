import uuid
from django.db import models

class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.id})"


class Room(models.Model):
    STATUS_CHOICES = [
        ("waiting", "waiting"),
        ("roles_assigned", "roles_assigned"),
        ("guess_submitted", "guess_submitted"),
        ("result", "result"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name="created_rooms")
    players = models.ManyToManyField(Player, through="RoomPlayer")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="waiting")

    roles = models.JSONField(null=True, blank=True)          # maps player_id -> role
    mantri_guess = models.JSONField(null=True, blank=True)   # {"by": player_id, "guessed": player_id}
    round_result = models.JSONField(null=True, blank=True)   # structure with points

    round = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id} ({self.status})"


class RoomPlayer(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "player")
