from django.db import models
from django.contrib.auth.models import User

# 1. Модель для списка друзей
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

# 2. Модель для чат-комнат
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True)
    users = models.ManyToManyField(User, related_name='rooms')

    def __str__(self):
        return self.name if self.name else f"Chat {self.id}"

# 3. Модель для самих текстовых сообщений
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']