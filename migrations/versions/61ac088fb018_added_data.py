"""adding data

Revision ID: b7102b92df61
Revises: 6ebd284fed25
Create Date: 2023-03-02 19:57:17.517199

"""
import csv
import pathlib
import random

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from app.questions.models import QuestionModel, AnswerModel
from app.web.config import get_config
# revision identifiers, used by Alembic.
revision = 'b7102b92df61'
down_revision = '6ebd284fed25'
branch_labels = None
depends_on = None

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
file_data = f"{BASE_DIR}/migrations/questions.csv"

debug = get_config(BASE_DIR)["app"]["debug"]
SUM_SCORE_ANSWER = get_config(BASE_DIR)["game"]["sum_score"]


def get_random_score(number: int, range_: int) -> list[int]:
    """
    Return list random numbers
    get_random_score(6, 100) -> [9, 14, 1, 2, 64, 10]
    where sum([9, 14, 1, 2, 64, 10]) == 100
    """
    result = []
    for i in range(number, 1, -1):
        n = random.randint(1, range_ - i)
        result.append(n)
        range_ -= n
    result.append(range_)
    random.shuffle(result)
    return result


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    questions = []
    with open(file_data, "r") as fl:
        raw_questions = csv.reader(fl, delimiter=';')
        title = []
        for q in raw_questions:
            if len(q) != 7 or str(q[0]) in title:
                continue
            scores = get_random_score(6, SUM_SCORE_ANSWER)
            answers_list = [AnswerModel(title=str(q[i + 1]).strip().lower(),
                                        score=scores[i]) for i in range(6)]
            question = QuestionModel(title=str(q[0]),
                                     answers=answers_list)
            questions.append(question)
            title.append(q[0])
    if debug:
        session.add(questions[0])
        print('First Questions added in database')
    else:
        session.add_all(questions)
        print('Questions added in database:', len(questions))
    session.commit()


def downgrade() -> None:
    # op.drop_table('answers')
    # op.drop_table('questions')
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.delete(AnswerModel)
    session.delete(QuestionModel)
