from marshmallow import Schema, fields


class AdminSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class StatisticSchema(Schema):
    games_count = fields.Int(dump_only=True)
    questions_count = fields.Int(dump_only=True)
    users_count = fields.Int(dump_only=True)


class UserSchema(Schema):
    fullname = fields.Str(dump_only=True)
    scores = fields.Int(dump_only=True)
    games = fields.Int(dump_only=True)


class StatisticUserSchema(Schema):
    users_count = fields.Int(dump_only=True)
    users = fields.Nested(UserSchema, many=True)


class GameSchema(Schema):
    status = fields.Str(dump_only=True)
    count = fields.Int(dump_only=True)


class StatisticGameSchema(Schema):
    games_count = fields.Int(dump_only=True)
    games = fields.Nested(GameSchema, many=True)
