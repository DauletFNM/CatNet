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
        room, created = ChatRoom.objects.get_or_create(
            name=f"Чат с {other_user.username}"
        )
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
        birth_date = request.POST.get('birth_date', '')
        
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
        
        if birth_date:
            profile.birth_date = birth_date
        elif birth_date == '':
            profile.birth_date = None
        
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
    

    if message.sender != request.user:
        return JsonResponse({'status': 'error', 'message': 'Ты не можешь удалить это сообщение'}, status=403)
    
    message.delete()
    
    return JsonResponse({'status': 'success', 'message': 'Сообщение удалено'})


@login_required
def manage_pinned(request):
    pinned_friends = PinnedFriend.objects.filter(user=request.user).select_related('friend')
    pinned_ids = [pf.friend.id for pf in pinned_friends]
    

    friend_requests = FriendRequest.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)) & Q(accepted=True)
    )
    
    friend_ids = set()
    for req in friend_requests:
        if req.from_user == request.user:
            friend_ids.add(req.to_user.id)
        else:
            friend_ids.add(req.from_user.id)
    
    friends = User.objects.filter(id__in=friend_ids)
    
    return render(request, 'manage_pinned.html', {
        'friends': friends,
        'pinned_ids': pinned_ids,
        'max_pinned': request.user.profile.max_pinned_friends,
        'current_pinned_count': pinned_friends.count(),
    })


@login_required
def view_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
   
    is_friend = False
    friend_request = FriendRequest.objects.filter(
        (Q(from_user=request.user, to_user=user) | Q(from_user=user, to_user=request.user)) & 
        Q(accepted=True)
    ).first()
    if friend_request:
        is_friend = True
    
    return render(request, 'user_profile.html', {
        'viewed_user': user,
        'viewed_profile': profile,
        'is_friend': is_friend,
    })


@login_required
@require_http_methods(["POST"])
def unfriend(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
 
    FriendRequest.objects.filter(
        (Q(from_user=request.user, to_user=other_user) | Q(from_user=other_user, to_user=request.user)) & 
        Q(accepted=True)
    ).delete()
    
   
    chatrooms = ChatRoom.objects.filter(users=request.user).filter(users=other_user)
    
  
    for room in chatrooms:
        Message.objects.filter(room=room).delete()
    
    
    chatrooms.delete()
    
  
    PinnedFriend.objects.filter(user=request.user, friend=other_user).delete()
    
    return JsonResponse({'status': 'success', 'message': 'Пользователь удалён из друзей'})

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '').strip()
        selected_users = request.POST.getlist('selected_users')
        
        if not group_name:
            return render(request, 'index.html', {
                'error': 'Введи название группового чата'
            })
        
        if not selected_users:
            return render(request, 'index.html', {
                'error': 'Выбери хотя бы одного друга'
            })
        

        friend_requests = FriendRequest.objects.filter(
            (Q(from_user=request.user) | Q(to_user=request.user)) & Q(accepted=True)
        )
        
        friend_ids = set()
        for req in friend_requests:
            if req.from_user == request.user:
                friend_ids.add(req.to_user.id)
            else:
                friend_ids.add(req.from_user.id)
        

        valid_user_ids = [int(uid) for uid in selected_users if int(uid) in friend_ids]
        
        if not valid_user_ids:
            return render(request, 'index.html', {
                'error': 'Ты не можешь добавить этих пользователей'
            })
        
    
        room = ChatRoom.objects.create(name=group_name)
        room.users.add(request.user)
        
        for user_id in valid_user_ids:
            room.users.add(User.objects.get(id=user_id))
        
        return redirect('chat_room', room_id=room.id)
    
   
    friend_requests = FriendRequest.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)) & Q(accepted=True)
    )
    
    friend_ids = set()
    for req in friend_requests:
        if req.from_user == request.user:
            friend_ids.add(req.to_user.id)
        else:
            friend_ids.add(req.from_user.id)
    
    friends = User.objects.filter(id__in=friend_ids)
    
    return render(request, 'create_group_chat.html', {
        'friends': friends,
    })


@login_required
@require_http_methods(["POST"])
def delete_group_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)
    
  
    if room.users.count() <= 2:
    
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Это не групповой чат'}, status=400)
        return redirect('home')
    
  
    Message.objects.filter(room=room).delete()
    

    room.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Групповой чат удалён'})
    return redirect('home')
