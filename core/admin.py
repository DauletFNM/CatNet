from django.contrib import admin
from .models import ChatRoom, Message, FriendRequest

# Настройка отображения друзей
@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at', 'accepted') # Что видим в списке
    list_filter = ('accepted',) # Фильтр справа (кто в ожидании, кто уже друг)
    search_fields = ('from_user__username', 'to_user__username') # Поиск по логину

# Настройка отображения сообщений
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'text_excerpt', 'created_at')
    list_filter = ('created_at', 'room')
    
    # Чтобы в списке не выводился огромный текст, обрезаем его
    def text_excerpt(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_excerpt.short_description = "Текст сообщения"

# Настройка чат-комнат
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('users',) # Удобный выбор пользователей в комнату (два окна)