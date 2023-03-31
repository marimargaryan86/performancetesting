import enum


class WeightUnitEnum(enum.Enum):
    """Weight unit enum."""

    kilogram = "kilogram"
    pounds = "pounds"


class DimensionUnitEnum(enum.Enum):
    """Dimension unit enum."""

    centimeter = "centimeter"
    inch = "inch"


class BagPieceAllowanceCombinationEnum(enum.Enum):
    """Bag piece allowance combination."""

    and_operand = "and"
    or_operator = "or"


class BagCategoryEnum(enum.Enum):
    """Bag category enum."""

    carry_on = "carry_on"
    checked = "checked"


class CabinTypeEnum(enum.Enum):
    """Cabin type enum."""

    first = "first"
    business = "business"
    premium_economy = "premium_economy"
    economy = "economy"
    unknown = "unknown"


class FareGroupEnum(enum.Enum):
    """Fare group enum."""

    fare_rules = "fare_rules"
    flexible_fare = "flexible_fare"
    negotiated_private_fare = "negotiated_private_fare"
    lowest_fare = "lowest_fare"
    corporate_fare = "corporate_fare"
    non_negotiated_public_fare = "non_negotiated_public_fare"
    refundable_fare = "refundable_fare"
    unknown = "unknown"


class RowTypeEnum(enum.Enum):
    """Row type enum."""

    # E - Exit row
    exit = "exit"  # noqa: A003
    # A - Extra leg room
    extra_leg_room = "extra_leg_room"
    # K - Overwing row
    overwing = "overwing"
    # L - Lowerdeck row
    lowerdeck = "lowerdeck"
    # M - Maindeck row
    maindeck = "maindeck"
    # MV - Row with movie screen
    with_movie_screen = "with_movie_screen"
    # N - No smoking row
    no_smoking = "no_smoking"
    # S - Smoking row
    smoking = "smoking"
    # U - Upperdeck row
    upperdeck = "upperdeck"
    # X - Not overwing row
    not_overwing = "not_overwing"
    # Z - Row does not exist
    not_exist = "not_exist"


class SeatTypeEnum(enum.Enum):
    """Seat type enum."""

    # A - Aisle seat
    aisle = "aisle"
    # B - Seat with bassinet facility
    bassinet = "bassinet"
    # CC - Center section seat(s)
    center_section = "center_section"
    # E - Exit row seat
    exit = "exit"  # noqa: A003
    # H - Seat with facilities for handicapped/incapacitated passenger
    handicapped = "handicapped"
    # I - Seat suitable for adult with an infant
    infant = "infant"
    # IE - Seat not suitable for child
    no_child = "no_child"
    # J - Rear facing seat
    rear_facing = "rear_facing"
    # K - Bulkhead seat
    bulkhead = "Bulkhead_seat"
    # LS - Left side of aircraft
    left_side = "left_side"
    # N - No smoking seat
    no_smoking = "no_smoking"
    # O - Preferential seat
    preferential = "preferential"
    # RS - Right side of aircraft
    right_side = "right_side"
    # S - Smoking seat
    smoking = "smoking"
    # W - Window seat
    window = "window"
    # TODO: remove todo
    todo = "todo"
