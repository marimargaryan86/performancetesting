import types
from collections.abc import Mapping
from gettext import gettext as _

import more_itertools
from pydantic import v1 as pydantic

from snowfall.vendor.benerail.models.enumeration import rcode
from snowfall.vendor.benerail.models.trip_offers import offer
from snowfall.vendor.benerail.models.trips import trips


class UrlHasNoIdError(ValueError):
    """Raised when the URL is expected to have an ID in the path, but it hasn't."""


def last_id_of_url(url: pydantic.AnyUrl) -> str:
    if not url.path:
        raise UrlHasNoIdError

    return url.path.rsplit("/", 1)[-1]


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


def get_train_number(trip: trips.Trip) -> str:
    for leg in trip.trip_legs:
        if isinstance(leg, trips.TimedLeg) and leg.train_numbers:
            return more_itertools.first(leg.train_numbers)

    return ""


def offer_matches(
    offer_obj: offer.Offer,
    comfort_class_value: str,
    flexibility_value: str,
) -> bool:
    if comfort_class_value != get_comfort_class_value(offer_obj):
        return False

    return flexibility_value == offer_obj.flexibility.flexibility_value


def get_comfort_class_value(offer_obj: offer.Offer) -> str:
    if offer_obj.comfort_class and offer_obj.comfort_class.comfort_class_value:
        return str(offer_obj.comfort_class.comfort_class_value)

    return ""
