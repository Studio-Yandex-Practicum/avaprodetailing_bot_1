from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, Integer, BigInteger, String, Boolean

MAX_NAME_LENGTH = 100


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)


class User(Base):
    telegram_id = Column(BigInteger, unique=True, name='telegram_id', nullable=True)
    first_name = Column(String(MAX_NAME_LENGTH), name='first_name', nullable=False)
    second_name = Column(String(MAX_NAME_LENGTH), name='second_name', nullable=False)
    last_name = Column(String(MAX_NAME_LENGTH), name='last_name', nullable=False)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
