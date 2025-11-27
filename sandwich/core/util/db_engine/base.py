import logging
import os
import threading

from django.db.backends.postgresql import base

logger = logging.getLogger(__name__)


def _connection(wrapper: base.DatabaseWrapper) -> str:
    try:
        if wrapper.connection:
            return str(wrapper.connection.pgconn.backend_pid)
        return "false"  # noqa:TRY300
    except AttributeError:
        return "unknown"


class DatabaseWrapper(base.DatabaseWrapper):
    def _extra(self):
        main_thread = threading.main_thread()
        current_thread = threading.current_thread()

        return {
            "db": {
                "id": id(self),
                "pid": os.getpid(),
                "ppid": os.getppid(),
                "connection": _connection(self),
                "main_thread": {
                    "name": main_thread.name,
                    "id": main_thread.ident,
                },
                "current_thread": {
                    "name": current_thread.name,
                    "id": current_thread.ident,
                },
            }
        }

    def __init__(self, *args, **kwargs):
        """Wrapper is created"""
        logger.info("__init__", extra=self._extra())
        super().__init__(*args, **kwargs)

    def __del__(self):
        """Wrapper is destroyed"""
        logger.info("__del__", extra=self._extra())

    def get_new_connection(self, conn_params):
        """Something tries to open the connection"""
        logger.info("get_new_connection", extra=self._extra())
        return super().get_new_connection(conn_params)

    def _close(self):
        """Something tries to close the connection"""
        logger.info("_close", extra=self._extra())
        return super()._close()  # type: ignore[misc]

    def cursor(self):
        """Something tries to use the connection"""
        logger.info("cursor", extra=self._extra())
        return super().cursor()
