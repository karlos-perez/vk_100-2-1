from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import docs, querystring_schema, request_schema, response_schema

from app.questions.models import AnswerModel, Answer
from app.questions.schemes import (
    QuestionSchema,
    ListQuestionResponseSchema,
    QuestionIdSchema,
    QuestionDeleteSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=["questions"], summary="Add question", description="Added new questions")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = self.data
        if len(data["answers"]) != 6:
            raise HTTPBadRequest(text="There must be six answers to the question")
        # Validation: unique title answer
        answers_title = [i["title"] for i in data["answers"]]
        if len(set(answers_title)) < 6:
            raise HTTPBadRequest(text="Answers to the question should not be repeated")
        # Validation: unique title question
        if await self.store.questions.get_question_by_title(data["title"]) is not None:
            raise HTTPConflict(text="Question title is not unique")
        # Validation: sum score answers
        sum_score = 0
        for a in data["answers"]:
            sum_score += a["score"]
        if sum_score != self.config.game.sum_score:
            raise HTTPConflict(
                text=f"Sum scores answers should be equal to {self.config.game.sum_score}"
            )
        answers_list = []
        for answer in data["answers"]:
            answers_list.append(Answer(title=answer["title"], score=answer["score"]))
        question = await self.store.questions.create_question(
            title=data["title"], answers=answers_list
        )
        raw_question = QuestionSchema().dump(question)
        return json_response(data=raw_question)


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Get questions",
        description="Get question by ID or list all questions",
    )
    @querystring_schema(QuestionIdSchema)
    @response_schema(ListQuestionResponseSchema, 200)
    async def get(self):
        question_id = self.request.query.get("question_id")
        if question_id:
            question_id = int(question_id)
        questions = await self.store.questions.list_questions(question_id)
        return json_response(
            data={"questions": [QuestionSchema().dump(q) for q in questions]}
        )


class QuestionDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"], summary="Delete questions", description="Delete questions"
    )
    @querystring_schema(QuestionDeleteSchema)
    @response_schema(OkResponseSchema, 200)
    async def delete(self):
        question_id = int(self.request.query.get("question_id"))
        if await self.store.questions.get_question_by_id(question_id) is None:
            raise HTTPConflict(text=f"Question with this id not found")
        await self.store.questions.delete_question(question_id)
        return json_response(data={"message": "Question successfully deleted"})
