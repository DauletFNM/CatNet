from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from .models import FriendRequest, ChatRoom, Message

# Функция для поиска людей
def user_search(request):
    query = request.GET.get('q')
    results = User.objects.filter(Q(username__icontains=query)).exclude(id=request.user.id) if query else []
    return render(request, 'user_search.html', {'results': results, 'query': query})

# Функция для отправки заявки
def send_friend_request(request, user_id):
    to_user = User.objects.get(id=user_id)
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect('user_search')

def home(request):
    # Если пользователь не вошел, просто показываем страницу
    if not request.user.is_authenticated:
        return render(request, 'index.html')
    
    # Получаем список друзей (те, кто принял запрос)
    friends = User.objects.filter(
        Q(received_requests__from_user=request.user, received_requests__accepted=True) |
        Q(sent_requests__to_user=request.user, sent_requests__accepted=True)
    ).distinct()

    return render(request, 'index.html', {'friends': friends})

# Показать список входящих запросов
def friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'friend_requests.html', {'requests': requests})

# Принять запрос
def accept_friend_request(request, request_id):
    friend_req = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_req.accepted = True
    friend_req.save()
    return redirect('friend_requests')

def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Ищем комнату, где есть оба пользователя
    room = ChatRoom.objects.filter(users=request.user).filter(users=other_user).first()
    
    if not room:
        # Если комнаты нет, создаем её (называем по ID пользователей, чтобы было уникально)
        room_name = f"chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"
        room = ChatRoom.objects.create(name=room_name)
        room.users.add(request.user, other_user)
    
    return redirect('chat_room', room_id=room.id)

def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)
    messages = room.messages.all()
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(room=room, sender=request.user, text=text)
            return redirect('chat_room', room_id=room.id)
            
    return render(request, 'chat.html', {'room': room, 'messages': messages})