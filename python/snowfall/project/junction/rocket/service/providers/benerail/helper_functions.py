import base64
import datetime
import tempfile
import types
import zoneinfo
from collections.abc import Mapping
from gettext import gettext as _

from snowfall.vendor.benerail.models.enumeration import rcode
from snowfall.vendor.benerail.models.trip_offers import offer, summary
from snowfall.vendor.benerail.models.trips import trips

_FLEXIBILITY_NAMES = types.MappingProxyType(
    {
        "FF": _("Full flex"),
        "MF": _("Mid flex"),
        "NF": _("Non flex"),
    },
)
_FLEX_NA = _("Flex info N/A")


def get_rcode_label(
    labels: Mapping[str, rcode.RcoderesultLabels],
) -> rcode.RcoderesultLabels:
    try:
        return labels["en"]
    except KeyError:
        return labels["*"]


def get_brand_name(comfort_class_name: str, flexibility_value: str) -> str:
    return "{0} / {1}".format(
        comfort_class_name,
        _FLEXIBILITY_NAMES.get(flexibility_value[-2:], _FLEX_NA),
    ).strip(" /")


def get_train_number(leg: trips.TimedLeg) -> str:
    if leg.train_numbers:
        return ", ".join(leg.train_numbers)

    return ""


def offer_matches(
    offer_obj: offer.Offer,
    comfort_class_value: str,
    flexibility_value: str,
) -> bool:
    if comfort_class_value != get_comfort_class_value(offer_obj):
        return False

    return flexibility_value == offer_obj.flexibility.flexibility_value


def get_comfort_class_value(obj: offer.Offer | summary.OfferSummary) -> str:
    if obj.comfort_class and obj.comfort_class.comfort_class_value:
        return str(obj.comfort_class.comfort_class_value)

    return ""


def get_flexibility_value(obj: offer.Offer | summary.OfferSummary) -> str:
    if obj.flexibility and obj.flexibility.flexibility_value:
        return str(obj.flexibility.flexibility_value)

    return ""


def normalize_datetime(
    dt: datetime.datetime,
    timezone: zoneinfo.ZoneInfo,
) -> datetime.datetime:
    dt = dt.astimezone(timezone)
    if dt.hour % 2 != 0:
        dt -= datetime.timedelta(hours=1)
    return dt.replace(minute=0, second=0, microsecond=0)


def cert_tmp_path(cert_base64: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(cert_base64))

        return tmp_file.name
