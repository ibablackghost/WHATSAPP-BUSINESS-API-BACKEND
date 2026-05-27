from rest_framework import serializers

from apps.conversations.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender_type",
            "sender_id",
            "content",
            "content_type",
            "is_read",
            "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    contact_name = serializers.CharField(source="contact.profile_name", read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "contact",
            "contact_name",
            "assigned_agent",
            "status",
            "channel",
            "priority",
            "is_bot_active",
            "last_message_at",
            "messages",
            "created_at",
        ]
