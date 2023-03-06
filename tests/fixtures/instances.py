import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.game.models import UserModel, GameModel, ParticipantModel
from app.questions.models import AnswerModel, QuestionModel, Answer
from tests.fixtures import DEFAULT_TIME


@pytest.fixture
def answers() -> list[Answer]:
    return [
        Answer(title="title1", score=11),
        Answer(title="title2", score=22),
        Answer(title="title3", score=33),
        Answer(title="title4", score=9),
        Answer(title="title5", score=5),
        Answer(title="title6", score=20),
    ]


@pytest.fixture
async def question_1(db_session: AsyncSession) -> QuestionModel:
    async with db_session.begin() as session:
        question = QuestionModel(
            title="title1",
            answers=[
                AnswerModel(title="title11", score=10),
                AnswerModel(title="title12", score=15),
                AnswerModel(title="title13", score=20),
                AnswerModel(title="title14", score=5),
                AnswerModel(title="title15", score=15),
                AnswerModel(title="title16", score=35),
            ],
        )
        session.add(question)
    return question


@pytest.fixture
async def question_2(db_session: AsyncSession) -> QuestionModel:
    async with db_session.begin() as session:
        question = QuestionModel(
            title="title2",
            answers=[
                AnswerModel(title="title21", score=12),
                AnswerModel(title="title22", score=18),
                AnswerModel(title="title23", score=17),
                AnswerModel(title="title24", score=8),
                AnswerModel(title="title25", score=20),
                AnswerModel(title="title26", score=25),
            ],
        )
        session.add(question)
    return question


@pytest.fixture
async def user_1(db_session: AsyncSession) -> UserModel:
    async with db_session.begin() as session:
        user = UserModel(
            id=1,
            fullname="Noname Nobody",
        )
        session.add(user)
    return user


@pytest.fixture
async def game_1(db_session: AsyncSession) -> UserModel:
    async with db_session.begin() as session:
        game = GameModel(
            date_begin=DEFAULT_TIME,
            date_end=DEFAULT_TIME + datetime.timedelta(hours=1),
            status=0,
            chat_id=1,
            question_id=1,
        )
        session.add(game)
    return game


@pytest.fixture
async def game_2(db_session: AsyncSession) -> UserModel:
    async with db_session.begin() as session:
        game = GameModel(
            date_begin=DEFAULT_TIME + datetime.timedelta(hours=1),
            date_end=DEFAULT_TIME + datetime.timedelta(hours=2),
            status=0,
            chat_id=1,
            question_id=1,
        )
        session.add(game)
    return game


@pytest.fixture
async def participant_1(db_session: AsyncSession) -> UserModel:
    async with db_session.begin() as session:
        game = ParticipantModel(
            user_id=1,
            score=13,
            game_id=1,
        )
        session.add(game)
    return game
