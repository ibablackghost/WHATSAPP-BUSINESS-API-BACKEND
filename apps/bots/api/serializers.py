from rest_framework import serializers

from apps.bots.models import BotFlow, BotStep


class BotStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotStep
        fields = [
            "id",
            "key",
            "node_type",
            "config",
            "next_step_key",
            "translations",
            "is_entry",
            "position_x",
            "position_y",
        ]


class BotFlowSerializer(serializers.ModelSerializer):
    steps = BotStepSerializer(many=True, read_only=True)

    class Meta:
        model = BotFlow
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "is_default",
            "default_language",
            "session_timeout_minutes",
            "fallback_text",
            "steps",
            "created_at",
        ]
