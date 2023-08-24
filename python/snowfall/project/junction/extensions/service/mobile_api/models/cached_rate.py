from pydantic import v1 as pydantic


class CachedRate(pydantic.BaseModel):
    rate: float
    currency: str
