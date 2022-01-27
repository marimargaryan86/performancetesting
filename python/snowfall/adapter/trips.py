import dataclasses
import datetime
import uuid


@dataclasses.dataclass(frozen=True)
class Trip(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime
