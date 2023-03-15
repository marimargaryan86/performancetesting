import pydantic


class CachedRate(pydantic.BaseModel):
    rate: float
    currency: str
