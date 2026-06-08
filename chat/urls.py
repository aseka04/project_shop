from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<str:room_id>/', views.chat_room, name='chat_room'),
    path('start/', views.start_chat, name='start_chat'),
    path('send/<str:room_id>/', views.send_message, name='send_message'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('close/<str:room_id>/', views.close_chat, name='close_chat'),
]