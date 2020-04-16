from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('leader/', views.leaderHome, name='leader-home'),
    path('leader/rounds/', views.RoundListView.as_view(), name='rounds'),
    path('leader/rounds/<int:pk>', views.RoundDetailView.as_view(), name='round-detail'),
    path('leader/rounds/<int:round_pk>/question/<int:pk>', views.QuestionDetailView.as_view(), name='question-detail'),
    path('leader/game/<int:room_code>/', views.leader_room, name='leader-room'),
    path('game/', views.player_game, name='player-room'),
]
