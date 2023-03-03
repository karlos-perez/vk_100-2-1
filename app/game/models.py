from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Boolean,
    Integer,
    BigInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.store.database import db

# Maximum number of incorrect answers per user
ATTEMPTS_ANSWER = 3

STATUS_ACTIVE = 0
STATUS_STOPPED = 1
STATUS_FINISH = 2
STATUS_ERROR = 3


STATUS_CHOICE = {
    STATUS_ACTIVE: "Игра запущенна",
    STATUS_STOPPED: "Остановлена игроком",
    STATUS_FINISH: "Игра пройдена",
    STATUS_ERROR: "Закрыта с ошибкой",
}

# class ChoiceType(types.TypeDecorator):
#     impl = types.Integer
#
#     def __init__(self, choices, **kw):
#         self.choices = dict(choices)
#         super(ChoiceType, self).__init__(**kw)
#
#     def process_bind_param(self, value, dialect):
#         # result = [k for k, v in self.choices.items() if v == value][0]
#         return value
#
#     def process_result_value(self, value, dialect):
#         return self.choices[value]


class UserModel(db):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    fullname = Column(String, default="")

    participant = relationship("ParticipantModel", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, fullname={self.fullname})>"


class ParticipantModel(db):
    __tablename__ = "participants"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, default=0)
    attempts = Column(Integer, default=ATTEMPTS_ANSWER)
    game_id = Column(
        BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )

    games = relationship(
        "GameModel",
        cascade="all, delete",
        passive_deletes=True,
        back_populates="participants",
    )
    user = relationship("UserModel", back_populates="participant")
    answers = relationship(
        "GameAnswersModel",
        cascade="all, delete",
        passive_deletes=True,
        back_populates="participant",
    )

    __table_args__ = (UniqueConstraint(user_id, game_id),)

    def __repr__(self):
        return f"<Participant(user_id={self.user_id}, game_id={self.game_id})>"


class GameModel(db):
    __tablename__ = "games"

    id = Column(BigInteger, primary_key=True)
    date_begin = Column(DateTime, nullable=False)
    date_end = Column(DateTime, default=None)
    # status = Column(ChoiceType(STATUS_CHOICE), default=STATUS_ACTIVE)
    status = Column(Integer, default=STATUS_ACTIVE)
    chat_id = Column(BigInteger, nullable=False)
    question_id = Column(BigInteger, ForeignKey("questions.id"), nullable=False)

    question = relationship("QuestionModel", back_populates="games")
    participants = relationship(
        "ParticipantModel",
        cascade="all, delete",
        passive_deletes=True,
        back_populates="games",
    )
    answers = relationship(
        "GameAnswersModel",
        cascade="all, delete",
        passive_deletes=True,
        back_populates="games",
    )

    def __str__(self):
        if self.vk_user_fullname:
            return self.vk_user_fullname
        else:
            return f"user_{self.vk_user_id_}"

    def __repr__(self):
        return f"<Game(game_id={self.game_id}, status={self.status})>"


class GameAnswersModel(db):
    __tablename__ = "game_answers"

    id = Column(BigInteger, primary_key=True)
    participant_id = Column(BigInteger, ForeignKey("participants.id"), nullable=False)
    game_id = Column(
        BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    answer = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)

    games = relationship("GameModel", back_populates="answers")
    participant = relationship("ParticipantModel", back_populates="answers")

    __table_args__ = (UniqueConstraint(answer, game_id),)

    def __repr__(self):
        return f"<GameAnswers(game_id={self.game_id}, answer={self.answer})>"
