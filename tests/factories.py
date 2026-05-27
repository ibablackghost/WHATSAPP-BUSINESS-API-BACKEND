import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import User
from apps.contacts.models import Contact
from apps.conversations.models import Conversation
from apps.organizations.models import Organization, OrganizationMembership


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@whatbot.pro")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Organization {n}")
    slug = factory.Sequence(lambda n: f"org-{n}")


class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

    organization = factory.SubFactory(OrganizationFactory)
    wa_id = factory.Sequence(lambda n: f"221700000{n:03d}")
    phone_number = factory.LazyAttribute(lambda o: o.wa_id)
    profile_name = factory.Faker("name")


class ConversationFactory(DjangoModelFactory):
    class Meta:
        model = Conversation

    organization = factory.SubFactory(OrganizationFactory)
    contact = factory.SubFactory(ContactFactory, organization=factory.SelfAttribute("..organization"))
