import pytest
from rest_framework.test import APIClient

from apps.core.middleware.organization import set_current_organization
from apps.organizations.models import Organization, OrganizationMembership


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name="Test Org", slug="test-org")


@pytest.fixture
def admin_user(db, organization):
    from apps.accounts.models import User

    user = User.objects.create_user(
        email="test@whatbot.pro",
        username="testuser",
        password="testpass123",
    )
    OrganizationMembership.objects.create(
        organization=organization,
        user=user,
        role=OrganizationMembership.Role.ADMIN,
        is_default=True,
    )
    return user


@pytest.fixture
def auth_client(api_client, admin_user, organization):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        HTTP_X_ORGANIZATION_ID=str(organization.id),
    )
    set_current_organization(organization)
    return api_client


@pytest.fixture(autouse=True)
def reset_org_context():
    yield
    set_current_organization(None)
