from logging.config import dictConfig


def setup_logging(level: str = "INFO") -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level (e.g., "DEBUG", "INFO", "WARNING").
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }
    dictConfig(config)
