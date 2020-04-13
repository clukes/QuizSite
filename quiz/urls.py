from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rounds/', views.RoundListView.as_view(), name='rounds'),
    path('rounds/<int:pk>', views.RoundDetailView.as_view(), name='round-detail'),
]
