from pydantic import BaseModel


class LoyalitySettings(BaseModel):
    default_value: int
