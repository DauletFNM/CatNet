from django.contrib import admin
from django.urls import path, include
from core import views # Импортируем все наши функции из core

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.user_search, name='user_search'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('requests/', views.friend_requests, name='friend_requests'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('chat/start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('pin-friend/<int:friend_id>/', views.pin_friend, name='pin_friend'),
    path('unpin-friend/<int:friend_id>/', views.unpin_friend, name='unpin_friend'),
]