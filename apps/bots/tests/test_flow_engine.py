import pytest

from apps.bots.models import BotFlow, BotStep
from apps.bots.services.flow_engine import FlowEngine
from tests.factories import ContactFactory, ConversationFactory, OrganizationFactory


@pytest.mark.django_db
class TestFlowEngine:
    def test_start_flow_message(self):
        org = OrganizationFactory()
        contact = ContactFactory(organization=org)
        conversation = ConversationFactory(organization=org, contact=contact)
        flow = BotFlow.all_objects.create(
            organization=org, name="Test", slug="test", is_default=True
        )
        BotStep.all_objects.create(
            organization=org,
            flow=flow,
            key="start",
            node_type=BotStep.NodeType.MESSAGE,
            is_entry=True,
            translations={"fr": "Hello!"},
            next_step_key="end",
        )
        BotStep.all_objects.create(
            organization=org,
            flow=flow,
            key="end",
            node_type=BotStep.NodeType.END,
            translations={"fr": "Goodbye!"},
        )
        result = FlowEngine().start_or_resume(org, contact, conversation)
        assert result.get("message") or result.get("action")
