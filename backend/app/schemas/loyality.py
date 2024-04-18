from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.loyality import LoyalityAction
from app.schemas.history import LoyalityHistoryDB


class LoyalitySettings(BaseModel):
    default_value: Optional[int]

    class Config:
        from_attibutes = True
        extra = 'forbid'


class LoyalityList(BaseModel):
    action: LoyalityAction
    amount: int

    class Config:
        extra = 'forbid'


class Loyality(LoyalityList):
    user_id: int


class LoyalityListDBAdmin(Loyality):
    date: datetime
    exp_date: datetime

    class Config:
        from_attributes = True


class LoyalityDBAdmin(Loyality):
    changes: list[LoyalityHistoryDB]

    class Config:
        from_attributes = True
