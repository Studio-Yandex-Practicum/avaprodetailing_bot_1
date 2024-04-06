from sqlalchemy import Column, BigInteger, String, Boolean
from app.core.db import Base
from app.core.config import MAX_LENGTH_USER_STRING, PHONE_LENGTH_STRING


class User(Base):
    telegram_id: int = Column(BigInteger, unique=True)
    first_name: str = Column(String(MAX_LENGTH_USER_STRING), nullable=False)
    second_name: str = Column(String(MAX_LENGTH_USER_STRING), nullable=False)
    last_name: str = Column(String(MAX_LENGTH_USER_STRING), nullable=False)
    phone_number: str = Column(
        String(PHONE_LENGTH_STRING), nullable=False, unique=True
    )
    is_admin: bool = Column(Boolean, default=False)
    is_superuser: bool = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__} (first_name: {self.first_name} '
            f'second_name = {self.second_name} '
            f'last_name = {self.last_name} phone_number = {self.phone_number}'
        )
