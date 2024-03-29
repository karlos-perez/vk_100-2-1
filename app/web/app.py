from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.admin.models import AdminModel
from app.store import setup_store, Store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database | None = None


class Request(AiohttpRequest):
    admin: AdminModel | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self):
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})

    @property
    def config(self) -> dict:
        return self.request.app.config


app = Application()


def setup_app(config_path=None) -> Application:
    setup_config(app, config_path)
    setup_logging(app)
    session_setup(
        app, EncryptedCookieStorage(app.config.session.key, cookie_name="sessionid")
    )
    setup_routes(app)
    setup_aiohttp_apispec(
        app, title="VK Game Bot", url="/docs/swagger.json", swagger_path="/docs"
    )
    setup_middlewares(app)
    setup_store(app)
    return app
