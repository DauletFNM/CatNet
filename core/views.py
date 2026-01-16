from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Max
from .models import FriendRequest, ChatRoom, Message, UserProfile, PinnedFriend, AVATARS
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@login_required
def home(request):
    chatrooms = ChatRoom.objects.filter(users=request.user).annotate(
        last_msg_time=Max('messages__created_at')
    ).order_by('-last_msg_time')
    
    pinned_friends = PinnedFriend.objects.filter(user=request.user).select_related('friend')

    return render(request, 'index.html', {
        'chatrooms': chatrooms,
        'pinned_friends': pinned_friends,
    })

def user_search(request):
    query = request.GET.get('q')
    users = User.objects.filter(Q(username__icontains=query)).exclude(id=request.user.id) if query else []
    return render(request, 'user_search.html', {'users': users, 'query': query})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect('user_search')

@login_required
def friend_requests(request):
    reqs = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'friend_requests.html', {'requests': reqs})

@login_required
def accept_friend_request(request, request_id):
    friend_req = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_req.accepted = True
    friend_req.save()
    return redirect('start_chat', user_id=friend_req.from_user.id)

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    room = ChatRoom.objects.filter(users=request.user).filter(users=other_user).first()
    
    if not room:
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

@login_required
def profile(request):
    profile = request.user.profile
    pinned_friends = PinnedFriend.objects.filter(user=request.user).select_related('friend')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        avatar_url = request.POST.get('avatar_url', '')
        
        if username and username != request.user.username:
            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                return render(request, 'profile.html', {
                    'avatars': AVATARS,
                    'error': 'Это имя уже занято!',
                    'pinned_friends': pinned_friends
                })
            request.user.username = username
        
        if avatar_url in [url for url, _ in AVATARS]:
            profile.avatar_url = avatar_url
        
        request.user.save()
        profile.save()
        
        return redirect('profile')
    
    return render(request, 'profile.html', {
        'avatars': AVATARS,
        'profile': profile,
        'pinned_friends': pinned_friends
    })


@login_required
@require_http_methods(["POST"])
def pin_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    profile = request.user.profile
    
    pinned_count = PinnedFriend.objects.filter(user=request.user).count()
    
    if pinned_count >= profile.max_pinned_friends:
        return JsonResponse({
            'status': 'limit_exceeded',
            'message': 'Лимит закреплений достигнут',
            'email': 'kdaulethtc@gmail.com',
            'card': '4400 4303 1034 3402'
        })
    
    pinned, created = PinnedFriend.objects.get_or_create(user=request.user, friend=friend)
    
    return JsonResponse({
        'status': 'success' if created else 'already_pinned',
        'message': 'Друг закреплён' if created else 'Друг уже закреплён'
    })


@login_required
@require_http_methods(["POST"])
def unpin_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    PinnedFriend.objects.filter(user=request.user, friend=friend).delete()
    
    return JsonResponse({'status': 'success', 'message': 'Друг откреплен'})


@login_required
@require_http_methods(["POST"])
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Только автор может удалить сообщение
    if message.sender != request.user:
        return JsonResponse({'status': 'error', 'message': 'Ты не можешь удалить это сообщение'}, status=403)
    
    message.delete()
    
    return JsonResponse({'status': 'success', 'message': 'Сообщение удалено'})