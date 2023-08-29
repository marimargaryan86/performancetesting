import datetime

from pydantic import v1 as pydantic


class PassengerInfo(pydantic.BaseModel):
    identifier: str
    etag: str
    date_of_birth: datetime.date


class DialogueInfo(pydantic.BaseModel):
    identifier: str
    etag: str
