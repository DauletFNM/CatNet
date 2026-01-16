from django.contrib import admin
from .models import ChatRoom, Message, FriendRequest, UserProfile, PinnedFriend

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_display', 'max_pinned_friends', 'created_at')
    search_fields = ('user__username',)
    fields = ('user', 'avatar_url', 'bio', 'max_pinned_friends', 'created_at')
    readonly_fields = ('created_at',)
    
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


@admin.register(PinnedFriend)
class PinnedFriendAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'pinned_at')
    search_fields = ('user__username', 'friend__username')
    list_filter = ('pinned_at',)