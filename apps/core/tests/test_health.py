import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_check(api_client):
    response = api_client.get("/health/")
    assert response.status_code in (200, 503)
