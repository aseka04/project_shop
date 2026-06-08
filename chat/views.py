from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import ChatRoom, Message
from apps.accounts.models import User
import uuid


@login_required
def chat_list(request):
    # Get all chat rooms for current user
    rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).order_by('-updated_at')

    # Get last message and unread count for each room
    for room in rooms:
        room.last_message = room.messages.last()
        room.unread_count = room.messages.filter(is_read=False).exclude(sender=request.user).count()
        room.other_user = room.get_other_user(request.user)

    return render(request, 'chat/list.html', {'rooms': rooms})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, room_id=room_id)

    # Check if user has access to this room
    if request.user != room.user1 and request.user != room.user2:
        messages.error(request, 'You do not have access to this chat')
        return redirect('chat:chat_list')

    # Mark messages as read
    Message.objects.filter(room=room).exclude(sender=request.user).update(is_read=True)

    # Get all messages
    messages_list = room.messages.all()

    # Get the other participant
    other_user = room.get_other_user(request.user)

    context = {
        'room': room,
        'messages': messages_list,
        'other_user': other_user,
    }
    return render(request, 'chat/room.html', context)


@login_required
def start_chat(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        message_text = request.POST.get('message', '')

        try:
            other_user = User.objects.get(id=user_id)

            # Don't allow chatting with yourself
            if other_user == request.user:
                messages.error(request, 'You cannot chat with yourself')
                return redirect('chat:chat_list')

            # Check if chat room already exists
            existing_room = ChatRoom.objects.filter(
                (Q(user1=request.user, user2=other_user) | Q(user1=other_user, user2=request.user))
            ).first()

            if existing_room:
                room_id = existing_room.room_id
                room = existing_room
            else:
                room_id = str(uuid.uuid4()).replace('-', '')[:20]
                room = ChatRoom.objects.create(
                    room_id=room_id,
                    user1=request.user,
                    user2=other_user
                )

            # Create initial message
            if message_text:
                Message.objects.create(
                    room=room,
                    sender=request.user,
                    message=message_text
                )

            return redirect('chat:chat_room', room_id=room.room_id)

        except User.DoesNotExist:
            messages.error(request, 'User not found')

    return redirect('chat:chat_list')


@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, room_id=room_id)
        message_text = request.POST.get('message')

        if message_text:
            Message.objects.create(
                room=room,
                sender=request.user,
                message=message_text
            )

            # Update room updated_at
            room.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('chat:chat_room', room_id=room_id)


@login_required
def get_unread_count(request):
    rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    total_unread = 0
    for room in rooms:
        total_unread += room.messages.filter(is_read=False).exclude(sender=request.user).count()

    return JsonResponse({'unread_count': total_unread})


@login_required
def close_chat(request, room_id):
    room = get_object_or_404(ChatRoom, room_id=room_id)
    room.is_active = False
    room.save()
    messages.success(request, 'Chat closed')
    return redirect('chat:chat_list')