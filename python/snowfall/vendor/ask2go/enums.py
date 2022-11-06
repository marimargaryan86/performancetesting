import enum


class AirCabinClassType(enum.Enum):
    any_ = "Any"
    premium_business = "PremiumBusiness"
    economy_with_restrictions = "EconomyWithRestrictions"
    economy_without_restrictions = "EconomyWithoutRestrictions"
    economy = "Economy"
    premium_economy = "PremiumEconomy"
    business = "Business"
    first = "First"


class PassengerType(enum.Enum):
    adult = "ADT"
    child = "CNN"
    infant = "INF"


class DocumentType(enum.Enum):
    passport = "passport"
    national_id = "nationalid"
    military = "military"
    naturalization = "naturalization"
    permit = "permit"


class Gender(enum.Enum):
    female = "Female"
    male = "Male"
    unknown = "Unknown"


class PenaltyType(enum.Enum):
    exchange = "Exchange"
    refund = "Refund"


class Applicability(enum.Enum):
    before = "Before"
    after = "After"


class OfferPriceDocType(enum.Enum):
    full_sfpd = "FullSfpd"
    basic_sfpd = "BasicSfpd"
    none = "None"
    foid = "Foid"
    russian_passport = "RussianPassport"
