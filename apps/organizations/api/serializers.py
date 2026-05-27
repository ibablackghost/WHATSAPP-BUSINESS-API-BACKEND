from rest_framework import serializers

from apps.organizations.models import Organization, OrganizationMembership


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "plan",
            "timezone",
            "default_language",
            "whatsapp_phone_number_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ["id", "organization", "role", "is_default", "is_active"]
