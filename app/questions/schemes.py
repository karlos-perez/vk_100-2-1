from marshmallow import Schema, fields, validate

from app.web.schemes import OkResponseSchema


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    score = fields.Int(required=True, validate=validate.Range(1, 95))


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    answers = fields.Nested(AnswerSchema, many=True, required=True)


class QuestionIdSchema(Schema):
    question_id = fields.Int(required=False)


class QuestionDeleteSchema(Schema):
    question_id = fields.Int(required=True)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)


class ListQuestionResponseSchema(OkResponseSchema):
    data = fields.Nested(ListQuestionSchema)
