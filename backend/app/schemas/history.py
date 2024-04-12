from datetime import datetime

from pydantic import BaseModel


class HistoryBase(BaseModel):
    id: int
    changed_by_id: int
    date: datetime
    object_id: int
    old_data: str
    new_data: str

    class Config:
        from_attributes = True


class CarHistoryDB(HistoryBase):

    class Config(HistoryBase.Config):
        pass


class UserHistoryDB(HistoryBase):

    class Config(HistoryBase.Config):
        pass


class LoyalityHistoryDB(BaseModel):
    id: int
    date: datetime
    admin_id: int
    user_id: int
    loyality_id: int
    new_data: str

    class Config:
        from_attributes = True
