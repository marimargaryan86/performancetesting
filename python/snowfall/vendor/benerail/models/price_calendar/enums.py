from enum import Enum


class PriceCalendarErrorCodes(Enum):
    destination_not_found = "destination.not.found"
    invalid_date_format = "invalid.date.format"
    origin_not_found = "origin.not.found"
    period_invalid = "period.invalid"
