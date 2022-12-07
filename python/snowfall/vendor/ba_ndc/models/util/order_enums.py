"""Contains application enums."""
import enum


class TicketTypeEnum(enum.Enum):
    """Ticket type enum."""

    ticket = "ticket"
    emd_associated = "emd_associated"
    emd_standalone = "emd_standalone"


class ServiceCombinationRuleEnum(enum.Enum):
    """Service combination rule enum."""

    not_permitted = "not_permitted"


class ServiceTypeEnum(enum.Enum):
    """Service type enum."""

    segment = "segment"
    seat = "seat"
    bag = "bag"
    meal = "meal"
    disability_assistance = "disability_assistance"
    unknown = "unknown"


class PenaltyTypeEnum(enum.Enum):
    """Penalty type enum."""

    change = "change"
    upgrade = "upgrade"
    cancel = "cancel"
