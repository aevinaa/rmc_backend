from django.urls import path
from . import views

urlpatterns = [
    path("room/create/", views.CreateRoomView.as_view(), name="create-room"),
    path("room/join/", views.JoinRoomView.as_view(), name="join-room"),
    path("room/<uuid:room_id>/players/", views.ListPlayersView.as_view(), name="list-players"),
    path("room/<uuid:room_id>/assign/", views.AssignRolesView.as_view(), name="assign-roles"),
    path("room/<uuid:room_id>/role/<uuid:player_id>/", views.MyRoleView.as_view(), name="my-role"),
    path("room/<uuid:room_id>/guess/", views.SubmitGuessView.as_view(), name="submit-guess"),
    path("room/<uuid:room_id>/result/", views.ResultView.as_view(), name="result"),
    path("room/<uuid:room_id>/leaderboard/", views.LeaderboardView.as_view(), name="leaderboard"),
]
