from datetime import date, datetime, time, timedelta

from xsdata.models.datatype import XmlDate, XmlDateTime, XmlDuration


def date_to_xml(dt: date | None) -> XmlDate | None:
    if dt:
        return XmlDate.from_date(dt)

    return None


def datetime_to_xml(dt: datetime | None) -> XmlDateTime | None:
    if dt:
        return XmlDateTime.from_datetime(dt)

    return None


def xml_duration_to_timedelta(xml_duration: XmlDuration) -> timedelta | None:
    if xml_duration:
        return timedelta(
            days=xml_duration.days or 0,
            hours=xml_duration.hours or 0,
            minutes=xml_duration.minutes or 0,
            seconds=xml_duration.seconds or 0,
        )

    return None


def xml_date_time_to_datetime(xml_date: XmlDate, str_time: str) -> datetime | None:
    if str_time:
        return datetime.combine(xml_date.to_date(), time.fromisoformat(str_time))

    return None


def xml_date_to_date(xml_date: XmlDate) -> date:
    return xml_date.to_date()


def xml_date_to_datetime(xml_date: XmlDate) -> datetime | None:
    return datetime.combine(xml_date.to_date(), time.min)
