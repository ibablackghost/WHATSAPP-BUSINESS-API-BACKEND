from rest_framework import serializers

from apps.ai.models import FAQEntry


class FAQEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQEntry
        fields = ["id", "question", "answer", "category", "language", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
