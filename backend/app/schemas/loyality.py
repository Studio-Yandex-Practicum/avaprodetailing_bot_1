from pydantic import BaseModel
from typing import Optional


class LoyalitySettings(BaseModel):
    default_value: Optional[int]

    class Config:
        from_attibutes = True
        extra = 'forbid'
