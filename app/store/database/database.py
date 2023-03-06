from logging import getLogger
from typing import TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

if TYPE_CHECKING:
    from app.web.app import Application


db = declarative_base()


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)
        self._engine: AsyncEngine | None = None
        self._db: declarative_base | None = None
        self.session: AsyncSession | None = None

    async def connect(self, *args, **kwargs) -> None:
        self._db = db
        url = self.app.config.database.url
        self._engine = create_async_engine(url, echo=True, future=True)
        self.session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def disconnect(self, *args, **kwargs) -> None:
        try:
            await self._engine.dispose()
        except Exception as err:
            self.logger.error(err)

    async def create(self, *args, **kwargs):
        async with self._engine.begin() as conn:
            db.metadata.bind = self._engine
            await conn.run_sync(db.metadata.create_all)

    async def clear(self, *args, **kwargs):
        async with self._engine.begin() as conn:
            db.metadata.bind = self._engine
            await conn.run_sync(db.metadata.drop_all)
