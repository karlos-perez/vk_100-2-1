import logging
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


level = {
    "noset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
    "critical": logging.CRITICAL,
}


def setup_logging(app: "Application") -> None:
    logging.basicConfig(level=level[app.config.logger.level])
