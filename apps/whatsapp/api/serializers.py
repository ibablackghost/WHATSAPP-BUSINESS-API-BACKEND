from rest_framework import serializers

from apps.whatsapp.models import WhatsAppMessageLog, WhatsAppTemplate


class SendMessageSerializer(serializers.Serializer):
    contact_id = serializers.UUIDField()
    conversation_id = serializers.UUIDField()
    body = serializers.CharField(max_length=4096)


class WhatsAppMessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessageLog
        fields = [
            "id",
            "wa_message_id",
            "direction",
            "message_type",
            "content",
            "status",
            "created_at",
        ]


class WhatsAppTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppTemplate
        fields = ["id", "name", "language", "category", "components", "status"]
