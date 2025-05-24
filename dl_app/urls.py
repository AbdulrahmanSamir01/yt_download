# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stream/', views.stream_video, name='stream_video'),
]