from typing import Optional

from pydantic import BaseModel


class LoyalitySettings(BaseModel):
    default_value: Optional[int]

    class Config:
        from_attibutes = True
        extra = 'forbid'


class LoyalityList(BaseModel):
    amount: int

    class Config:
        extra = 'forbid'


class Loyality(LoyalityList):
    user_id: int
