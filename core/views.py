from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Max
from .models import FriendRequest, ChatRoom, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def home(request):
    # Получаем все комнаты пользователя и сортируем по последнему сообщению
    chatrooms = ChatRoom.objects.filter(users=request.user).annotate(
        last_msg_time=Max('messages__created_at')
    ).order_by('-last_msg_time')

    return render(request, 'index.html', {
        'chatrooms': chatrooms,
    })

def user_search(request):
    query = request.GET.get('q')
    # Заменяем results на users для соответствия шаблону
    users = User.objects.filter(Q(username__icontains=query)).exclude(id=request.user.id) if query else []
    return render(request, 'user_search.html', {'users': users, 'query': query})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    # Используем поле accepted как в твоем коде
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect('user_search')

@login_required
def friend_requests(request):
    # Список входящих запросов
    reqs = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'friend_requests.html', {'requests': reqs})

@login_required
def accept_friend_request(request, request_id):
    friend_req = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_req.accepted = True
    friend_req.save()
    # После принятия дружбы сразу создаем чат и переходим в него
    return redirect('start_chat', user_id=friend_req.from_user.id)

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Ищем существующую комнату на двоих
    room = ChatRoom.objects.filter(users=request.user).filter(users=other_user).first()
    
    if not room:
        # Создаем новую комнату, если её нет
        room = ChatRoom.objects.create(name=f"Чат с {other_user.username}")
        room.users.add(request.user, other_user)
    
    return redirect('chat_room', room_id=room.id)

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)
    messages = room.messages.all().select_related('sender').order_by('created_at')
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(room=room, sender=request.user, text=text)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
            return redirect('chat_room', room_id=room.id)
            
    return render(request, 'chat.html', {'room': room, 'messages': messages})