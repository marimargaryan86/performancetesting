import pydantic


class PlaceUrnStr(pydantic.ConstrainedStr):
    regex = "^urn:[a-z]*:tstatn_id:[A-Z_]*$"


class ZonedDatetimeStr(pydantic.ConstrainedStr):
    regex = "".join(
        [
            "^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][",
            "0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):?([0-5][0-9])?([+-](?:2[0-3]|[",
            "01][0-9]):[0-5][0-9])$",
        ],
    )


class Longitude(pydantic.ConstrainedFloat):
    ge = -180.0
    le = 180.0


class Latitude(pydantic.ConstrainedFloat):
    ge = -90.0
    le = 90.0
