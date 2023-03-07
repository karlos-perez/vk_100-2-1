from datetime import datetime
from typing import Any

from sqlalchemy import select, update, and_
from sqlalchemy.orm import joinedload

from app.game.models import (
    GameModel,
    UserModel,
    ParticipantModel,
    GameAnswersModel,
    STATUS_ACTIVE,
)
from app.questions.models import QuestionModel
from app.store.base_accessor import BaseAccessor


class GameAccessor(BaseAccessor):
    async def create_game(
        self, chat_id: int, date: datetime, question_id: id
    ) -> GameModel:
        async with self.app.database.session() as session:
            async with session.begin():
                new_game = GameModel(
                    question_id=question_id, date_begin=date, chat_id=chat_id
                )
                session.add(new_game)
        return new_game

    async def update_game(self, game_id: int, values: dict[str, Any]) -> None:
        query = update(GameModel).where(GameModel.id == game_id).values(values)
        async with self.app.database.session() as session:
            async with session.begin():
                await session.execute(query)

    async def get_user_by_id(self, vk_id: int) -> UserModel | None:
        async with self.app.database.session() as session:
            return await session.get(UserModel, vk_id)

    async def create_user(self, vk_id, fullname):
        async with self.app.database.session() as session:
            async with session.begin():
                new_user = UserModel(id=vk_id, fullname=fullname)
                session.add(new_user)
        return new_user

    async def get_or_create_user(self, user_id: int) -> UserModel:
        """
        Сhecking user. Get user from database or create new user
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            user_info = await self.app.store.vk_api.get_user_info(user_id)
            user_fullname = (
                f"{user_info[0].get('last_name', '')} "
                f"{user_info[0].get('first_name', '')}"
            )
            user = await self.app.store.game.create_user(user_id, user_fullname)
        return user

    async def create_participant(self, vk_id, game_id) -> ParticipantModel:
        async with self.app.database.session() as session:
            async with session.begin():
                new_gamer = ParticipantModel(user_id=vk_id, game_id=game_id)
                session.add(new_gamer)
        return new_gamer

    async def update_participant(self, id_: int, values: dict) -> None:
        query = (
            update(ParticipantModel).where(ParticipantModel.id == id_).values(values)
        )
        async with self.app.database.session() as session:
            async with session.begin():
                await session.execute(query)

    async def get_participant_by_user_id(
        self, user_id: int, game_id: int
    ) -> ParticipantModel:
        query = (
            select(ParticipantModel)
            .where(
                and_(
                    ParticipantModel.user_id == user_id,
                    ParticipantModel.game_id == game_id,
                )
            )
            .options(joinedload(ParticipantModel.user))
        )
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.scalar(query)
                return result

    async def create_answer_game(
        self, user_id: int, game_id: int, answer: str, is_correct: bool = False
    ) -> GameAnswersModel:
        async with self.app.database.session() as session:
            async with session.begin():
                new_answer = GameAnswersModel(
                    participant_id=user_id,
                    game_id=game_id,
                    answer=answer,
                    is_correct=is_correct,
                )
                session.add(new_answer)
        return new_answer

    async def get_active_games(self) -> dict[GameModel.chat_id : GameModel.id]:
        """
        Return dict games with status Active
        """
        result = []
        query = (
            select(GameModel)
            .where(GameModel.status == STATUS_ACTIVE)
            .order_by(GameModel.date_begin.desc())
            .options(joinedload(GameModel.question).joinedload(QuestionModel.answers))
        )
        async with self.app.database.session() as session:
            async with session.begin():
                games = await session.scalars(query)
                if games:
                    result = list(games.unique())
        return result

    async def get_respondent_user(self, game_id: int) -> ParticipantModel:
        query = select(ParticipantModel).where(
            and_(ParticipantModel.game_id == game_id, ParticipantModel.attempts > 0)
        )
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.scalar(query)
                return result

    async def get_correct_answers(self, game_id: int) -> list[GameAnswersModel]:
        result = []
        query = select(GameAnswersModel).where(
            and_(
                GameAnswersModel.game_id == game_id, GameAnswersModel.is_correct == True
            )
        )
        async with self.app.database.session() as session:
            async with session.begin():
                answers = await session.scalars(query)
                if answers:
                    result = list(answers.unique())
        return result

    async def get_user_game_points(self, game_id: int):
        result = []
        query = (
            select(ParticipantModel)
            .where(ParticipantModel.game_id == game_id)
            .options(joinedload(ParticipantModel.user))
            .order_by(ParticipantModel.score.desc())
        )
        async with self.app.database.session() as session:
            async with session.begin():
                recipients = await session.scalars(query)
                result = list(recipients.unique())
        return result
