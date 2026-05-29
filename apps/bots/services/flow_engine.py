"""Dynamic conversation flow engine."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

from apps.bots.models import BotFlow, BotStep, SessionState
from apps.bots.repositories.flow_repository import FlowRepository
from apps.contacts.models import Contact
from apps.conversations.models import Conversation
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class FlowEngine:
    """Executes USSD-style conversational flows."""

    def __init__(self) -> None:
        self._repo = FlowRepository()

    def start_or_resume(
        self,
        organization: Organization,
        contact: Contact,
        conversation: Conversation,
        user_input: str = "",
    ) -> dict[str, Any]:
        session = self._get_active_session(organization, contact)
        if session and self._is_expired(session):
            session.is_active = False
            session.save(update_fields=["is_active"])
            session = None

        if not session:
            flow = self._repo.get_default_flow(organization.id)
            if not flow:
                return {"action": "no_flow"}
            if not flow.steps.exists():
                logger.warning("Flow %s has no steps — skipping bot", flow.id)
                return {"action": "no_flow", "message": "Flux sans étapes configurées."}
            session = self._create_session(organization, contact, conversation, flow)

        return self._process_step(session, user_input)

    def _process_step(self, session: SessionState, user_input: str) -> dict[str, Any]:
        step = self._repo.get_step(session.flow_id, session.current_step_key)
        if not step:
            return {"action": "error", "message": "Step not found"}

        lang = session.language
        result: dict[str, Any] = {"action": step.node_type, "step_key": step.key}

        if step.node_type == BotStep.NodeType.MESSAGE:
            result["message"] = self._translate(step, lang)
            session.current_step_key = step.next_step_key or step.key
            session.save(update_fields=["current_step_key", "updated_at"])

        elif step.node_type == BotStep.NodeType.MENU:
            if not user_input:
                result["menu"] = step.config.get("options", [])
                result["message"] = self._translate(step, lang)
            else:
                options = {o["key"]: o["next"] for o in step.config.get("options", [])}
                next_key = options.get(user_input)
                if next_key:
                    session.current_step_key = next_key
                    session.invalid_input_count = 0
                    session.save(
                        update_fields=["current_step_key", "invalid_input_count", "updated_at"]
                    )
                    return self._process_step(session, "")
                session.invalid_input_count += 1
                session.save(update_fields=["invalid_input_count", "updated_at"])
                if session.invalid_input_count >= session.flow.max_invalid_retries:
                    result["message"] = session.flow.fallback_text.get(lang, "")
                else:
                    result["message"] = step.config.get("invalid_message", {}).get(lang, "")
                    result["retry"] = True

        elif step.node_type == BotStep.NodeType.CONDITION:
            var = step.config.get("variable", "")
            op = step.config.get("operator", "eq")
            value = step.config.get("value", "")
            actual = session.context_variables.get(var, "")
            if self._eval_condition(actual, op, value):
                session.current_step_key = step.config.get("true_next", step.next_step_key)
            else:
                session.current_step_key = step.config.get("false_next", step.next_step_key)
            session.save(update_fields=["current_step_key", "updated_at"])
            return self._process_step(session, user_input)

        elif step.node_type == BotStep.NodeType.AI:
            from apps.ai.services.chat_service import ChatService

            response = ChatService().generate_response(
                organization_id=session.organization_id,
                contact_id=session.contact_id,
                message=user_input,
            )
            result["message"] = response.get("text", "")
            if response.get("escalate"):
                result["action"] = "assign_agent"

        elif step.node_type == BotStep.NodeType.PAYMENT:
            from apps.payments.services.payment_service import PaymentService

            payment = PaymentService().initiate_from_flow(
                session=session, config=step.config
            )
            result["payment_id"] = str(payment.id)
            result["payment_url"] = payment.payment_url

        elif step.node_type == BotStep.NodeType.ASSIGN_AGENT:
            from apps.conversations.services.conversation_service import ConversationService

            ConversationService().escalate_to_human(session.conversation)
            result["action"] = "assigned"

        elif step.node_type == BotStep.NodeType.API_CALL:
            result = self._execute_api_call(step, session)

        elif step.node_type == BotStep.NodeType.END:
            session.is_active = False
            session.save(update_fields=["is_active", "updated_at"])
            result["message"] = self._translate(step, lang)
            result["action"] = "end"

        return result

    def _execute_api_call(self, step: BotStep, session: SessionState) -> dict:
        import httpx

        config = step.config
        url = config.get("url", "")
        method = config.get("method", "GET").upper()
        try:
            with httpx.Client(timeout=10.0) as client:
                response = getattr(client, method.lower())(url, json=config.get("body", {}))
                session.context_variables[config.get("result_var", "api_result")] = (
                    response.json()
                )
                session.save(update_fields=["context_variables", "updated_at"])
        except Exception as exc:
            logger.exception("API call failed in flow")
            session.context_variables["api_error"] = str(exc)
            session.save(update_fields=["context_variables", "updated_at"])
        session.current_step_key = step.next_step_key
        session.save(update_fields=["current_step_key", "updated_at"])
        return self._process_step(session, "")

    @staticmethod
    def _eval_condition(actual: Any, op: str, expected: Any) -> bool:
        ops = {
            "eq": lambda a, e: str(a) == str(e),
            "neq": lambda a, e: str(a) != str(e),
            "gt": lambda a, e: float(a) > float(e),
            "lt": lambda a, e: float(a) < float(e),
            "contains": lambda a, e: str(e) in str(a),
        }
        return ops.get(op, ops["eq"])(actual, expected)

    @staticmethod
    def _translate(step: BotStep, lang: str) -> str:
        return step.translations.get(lang) or step.translations.get("fr", "")

    def _get_active_session(
        self, organization: Organization, contact: Contact
    ) -> SessionState | None:
        return SessionState.all_objects.filter(
            organization=organization,
            contact=contact,
            is_active=True,
        ).first()

    def _create_session(
        self,
        organization: Organization,
        contact: Contact,
        conversation: Conversation,
        flow: BotFlow,
    ) -> SessionState:
        entry = flow.steps.filter(is_entry=True).first()
        first_step = flow.steps.first()
        if not first_step:
            raise ValueError(f"Flow {flow.id} has no steps")
        entry_key = entry.key if entry else first_step.key
        expires = timezone.now() + timedelta(minutes=flow.session_timeout_minutes)
        return SessionState.all_objects.create(
            organization=organization,
            flow=flow,
            contact=contact,
            conversation=conversation,
            current_step_key=entry_key,
            expires_at=expires,
        )

    @staticmethod
    def _is_expired(session: SessionState) -> bool:
        return session.expires_at and timezone.now() > session.expires_at
