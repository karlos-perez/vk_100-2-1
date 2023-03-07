import typing

from app.questions.views import (
    QuestionAddView,
    QuestionListView,
    QuestionDeleteView,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/questions.add_question", QuestionAddView)
    app.router.add_view("/questions.list_questions", QuestionListView)
    app.router.add_view("/questions.delete", QuestionDeleteView)
