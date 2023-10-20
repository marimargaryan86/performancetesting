from gettext import gettext as _
from types import MappingProxyType
from typing import Any

from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2

_CODE_TO_MESSAGE: MappingProxyType[int, dict[str, Any]] = MappingProxyType(
    {
        models_pb2.Channel.CHANNEL_WHATSAPP: {
            "DGT": {
                "body": _(
                    "Your gate for flight *{0}* > *{1}* has changed from *{2}* to"
                    " *{3}*",
                ),
            },
            "DTM": {
                "body": _(
                    "Your terminal for flight *{0}* > *{1}* has changed from *{2}* to"
                    " *{3}*",
                ),
            },
            "EGD": {
                "body": _(
                    "Your flight *{0}* > *{1}* is delayed.\nOld time of departure:"
                    " {2}\nNew estimated time of departure: {3}",
                ),
            },
            "DIV": {
                "body": _(
                    "Your flight from *{0}* > *{1}* has been diverted from *{2}* to"
                    " *{3}*",
                ),
            },
            "BGG": {
                "body": _(
                    "Your bag pickup location for your flight from *{0}* > *{1}* has"
                    " changed from *{2}* to *{3}*",
                ),
            },
        },
        models_pb2.Channel.CHANNEL_PUSH_NOTIFICATION: {
            "DGT": {
                "title": _("Departure gate has changed!"),
                "body": _(
                    "Your gate for flight *{0}* > *{1}* has changed from *{2}* to"
                    " *{3}*",
                ),
            },
            "DTM": {
                "title": _("Departure terminal has changed!"),
                "body": _(
                    "Your terminal for flight *{0}* > *{1}* has changed from *{2}* to"
                    " *{3}*",
                ),
            },
            "EGD": {
                "title": _("Your flight is getting delayed!"),
                "body": _(
                    "Your flight *{0}* > *{1}* is delayed.\nOld time of departure:"
                    " {2}\nNew estimated time of departure: {3}",
                ),
            },
            "DIV": {
                "title": _("Your flight has been diverted!"),
                "body": _(
                    "Your flight from *{0}* > *{1}* has been diverted from *{2}* to"
                    " *{3}*",
                ),
            },
            "BGG": {
                "title": _("Your bag pickup location has changed!"),
                "body": _(
                    "Your bag pickup location for your flight from *{0}* > *{1}* has"
                    " changed from *{2}* to *{3}*",
                ),
            },
        },
    },
)


def get_message_from_code(
    code: str,
    channel_type: int,
) -> dict[str, Any]:
    return _CODE_TO_MESSAGE[channel_type][code.upper()]
