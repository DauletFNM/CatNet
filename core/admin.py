from django.contrib import admin
from .models import ChatRoom, Message, FriendRequest, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_display', 'created_at')
    search_fields = ('user__username',)
    
    def avatar_display(self, obj):
        return f'<img src="{obj.avatar_url}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />'
    avatar_display.allow_tags = True
    avatar_display.short_description = "Аватар"

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at', 'accepted')
    list_filter = ('accepted',)
    search_fields = ('from_user__username', 'to_user__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'text_excerpt', 'created_at')
    list_filter = ('created_at', 'room')
    
    def text_excerpt(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_excerpt.short_description = "Текст сообщения"

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('users',)