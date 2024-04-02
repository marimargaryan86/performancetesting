import datetime

from pydantic import v1 as pyd


class PassengerInfo(pyd.BaseModel):
    identifier: str
    etag: str
    date_of_birth: datetime.date


class DialogueInfo(pyd.BaseModel):
    identifier: str
    etag: str
