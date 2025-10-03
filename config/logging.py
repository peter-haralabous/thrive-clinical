import logging
from typing import Any

from django_datadog_logger.formatters.datadog import DataDogJSONFormatter


class CustomDataDogJSONFormatter(DataDogJSONFormatter):
    def json_record(self, *args: Any, **kwargs: Any) -> dict[str, str]:
        log_entry_dict = super().json_record(*args, **kwargs)
        # Remove PII
        log_entry_dict.pop("usr.name", None)
        log_entry_dict.pop("usr.email", None)
        return log_entry_dict


class ProcrastinateBlueprintFilter(logging.Filter):
    """Filter out Procrastinate's Blueprint info log message.

    This message is logged anytime a django management command is run,
    which is starting to clutter the logs and is frankly annoying to see.

    We aren't using blueprints yet. This message is not helpful.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return record.msg != "Adding tasks from blueprint"
