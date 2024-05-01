import datetime
from typing import Any

from pydantic import v1 as pyd

from snowfall.stdlib import money


class PassengerInfo(pyd.BaseModel):
    identifier: str
    etag: str
    date_of_birth: datetime.date


class DialogueInfo(pyd.BaseModel):
    identifier: str
    etag: str


class QuotedOffer(pyd.BaseModel):
    offer_id: str
    price: money.Money
    required_documents: Any
    rules: Any
    price_breakdown: Any
