from sqlalchemy import Column, String, DateTime, Boolean, Integer

from app.core.db import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(length=8), unique=True)
    telegram_id = Column(String(length=32), unique=True)
    first_name = Column(String(length=32))
    second_name = Column(String(length=32))
    last_name = Column(String(length=64))
    birth_date = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
