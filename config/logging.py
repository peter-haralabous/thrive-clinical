from typing import Any

from django_datadog_logger.formatters.datadog import DataDogJSONFormatter


class CustomDataDogJSONFormatter(DataDogJSONFormatter):
    def json_record(self, *args: Any, **kwargs: Any) -> dict[str, str]:
        log_entry_dict = super().json_record(*args, **kwargs)
        # Remove PII
        log_entry_dict.pop("usr.name", None)
        log_entry_dict.pop("usr.email", None)
        return log_entry_dict
