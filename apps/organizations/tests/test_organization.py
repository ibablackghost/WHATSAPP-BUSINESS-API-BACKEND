import pytest


@pytest.mark.django_db
def test_current_organization(auth_client, organization):
    response = auth_client.get("/api/v1/organizations/current/")
    assert response.status_code == 200
    assert response.data["slug"] == organization.slug
