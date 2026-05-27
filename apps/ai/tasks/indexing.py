from celery import shared_task


@shared_task
def index_faq_entry(faq_id: str) -> None:
    from apps.ai.models import FAQEntry
    from apps.ai.services.rag_service import RAGService

    faq = FAQEntry.all_objects.get(id=faq_id)
    RAGService().index_faq(faq)
