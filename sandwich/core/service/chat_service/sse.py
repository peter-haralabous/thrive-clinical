import logging
from typing import TYPE_CHECKING

from django.template import loader

from sandwich.core.models import Patient
from sandwich.core.service.markdown_service import markdown_to_html
from sandwich.core.service.sse_service import EventType
from sandwich.core.service.sse_service import sse_patient_channel
from sandwich.core.service.sse_service import sse_send_html
from sandwich.core.service.sse_service import sse_send_json

if TYPE_CHECKING:
    from sandwich.core.service.chat_service.chat import AssistantMessageEvent
    from sandwich.core.service.chat_service.chat import ChatEvent
    from sandwich.core.service.chat_service.chat import UserMessageEvent

logger = logging.getLogger(__name__)


def send_user_message(event: "UserMessageEvent") -> None:
    from sandwich.core.service.chat_service.chat import user_message  # noqa: PLC0415

    sse_send_html(
        sse_patient_channel(event.context.patient),
        EventType.USER_MESSAGE,
        user_message(
            patient=event.context.patient,
            content=event.content,
            timestamp=event.timestamp,
            context={"oob": True},
        ),
    )


def send_assistant_thinking(event: "ChatEvent") -> None:
    sse_send_html(
        sse_patient_channel(event.context.patient),
        EventType.ASSISTANT_THINKING,
        loader.render_to_string(
            "patient/chatty/partials/assistant_message_skeleton.html",
            context={"oob": True, "message_id": "assistant-thinking"},
        ),
    )


def send_assistant_message(event: "AssistantMessageEvent") -> None:
    sse_send_html(
        sse_patient_channel(event.context.patient),
        EventType.ASSISTANT_MESSAGE,
        loader.render_to_string(
            "patient/chatty/partials/assistant_message.html",
            context={
                "message": markdown_to_html(event.response.message),
                "buttons": event.response.buttons,
                "oob": True,
                "message_id": event.id,
            },
        ),
    )


def send_records_updated(patient: Patient) -> None:
    sse_send_json(sse_patient_channel(patient), EventType.RECORDS_UPDATED, None)
