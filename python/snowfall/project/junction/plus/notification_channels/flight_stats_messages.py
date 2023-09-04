from gettext import gettext as _
from types import MappingProxyType

_CODE_TO_MESSAGE = MappingProxyType(
    {
        "DGT": _("Your gate for flight *{0}* > *{1}* has changed from *{2}* to *{3}*"),
        "EGD": _(
            "Your flight *{0}* > *{1}* is delayed.\nOld time of departure: {2}\nNew"
            " estimated time of departure: {3}",
        ),
    },
)


def get_message_from_code(code: str) -> str:
    return _CODE_TO_MESSAGE[code.upper()]
