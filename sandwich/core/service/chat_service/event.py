import abc
import dataclasses
import datetime
import uuid
from enum import StrEnum
from typing import Unpack

from django.utils import timezone
from langchain_core.messages import HumanMessage
from langgraph._internal._typing import StateLike
from pydantic import BaseModel

from sandwich.core.service.agent_service.agent import AgentParameters
from sandwich.core.service.chat_service.agents import chat_agent
from sandwich.core.service.chat_service.chat import ChatContext
from sandwich.core.service.chat_service.response import ChatResponse
from sandwich.core.service.chat_service.sse import send_assistant_message
from sandwich.core.service.chat_service.sse import send_assistant_thinking
from sandwich.core.service.ingest.extract_records import RecordsResponse
from sandwich.core.service.prompt_service.chat import document_upload_template
from sandwich.core.service.prompt_service.chat import file_upload_context


class ChatEventType(StrEnum):
    ASSISTANT_MESSAGE = "assistant_message"
    USER_MESSAGE = "user_message"
    FILE_UPLOADED = "file_uploaded"


class ChatEvent(BaseModel, abc.ABC):
    context: ChatContext
    type: ChatEventType

    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = dataclasses.field(default_factory=lambda: timezone.now())


class AssistantMessageEvent(ChatEvent):
    type: ChatEventType = ChatEventType.ASSISTANT_MESSAGE
    response: ChatResponse


class IncomingChatEvent(ChatEvent, abc.ABC):
    @abc.abstractmethod
    def build_state(self) -> "StateLike":
        """Build the agent state for this event."""


class FileUploadEvent(IncomingChatEvent):
    type: ChatEventType = ChatEventType.FILE_UPLOADED
    document_id: str
    document_filename: str
    records: RecordsResponse

    def build_state(self) -> "StateLike":
        return document_upload_template.invoke(file_upload_context(self))


class UserMessageEvent(IncomingChatEvent):
    type: ChatEventType = ChatEventType.USER_MESSAGE
    content: str

    def build_state(self) -> "StateLike":
        return {  # type: ignore[return-value]
            "messages": [
                HumanMessage(
                    content=self.content,
                    response_metadata={
                        "timestamp": self.timestamp,
                        "message_id": self.id,
                    },
                ),
            ],
        }


def receive_chat_event(
    event: "IncomingChatEvent",
    **params: "Unpack[AgentParameters]",
) -> None:
    # 1. Notify that the assistant is thinking
    send_assistant_thinking(event)

    # 2. Process the event with the chat agent
    with chat_agent(event.context.user, event.context.patient, **params) as agent:
        response = agent.invoke(
            agent=agent,
            input=event.build_state(),
            config=event.context.config(),
        )

    # 3. Send the assistant's message
    message = AssistantMessageEvent(response=response["structured_response"], context=event.context)
    send_assistant_message(message)
