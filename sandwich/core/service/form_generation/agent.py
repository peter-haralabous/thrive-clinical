from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from typing import Unpack

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from sandwich.core.models.form import Form
from sandwich.core.service.agent_service.agent import AgentParameters
from sandwich.core.service.agent_service.agent import thrive_agent
from sandwich.core.service.form_generation.prompt import system_prompt
from sandwich.core.service.tool_service.forms import build_add_new_page_to_schema_tool
from sandwich.core.service.tool_service.forms import build_append_elements_to_existing_page_tool


@contextmanager
def form_gen_agent(
    form: Form,
    **params: Unpack[AgentParameters],
) -> Generator[CompiledStateGraph, Any, None]:
    # We don't need to persist form generation history in the db
    checkpointer = InMemorySaver()
    params.setdefault("checkpointer", checkpointer)
    params.setdefault(
        "tools", [build_add_new_page_to_schema_tool(form.id), build_append_elements_to_existing_page_tool(form.id)]
    )

    with thrive_agent(
        name="form_gen_agent",
        system_prompt=system_prompt,
        **params,
    ) as agent:
        yield agent
