from django.db import models
from django.contrib.auth.models import User
from datetime import date
from dateutil.relativedelta import relativedelta

AVATARS = [
    ('https://i.pinimg.com/736x/93/ce/0f/93ce0faec07582c48a51494374f5f7fb.jpg', 'Черный парень следит'),
    ('https://i.pinimg.com/736x/bc/77/4e/bc774eadc4eec3a42f68ed3f7eaf34f1.jpg', 'Кот позади взрыв'),
    ('https://i.pinimg.com/736x/15/28/32/1528324423acc55f1ebde5a74899eb9b.jpg', 'Пепа'),
    ('https://i.pinimg.com/1200x/f6/f6/cc/f6f6ccb510466e0736f224316e9c5187.jpg', 'я газель'),
    ('https://i.pinimg.com/736x/82/e5/00/82e50027d447e50b89182f6670240c36.jpg', 'кот на троне'),
    ('https://i.pinimg.com/736x/13/5c/27/135c27e76a14e2477059cea160c81dac.jpg', 'Симпатичная собака'),
    ('https://i.pinimg.com/736x/4e/84/5d/4e845dfa164626eb4eea09ddb8e9576e.jpg', 'Симпл'),
    ('https://i.pinimg.com/736x/b4/18/33/b418335314fbf4be4aa3b840eda9c840.jpg', 'вьетнам кот'),
]

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
    birth_date = models.DateField(blank=True, null=True)
    max_pinned_friends = models.IntegerField(default=2)

    def get_age(self):
        if self.birth_date:
            return relativedelta(date.today(), self.birth_date).years
        return None

    def __str__(self):
        return f"Профиль {self.user.username}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True)
    users = models.ManyToManyField(User, related_name='rooms')

    def __str__(self):
        return self.name if self.name else f"Chat {self.id}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class PinnedFriend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pinned_friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pinned_by')
    pinned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        ordering = ['-pinned_at']

    def __str__(self):
        return f"{self.user.username} закрепил {self.friend.username}"
