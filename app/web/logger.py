import logging
import pathlib
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


BASE_DIR = pathlib.Path(__file__).parent.parent.parent

LEVEL = {
    "noset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
    "critical": logging.CRITICAL,
}


def setup_logging(app: "Application") -> None:
    path_log_file = f"{BASE_DIR}/logs/app.log"
    file_log = logging.FileHandler(path_log_file)
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out),
                        format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=LEVEL[app.config.logger.level])
