import datetime
from typing import Any, TypeVar

from xsdata.formats.dataclass import serializers
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.models.datatype import XmlDate

T = TypeVar("T")  # noqa: WPS111


def serialize(obj: Any) -> str:
    return serializers.XmlSerializer().render(obj)


def parse_xml(raw: str, obj_class: type[T]) -> T:
    return XmlParser().from_string(raw, obj_class)


def date_to_xml(dt: datetime.date | None) -> XmlDate | None:
    if dt:
        return XmlDate.from_date(dt)

    return None
