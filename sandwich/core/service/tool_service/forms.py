import logging
import uuid
from typing import Any

from django.db import connection
from django.db import transaction
from langchain_core.tools import BaseTool
from langchain_core.tools import tool

from sandwich.core.models.form import Form

logger = logging.getLogger(__name__)

# Note(MM): Instead of writing to the db directly from tools, a possible
# improvement here would be to use graph state to track a working copy of the
# form schema that tools can make changes to. Once the agent has completed its
# tool calls, we pull the schema of out of state and write it to the database.
#
# We cut down on db calls, but lose granularity in form "edit" history.


def build_form_schema_tools(target_form_id: uuid.UUID) -> list[BaseTool]:
    @tool
    def add_new_page_to_schema(page_name: str, page_title: str, elements: list[dict[str, Any]] | None = None) -> None:
        """
        Adds a new page to the SurveyJS form schema.

        Args:
            page_name (str): The indentifier of the new page -- this must be
            unique.
            page_title (str): The title of the new page that will be displayed
            in the form.
            elements (list[dict[str, Any]]): A list of SurveyJS elements to include in
            the new page. Defaults to `[]`.
        """

        with transaction.atomic():
            # NB: Despite asking the LLM to run tools synchronously, put a
            # lock on the object we're updating as an extra layer of safety.
            form = Form.objects.select_for_update().get(id=target_form_id)

            new_page = {"name": page_name, "title": page_title, "elements": elements if elements else []}
            logger.info("add_new_page_to_schema tool generating page", extra={"page_name": page_name})
            form.schema.setdefault("pages", []).append(new_page)
            form.save()

        # Explicitly close the connection when the tool finishes to avoid
        # pg connection timeout issues
        connection.close_if_unusable_or_obsolete()

    return [add_new_page_to_schema]
