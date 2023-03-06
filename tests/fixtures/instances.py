import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.questions.models import AnswerModel, QuestionModel, Answer


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
