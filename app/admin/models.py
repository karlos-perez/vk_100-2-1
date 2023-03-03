from hashlib import sha256

from sqlalchemy import Column, String, BigInteger

from app.store.database.database import db


class AdminModel(db):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: dict | None):
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])
