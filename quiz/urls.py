from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('leader/', views.leaderHome, name='leader-home'),
    path('leader/scores/', views.scores, name='scores'),
    path('leader/quiz/', views.QuizListView.as_view(), name='quizzes'),
    path('leader/quiz/<int:pk>/rounds/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('leader/quiz/<int:quiz_pk>/rounds/<int:pk>', views.RoundDetailView.as_view(), name='round-detail'),
    path('leader/quiz/<int:quiz_pk>/rounds/<int:round_pk>/question/<int:pk>', views.GenericQuestionDetailView.as_view(), name='question-detail'),
    path('leader/game/<int:room_code>/', views.leader_room, name='leader-room'),
    path('game/', views.player_game, name='player-room'),
    path('final_results/', views.FinalResultsListView.as_view(), name='final-results'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
