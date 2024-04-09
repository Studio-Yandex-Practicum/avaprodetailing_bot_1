from pydantic import BaseModel
from typing import Optional


class LoyalitySettings(BaseModel):
    default_value: Optional[int]

    class Config:
        from_attibutes = True
        extra = 'forbid'


class LoyalityList(BaseModel):
    amount: int

    class Config:
        forbid_extra = True


class Loyality(LoyalityList):
    user_id: int
