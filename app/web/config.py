import pathlib
import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


BASE_DIR = pathlib.Path(__file__).parent.parent.parent


@dataclass
class SessionConfig:
    key: str


@dataclass
class LoggerConfig:
    level: str = "error"


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class DatabaseConfig:
    url: str


@dataclass
class QueueConfig:
    enable: bool
    url: str


@dataclass
class Config:
    admin: AdminConfig
    bot: BotConfig = None
    database: DatabaseConfig = None
    logger: LoggerConfig = None
    session: SessionConfig = None
    queue: QueueConfig = None


def get_database_url(conf) -> str:
    url = f'postgresql+asyncpg://{conf["user"]}:{conf["password"]}@{conf["host"]}:{conf["port"]}/{conf["database"]}'
    return url


def get_config(path):
    config_path = f"{path}/config.yml"
    with open(config_path) as f:
        parsed_config = yaml.safe_load(f)
    return parsed_config


def setup_config(app: "Application"):
    raw_config = get_config(BASE_DIR)

    app.config = Config(
        logger=LoggerConfig(
            level=raw_config["logger"]["level"],
        ),
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        admin=AdminConfig(
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
        ),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
            group_id=raw_config["bot"]["group_id"],
        ),
        database=DatabaseConfig(url=get_database_url(raw_config["database"])),
        queue=QueueConfig(
            enable=raw_config["queue"]["enable"], url=raw_config["queue"]["url"]
        ),
    )
