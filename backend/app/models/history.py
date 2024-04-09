from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.core.config import HISTORY_MAX_LENGTH_STRING
from app.core.db import Base


class History(Base):
    date: DateTime = Column(DateTime, default=datetime.now())
    user: int = Column(int, nullable=False)
    table: str = Column(String(HISTORY_MAX_LENGTH_STRING), nullable=False)
    comment: str = Column(String(HISTORY_MAX_LENGTH_STRING), nullable=False)
