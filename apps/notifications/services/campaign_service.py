from django.utils import timezone

from apps.notifications.models import CampaignRecipient, NotificationCampaign
from apps.notifications.tasks.send import send_campaign_batch


class CampaignService:
    def schedule(self, campaign: NotificationCampaign) -> NotificationCampaign:
        campaign.status = NotificationCampaign.Status.SCHEDULED
        campaign.save(update_fields=["status", "updated_at"])
        if campaign.scheduled_at:
            send_campaign_batch.apply_async(
                args=[str(campaign.id)],
                eta=campaign.scheduled_at,
            )
        else:
            send_campaign_batch.delay(str(campaign.id))
        return campaign

    def start(self, campaign: NotificationCampaign) -> None:
        campaign.status = NotificationCampaign.Status.RUNNING
        campaign.started_at = timezone.now()
        campaign.save(update_fields=["status", "started_at", "updated_at"])

        recipients = CampaignRecipient.all_objects.filter(
            campaign=campaign, status="pending"
        ).select_related("contact")[:100]

        from apps.organizations.services.organization_service import OrganizationService
        from apps.whatsapp.services.whatsapp_client import WhatsAppClient

        org = campaign.organization
        token = OrganizationService().get_access_token(org)
        client = WhatsAppClient(token, org.whatsapp_phone_number_id)

        for recipient in recipients:
            try:
                result = client.send_template(
                    recipient.contact.wa_id,
                    campaign.template_name,
                    campaign.template_language,
                    campaign.template_components,
                )
                recipient.wa_message_id = result.get("messages", [{}])[0].get("id", "")
                recipient.status = "sent"
                recipient.sent_at = timezone.now()
                campaign.sent_count += 1
            except Exception as exc:
                recipient.status = "failed"
                recipient.error_message = str(exc)
                campaign.failed_count += 1
            recipient.save()
        campaign.save(
            update_fields=["sent_count", "failed_count", "updated_at"]
        )
