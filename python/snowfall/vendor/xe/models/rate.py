from pydantic.v1 import BaseModel


class RateResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
