from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import docs, querystring_schema, request_schema, response_schema

from app.questions.models import AnswerModel
from app.questions.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ListQuestionResponseSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
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
        answers_list = []
        for answer in data["answers"]:
            answers_list.append(
                AnswerModel(title=answer["title"], score=answer["score"])
            )
        question = await self.store.questions.create_question(
            title=data["title"], answers=answers_list
        )
        raw_question = QuestionSchema().dump(question)
        return json_response(data=raw_question)


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"], summary="List questions", description="List all questions"
    )
    @response_schema(ListQuestionResponseSchema, 200)
    async def get(self):
        questions = await self.store.questions.list_questions()
        return json_response(
            data={"questions": [QuestionSchema().dump(q) for q in questions]}
        )
