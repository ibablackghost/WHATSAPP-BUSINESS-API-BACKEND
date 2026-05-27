from rest_framework import serializers

from apps.notifications.models import NotificationCampaign


class NotificationCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCampaign
        fields = [
            "id",
            "name",
            "template_name",
            "template_language",
            "status",
            "scheduled_at",
            "total_recipients",
            "sent_count",
            "delivered_count",
            "read_count",
            "failed_count",
            "created_at",
        ]
