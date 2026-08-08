"""Structured logging configuration for the whole backend.

Every module obtains a logger via `logging.getLogger(__name__)`; this
module is responsible only for *wiring up* handlers/formatters once, at
application startup, so business/service code never touches `print()` or
configures logging ad-hoc.
"""

import logging
import logging.config
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging() -> None:
    """Configure root + uvicorn loggers with a consistent format/level."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": _LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "app": {
                    "handlers": ["console"],
                    "level": settings.log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "sqlalchemy.engine": {
                    "handlers": ["console"],
                    "level": "WARNING" if not settings.debug else "INFO",
                    "propagate": False,
                },
            },
            "root": {"handlers": ["console"], "level": settings.log_level},
        }
    )
