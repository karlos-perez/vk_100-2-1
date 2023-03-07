import random

from sqlalchemy import select, delete

from sqlalchemy.orm import joinedload

from app.store.base_accessor import BaseAccessor
from app.questions.models import AnswerModel, QuestionModel, Answer


class QuestionAccessor(BaseAccessor):
    async def create_question(self, title: str, answers: list[Answer]) -> QuestionModel:
        answers_list = [AnswerModel(title=a.title, score=a.score) for a in answers]
        async with self.app.database.session() as session:
            async with session.begin():
                question = QuestionModel(title=title, answers=answers_list)
                session.add(question)
        return question

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        query = (
            select(QuestionModel)
            .where(QuestionModel.title == title)
            .options(joinedload(QuestionModel.answers))
        )
        async with self.app.database.session() as session:
            return await session.scalar(query)

    async def get_question_by_id(self, id_: int) -> QuestionModel | None:
        query = (
            select(QuestionModel)
            .where(QuestionModel.id == id_)
            .options(joinedload(QuestionModel.answers))
        )
        async with self.app.database.session() as session:
            return await session.scalar(query)

    async def list_questions(
        self, question_id: int | None = None
    ) -> list[QuestionModel]:
        if question_id is None:
            query = select(QuestionModel).options(joinedload(QuestionModel.answers))
        else:
            query = (
                select(QuestionModel)
                .where(QuestionModel.id == question_id)
                .options(joinedload(QuestionModel.answers))
            )
        async with self.app.database.session() as session:
            result = await session.scalars(query)
            return list(result.unique())

    async def get_random_questions(self) -> QuestionModel:
        query = select(QuestionModel.id)
        async with self.app.database.session() as session:
            ids = await session.scalars(query)
            random_id = random.choice(list(ids))
            return await self.get_question_by_id(random_id)

    async def delete_question(self, question_id: int):
        query = delete(QuestionModel).where(QuestionModel.id == question_id)
        async with self.app.database.session() as session:
            async with session.begin():
                return await session.execute(query)
