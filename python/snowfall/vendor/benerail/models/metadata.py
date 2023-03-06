import datetime

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class MetaData(BenerailBaseModel):
    api_version: str | None
    build_version: str | None
    environment: str | None
    responded_at: datetime.datetime | None
    resource_type: str | None
    resource_etag: str | None
