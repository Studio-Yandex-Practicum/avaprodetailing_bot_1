from sqlalchemy import Column, BigInteger, String
from app.core.db import Base
from app.core.config import MAX_LENGTH_USER_STRING


class User(Base):
    telegram_id: int = Column(BigInteger, unique=True)
    first_anme: str = Column(String(MAX_LENGTH_USER_STRING), nullable=False)
    