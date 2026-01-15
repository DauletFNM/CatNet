from django.db import models
from django.contrib.auth.models import User

# Список доступных аватаров
AVATARS = [
    ('https://i.pinimg.com/736x/64/ba/12/64ba126baf766711499a946cfc2e5af4.jpg', 'Кот оранжевый'),
    ('https://i.pinimg.com/736x/bd/83/62/bd8362f098ebfa82df5cdbf57e8e6b19.jpg', 'Кот чёрный'),
    ('https://i.pinimg.com/736x/f4/5a/09/f45a09fecd73e0d72e19a1bc35f38c67.jpg', 'Кот серый'),
    ('https://i.pinimg.com/736x/a1/2b/3c/a12b3c5f6e8d9f0a1b2c3d4e5f6a7b8c.jpg', 'Кот белый'),
    ('https://i.pinimg.com/736x/9e/7d/6c/9e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b.jpg', 'Полосатый кот'),
    ('https://i.pinimg.com/736x/c3/b2/a1/c3b2a1f9e8d7c6b5a4f3e2d1c0b9a8f7.jpg', 'Симпатичный кот'),
    ('https://i.pinimg.com/736x/d5/e4/f3/d5e4f3c2b1a9f8e7d6c5b4a3f2e1d0c9.jpg', 'Кот спит'),
    ('https://i.pinimg.com/736x/e6/f5/a4/e6f5a4d3c2b1a0f9e8d7c6b5a4f3e2d1.jpg', 'Молодой кот'),
]

# 0. Модель для профиля пользователя
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        choices=[(url, name) for url, name in AVATARS],
        default=AVATARS[0][0]
    )
    bio = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

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