from hashlib import sha256

from sqlalchemy import select

from app.admin.models import AdminModel
from app.store.base_accessor import BaseAccessor


class AdminAccessor(BaseAccessor):
    async def connect(self, *args, **kwargs):
        email = self.app.config.admin.email
        admin = await self.get_by_email(email)
        if admin is None:
            password = sha256(self.app.config.admin.password.encode()).hexdigest()
            await self.create_admin(email, password)

    async def get_by_email(self, email: str) -> AdminModel | None:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session() as session:
            return await session.scalar(query)

    async def create_admin(self, email: str, password: str) -> AdminModel:
        async with self.app.database.session() as session:
            async with session.begin():
                session.add(AdminModel(email=email, password=password))
