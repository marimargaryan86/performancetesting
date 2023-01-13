import enum


class PhoneTypeEnum(enum.Enum):
    """Phone type enum."""

    mobile = "mobile"
    personal = "personal"


class PassengerTypeEnum(enum.Enum):
    """Passenger type enum."""

    # age above 15
    adult = "adult"
    # age 12 - 15
    # YOUNG_ADULT = "young_adult"  # TODO: Impl?
    # age 2 - 11
    child = "child"
    # age under 2
    infant = "infant"


class GenderEnum(enum.Enum):
    """Gender enum."""

    male = "male"
    female = "female"
    unspecified = "unspecified"


class PaymentCardTypeEnum(enum.Enum):
    """Payment card type enum."""

    debit = "debit"
    credit = "credit"
