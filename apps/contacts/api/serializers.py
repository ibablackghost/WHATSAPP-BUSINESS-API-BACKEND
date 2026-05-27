from rest_framework import serializers

from apps.contacts.models import Contact, ContactTag


class ContactTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactTag
        fields = ["id", "name", "color"]


class ContactSerializer(serializers.ModelSerializer):
    tags = ContactTagSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "wa_id",
            "phone_number",
            "profile_name",
            "email",
            "metadata",
            "tags",
            "language",
            "last_interaction_at",
            "created_at",
        ]
        read_only_fields = ["id", "wa_id", "created_at"]
