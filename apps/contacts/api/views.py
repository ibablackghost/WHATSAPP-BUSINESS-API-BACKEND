from rest_framework import viewsets

from apps.contacts.api.serializers import ContactSerializer
from apps.contacts.models import Contact
from apps.core.api.permissions import IsOrganizationMember


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["phone_number", "language"]
    search_fields = ["profile_name", "phone_number", "email"]
    ordering_fields = ["created_at", "last_interaction_at"]

    def get_queryset(self):
        return Contact.objects.select_related("organization").prefetch_related("tags")
