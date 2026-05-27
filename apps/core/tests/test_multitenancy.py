import pytest

from apps.contacts.models import Contact
from apps.core.middleware.organization import set_current_organization
from tests.factories import ContactFactory, OrganizationFactory


@pytest.mark.django_db
class TestMultiTenancy:
    def test_organization_isolation(self):
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        ContactFactory(organization=org1, wa_id="111", phone_number="111")
        ContactFactory(organization=org2, wa_id="222", phone_number="222")

        set_current_organization(org1)
        assert Contact.objects.count() == 1

        set_current_organization(org2)
        assert Contact.objects.count() == 1

        set_current_organization(None)
