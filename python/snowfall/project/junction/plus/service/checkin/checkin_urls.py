from types import MappingProxyType
from typing import Any

_IATA_TO_CHECKIN: MappingProxyType[str, dict[str, Any]] = MappingProxyType(
    {
        "A3": {
            "url": "https://en.aegeanair.com/plan/check-in/",
            "open_hours": 48,
        },
        "AF": {
            "url": "https://wwws.airfrance.fr/en/check-in",
            "open_hours": 30,
        },
        "LH": {
            "url": "https://www.lufthansa.com/de/en/online-check-in",
            "open_hours": 30,
        },
        "BA": {
            "url": (
                "https://www.britishairways.com/travel/olcilandingpageauthreq/public"
            ),
            "open_hours": 24,
        },
        "FR": {
            "url": "https://www.ryanair.com/gb/en/lp/check-in",
            "open_hours": 48,
        },
        "QR": {
            "url": "https://cki.qatarairways.com/cki/dashboard",
            "open_hours": 36,
        },
        "LX": {
            "url": "https://checkin.swiss.com/web#ck_retrieve",
            "open_hours": 23,
        },
        "U2": {
            "url": "https://www.easyjet.com/en?accntmdl=2",
            "open_hours": 720,
        },
        "OS": {
            "url": "https://www.austrian.com/us/en/online-check-in",
            "open_hours": 47,
        },
        "TK": {
            "url": "https://www.turkishairlines.com/en-int/flights/manage-booking/",
            "open_hours": 24,
        },
    },
)


def get_url_from_iata(iata_code: str) -> str:
    return _IATA_TO_CHECKIN[iata_code.upper()]["url"]


def get_open_hours_from_iata(iata_code: str) -> int:
    return _IATA_TO_CHECKIN[iata_code.upper()]["open_hours"]
