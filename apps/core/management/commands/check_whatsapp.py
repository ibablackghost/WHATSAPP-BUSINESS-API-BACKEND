"""Vérifie la configuration WhatsApp de l'organisation demo."""
from django.core.management.base import BaseCommand

from apps.organizations.models import Organization
from apps.organizations.services.organization_service import OrganizationService
from apps.whatsapp.services.credential_validator import WhatsAppCredentialValidator


class Command(BaseCommand):
    help = "Vérifie le token Meta et le phone_number_id en base (organisation demo)."

    def handle(self, *args, **options):
        org = Organization.objects.filter(slug="demo").first()
        if not org:
            org = Organization.objects.first()
        if not org:
            self.stderr.write("Aucune organisation en base.")
            return

        self.stdout.write(f"Organisation: {org.name} ({org.id})")
        self.stdout.write(f"phone_number_id: {org.whatsapp_phone_number_id or '(vide)'}")

        service = OrganizationService()
        token = service.get_access_token(org)
        if not token:
            self.stderr.write(self.style.ERROR("access_token: (vide)"))
            self.stderr.write(
                "→ POST /api/v1/organizations/whatsapp-config/ ou scripts/configure_whatsapp.ps1"
            )
            return

        self.stdout.write(f"access_token: {token[:12]}... ({len(token)} chars)")

        result = WhatsAppCredentialValidator().validate(token, org.whatsapp_phone_number_id)
        if result.get("valid"):
            self.stdout.write(self.style.SUCCESS("OK — credentials Meta valides"))
            self.stdout.write(f"  Numéro: {result.get('display_phone_number')}")
            self.stdout.write(f"  Nom: {result.get('verified_name')}")
            return

        self.stderr.write(self.style.ERROR(f"INVALIDE — {result.get('error')}"))
        if result.get("code"):
            self.stderr.write(f"  Code Meta: {result['code']}")
        self.stderr.write(f"  → {result.get('hint')}")
