from dataclasses import dataclass
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import relationship

from app.store.database.database import db


@dataclass
class Answer:
    title: str
    score: int


@dataclass
class Question:
    title: str
    answers: list[Answer]


class QuestionModel(db):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False, unique=True)

    games = relationship("GameModel", back_populates="question")
    answers = relationship(
        "AnswerModel",
        back_populates="question",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Question(id={self.id}, title={self.title})>"

    def to_dict(self):
        answers = {i.title: i.score for i in self.answers}
        return {"title": self.title, "answers": answers}


class AnswerModel(db):
    __tablename__ = "answers"

    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    score = Column(Integer, nullable=False, default=False)
    question_id = Column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )

    question = relationship("QuestionModel", back_populates="answers")

    def __repr__(self):
        return f"<Answer(id={self.id}, title={self.title})>"
