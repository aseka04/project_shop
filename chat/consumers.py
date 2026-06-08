import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatNotification
from datetime import datetime
import base64
from django.core.files.base import ContentFile
import uuid

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Check if user is authorized
        if not self.user.is_authenticated:
            await self.close()
            return

        # Verify user has access to this room
        if not await self.user_has_access():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Mark messages as read
        await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')

        if message_type == 'message':
            content = text_data_json['content']

            # Save message to database
            message = await self.save_message(content)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender': self.user.username,
                    'sender_id': self.user.id,
                    'content': content,
                    'timestamp': str(message.created_at),
                    'is_read': message.is_read
                }
            )

            # Create notification for other users
            await self.create_notification(message)

        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'sender': self.user.username,
                    'is_typing': text_data_json.get('is_typing', True)
                }
            )

        elif message_type == 'read_receipt':
            await self.mark_messages_as_read()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user': self.user.username,
                    'read_at': str(datetime.now())
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender': event['sender'],
            'is_typing': event['is_typing']
        }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'user': event['user'],
            'read_at': event['read_at']
        }))

    @database_sync_to_async
    def user_has_access(self):
        try:
            room = ChatRoom.objects.get(room_id=self.room_id)
            return self.user == room.customer or self.user == room.vendor or self.user.is_staff
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(room_id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        # Update room updated_at
        room.save(update_fields=['updated_at'])
        return message

    @database_sync_to_async
    def mark_messages_as_read(self):
        room = ChatRoom.objects.get(room_id=self.room_id)
        Message.objects.filter(
            room=room
        ).exclude(
            sender=self.user
        ).update(is_read=True, read_at=datetime.now())

    @database_sync_to_async
    def create_notification(self, message):
        room = message.room
        recipients = []
        if self.user == room.customer and room.vendor:
            recipients.append(room.vendor)
        elif self.user == room.vendor and room.customer:
            recipients.append(room.customer)

        for recipient in recipients:
            ChatNotification.objects.create(
                user=recipient,
                message=message
            )