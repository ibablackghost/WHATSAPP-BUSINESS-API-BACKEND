from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.agents.models import AgentPresence


class AgentPresenceSerializer(serializers.ModelSerializer):
    agent = UserSerializer(read_only=True)

    class Meta:
        model = AgentPresence
        fields = [
            "id",
            "agent",
            "status",
            "active_conversations",
            "max_conversations",
            "last_seen_at",
        ]
