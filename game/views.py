import random
from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Player, Room, RoomPlayer

# Base points (per-round holdings)
BASE_POINTS = {
    "Raja": 1000,
    "Mantri": 800,
    "Sipahi": 500,
    "Chor": 0
}

# Maximum players in a room
MAX_PLAYERS = 4

# Helper: get players in order they joined (for listing)
def get_room_players(room):
    rps = RoomPlayer.objects.filter(room=room).order_by("joined_at")
    players = []
    for rp in rps:
        players.append({
            "player_id": str(rp.player.id),
            "username": rp.player.username,
            "display_name": rp.player.display_name or rp.player.username
        })
    return players

# Helper: assign roles randomly to the 4 players (updates room.roles and status)
def assign_roles_to_room(room):
    rps = RoomPlayer.objects.filter(room=room).order_by("joined_at")
    players = [str(rp.player.id) for rp in rps]
    roles = ["Raja", "Mantri", "Chor", "Sipahi"]
    random.shuffle(roles)
    mapping = {}
    for pid, role in zip(players, roles):
        mapping[pid] = role
    room.roles = mapping
    room.status = "roles_assigned"
    room.save()
    return mapping

# Create Room
class CreateRoomView(APIView):
    def post(self, request):
        username = request.data.get("username")
        display_name = request.data.get("display_name", "")
        if not username:
            return Response({"detail": "username required"}, status=status.HTTP_400_BAD_REQUEST)
        player = Player.objects.create(username=username, display_name=display_name)
        room = Room.objects.create(creator=player)
        RoomPlayer.objects.create(room=room, player=player)
        data = {
            "room_id": str(room.id),
            "player_id": str(player.id),
            "status": room.status
        }
        return Response(data, status=status.HTTP_201_CREATED)

# Join Room (robust — validates UUID and trims whitespace)
class JoinRoomView(APIView):
    def post(self, request):
        room_id_raw = request.data.get("room_id")
        username = request.data.get("username")
        display_name = request.data.get("display_name", "")

        if not room_id_raw or not username:
            return Response({"detail": "room_id and username required"}, status=status.HTTP_400_BAD_REQUEST)

        room_id_str = str(room_id_raw).strip()

        # Validate UUID format
        try:
            UUID(room_id_str, version=4)
        except ValueError:
            return Response({"detail": "invalid room_id format (must be UUID)"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch room
        try:
            room = Room.objects.get(id=room_id_str)
        except Room.DoesNotExist:
            return Response({"detail": "room not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": "internal server error while fetching room", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if room.status != "waiting":
            return Response({"detail": "room not accepting players"}, status=status.HTTP_400_BAD_REQUEST)

        current_count = RoomPlayer.objects.filter(room=room).count()
        if current_count >= MAX_PLAYERS:
            return Response({"detail": "room full"}, status=status.HTTP_400_BAD_REQUEST)

        player = Player.objects.create(username=username, display_name=display_name)
        RoomPlayer.objects.create(room=room, player=player)

        # Auto assign when room reaches MAX_PLAYERS
        if RoomPlayer.objects.filter(room=room).count() == MAX_PLAYERS:
            assign_roles_to_room(room)

        return Response({
            "room_id": str(room.id),
            "player_id": str(player.id),
            "players_count": RoomPlayer.objects.filter(room=room).count()
        }, status=status.HTTP_201_CREATED)

# List players in room
class ListPlayersView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        players = get_room_players(room)
        return Response({"players": players})

# Assign roles manually (if you ever want to)
class AssignRolesView(APIView):
    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if room.status != "waiting":
            return Response({"detail": "cannot assign now"}, status=status.HTTP_400_BAD_REQUEST)
        count = RoomPlayer.objects.filter(room=room).count()
        if count != MAX_PLAYERS:
            return Response({"detail": "need 4 players to assign roles"}, status=status.HTTP_400_BAD_REQUEST)
        mapping = assign_roles_to_room(room)
        return Response({"assigned": True, "roles_assigned_to_count": len(mapping)})

# Get my role (private)
class MyRoleView(APIView):
    def get(self, request, room_id, player_id):
        room = get_object_or_404(Room, id=room_id)
        if not room.roles:
            return Response({"detail": "roles not yet assigned"}, status=status.HTTP_400_BAD_REQUEST)
        # validate player is in room
        if not RoomPlayer.objects.filter(room=room, player__id=player_id).exists():
            return Response({"detail": "player not in room"}, status=status.HTTP_403_FORBIDDEN)
        role = room.roles.get(player_id)
        if not role:
            return Response({"detail": "role not found for this player (maybe db mismatch)"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({"role": role})

# Submit guess (Mantri only)
class SubmitGuessView(APIView):
    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        player_id = request.data.get("player_id")
        guessed_player_id = request.data.get("guessed_player_id")
        if not player_id or not guessed_player_id:
            return Response({"detail": "player_id and guessed_player_id required"}, status=status.HTTP_400_BAD_REQUEST)
        if room.status not in ("roles_assigned",):
            return Response({"detail": "cannot accept guess in current room state"}, status=status.HTTP_400_BAD_REQUEST)
        if not room.roles:
            return Response({"detail": "roles not assigned"}, status=status.HTTP_400_BAD_REQUEST)
        # check player is mantri
        actual_role = room.roles.get(player_id)
        if actual_role != "Mantri":
            return Response({"detail": "only Mantri can submit guess"}, status=status.HTTP_403_FORBIDDEN)
        if room.mantri_guess:
            return Response({"detail": "mantri already guessed"}, status=status.HTTP_400_BAD_REQUEST)
        # validate guessed player is in room
        if guessed_player_id not in room.roles:
            return Response({"detail": "guessed player not in this room"}, status=status.HTTP_400_BAD_REQUEST)
        room.mantri_guess = {"by": player_id, "guessed": guessed_player_id}
        # evaluate
        correct = room.roles.get(guessed_player_id) == "Chor"
        # compute points map
        points = {}
        for pid, role in room.roles.items():
            points[pid] = BASE_POINTS.get(role, 0)
        if correct:
            result_note = "Mantri guessed correctly"
        else:
            # Chor steals Mantri's points
            mantri_pid = player_id
            chor_pid = None
            for pid, role in room.roles.items():
                if role == "Chor":
                    chor_pid = pid
                    break
            if chor_pid:
                steal_amount = BASE_POINTS.get("Mantri", 0)
                points[chor_pid] = points.get(chor_pid, 0) + steal_amount
                points[mantri_pid] = 0
            result_note = "Mantri guessed wrongly; Chor steals Mantri's points"
        room.round_result = {
            "correct": correct,
            "note": result_note,
            "points": points
        }
        room.status = "result"
        room.save()
        return Response({
            "mantri_guess": room.mantri_guess,
            "correct": correct,
            "round_result": room.round_result
        })

# Result view
class ResultView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if room.status != "result":
            return Response({"detail": "result not ready"}, status=status.HTTP_400_BAD_REQUEST)
        roles = room.roles or {}
        username_map = {}
        for pid, role in roles.items():
            try:
                p = Player.objects.get(id=pid)
                username_map[pid] = {"username": p.username, "display_name": p.display_name}
            except Player.DoesNotExist:
                username_map[pid] = {"username": "unknown", "display_name": ""}
        return Response({
            "roles": roles,
            "players": username_map,
            "mantri_guess": room.mantri_guess,
            "round_result": room.round_result
        })

# Leaderboard
class LeaderboardView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        players = get_room_players(room)
        last_points = {}
        if room.round_result and room.round_result.get("points"):
            last_points = room.round_result.get("points")
        mapped = []
        for p in players:
            pid = p["player_id"]
            mapped.append({
                "player_id": pid,
                "username": p["username"],
                "display_name": p["display_name"],
                "last_round_points": last_points.get(pid)
            })
        return Response({"leaderboard": mapped})
