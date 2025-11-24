import datetime

from django.utils import timezone
from langchain_core.tools import tool


@tool
def current_date_and_time() -> datetime.datetime:
    """Get the current date and time."""
    return timezone.now()
