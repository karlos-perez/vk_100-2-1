from dataclasses import asdict

from sqlalchemy import select, delete

from app.questions.models import AnswerModel, QuestionModel, Answer
from app.store import Store
from tests.app import question_to_dict
from tests.utils import ok_response, check_empty_table_exists, error_response


class TestQuestionsAccessor:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "questions")
        await check_empty_table_exists(cli, "answers")

    async def test_create_question(self, cli, store: Store, answers):
        question_title = "title"
        question = await store.questions.create_question(question_title, answers)
        assert type(question) is QuestionModel

        async with cli.app.database.session() as session:
            result = await session.execute(select(QuestionModel))
            questions = result.scalars().all()

            result = await session.execute(select(AnswerModel))
            db_answers = result.scalars().all()

        assert len(questions) == 1
        db_question = questions[0]

        assert db_question.title == question_title
        assert len(db_answers) == len(answers)

        for answer_in_db, answer_actual in zip(db_answers, answers):
            assert answer_in_db.title == answer_actual.title
            assert answer_in_db.score == answer_actual.score

    async def test_get_question_by_title(
        self, cli, store: Store, question_1: QuestionModel
    ):
        title = question_1.title
        question = await store.questions.get_question_by_title(title)
        assert question_1.to_dict() == question.to_dict()

    async def test_get_question_by_id(
        self, cli, store: Store, question_1: QuestionModel
    ):
        id_ = question_1.id
        question = await store.questions.get_question_by_id(id_)
        assert question_1.to_dict() == question.to_dict()

    # async def test_list_questions(self, cli, store: Store, question_1: QuestionModel, question_2: QuestionModel):
    #     questions = await store.questions.list_questions()
    #     assert list(questions) == [question_1, question_2]

    async def test_check_cascade_delete(self, cli, question_1: QuestionModel):
        async with cli.app.database.session() as session:
            await session.execute(
                delete(QuestionModel).where(QuestionModel.id == question_1.id)
            )
            await session.commit()

            result = await session.execute(
                select(AnswerModel).where(AnswerModel.question_id == question_1.id)
            )
            db_answers = result.scalars().all()
        assert len(db_answers) == 0


class TestQuestionAddView:
    url = "/questions.add_question"

    async def test_success(self, authed_cli, answers: list[Answer]):
        response = await authed_cli.post(
            self.url,
            json=dict(title="title3", answers=[asdict(a) for a in answers]),
        )
        assert response.status == 200
        data = await response.json()
        question = {
            "id": 1,
            "title": "title3",
            "answers": [
                {"score": 11, "title": "title1"},
                {"score": 22, "title": "title2"},
                {"score": 33, "title": "title3"},
                {"score": 9, "title": "title4"},
                {"score": 5, "title": "title5"},
                {"score": 20, "title": "title6"},
            ],
        }
        assert data == ok_response(data=question)

    async def test_unauthorized(self, cli, answers):
        response = await cli.post(
            self.url,
            json=dict(title="title", answers=[asdict(a) for a in answers]),
        )
        assert response.status == 401
        data = await response.json()
        assert data == error_response(
            status="unauthorized",
            message="401: Unauthorized",
        )

    async def test_question_exists(self, authed_cli, question_1, answers):
        response = await authed_cli.post(
            self.url,
            json=dict(title=question_1.title, answers=[asdict(a) for a in answers]),
        )
        assert response.status == 409
        data = await response.json()
        assert data == error_response(
            status="conflict",
            message="Question title is not unique",
        )

    async def test_answers_length(self, authed_cli, answers):
        response = await authed_cli.post(
            self.url,
            json=dict(title="title", answers=[asdict(a) for a in answers][:2]),
        )
        assert response.status == 400
        data = await response.json()
        assert data == error_response(
            status="bad_request",
            message="There must be six answers to the question",
        )

    async def test_answers_are_unique(self, authed_cli, answers):
        answers[0] = Answer(title="title2", score=11)
        response = await authed_cli.post(
            self.url,
            json=dict(title="title", answers=[asdict(a) for a in answers]),
        )
        assert response.status == 400
        data = await response.json()
        assert data == error_response(
            status="bad_request",
            message="Answers to the question should not be repeated",
        )

    async def test_answers_sum_score(self, authed_cli, answers):
        answers[0] = Answer(title="title1", score=22)
        response = await authed_cli.post(
            self.url,
            json=dict(title="title", answers=[asdict(a) for a in answers]),
        )
        assert response.status == 409
        data = await response.json()
        assert data == error_response(
            status="conflict",
            message="Sum scores answers should be equal to 100",
        )


class TestQuestionListView:
    url = "/questions.list_questions"

    async def test_success(self, authed_cli, question_1, question_2):
        response = await authed_cli.get(self.url)
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "questions": [
                    question_to_dict(question_1),
                    question_to_dict(question_2),
                ]
            }
        )

    async def test_one_question(self, authed_cli, question_1, question_2):
        response = await authed_cli.get(self.url, params={"question_id": 1})
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "questions": [
                    question_to_dict(question_1),
                ]
            }
        )

    async def test_no_question(self, authed_cli, question_1, question_2):
        response = await authed_cli.get(self.url, params={"question_id": 5})
        assert response.status == 200
        data = await response.json()
        assert data == ok_response({"questions": []})


class TestQuestionDeleteView:
    url = "/questions.delete"

    async def test_success(self, authed_cli, question_1):
        response = await authed_cli.delete(self.url, params={"question_id": 1})
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(data={"message": "Question successfully deleted"})

    async def test_unauthorized(self, cli, question_1):
        response = await cli.delete(self.url, params={"question_id": 1})
        assert response.status == 401
        data = await response.json()
        assert data == error_response(
            status="unauthorized",
            message="401: Unauthorized",
        )

    async def test_question_not_exists(self, authed_cli):
        response = await authed_cli.delete(self.url, params={"question_id": 1})
        assert response.status == 409
        data = await response.json()
        assert data == error_response(
            status="conflict",
            message="Question with this id not found",
        )

    async def test_no_params(self, authed_cli):
        response = await authed_cli.delete(self.url)
        assert response.status == 400
        data = await response.json()
        assert data == error_response(
            status="bad_request",
            message="Unprocessable Entity",
            data={"question_id": ["Missing data for required field."]},
        )

    async def test_different_method(self, authed_cli, question_1):
        response = await authed_cli.get(self.url, params={"question_id": 1})
        assert response.status == 405
        data = await response.json()
        assert data == error_response(
            status="not_implemented", message="405: Method Not Allowed"
        )
