from celery import shared_task


@shared_task
def send_campaign_batch(campaign_id: str) -> None:
    from apps.notifications.models import NotificationCampaign
    from apps.notifications.services.campaign_service import CampaignService

    campaign = NotificationCampaign.all_objects.get(id=campaign_id)
    CampaignService().start(campaign)
