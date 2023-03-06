import logging
import pathlib
from unittest.mock import AsyncMock, patch

import pytest

from aiohttp.test_utils import TestClient, loop_context
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.store import Store
from app.store.vk_api.accessor import VkApiAccessor
from app.web.app import setup_app, Application
from app.web.config import Config


BASE_DIR = pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session")
def event_loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
async def server() -> Application:
    config_path = f"{BASE_DIR}/test_config.yml"
    app = setup_app(config_path)
    return app


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture
def db_session(server):
    return server.database.session


# DB transaction rollback
# @pytest.fixture
# async def db_session(server):
#     session = await server.database.session()
#     transaction = await session.begin()
#     yield session
#     await transaction.rollback()
#     await session.close()


@pytest.fixture(autouse=True)
def cli(aiohttp_client, event_loop, server) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(server))


@pytest.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin.login",
        data={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    yield cli


@pytest.fixture(autouse=True, scope="function")
async def clear_db(server):
    yield
    try:
        session = AsyncSession(server.database._engine)
        connection = session.connection()
        for table in server.database._db.metadata.tables:
            await session.execute(text(f"TRUNCATE {table} CASCADE"))
            await session.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1"))

        await session.commit()
        connection.close()

    except Exception as err:
        logging.warning(err)


# Mock VK_api accessor
@pytest.fixture(scope="session", autouse=True)
def vk_api():
    with patch(
        "app.store.vk_api.accessor.VkApiAccessor", AsyncMock(spec=VkApiAccessor)
    ):
        yield
