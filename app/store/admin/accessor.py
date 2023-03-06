from hashlib import sha256

from sqlalchemy import func, select

from app.admin.models import AdminModel
from app.game.models import GameModel, UserModel, ParticipantModel, STATUS_CHOICE
from app.questions.models import QuestionModel
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
            async with session.begin():
                return await session.scalar(query)

    async def create_admin(self, email: str, password: str) -> AdminModel:
        async with self.app.database.session() as session:
            async with session.begin():
                session.add(AdminModel(email=email, password=password))

    async def get_full_statistic(self) -> dict[str:int]:
        async with self.app.database.session() as session:
            async with session.begin():
                games_count = await session.execute(select(func.count(GameModel.id)))
                users_count = await session.execute(select(func.count(UserModel.id)))
                questions_count = await session.execute(
                    select(func.count(QuestionModel.id))
                )
                return {
                    "games_count": games_count.scalar(),
                    "users_count": users_count.scalar(),
                    "questions_count": questions_count.scalar(),
                }

    async def get_user_statistic(self) -> dict[str:int]:
        async with self.app.database.session() as session:
            async with session.begin():
                users_count = await session.execute(select(func.count(UserModel.id)))
                query = (
                    select(
                        UserModel.fullname,
                        func.count(ParticipantModel.user_id),
                        func.sum(ParticipantModel.score),
                    )
                    .select_from(UserModel)
                    .join(UserModel.participant)
                    .group_by(UserModel.fullname)
                )
                result = await session.execute(query)
                users = [
                    {"fullname": u[0], "games": u[1], "scores": u[2]}
                    for u in result.all()
                ]
                return {"users_count": users_count.scalar(), "users": users}

    async def get_game_statistic(self) -> dict[str:int]:
        async with self.app.database.session() as session:
            async with session.begin():
                game_count = await session.execute(select(func.count(GameModel.id)))
                query = select(GameModel.status, func.count(GameModel.status)).group_by(
                    GameModel.status
                )
                result = await session.execute(query)
                games = [
                    {"status": STATUS_CHOICE[g[0]], "count": g[1]} for g in result.all()
                ]
                return {"games_count": game_count.scalar(), "games": games}
