from app.questions.models import QuestionModel, AnswerModel


def answer2dict(answer: AnswerModel) -> dict:
    return {
        "title": answer.title,
        "score": answer.score,
    }


def question_to_dict(question: QuestionModel) -> dict:
    return {
        "id": int(question.id),
        "title": str(question.title),
        "answers": [answer2dict(answer) for answer in question.answers],
    }
