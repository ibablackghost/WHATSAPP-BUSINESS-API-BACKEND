from django.utils import timezone

from apps.agents.models import AgentPresence
from apps.core.middleware.organization import get_current_organization


class PresenceService:
    def set_status(self, user, status: str) -> AgentPresence:
        org = get_current_organization()
        presence, _ = AgentPresence.all_objects.update_or_create(
            organization=org,
            agent=user,
            defaults={"status": status, "last_seen_at": timezone.now()},
        )
        return presence
