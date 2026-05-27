"""Seed database with demo data."""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.accounts.models import User
from apps.bots.models import BotFlow, BotStep
from apps.organizations.models import Organization, OrganizationMembership
from apps.organizations.services.organization_service import OrganizationService


class Command(BaseCommand):
    help = "Seed demo organization, admin user, and sample bot flow"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            email="admin@whatbot.pro",
            defaults={
                "username": "admin",
                "first_name": "Admin",
                "last_name": "WhatBot",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("Admin@WhatBot2024!")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user"))

        org, _ = Organization.objects.get_or_create(
            slug="demo",
            defaults={"name": "Demo Organization", "plan": Organization.Plan.BUSINESS},
        )
        OrganizationMembership.objects.get_or_create(
            organization=org,
            user=user,
            defaults={
                "role": OrganizationMembership.Role.ADMIN,
                "is_default": True,
            },
        )

        flow, _ = BotFlow.all_objects.get_or_create(
            organization=org,
            slug="welcome",
            defaults={
                "name": "Welcome Flow",
                "is_default": True,
                "fallback_text": {"fr": "Je n'ai pas compris, veuillez réessayer."},
            },
        )
        if not flow.steps.exists():
            BotStep.all_objects.create(
                organization=org,
                flow=flow,
                key="welcome",
                node_type=BotStep.NodeType.MESSAGE,
                is_entry=True,
                translations={"fr": "Bienvenue sur WhatBot Pro! Comment puis-je vous aider?"},
                next_step_key="menu",
            )
            BotStep.all_objects.create(
                organization=org,
                flow=flow,
                key="menu",
                node_type=BotStep.NodeType.MENU,
                config={
                    "options": [
                        {"key": "1", "label": "Support", "next": "support"},
                        {"key": "2", "label": "Paiement", "next": "payment"},
                    ],
                    "invalid_message": {"fr": "Choix invalide. Tapez 1 ou 2."},
                },
                translations={"fr": "Choisissez une option:\n1. Support\n2. Paiement"},
            )

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Org: {org.slug}, User: {user.email}"))
