from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional

from xsdata.models.datatype import (
    XmlDate,
    XmlDateTime,
    XmlDuration,
    XmlPeriod,
    XmlTime,
)


class AdjustCostAndRevenueTicketableFareTypeAdjustmentReason(Enum):
    DELAYED_COMPENSATION = "DELAYED_COMPENSATION"
    STRIKE = "STRIKE"
    TRAIN_CANCELLATION = "TRAIN_CANCELLATION"
    SUPPLY_CHANNEL_SYSTEM_ISSUE = "SUPPLY_CHANNEL_SYSTEM_ISSUE"
    RETURNED_COUPON = "RETURNED_COUPON"
    MISCELLANEOUS_ADJUSTMENT = "MISCELLANEOUS_ADJUSTMENT"


class AuthenticatePayerV2AuthenticationStatusType(Enum):
    """Acceptable values: AUTHENTICATION_SUCCESSFUL, AUTHENTICATION_FAILED, CHALLENGE_REQUIRED,
    RETRY"""

    AUTHENTICATION_SUCCESSFUL = "AUTHENTICATION_SUCCESSFUL"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    CHALLENGE_REQUIRED = "CHALLENGE_REQUIRED"
    RETRY = "RETRY"


class AuthenticatePayerV2BrowserChallengeWindowSizeType(Enum):
    """Acceptable values: WINDOWED_250X400, WINDOWED_390X400, WINDOWED_500X600, WINDOWED_600X400,
    FULL_SCREEN"""

    WINDOWED_250_X400 = "WINDOWED_250X400"
    WINDOWED_390_X400 = "WINDOWED_390X400"
    WINDOWED_500_X600 = "WINDOWED_500X600"
    WINDOWED_600_X400 = "WINDOWED_600X400"
    FULL_SCREEN = "FULL_SCREEN"


class AuthenticatePayerV2BrowserColorDepthType(Enum):
    """Acceptable values: ONE_BIT, TWO_BITS, FOUR_BITS, EIGHT_BITS, FIFTEEN_BITS,
    SIXTEEN_BITS,TWENTY_FOUR_BITS, THIRTY_TWO_BITS, FORTY_EIGHT_BITS"""

    ONE_BIT = "ONE_BIT"
    TWO_BITS = "TWO_BITS"
    FOUR_BITS = "FOUR_BITS"
    FIFTEEN_BITS = "FIFTEEN_BITS"
    SIXTEEN_BITS = "SIXTEEN_BITS"
    TWENTY_FOUR_BITS = "TWENTY_FOUR_BITS"
    THIRTY_TWO_BITS = "THIRTY_TWO_BITS"
    FORTY_EIGHT_BITS = "FORTY_EIGHT_BITS"


class AuthenticatePayerV2CreditCardTypeType(Enum):
    AX = "AX"
    VI = "VI"
    CA = "CA"


class AuthenticatePayerV2DebitCardTypeType(Enum):
    AX = "AX"
    VI = "VI"
    CA = "CA"


@dataclass(frozen=True)
class BookingServicesException:
    class Meta:
        namespace = "http://railgds.net/ws/booking"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class CostAdjustmentTypeType(Enum):
    TICKET = "TICKET"
    RESERVATION = "RESERVATION"
    TICKETED_RES = "TICKETED_RES"


@dataclass(frozen=True)
class DelayRefundEligibilityType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    eligible: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ExchangeShoppingQueryFareFilter(Enum):
    NONE = "NONE"
    CHEAPEST = "CHEAPEST"
    CHEAPEST_ONEWAY_AND_ROUNDTRIP = "CHEAPEST_ONEWAY_AND_ROUNDTRIP"
    CHEAPEST_WITH_TC_GROUPS = "CHEAPEST_WITH_TC_GROUPS"
    CHEAPEST_ONEWAY_AND_ROUNDTRIP_WITH_TC_GROUPS = (
        "CHEAPEST_ONEWAY_AND_ROUNDTRIP_WITH_TC_GROUPS"
    )
    CHEAPEST_ONEWAY_AND_ROUNDTRIP_WITH_TC_GROUPS_AND_CORP_FARES = (
        "CHEAPEST_ONEWAY_AND_ROUNDTRIP_WITH_TC_GROUPS_AND_CORP_FARES"
    )
    OPEN = "OPEN"
    CHEAPEST_OPEN = "CHEAPEST_OPEN"
    GB_FARES = "GB_FARES"


class FareAcceptanceType(Enum):
    ANY = "ANY"
    ALL = "ALL"


class IntermediateTravelPointActivityEnumeration(Enum):
    NORMAL = "NORMAL"
    PICK_UP_ONLY = "PICK_UP_ONLY"
    SET_DOWN_ONLY = "SET_DOWN_ONLY"
    REQUEST_STOP = "REQUEST_STOP"


class IntermediateTravelPointStatusEnumeration(Enum):
    SCHEDULED = "SCHEDULED"
    ON_TIME = "ON_TIME"
    DELAYED = "DELAYED"
    OVERDUE = "OVERDUE"
    CANCELED = "CANCELED"


class IntermediateTravelPointTypeEnumeration(Enum):
    ORIGIN = "ORIGIN"
    INTERMEDIATE = "INTERMEDIATE"
    DESTINATION = "DESTINATION"


class OneOrTwoType(Enum):
    VALUE_1 = "1"
    VALUE_2 = "2"


class OrderStatusFilterType(Enum):
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    TICKETED = "TICKETED"
    ABANDONED = "ABANDONED"
    RELEASED = "RELEASED"
    CANCELED = "CANCELED"
    RETURNED = "RETURNED"
    WITHDRAWN = "WITHDRAWN"
    PRINTING = "PRINTING"
    REPLACED = "REPLACED"


@dataclass(frozen=True)
class ParametersValidateDelayRepayRefundStatusRequestType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    set_delay_repay: bool | None = field(
        default=None,
        metadata={
            "name": "setDelayRepay",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class PriceAcceptanceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    value: bool | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    threshold: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "fraction_digits": 2,
        },
    )
    currency: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class ReasonForRejectionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


class ReasonTypeType(Enum):
    DELAY_REPAID = "DELAY_REPAID"
    CANCELLED = "CANCELLED"
    PART_CANCELLED = "PART_CANCELLED"
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class RefundAmountType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    value: Decimal | None = field(
        default=None,
        metadata={
            "required": True,
            "min_exclusive": Decimal(0),
        },
    )
    currency: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ReservationType(Enum):
    SEAT = "SEAT"
    ROOM = "ROOM"
    TICKET = "TICKET"
    TICKETED_RES = "TICKETED_RES"
    BIKE = "BIKE"


class ReservationTypeEnum(Enum):
    SEAT = "SEAT"


class SearchBookFilterType(Enum):
    TRAVEL_PASS = "travelPass"


@dataclass(frozen=True)
class TicketableFareLocatorsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    any_element: object | None = field(
        default=None,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
        },
    )
    ticketable_fare_locator: list[str] = field(
        default_factory=list,
        metadata={
            "name": "ticketableFareLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "min_occurs": 1,
        },
    )


class TokenPaymentTypeType(Enum):
    CC = "CC"
    DB = "DB"


class VoidOverrideTypeType(Enum):
    EXCEPTION = "EXCEPTION"


class BookingRecordStatus(Enum):
    BALANCED = "BALANCED"
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    CLOSED = "CLOSED"


class CarrierRestrictionType2(Enum):
    PREFERRED = "PREFERRED"
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"


class CarrierRestrictionsType2(Enum):
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"
    PREFERRED = "PREFERRED"


class CouponType(Enum):
    SEAT = "SEAT"
    TICKET = "TICKET"


class EquipmentTypeRestrictionCode(Enum):
    HSP = "HSP"
    ICY = "ICY"
    BLR = "BLR"
    APT = "APT"
    CMT = "CMT"
    BUS = "BUS"
    BUR = "BUR"
    XBU = "XBU"
    MCT = "MCT"
    NIT = "NIT"
    NAT = "NAT"
    FRY = "FRY"
    PED = "PED"
    STR = "STR"
    TAX = "TAX"
    TRM = "TRM"
    TRL = "TRL"
    PFC = "PFC"
    HOV = "HOV"
    TRS = "TRS"
    UNK = "UNK"


class EquipmentTypeRestrictionType(Enum):
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"


class OrderStatus(Enum):
    PENDING = "PENDING"
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    TICKETED = "TICKETED"
    ABANDONED = "ABANDONED"
    RELEASED = "RELEASED"
    CANCELED = "CANCELED"
    RETURNED = "RETURNED"
    WITHDRAWN = "WITHDRAWN"
    INVALID = "INVALID"
    PRINTING = "PRINTING"
    REPLACED = "REPLACED"


class ReceiveCouponsReturnType(Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"


class ResponseSpecIntermediatePoints(Enum):
    CONNECTION_POINTS_ONLY = "CONNECTION_POINTS_ONLY"
    CONNECTION_POINTS_AND_STOPS = "CONNECTION_POINTS_AND_STOPS"
    NONE = "NONE"


class ResponseSpecProductType(Enum):
    TICKET = "TICKET"
    RESERVATION = "RESERVATION"


class ResponseSpecValidFareTypes(Enum):
    ALL = "ALL"
    PRIVATE_ONLY = "PRIVATE_ONLY"
    PUBLIC_ONLY = "PUBLIC_ONLY"


class AddressTypeAddressType(Enum):
    HOME = "HOME"
    BUSINESS = "BUSINESS"
    UNKNOWN = "UNKNOWN"


class AmenityTypeType(Enum):
    BAGGAGE = "BAGGAGE"
    BAR = "BAR"
    BUFFET = "BUFFET"
    DINING = "DINING"
    HOT_FOOD = "HOT_FOOD"
    LOUNGE = "LOUNGE"
    MEAL = "MEAL"
    NETWORK = "NETWORK"
    NEWSPAPER = "NEWSPAPER"
    QUIET = "QUIET"
    SNACK = "SNACK"
    TAXI = "TAXI"
    TROLLEY = "TROLLEY"
    WHEELCHAIR = "WHEELCHAIR"
    WHEELCHAIR_RES = "WHEELCHAIR_RES"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    POWER_SOCKET = "POWER_SOCKET"
    LOUNGE_ACCESS = "LOUNGE_ACCESS"
    INTERNET = "INTERNET"
    INTERNET_AVAILABLE = "INTERNET_AVAILABLE"
    PARKING = "PARKING"
    PRIVATE = "PRIVATE"
    TOILET = "TOILET"
    BICYCLE = "BICYCLE"
    BICYCLE_AVAILABLE = "BICYCLE_AVAILABLE"
    PRIORITY_BOARDING = "PRIORITY_BOARDING"
    VALET_PARKING = "VALET_PARKING"
    RESTAURANT_1_ST = "RESTAURANT_1ST"


@dataclass(frozen=True)
class AuthorizationNumbersType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    authorization_number: list["AuthorizationNumbersType.AuthorizationNumber"] = field(
        default_factory=list,
        metadata={
            "name": "authorizationNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )

    @dataclass(frozen=True)
    class AuthorizationNumber:
        passenger_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "passengerIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )
        value: str | None = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass(frozen=True)
class BarCodeTypes:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    bar_code_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "barCodeType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class BaseConfirmationCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    cardholder_name_last: str | None = field(
        default=None,
        metadata={
            "name": "cardholderNameLast",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    cardholder_name_first: str | None = field(
        default=None,
        metadata={
            "name": "cardholderNameFirst",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cardholder_name_middle: str | None = field(
        default=None,
        metadata={
            "name": "cardholderNameMiddle",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    card_number: str | None = field(
        default=None,
        metadata={
            "name": "cardNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    expiration_year_month: XmlPeriod | None = field(
        default=None,
        metadata={
            "name": "expirationYearMonth",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


class BaseCreditCardTypeType(Enum):
    AX = "AX"
    VI = "VI"
    CA = "CA"
    DI = "DI"
    UA = "UA"
    DC = "DC"
    JC = "JC"


class BaseDebitCardTypeType(Enum):
    SD = "SD"
    VD = "VD"
    MD = "MD"


@dataclass(frozen=True)
class BaseEcheckType:
    class Meta:
        name = "BaseECheckType"
        target_namespace = "http://railgds.net/ws/commontypes"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


class BaseExchangeOptionTypeExchangeOptionType(Enum):
    EVEN_EXCHANGE = "EVEN_EXCHANGE"
    ADD_COLLECT = "ADD_COLLECT"
    REFUND = "REFUND"


@dataclass(frozen=True)
class BaseExchangeSetType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    exchange_set_id: str | None = field(
        default=None,
        metadata={
            "name": "exchangeSetID",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class BaseVoucherType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    validation_code: str | None = field(
        default=None,
        metadata={
            "name": "validationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    recipient_name: str | None = field(
        default=None,
        metadata={
            "name": "recipientName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class BookingNoteType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    created_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "createdDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    booking_note_locator: str | None = field(
        default=None,
        metadata={
            "name": "bookingNoteLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    agent_id: str | None = field(
        default=None,
        metadata={
            "name": "agentId",
            "type": "Attribute",
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class BookingRecordTypeStatus(Enum):
    BALANCED = "BALANCED"
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class CampaignResponseType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    success: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    display_method: str | None = field(
        default=None,
        metadata={
            "name": "displayMethod",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class CampaignType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    campaign_code: str | None = field(
        default=None,
        metadata={
            "name": "campaignCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    validation_code: str | None = field(
        default=None,
        metadata={
            "name": "validationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    recipient_name: str | None = field(
        default=None,
        metadata={
            "name": "recipientName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


class CancellationReasonType(Enum):
    DISRUPTION = "DISRUPTION"
    FULFILLMENT_FAILURE = "FULFILLMENT_FAILURE"
    FULL_TICKET_NOT_REQD = "FULL_TICKET_NOT_REQD"
    NO_UPGRADE_AVAILABLE = "NO_UPGRADE_AVAILABLE"
    NO_RESERVATION_AVAILABLE = "NO_RESERVATION_AVAILABLE"
    PARTIAL_TICKET_NOT_REQD = "PARTIAL_TICKET_NOT_REQD"
    OTHER = "OTHER"
    EXCHANGED = "EXCHANGED"
    TRAVEL_PASS_EXCHANGED = "TRAVEL_PASS_EXCHANGED"
    VOID = "VOID"
    VOID_EXCEPTION = "VOID_EXCEPTION"


@dataclass(frozen=True)
class CarbonDataComparisonType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    rail_data: Decimal | None = field(
        default=None,
        metadata={
            "name": "railData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    car_data: Decimal | None = field(
        default=None,
        metadata={
            "name": "carData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    bus_data: Decimal | None = field(
        default=None,
        metadata={
            "name": "busData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    plane_data: Decimal | None = field(
        default=None,
        metadata={
            "name": "planeData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    leg_grouping: str | None = field(
        default=None,
        metadata={
            "name": "legGrouping",
            "type": "Attribute",
        },
    )
    unit: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CarrierRestrictionTypeType(Enum):
    PREFERRED = "PREFERRED"
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"


@dataclass(frozen=True)
class CarrierType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass(frozen=True)
class CheckType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class CombinedTicketableFareSetType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    combined_ticketable_fare_locators: Optional[
        "CombinedTicketableFareSetType.CombinedTicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "combinedTicketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    combined_ticketable_fare_set_id: str | None = field(
        default=None,
        metadata={
            "name": "combinedTicketableFareSetId",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class CombinedTicketableFareLocators:
        combined_ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "combinedTicketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


class CommissionTypeType(Enum):
    SUPPLIER = "SUPPLIER"
    DISTRIBUTOR = "DISTRIBUTOR"


@dataclass(frozen=True)
class CompatiblePricesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    compatible_price_idref: list[str] = field(
        default_factory=list,
        metadata={
            "name": "compatiblePriceIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ConsumptionRuleType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    min_quantity: int | None = field(
        default=None,
        metadata={
            "name": "minQuantity",
            "type": "Attribute",
            "required": True,
        },
    )
    max_quantity: int | None = field(
        default=None,
        metadata={
            "name": "maxQuantity",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ContextType:
    """Context defines the parameters of the API request."""

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    distributor_code: str | None = field(
        default=None,
        metadata={
            "name": "distributorCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
            "min_length": 1,
            "max_length": 10,
            "pattern": r"[a-zA-Z0-9]+",
        },
    )
    point_of_sale_code: str | None = field(
        default=None,
        metadata={
            "name": "pointOfSaleCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
            "min_length": 2,
            "max_length": 2,
            "pattern": r"[A-Z][A-Z]",
        },
    )
    channel: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 10,
            "pattern": r"[a-zA-Z0-9]+",
        },
    )
    channel_code: str | None = field(
        default=None,
        metadata={
            "name": "channelCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 10,
            "pattern": r"[a-zA-Z0-9]+",
        },
    )
    agency_code: str | None = field(
        default=None,
        metadata={
            "name": "agencyCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 10,
            "pattern": r"[a-zA-Z0-9]+",
        },
    )
    company_code: str | None = field(
        default=None,
        metadata={
            "name": "companyCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 10,
            "pattern": r"[a-zA-Z0-9]+",
        },
    )


class CostTypeType(Enum):
    TICKET = "TICKET"
    TRAVEL_PASS = "TRAVEL_PASS"
    RESERVATION = "RESERVATION"
    TICKETED_RES = "TICKETED_RES"
    ACCOMMODATION = "ACCOMMODATION"
    TAX = "TAX"
    TAX_NATIONAL = "TAX_NATIONAL"
    TAX_STATEPROVINCE = "TAX_STATEPROVINCE"
    FEE = "FEE"
    VAT = "VAT"
    ONBOARD_SERVICES = "ONBOARD_SERVICES"
    CORP_DISCOUNT = "CORP_DISCOUNT"
    VAT_TICKET = "VAT_TICKET"
    VAT_RESERVATION = "VAT_RESERVATION"
    VAT_FEE = "VAT_FEE"
    VAT_ONBOARD_SERVICES = "VAT_ONBOARD_SERVICES"
    SUPPLEMENT = "SUPPLEMENT"


@dataclass(frozen=True)
class CouponTypeAbstract:
    class Meta:
        name = "CouponType"
        target_namespace = "http://railgds.net/ws/commontypes"

    coupon_number: str | None = field(
        default=None,
        metadata={
            "name": "couponNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    original_coupon_number: str | None = field(
        default=None,
        metadata={
            "name": "originalCouponNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


class CreditCardSurchargeFeeTypeFormOfPayment(Enum):
    AX = "AX"
    VI = "VI"
    CA = "CA"
    DI = "DI"
    UA = "UA"
    DC = "DC"
    JC = "JC"


class CreditCardSurchargeFeeTypePaymentType(Enum):
    CC = "CC"
    CK = "CK"
    OA = "OA"
    DB = "DB"
    VO = "VO"
    EK = "EK"
    EP = "EP"


@dataclass(frozen=True)
class CustomInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    custom_information_pair: list["CustomInformationType.CustomInformationPair"] = (
        field(
            default_factory=list,
            metadata={
                "name": "customInformationPair",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )
    )

    @dataclass(frozen=True)
    class CustomInformationPair:
        key: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        value: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        created_date_time: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "createdDateTime",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        updated_date_time: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "updatedDateTime",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


class CustomerContactTypeContactMedium(Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    FAX = "FAX"
    GDPR = "GDPR"


class CustomerContactTypeContactType(Enum):
    BUSINESS = "BUSINESS"
    HOME = "HOME"
    MOBILE = "MOBILE"
    AGENCY = "AGENCY"
    HOTEL = "HOTEL"
    COMMERCIAL = "COMMERCIAL"
    DESTINATION = "DESTINATION"
    UNKNOWN = "UNKNOWN"
    ASSISTANT = "ASSISTANT"


@dataclass(frozen=True)
class DateTimeWindowType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    date: XmlDate | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    time: Optional["DateTimeWindowType.Time"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class Time:
        value: XmlTime | None = field(
            default=None,
            metadata={
                "required": True,
            },
        )
        hours_before_offset: int | None = field(
            default=None,
            metadata={
                "name": "hoursBeforeOffset",
                "type": "Attribute",
            },
        )
        hours_after_offset: int | None = field(
            default=None,
            metadata={
                "name": "hoursAfterOffset",
                "type": "Attribute",
            },
        )


class DistanceTypeUnitOfMeasure(Enum):
    MILES = "MILES"
    KILOMETERS = "KILOMETERS"


class EquipmentTypeRestrictionsTypeType(Enum):
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"


class EquipmentTypeTypeCode(Enum):
    HSP = "HSP"
    ICY = "ICY"
    BLR = "BLR"
    APT = "APT"
    CMT = "CMT"
    BUS = "BUS"
    BUR = "BUR"
    XBU = "XBU"
    MCT = "MCT"
    NIT = "NIT"
    NAT = "NAT"
    FRY = "FRY"
    PED = "PED"
    STR = "STR"
    TAX = "TAX"
    TRM = "TRM"
    TRL = "TRL"
    PFC = "PFC"
    HOV = "HOV"
    TRS = "TRS"
    UNK = "UNK"


@dataclass(frozen=True)
class ExactSeatLocationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    coach: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ExchangeableTicketableFareLocatorsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    exchangeable_ticketable_fare_locator: list[str] = field(
        default_factory=list,
        metadata={
            "name": "exchangeableTicketableFareLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ExternalIdentificationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    reference_number: str | None = field(
        default=None,
        metadata={
            "name": "referenceNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 25,
        },
    )
    purchase_order_number: str | None = field(
        default=None,
        metadata={
            "name": "purchaseOrderNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 25,
        },
    )
    customer_number: str | None = field(
        default=None,
        metadata={
            "name": "customerNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 1,
            "max_length": 25,
        },
    )


@dataclass(frozen=True)
class ExternalPaymentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    provider: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    reference: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    reference_two: str | None = field(
        default=None,
        metadata={
            "name": "referenceTwo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


class FareApplicabilityBasisType(Enum):
    SCHEDULE = "SCHEDULE"


class FareApplicabilityRestrictionType(Enum):
    OPEN = "OPEN"
    SEMI_OPEN = "SEMI-OPEN"
    RESTRICTED = "RESTRICTED"


class FareQualifierTypeType(Enum):
    CORPORATE = "CORPORATE"
    DISCOUNT_CARD = "DISCOUNT_CARD"
    PROMOTION = "PROMOTION"


@dataclass(frozen=True)
class FareSignatureType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    fare_signature: list[str] = field(
        default_factory=list,
        metadata={
            "name": "fareSignature",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


class FormOfPaymentTypeType(Enum):
    CC = "CC"
    CK = "CK"
    OA = "OA"
    DB = "DB"
    VO = "VO"
    EK = "EK"
    EP = "EP"


@dataclass(frozen=True)
class FulfillmentPhoneNumberType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    calling_country_code: int | None = field(
        default=None,
        metadata={
            "name": "callingCountryCode",
            "type": "Attribute",
        },
    )


class GenderType(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class InformationTypeType(Enum):
    TRAVEL_ADVICE = "TRAVEL_ADVICE"


class IssueType(Enum):
    NEW = "NEW"


@dataclass(frozen=True)
class LegReferencesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    leg_idref: list[str] = field(
        default_factory=list,
        metadata={
            "name": "legIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    leg_solution_idref: list[str] = field(
        default_factory=list,
        metadata={
            "name": "legSolutionIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class LoyaltyCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    marketing_carrier: list[str] = field(
        default_factory=list,
        metadata={
            "name": "marketingCarrier",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )
    program: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class MarketingInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    service_code: object | None = field(
        default=None,
        metadata={
            "name": "serviceCode",
            "type": "Attribute",
            "required": True,
        },
    )
    service_brand: object | None = field(
        default=None,
        metadata={
            "name": "serviceBrand",
            "type": "Attribute",
        },
    )
    service_line: object | None = field(
        default=None,
        metadata={
            "name": "serviceLine",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class MoneyType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: Decimal | None = field(
        default=None,
        metadata={
            "required": True,
            "fraction_digits": 2,
        },
    )
    currency: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    currency_symbol: str | None = field(
        default=None,
        metadata={
            "name": "currencySymbol",
            "type": "Attribute",
        },
    )


class NonValidatedServiceFeeType(Enum):
    CC_SURCHARGE_FEE_ASSESSMENT = "CC_Surcharge_Fee_Assessment"
    MISC_FEE_ASSESSMENT = "Misc_Fee_Assessment"
    MISC_AGENCY_SERVICE_FEE_ASSESSMENT = "Misc_Agency_Service_Fee_Assessment"
    MISC_DISTRIBUTOR_SERVICE_FEE_ASSESSMENT = "Misc_Distributor_Service_Fee_Assessment"
    MISC_COMPANY_SERVICE_FEE_ASSESSMENT = "Misc_Company_Service_Fee_Assessment"
    ORDER_REFUND_FEE_ASSESSMENT = "Order_Refund_Fee_Assessment"


class OptionalPriceTypeCategory(Enum):
    SEAT_RESERVATION = "SEAT_RESERVATION"
    ACCOMMODATION = "ACCOMMODATION"
    MEAL = "MEAL"
    INTERNET = "INTERNET"
    LOCAL_TRANSIT = "LOCAL_TRANSIT"
    OFFICE_SPACE = "OFFICE_SPACE"
    SUPPLEMENT = "SUPPLEMENT"
    LOCAL_BUS = "LOCAL_BUS"


@dataclass(frozen=True)
class OrderNoteType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    created_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "createdDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class OrderTypeStatus(Enum):
    PENDING = "PENDING"
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    TICKETED = "TICKETED"
    ABANDONED = "ABANDONED"
    RELEASED = "RELEASED"
    CANCELED = "CANCELED"
    RETURNED = "RETURNED"
    WITHDRAWN = "WITHDRAWN"
    INVALID = "INVALID"
    PRINTING = "PRINTING"
    REPLACED = "REPLACED"


class PassengerFareQualifierTypeType(Enum):
    LOYALTY = "LOYALTY"


class PassengerInformationTypeAcceptableFormOfTravelDocument(Enum):
    PERMRESIDENT = "PERMRESIDENT"
    PASSPORT = "PASSPORT"
    NATURALCERT = "NATURALCERT"
    MILORDER = "MILORDER"
    PHOTOCARD = "PHOTOCARD"
    IDENTITYCARD = "IDENTITYCARD"


class PassengerInformationTypeType(Enum):
    PASSENGER_ADDRESS = "PASSENGER_ADDRESS"
    TRAVEL_DOCUMENTS = "TRAVEL_DOCUMENTS"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    GENDER = "GENDER"
    RESIDENCE_INFORMATION = "RESIDENCE_INFORMATION"
    PASSENGER_NAME = "PASSENGER_NAME"
    PASSENGER_TITLE = "PASSENGER_TITLE"
    PASSENGER_EMAIL = "PASSENGER_EMAIL"
    PASSENGER_PHONE = "PASSENGER_PHONE"
    PLACE_OF_BIRTH = "PLACE_OF_BIRTH"


@dataclass(frozen=True)
class PassengerLoyaltyCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    program: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class PassengerRightType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    descriptions: Optional["PassengerRightType.Descriptions"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    segments: Optional["PassengerRightType.Segments"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    passenger_right_id: str | None = field(
        default=None,
        metadata={
            "name": "passengerRightID",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Descriptions:
        description: list["PassengerRightType.Descriptions.Description"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Description:
            value: str = field(
                default="",
                metadata={
                    "required": True,
                },
            )
            lang: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            rights: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class Segments:
        travel_segment_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "travelSegmentIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        leg_travel_segment_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "legTravelSegmentIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


@dataclass(frozen=True)
class PaymentProcessorInfoType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    approval_number: str | None = field(
        default=None,
        metadata={
            "name": "approvalNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    payment_processor: str | None = field(
        default=None,
        metadata={
            "name": "paymentProcessor",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    doing_business_as: str | None = field(
        default=None,
        metadata={
            "name": "doingBusinessAs",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    error: Optional["PaymentProcessorInfoType.Error"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    descriptive_billing_information_collection: Optional[
        "PaymentProcessorInfoType.DescriptiveBillingInformationCollection"
    ] = field(
        default=None,
        metadata={
            "name": "descriptiveBillingInformationCollection",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    transaction_code: str | None = field(
        default=None,
        metadata={
            "name": "transactionCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class Error:
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        code: object | None = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(frozen=True)
    class DescriptiveBillingInformationCollection:
        descriptive_billing_information: list[str] = field(
            default_factory=list,
            metadata={
                "name": "descriptiveBillingInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "max_occurs": 10,
            },
        )


class PaymentTypeType(Enum):
    PAYMENT = "PAYMENT"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    DEPOSIT = "DEPOSIT"
    REFUND = "REFUND"
    REFUND_FAILED = "REFUND_FAILED"
    CREDIT = "CREDIT"


@dataclass(frozen=True)
class PlaceOfBirthInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    country: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    province: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    city: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


class PriceTypeType(Enum):
    TICKET = "TICKET"
    RESERVATION = "RESERVATION"
    TICKETED_RES = "TICKETED_RES"
    TRAVEL_PASS = "TRAVEL_PASS"
    ACCOMMODATION = "ACCOMMODATION"
    TAX = "TAX"
    TAX_NATIONAL = "TAX_NATIONAL"
    TAX_STATEPROVINCE = "TAX_STATEPROVINCE"
    FEE = "FEE"
    CORP_DISCOUNT = "CORP_DISCOUNT"
    VAT = "VAT"
    VAT_TICKET = "VAT_TICKET"
    VAT_RESERVATION = "VAT_RESERVATION"
    VAT_FEE = "VAT_FEE"
    VAT_ONBOARD_SERVICES = "VAT_ONBOARD_SERVICES"
    ONBOARD_SERVICES = "ONBOARD_SERVICES"
    SUPPLEMENT = "SUPPLEMENT"


class RefundTargetType(Enum):
    FORM_OF_PAYMENT = "FORM_OF_PAYMENT"
    VOUCHER = "VOUCHER"
    SPLIT_FORM_OF_PAYMENT_VOUCHER = "SPLIT_FORM_OF_PAYMENT_VOUCHER"


class RequestSummatedFareFilterTypeFareCategory(Enum):
    ALL = "All"
    ADVANCE = "Advance"
    WALK_ON = "WalkOn"


class RequestSummatedFareFilterTypeFareClass(Enum):
    ALL = "All"
    FIRST = "First"
    STANDARD = "Standard"


@dataclass(frozen=True)
class ReservableTicketableFareType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    reservable_fare_code_locators: Optional[
        "ReservableTicketableFareType.ReservableFareCodeLocators"
    ] = field(
        default=None,
        metadata={
            "name": "reservableFareCodeLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    ticketable_fare_id: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareID",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ReservableFareCodeLocators:
        reservable_fare_code_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "reservableFareCodeLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


class ReservableType(Enum):
    MANDATORY = "MANDATORY"
    NOT_POSSIBLE = "NOT_POSSIBLE"
    OPTIONAL = "OPTIONAL"
    INCLUDED = "INCLUDED"


@dataclass(frozen=True)
class ResidenceInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    country_code: str | None = field(
        default=None,
        metadata={
            "name": "countryCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
            "length": 2,
            "pattern": r"[a-zA-Z]+",
        },
    )
    state_prov: str | None = field(
        default=None,
        metadata={
            "name": "stateProv",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class RevisionReasonType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    code: object | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        },
    )


class RevisionTypeStatus(Enum):
    CANCELLED = "CANCELLED"
    DELAYED = "DELAYED"
    BOARDING_NOT_POSSIBLE = "BOARDING_NOT_POSSIBLE"
    ALIGHTING_NOT_POSSIBLE = "ALIGHTING_NOT_POSSIBLE"
    RESCHEDULED = "RESCHEDULED"


class RoutingRestrictionTypeType(Enum):
    PREFERRED = "PREFERRED"
    RESTRICTED = "RESTRICTED"
    PERMITTED = "PERMITTED"


class RuleTypeApplicableOrderStatus(Enum):
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    TICKETED = "TICKETED"
    RETURNED = "RETURNED"


class RuleTypeApplicableTicketingOption(Enum):
    TVM = "TVM"
    TBX = "TBX"
    TBM = "TBM"
    TBO = "TBO"
    TML = "TML"
    TOF = "TOF"
    TBC = "TBC"
    TVP = "TVP"
    TOP = "TOP"
    PAH = "PAH"
    PRN = "PRN"
    ETK = "ETK"
    SMS = "SMS"
    XVD = "XVD"
    MVD = "MVD"
    SCT = "SCT"
    MTD = "MTD"


class RuleTypePriceType(Enum):
    TICKET = "TICKET"
    RESERVATION = "RESERVATION"
    TRAVEL_PASS = "TRAVEL_PASS"
    FEE = "FEE"
    ACCOMMODATION = "ACCOMMODATION"
    LOCAL_SERVICE = "LOCAL_SERVICE"
    ONBOARD_SERVICES = "ONBOARD_SERVICES"


class RuleTypeRefundToVoucher(Enum):
    NOT_POSSIBLE = "NOT_POSSIBLE"
    OPTIONAL = "OPTIONAL"
    MANDATORY = "MANDATORY"
    SPLIT = "SPLIT"


class RuleTypeType(Enum):
    EXCHANGE_ALLOWED = "EXCHANGE_ALLOWED"
    EXCHANGE_PROHIBITED = "EXCHANGE_PROHIBITED"
    REFUND_ALLOWED = "REFUND_ALLOWED"
    REFUND_PROHIBITED = "REFUND_PROHIBITED"
    TEXT = "TEXT"


class SeatAssignmentDirectionType(Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    UNKNOWN = "UNKNOWN"
    UNASSIGNED = "UNASSIGNED"
    AIRLINE = "AIRLINE"


class SeatAttributeType(Enum):
    WINDOW = "WINDOW"
    AISLE = "AISLE"
    COMPARTMENT = "COMPARTMENT"
    MIDDLE = "MIDDLE"
    QUIET = "QUIET"
    TABLE = "TABLE"
    POWER = "POWER"
    PHONE = "PHONE"
    LUGGAGE = "LUGGAGE"
    LAVATORY = "LAVATORY"
    SINGLE = "SINGLE"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    ROOM = "ROOM"
    SIDEBYSIDE = "SIDEBYSIDE"
    TWO_FACING = "TWO_FACING"
    FOUR_FACING = "FOUR_FACING"
    SIX_FACING = "SIX_FACING"
    PANORAMA = "PANORAMA"
    FAMILY = "FAMILY"
    FOLDING_SEAT = "FOLDING_SEAT"


@dataclass(frozen=True)
class SeatMapInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    external_proposal: str | None = field(
        default=None,
        metadata={
            "name": "externalProposal",
            "type": "Attribute",
        },
    )
    external_travel_segment: str | None = field(
        default=None,
        metadata={
            "name": "externalTravelSegment",
            "type": "Attribute",
        },
    )
    carrier: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    vehicle_id: str | None = field(
        default=None,
        metadata={
            "name": "vehicleId",
            "type": "Attribute",
        },
    )
    board_location: str | None = field(
        default=None,
        metadata={
            "name": "boardLocation",
            "type": "Attribute",
        },
    )
    alight_location: str | None = field(
        default=None,
        metadata={
            "name": "alightLocation",
            "type": "Attribute",
        },
    )
    departure_date_time: XmlDate | None = field(
        default=None,
        metadata={
            "name": "departureDateTime",
            "type": "Attribute",
        },
    )
    ticket_class: str | None = field(
        default=None,
        metadata={
            "name": "ticketClass",
            "type": "Attribute",
        },
    )
    external_supplier: str | None = field(
        default=None,
        metadata={
            "name": "externalSupplier",
            "type": "Attribute",
        },
    )
    external_search_token: str | None = field(
        default=None,
        metadata={
            "name": "externalSearchToken",
            "type": "Attribute",
        },
    )
    seat_reservation_group: str | None = field(
        default=None,
        metadata={
            "name": "seatReservationGroup",
            "type": "Attribute",
        },
    )


class SeatPreferenceType(Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    AIRLINE = "AIRLINE"
    WINDOW = "WINDOW"
    AISLE = "AISLE"
    COMPARTMENT = "COMPARTMENT"
    MIDDLE = "MIDDLE"
    QUIET = "QUIET"
    TABLE = "TABLE"
    POWER = "POWER"
    PHONE = "PHONE"
    LUGGAGE = "LUGGAGE"
    LAVATORY = "LAVATORY"
    SINGLE = "SINGLE"
    NEARBY = "NEARBY"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    ROOM = "ROOM"
    SIDEBYSIDE = "SIDEBYSIDE"
    TWO_FACING = "TWO_FACING"
    FOUR_FACING = "FOUR_FACING"
    SIX_FACING = "SIX_FACING"
    PANORAMA = "PANORAMA"
    FAMILY = "FAMILY"
    SEAT_MAP = "SEAT_MAP"


@dataclass(frozen=True)
class SegmentServiceListType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    station: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ServiceAlertType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    summary: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


class ServiceClassType(Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"
    THIRD = "THIRD"
    PREMIER = "PREMIER"
    SLEEPER = "SLEEPER"
    AUTO = "AUTO"
    BEDROOM = "BEDROOM"
    MISC = "MISC"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    SLEEPERPLUS = "SLEEPERPLUS"


@dataclass(frozen=True)
class ShipmentTrackingType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    shipment_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "shipmentDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    delivery_method: str | None = field(
        default=None,
        metadata={
            "name": "deliveryMethod",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    tracking_number: str | None = field(
        default=None,
        metadata={
            "name": "trackingNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    shipper_url: str | None = field(
        default=None,
        metadata={
            "name": "shipperUrl",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class StatusMessageType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    internal: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class StatusMessages:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"


@dataclass(frozen=True)
class SupplierEquipmentTypeType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass(frozen=True)
class SupplierNoteSpecType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: bool | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    max_notes: int | None = field(
        default=None,
        metadata={
            "name": "maxNotes",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class SupplierNoteType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    supplier_note: list[str] = field(
        default_factory=list,
        metadata={
            "name": "supplierNote",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class TicketingCodeConfirmationRequiredOverride:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class TicketingOptionTypeCode(Enum):
    TVM = "TVM"
    TBX = "TBX"
    TBM = "TBM"
    TBO = "TBO"
    TML = "TML"
    TOF = "TOF"
    TBC = "TBC"
    TVP = "TVP"
    TOP = "TOP"
    PAH = "PAH"
    PRN = "PRN"
    ETK = "ETK"
    EML = "EML"
    SMS = "SMS"
    XVD = "XVD"
    SCT = "SCT"
    MTD = "MTD"
    MVD = "MVD"


@dataclass(frozen=True)
class TicketingOptionsAvailableType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    tod: bool | None = field(
        default=None,
        metadata={
            "name": "TOD",
            "type": "Attribute",
            "required": True,
        },
    )
    etk: bool | None = field(
        default=None,
        metadata={
            "name": "ETK",
            "type": "Attribute",
            "required": True,
        },
    )
    pah: bool | None = field(
        default=None,
        metadata={
            "name": "PAH",
            "type": "Attribute",
            "required": True,
        },
    )
    prn: bool | None = field(
        default=None,
        metadata={
            "name": "PRN",
            "type": "Attribute",
        },
    )
    eml: bool | None = field(
        default=None,
        metadata={
            "name": "EML",
            "type": "Attribute",
        },
    )
    departure_station_tod: bool | None = field(
        default=None,
        metadata={
            "name": "DEPARTURE_STATION_TOD",
            "type": "Attribute",
            "required": True,
        },
    )
    sms: bool | None = field(
        default=None,
        metadata={
            "name": "SMS",
            "type": "Attribute",
        },
    )
    xvd: bool | None = field(
        default=None,
        metadata={
            "name": "XVD",
            "type": "Attribute",
        },
    )
    sct: bool | None = field(
        default=None,
        metadata={
            "name": "SCT",
            "type": "Attribute",
        },
    )
    mtd: bool | None = field(
        default=None,
        metadata={
            "name": "MTD",
            "type": "Attribute",
        },
    )
    mvd: bool | None = field(
        default=None,
        metadata={
            "name": "MVD",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class TravelCardZoneConsumptionRuleType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    travel_card_zone: str | None = field(
        default=None,
        metadata={
            "name": "travelCardZone",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


class TravelDocumentTypeDocumentAffiliation(Enum):
    CITIZENSHIP = "CITIZENSHIP"


class TravelDocumentTypeDocumentType(Enum):
    PHOTOCARD = "PHOTOCARD"
    PERMRESIDENT = "PERMRESIDENT"
    PASSPORT = "PASSPORT"
    NATURALCERT = "NATURALCERT"
    MILORDER = "MILORDER"
    IDENTITYCARD = "IDENTITYCARD"


class TravelPassCodeTypeType(Enum):
    RANGERS_AND_ROVERS = "RANGERS_AND_ROVERS"


@dataclass(frozen=True)
class TravelPassType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number_of_passes: str | None = field(
        default=None,
        metadata={
            "name": "numberOfPasses",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    unused_passes: str | None = field(
        default=None,
        metadata={
            "name": "unusedPasses",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    fare_code: str | None = field(
        default=None,
        metadata={
            "name": "fareCode",
            "type": "Attribute",
        },
    )


class TravelPointTypeEnumeration(Enum):
    STATION = "STATION"
    CITY = "CITY"
    REGION = "REGION"
    COUNTRY = "COUNTRY"


@dataclass(frozen=True)
class TypesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    type_value: list[str] = field(
        default_factory=list,
        metadata={
            "name": "type",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


class UnitCarbonTypeUnit(Enum):
    KG_CO2 = "kgCO2"


@dataclass(frozen=True)
class UpdateableBookingType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    passenger_identity: bool | None = field(
        default=None,
        metadata={
            "name": "passengerIdentity",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    passenger_address: bool | None = field(
        default=None,
        metadata={
            "name": "passengerAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    passenger_contact_info: bool | None = field(
        default=None,
        metadata={
            "name": "passengerContactInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    loyalty_card: bool | None = field(
        default=None,
        metadata={
            "name": "loyaltyCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    travel_document: bool | None = field(
        default=None,
        metadata={
            "name": "travelDocument",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


class ValueDocumentCouponTypeType(Enum):
    SEAT = "SEAT"
    ROOM = "ROOM"
    TICKET = "TICKET"
    TICKETED_RES = "TICKETED_RES"
    BIKE = "BIKE"


@dataclass(frozen=True)
class ValueDocumentTicketReservationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    coach: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


class ValueDocumentTypeStatus(Enum):
    READY = "READY"
    CANCELED = "CANCELED"
    PROCESSED = "PROCESSED"
    ISSUED = "ISSUED"
    RETURNED = "RETURNED"
    RETURNED_PARTIAL = "RETURNED_PARTIAL"
    CONSUMED = "CONSUMED"
    PRINTING = "PRINTING"
    FAILED = "FAILED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class VoidSummaryType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    is_voidable: bool | None = field(
        default=None,
        metadata={
            "name": "isVoidable",
            "type": "Attribute",
        },
    )
    until_when: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "untilWhen",
            "type": "Attribute",
        },
    )
    is_voidable_exception: bool | None = field(
        default=None,
        metadata={
            "name": "isVoidableException",
            "type": "Attribute",
        },
    )
    until_when_exception: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "untilWhenException",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class VoidableTicketableFareLocatorsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    voidable_ticketable_fare_locator: list[str] = field(
        default_factory=list,
        metadata={
            "name": "voidableTicketableFareLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


class WarningTypeCategory(Enum):
    FIRST_CLASS_SEATING_NOT_AVAILABLE = "FIRST_CLASS_SEATING_NOT_AVAILABLE"


class YesNoType(Enum):
    YES = "YES"
    NO = "NO"


class BackOfficeFulfillmentType(Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"


class ComponentType(Enum):
    TICKET = "TICKET"
    RESERVATION = "RESERVATION"
    ACCOMMODATION = "ACCOMMODATION"
    FEE = "FEE"
    TRAVEL_PASS = "TRAVEL_PASS"


@dataclass(frozen=True)
class ExchangeableTicketableFaresType:
    class Meta:
        name = "exchangeableTicketableFaresType"
        target_namespace = "http://railgds.net/ws/commontypes"

    exchangeable_ticketable_fare: list[str] = field(
        default_factory=list,
        metadata={
            "name": "exchangeableTicketableFare",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


class IsNotBookableReason(Enum):
    DELAYED = "DELAYED"


class PaymentRequirementsPaymentInformation(Enum):
    ANY = "ANY"
    ORDER_TOTAL = "ORDER_TOTAL"
    BOOKING_TOTAL = "BOOKING_TOTAL"


class PenaltyItemType(Enum):
    TICKET = "TICKET"
    TICKETED_RES = "TICKETED_RES"
    RESERVATION = "RESERVATION"
    FEE = "FEE"
    TRAVEL_PASS = "TRAVEL_PASS"


@dataclass(frozen=True)
class PlusBusZoneConsumptionRuleType:
    class Meta:
        name = "plusBusZoneConsumptionRuleType"
        target_namespace = "http://railgds.net/ws/commontypes"

    plus_bus_zone: str | None = field(
        default=None,
        metadata={
            "name": "plusBusZone",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


class PriceType2(Enum):
    RESERVATION = "RESERVATION"
    ACCOMMODATION = "ACCOMMODATION"
    AMENITY = "AMENITY"
    LOCAL_SERVICE = "LOCAL_SERVICE"
    ONBOARD_SERVICES = "ONBOARD_SERVICES"
    SUPPLEMENT = "SUPPLEMENT"


@dataclass(frozen=True)
class SupplementAvailabilityType:
    class Meta:
        name = "supplementAvailabilityType"
        target_namespace = "http://railgds.net/ws/commontypes"

    value: int | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Attribute",
        },
    )


class TicketingDetailTypeCode(Enum):
    TVM = "TVM"
    TBX = "TBX"
    TBM = "TBM"
    TBO = "TBO"
    TML = "TML"
    TOF = "TOF"
    TBC = "TBC"
    TVP = "TVP"
    TOP = "TOP"
    PAH = "PAH"
    PRN = "PRN"
    ETK = "ETK"
    EML = "EML"
    SMS = "SMS"
    XVD = "XVD"
    MVD = "MVD"
    SCT = "SCT"


@dataclass(frozen=True)
class AuthenticatePayerV2CreditCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    type_value: AuthenticatePayerV2CreditCardTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AuthenticatePayerV2DebitCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    type_value: AuthenticatePayerV2DebitCardTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class BookingNotesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    note: list[BookingNoteType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class CostAdjustmentType(MoneyType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    type_value: CostAdjustmentTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class JourneyAndFareSignaturesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    journey_signature: str | None = field(
        default=None,
        metadata={
            "name": "journeySignature",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    fare_signatures: FareSignatureType | None = field(
        default=None,
        metadata={
            "name": "fareSignatures",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ReasonType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    type_value: ReasonTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "dateTime",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class RefundDetailsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    refund_amount: RefundAmountType | None = field(
        default=None,
        metadata={
            "name": "refundAmount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    delay_repay_refund_reference: str | None = field(
        default=None,
        metadata={
            "name": "delayRepayRefundReference",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
            "min_length": 1,
        },
    )


@dataclass(frozen=True)
class RefundInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    process_refund_with_cancel: bool = field(
        default=False,
        metadata={
            "name": "processRefundWithCancel",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    receipt_number: str | None = field(
        default=None,
        metadata={
            "name": "receiptNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_amount: MoneyType | None = field(
        default=None,
        metadata={
            "name": "refundAmount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_reason: str | None = field(
        default=None,
        metadata={
            "name": "refundReason",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    external_payment: ExternalPaymentType | None = field(
        default=None,
        metadata={
            "name": "externalPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class RefundStatusType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    refund_approved: bool | None = field(
        default=None,
        metadata={
            "name": "refundApproved",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    refund_transaction_id: str | None = field(
        default=None,
        metadata={
            "name": "refundTransactionId",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    delay_repay_refund_reference: str | None = field(
        default=None,
        metadata={
            "name": "delayRepayRefundReference",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_amount: RefundAmountType | None = field(
        default=None,
        metadata={
            "name": "refundAmount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "refundDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    reason_for_rejection: ReasonForRejectionType | None = field(
        default=None,
        metadata={
            "name": "reasonForRejection",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class TokenPaymentType:
    """Acceptable Values for 'CC' type: AX, CA, VI, DI, UA, MC Acceptable Values for
    'DB' type: DS, DV, DM."""

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: TokenPaymentTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class VoidOverrideType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    value: bool | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    type_value: VoidOverrideTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class AddedOrderNoteType(OrderNoteType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    order_id: str | None = field(
        default=None,
        metadata={
            "name": "orderID",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AddressType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    company: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    address1: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
            "min_length": 1,
        },
    )
    address2: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    city: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
            "min_length": 1,
        },
    )
    state_prov: str | None = field(
        default=None,
        metadata={
            "name": "stateProv",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    zip_code: str | None = field(
        default=None,
        metadata={
            "name": "zipCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    country: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
            "length": 2,
            "pattern": r"[a-zA-Z]+",
        },
    )
    country3: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "length": 3,
            "pattern": r"[a-zA-Z]+",
        },
    )
    email: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    address_type: AddressTypeAddressType | None = field(
        default=None,
        metadata={
            "name": "addressType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AgeBreakConsumptionRuleType(ConsumptionRuleType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    min_age: int | None = field(
        default=None,
        metadata={
            "name": "minAge",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    max_age: int | None = field(
        default=None,
        metadata={
            "name": "maxAge",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class AmenityType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: AmenityTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AvailableSeatPreferenceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: SeatPreferenceType | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    marketing_carrier: str | None = field(
        default=None,
        metadata={
            "name": "marketingCarrier",
            "type": "Attribute",
            "required": True,
        },
    )
    service_class: ServiceClassType | None = field(
        default=None,
        metadata={
            "name": "serviceClass",
            "type": "Attribute",
            "required": True,
        },
    )
    supplier_equipment_type: str | None = field(
        default=None,
        metadata={
            "name": "supplierEquipmentType",
            "type": "Attribute",
        },
    )
    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class BaseCancellationOptionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    refund_target: Optional["BaseCancellationOptionType.RefundTarget"] = field(
        default=None,
        metadata={
            "name": "refundTarget",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class RefundTarget:
        voucher_amount: MoneyType | None = field(
            default=None,
            metadata={
                "name": "voucherAmount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        voucher_value: MoneyType | None = field(
            default=None,
            metadata={
                "name": "voucherValue",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        type_value: RefundTargetType | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass(frozen=True)
class BaseExchangeOptionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    total: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    refund_target: Optional["BaseExchangeOptionType.RefundTarget"] = field(
        default=None,
        metadata={
            "name": "refundTarget",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    exchange_option_type: BaseExchangeOptionTypeExchangeOptionType | None = field(
        default=None,
        metadata={
            "name": "exchangeOptionType",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class RefundTarget:
        voucher_amount: MoneyType | None = field(
            default=None,
            metadata={
                "name": "voucherAmount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        voucher_value: MoneyType | None = field(
            default=None,
            metadata={
                "name": "voucherValue",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        type_value: RefundTargetType | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass(frozen=True)
class BaseRequestExchangeSetType(BaseExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    ticketable_fare_locators: Optional[
        "BaseRequestExchangeSetType.TicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "ticketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class TicketableFareLocators:
        ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class BaseRequestType:
    """:ivar context:

    :ivar overrides: Optional request overrides for testing. :ivar
    conversation_token: :ivar version: :ivar date_time:
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    context: ContextType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    overrides: Optional["BaseRequestType.Overrides"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    conversation_token: str | None = field(
        default=None,
        metadata={
            "name": "conversationToken",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    date_time: str | None = field(
        default=None,
        metadata={
            "name": "dateTime",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class Overrides:
        override: list["BaseRequestType.Overrides.Override"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Override:
            name: object | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            type_value: object | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Attribute",
                    "required": True,
                },
            )
            value: object | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )


@dataclass(frozen=True)
class BaseSeatPreferenceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    marketing_carrier: str | None = field(
        default=None,
        metadata={
            "name": "marketingCarrier",
            "type": "Attribute",
            "required": True,
        },
    )
    service_class: ServiceClassType | None = field(
        default=None,
        metadata={
            "name": "serviceClass",
            "type": "Attribute",
            "required": True,
        },
    )
    supplier_equipment_type: str | None = field(
        default=None,
        metadata={
            "name": "supplierEquipmentType",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class BaseTransactionFeeType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    fee: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    transaction_fee_id: str | None = field(
        default=None,
        metadata={
            "name": "transactionFeeID",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class CampaignFareType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    success: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    value: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    campaign_code: str | None = field(
        default=None,
        metadata={
            "name": "campaignCode",
            "type": "Attribute",
        },
    )
    validation_code: str | None = field(
        default=None,
        metadata={
            "name": "validationCode",
            "type": "Attribute",
        },
    )
    recipient_name: str | None = field(
        default=None,
        metadata={
            "name": "recipientName",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class CarrierRestrictionType1:
    class Meta:
        name = "CarrierRestrictionType"
        target_namespace = "http://railgds.net/ws/commontypes"

    carrier: CarrierType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    type_value: CarrierRestrictionTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class CommissionType(MoneyType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    type_value: CommissionTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    is_estimated: bool | None = field(
        default=None,
        metadata={
            "name": "isEstimated",
            "type": "Attribute",
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class ConfirmationInformationRequiredOverrideType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    ticketing_option_code: list[TicketingCodeConfirmationRequiredOverride] = field(
        default_factory=list,
        metadata={
            "name": "ticketingOptionCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class ConfirmationOptionsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    credit_card_option: Optional["ConfirmationOptionsType.CreditCardOption"] = field(
        default=None,
        metadata={
            "name": "creditCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    debit_card_option: Optional["ConfirmationOptionsType.DebitCardOption"] = field(
        default=None,
        metadata={
            "name": "debitCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    loyalty_card_option: Optional["ConfirmationOptionsType.LoyaltyCardOption"] = field(
        default=None,
        metadata={
            "name": "loyaltyCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    personal_information_card_option: Optional[
        "ConfirmationOptionsType.PersonalInformationCardOption"
    ] = field(
        default=None,
        metadata={
            "name": "personalInformationCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class CreditCardOption:
        types: TypesType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class DebitCardOption:
        types: TypesType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        sort_code_required: bool | None = field(
            default=None,
            metadata={
                "name": "sortCodeRequired",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class LoyaltyCardOption:
        programs: Optional["ConfirmationOptionsType.LoyaltyCardOption.Programs"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
        )
        expiration_date_required: bool | None = field(
            default=None,
            metadata={
                "name": "expirationDateRequired",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )

        @dataclass(frozen=True)
        class Programs:
            program: list[str] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

    @dataclass(frozen=True)
    class PersonalInformationCardOption:
        country_codes: Optional[
            "ConfirmationOptionsType.PersonalInformationCardOption.CountryCodes"
        ] = field(
            default=None,
            metadata={
                "name": "countryCodes",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )

        @dataclass(frozen=True)
        class CountryCodes:
            country_code: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "countryCode",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )


@dataclass(frozen=True)
class CostType(MoneyType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    type_value: CostTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    is_estimated: bool | None = field(
        default=None,
        metadata={
            "name": "isEstimated",
            "type": "Attribute",
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class CreditCardSurchargeFeeType(MoneyType):
    """Acceptable Values for 'CC' type: AX, CA, VI, DI, UA, MC Acceptable Values for
    'DB' type: DS, DV, DM."""

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    payment_type: CreditCardSurchargeFeeTypePaymentType | None = field(
        default=None,
        metadata={
            "name": "paymentType",
            "type": "Attribute",
        },
    )
    form_of_payment: CreditCardSurchargeFeeTypeFormOfPayment | None = field(
        default=None,
        metadata={
            "name": "formOfPayment",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class CustomerContactType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    contact_type: CustomerContactTypeContactType | None = field(
        default=None,
        metadata={
            "name": "contactType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    contact_medium: CustomerContactTypeContactMedium | None = field(
        default=None,
        metadata={
            "name": "contactMedium",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    contact_info: str | None = field(
        default=None,
        metadata={
            "name": "contactInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class DistanceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: float | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    unit_of_measure: DistanceTypeUnitOfMeasure | None = field(
        default=None,
        metadata={
            "name": "unitOfMeasure",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class EcheckType(BaseEcheckType):
    class Meta:
        name = "ECheckType"
        target_namespace = "http://railgds.net/ws/commontypes"

    payment_processor_info: PaymentProcessorInfoType | None = field(
        default=None,
        metadata={
            "name": "paymentProcessorInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class EquipmentTypeType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    code: EquipmentTypeTypeCode | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class FareQualifierType:
    """:ivar program:

    :ivar identifier: :ivar authorization_numbers: :ivar passenger_references:
    :ivar quantity: This optional element will be populated only when
    FareQualifierType is used at the PointToPointPriceType level. :ivar
    type_value: :ivar fare_qualifier_id: :ivar authorization_number_required:
    :ivar identifier_required: :ivar cards_used:
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    program: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    identifier: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    authorization_numbers: AuthorizationNumbersType | None = field(
        default=None,
        metadata={
            "name": "authorizationNumbers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    passenger_references: Optional["FareQualifierType.PassengerReferences"] = field(
        default=None,
        metadata={
            "name": "passengerReferences",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    quantity: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: FareQualifierTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    fare_qualifier_id: str | None = field(
        default=None,
        metadata={
            "name": "fareQualifierID",
            "type": "Attribute",
        },
    )
    authorization_number_required: bool | None = field(
        default=None,
        metadata={
            "name": "authorizationNumberRequired",
            "type": "Attribute",
        },
    )
    identifier_required: bool | None = field(
        default=None,
        metadata={
            "name": "identifierRequired",
            "type": "Attribute",
        },
    )
    cards_used: int | None = field(
        default=None,
        metadata={
            "name": "cardsUsed",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class PassengerReferences:
        passenger_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "passengerIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class FeeType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    amount: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    fee_type: NonValidatedServiceFeeType | None = field(
        default=None,
        metadata={
            "name": "feeType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class FormOfPaymentType:
    """Acceptable Values for 'CC' type: AX, CA, VI, DI, UA, MC Acceptable Values for
    'DB' type: DS, DV, DM."""

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: FormOfPaymentTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    authenticate_payer_required: bool | None = field(
        default=None,
        metadata={
            "name": "authenticatePayerRequired",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class InformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: InformationTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class OnAccountType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    validation_code: str | None = field(
        default=None,
        metadata={
            "name": "validationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    account_name: str | None = field(
        default=None,
        metadata={
            "name": "accountName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    external_payment: ExternalPaymentType | None = field(
        default=None,
        metadata={
            "name": "externalPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class OptionalPriceFareCodeType:
    """We have to add OptionalPriceFareCodeType instead of just reusing FareCodeType.

    If we made the changes needed for optional prices to FareCodeType, it would
    no longer be backwards compatible. Once we go to the next major version of
    the API, we can coalesce FareCodeType and OptionalPriceFareCodeType then.
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    service_class: ServiceClassType | None = field(
        default=None,
        metadata={
            "name": "serviceClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cabin_class: str | None = field(
        default=None,
        metadata={
            "name": "cabinClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_class: str | None = field(
        default=None,
        metadata={
            "name": "fareClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    fare_display_name: str | None = field(
        default=None,
        metadata={
            "name": "fareDisplayName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seats_available: int | None = field(
        default=None,
        metadata={
            "name": "seatsAvailable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    code: object | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class PassFareCodeType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    service_class: ServiceClassType | None = field(
        default=None,
        metadata={
            "name": "serviceClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    cabin_class: str | None = field(
        default=None,
        metadata={
            "name": "cabinClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    rewards_eligible: YesNoType | None = field(
        default=None,
        metadata={
            "name": "rewardsEligible",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_class: str | None = field(
        default=None,
        metadata={
            "name": "fareClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_display_name: str | None = field(
        default=None,
        metadata={
            "name": "fareDisplayName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    services: Optional["PassFareCodeType.Services"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_applicabilities: Optional["PassFareCodeType.FareApplicabilities"] = field(
        default=None,
        metadata={
            "name": "fareApplicabilities",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    optional_prices_requested: Optional["PassFareCodeType.OptionalPricesRequested"] = (
        field(
            default=None,
            metadata={
                "name": "optionalPricesRequested",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    code: object | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Services:
        service: list["PassFareCodeType.Services.Service"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Service:
            value: str = field(
                default="",
                metadata={
                    "required": True,
                },
            )
            category: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class FareApplicabilities:
        fare_applicability: list[
            "PassFareCodeType.FareApplicabilities.FareApplicability"
        ] = field(
            default_factory=list,
            metadata={
                "name": "fareApplicability",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class FareApplicability:
            fare_applicability_text: str | None = field(
                default=None,
                metadata={
                    "name": "fareApplicabilityText",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            outbound: FareApplicabilityRestrictionType | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            return_value: FareApplicabilityRestrictionType | None = field(
                default=None,
                metadata={
                    "name": "return",
                    "type": "Attribute",
                },
            )
            type_value: FareApplicabilityBasisType | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class OptionalPricesRequested:
        optional_price_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "optionalPriceIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PassengerFareQualifierType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    program: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    identifier: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: PassengerFareQualifierTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class PassengerInformationType:
    """:ivar acceptable_form_of_travel_document: PERMRESIDENT: Legal
        Permanent Resident Card PASSPORT: Passport NATURALCERT:
        Naturalization Certificate MILORDER: Military Order PHOTOCARD:
        Photocard required in the UK for acquiring season tickets
        IDENTITYCARD : National Identity Card Consult the SilverRail
        Documentation Portal for further information.
    :ivar type_value:
    :ivar all_passengers:
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    acceptable_form_of_travel_document: list[
        PassengerInformationTypeAcceptableFormOfTravelDocument
    ] = field(
        default_factory=list,
        metadata={
            "name": "acceptableFormOfTravelDocument",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: PassengerInformationTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    all_passengers: bool | None = field(
        default=None,
        metadata={
            "name": "allPassengers",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class PassengerRightsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    passenger_right: list[PassengerRightType] = field(
        default_factory=list,
        metadata={
            "name": "passengerRight",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class PassengerSpecType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    age: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    date_of_birth: XmlDate | None = field(
        default=None,
        metadata={
            "name": "dateOfBirth",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    residence_information: ResidenceInformationType | None = field(
        default=None,
        metadata={
            "name": "residenceInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    passenger_spec_id: str | None = field(
        default=None,
        metadata={
            "name": "passengerSpecID",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class PriceType1(MoneyType):
    class Meta:
        name = "PriceType"
        target_namespace = "http://railgds.net/ws/commontypes"

    type_value: PriceTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    is_estimated: bool | None = field(
        default=None,
        metadata={
            "name": "isEstimated",
            "type": "Attribute",
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    requires_discount_code: bool | None = field(
        default=None,
        metadata={
            "name": "requiresDiscountCode",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class PromotionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    promotion_code: str | None = field(
        default=None,
        metadata={
            "name": "promotionCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    validation_code: str | None = field(
        default=None,
        metadata={
            "name": "validationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    value: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    customer_profile_id: str | None = field(
        default=None,
        metadata={
            "name": "customerProfileId",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    remove_current_promotion: bool | None = field(
        default=None,
        metadata={
            "name": "removeCurrentPromotion",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class RefundableMoneyType(MoneyType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    is_refundable: bool | None = field(
        default=None,
        metadata={
            "name": "isRefundable",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class RequestStatusType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    success: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    status_messages: Optional["RequestStatusType.StatusMessages"] = field(  # type: ignore[misc]
        default=None,
        metadata={
            "name": "statusMessages",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    debug: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    system_id: str | None = field(
        default=None,
        metadata={
            "name": "systemId",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class StatusMessages(StatusMessages):  # type: ignore[misc]
        status_message: list[StatusMessageType] = field(
            default_factory=list,
            metadata={
                "name": "statusMessage",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class RequestSummatedFareFilterType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    fare_category: RequestSummatedFareFilterTypeFareCategory | None = field(
        default=None,
        metadata={
            "name": "fareCategory",
            "type": "Attribute",
            "required": True,
        },
    )
    fare_class: RequestSummatedFareFilterTypeFareClass | None = field(
        default=None,
        metadata={
            "name": "fareClass",
            "type": "Attribute",
            "required": True,
        },
    )
    only_single_fares: bool | None = field(
        default=None,
        metadata={
            "name": "onlySingleFares",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class RuleType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    penalty: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    penalty_cost: MoneyType | None = field(
        default=None,
        metadata={
            "name": "penaltyCost",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    category: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    type_value: RuleTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    price_type: RuleTypePriceType | None = field(
        default=None,
        metadata={
            "name": "priceType",
            "type": "Attribute",
        },
    )
    applicable_order_status: RuleTypeApplicableOrderStatus | None = field(
        default=None,
        metadata={
            "name": "applicableOrderStatus",
            "type": "Attribute",
        },
    )
    applicable_ticketing_option: RuleTypeApplicableTicketingOption | None = field(
        default=None,
        metadata={
            "name": "applicableTicketingOption",
            "type": "Attribute",
        },
    )
    expiration_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "expirationDateTime",
            "type": "Attribute",
        },
    )
    estimated: bool | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    refund_to_voucher: RuleTypeRefundToVoucher | None = field(
        default=None,
        metadata={
            "name": "refundToVoucher",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class SeatAssignmentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    coach: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    direction: SeatAssignmentDirectionType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    seat_attributes: Optional["SeatAssignmentType.SeatAttributes"] = field(
        default=None,
        metadata={
            "name": "seatAttributes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class SeatAttributes:
        seat_attribute: list[SeatAttributeType] = field(
            default_factory=list,
            metadata={
                "name": "seatAttribute",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class SeatLocationListType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    seat: list[ExactSeatLocationType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class SupplyChannelPassengerReferenceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    passenger_idref: str | None = field(
        default=None,
        metadata={
            "name": "passengerIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    name_first: str | None = field(
        default=None,
        metadata={
            "name": "nameFirst",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    name_middle: str | None = field(
        default=None,
        metadata={
            "name": "nameMiddle",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    name_last: str | None = field(
        default=None,
        metadata={
            "name": "nameLast",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    loyalty_cards: Optional["SupplyChannelPassengerReferenceType.LoyaltyCards"] = field(
        default=None,
        metadata={
            "name": "loyaltyCards",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class LoyaltyCards:
        loyalty_card: list[PassengerLoyaltyCardType] = field(
            default_factory=list,
            metadata={
                "name": "loyaltyCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class TaxType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    amount: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class TotalPassengersConsumptionRuleType(ConsumptionRuleType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"


@dataclass(frozen=True)
class TotalPriceType(MoneyType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    is_estimated: bool | None = field(
        default=None,
        metadata={
            "name": "isEstimated",
            "type": "Attribute",
        },
    )
    requires_discount_code: bool | None = field(
        default=None,
        metadata={
            "name": "requiresDiscountCode",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class TravelDocumentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    document_number: str | None = field(
        default=None,
        metadata={
            "name": "documentNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    document_type: TravelDocumentTypeDocumentType | None = field(
        default=None,
        metadata={
            "name": "documentType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    expiration_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "expirationDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    issuing_authority: Optional["TravelDocumentType.IssuingAuthority"] = field(
        default=None,
        metadata={
            "name": "issuingAuthority",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    document_affiliation: TravelDocumentTypeDocumentAffiliation | None = field(
        default=None,
        metadata={
            "name": "documentAffiliation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class IssuingAuthority:
        country_code: str | None = field(
            default=None,
            metadata={
                "name": "countryCode",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
                "length": 2,
                "pattern": r"[a-zA-Z]+",
            },
        )
        state_prov: str | None = field(
            default=None,
            metadata={
                "name": "stateProv",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


@dataclass(frozen=True)
class TravelPassCodeType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: TravelPassCodeTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class TravelPointType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: TravelPointTypeEnumeration | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    request_stop: bool | None = field(
        default=None,
        metadata={
            "name": "requestStop",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class UnitCarbonType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value: float | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    unit: UnitCarbonTypeUnit | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class UpdateableOrderType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    ticket_option: bool | None = field(
        default=None,
        metadata={
            "name": "ticketOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    supplier_note: SupplierNoteSpecType | None = field(
        default=None,
        metadata={
            "name": "supplierNote",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class VoucherSpecType(BaseVoucherType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class VoucherType(BaseVoucherType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    expiration_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "expirationDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    value: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class WarningType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Attribute",
            "required": True,
        },
    )
    category: WarningTypeCategory | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ExchangeSetType:
    class Meta:
        name = "exchangeSetType"
        target_namespace = "http://railgds.net/ws/commontypes"

    exchangeable_ticketable_fares: ExchangeableTicketableFaresType | None = field(
        default=None,
        metadata={
            "name": "exchangeableTicketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    exchange_set_id: str | None = field(
        default=None,
        metadata={
            "name": "exchangeSetID",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class SelectedConfirmationOptionType:
    class Meta:
        name = "selectedConfirmationOptionType"
        target_namespace = "http://railgds.net/ws/commontypes"

    credit_card_option: BaseConfirmationCardType | None = field(
        default=None,
        metadata={
            "name": "creditCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    debit_card_option: Optional["SelectedConfirmationOptionType.DebitCardOption"] = (
        field(
            default=None,
            metadata={
                "name": "debitCardOption",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    loyalty_card_option: Optional[
        "SelectedConfirmationOptionType.LoyaltyCardOption"
    ] = field(
        default=None,
        metadata={
            "name": "loyaltyCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    personal_identification_card_option: Optional[
        "SelectedConfirmationOptionType.PersonalIdentificationCardOption"
    ] = field(
        default=None,
        metadata={
            "name": "personalIdentificationCardOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class DebitCardOption(BaseConfirmationCardType):
        sort_code: str | None = field(
            default=None,
            metadata={
                "name": "sortCode",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

    @dataclass(frozen=True)
    class LoyaltyCardOption:
        program: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        identifier: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        expiration_year_month_day: XmlDate | None = field(
            default=None,
            metadata={
                "name": "expirationYearMonthDay",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

    @dataclass(frozen=True)
    class PersonalIdentificationCardOption:
        cardholder_name_last: str | None = field(
            default=None,
            metadata={
                "name": "cardholderNameLast",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        cardholder_name_first: str | None = field(
            default=None,
            metadata={
                "name": "cardholderNameFirst",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        cardholder_name_middle: str | None = field(
            default=None,
            metadata={
                "name": "cardholderNameMiddle",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        identifier: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        country_code: str | None = field(
            default=None,
            metadata={
                "name": "countryCode",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        expiration_year_month_day: XmlDate | None = field(
            default=None,
            metadata={
                "name": "expirationYearMonthDay",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        date_of_birth: XmlDate | None = field(
            default=None,
            metadata={
                "name": "dateOfBirth",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


@dataclass(frozen=True)
class TicketingDetailType:
    class Meta:
        name = "ticketingDetailType"
        target_namespace = "http://railgds.net/ws/commontypes"

    code: TicketingDetailTypeCode | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class AddPaymentVoucherType(VoucherSpecType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AddedOrderNotesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    order_note: list[AddedOrderNoteType] = field(
        default_factory=list,
        metadata={
            "name": "orderNote",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class AdjustCostAndRevenueTicketableFareType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    cost_amounts: Optional["AdjustCostAndRevenueTicketableFareType.CostAmounts"] = (
        field(
            default=None,
            metadata={
                "name": "costAmounts",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
    )
    supplier_authorization_code: str | None = field(
        default=None,
        metadata={
            "name": "supplierAuthorizationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
            "min_length": 1,
            "max_length": 25,
        },
    )
    silver_core_authorization_code: str | None = field(
        default=None,
        metadata={
            "name": "silverCoreAuthorizationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "min_length": 1,
            "max_length": 25,
        },
    )
    adjustment_reason: AdjustCostAndRevenueTicketableFareTypeAdjustmentReason | None = (
        field(
            default=None,
            metadata={
                "name": "adjustmentReason",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
    )
    ticketable_fare_id: object | None = field(
        default=None,
        metadata={
            "name": "ticketableFareID",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class CostAmounts:
        cost_adjustment: list[CostAdjustmentType] = field(
            default_factory=list,
            metadata={
                "name": "costAdjustment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class AuditableRequestType(BaseRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    agent_information: Optional["AuditableRequestType.AgentInformation"] = field(
        default=None,
        metadata={
            "name": "agentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class AgentInformation:
        external_id: str | None = field(
            default=None,
            metadata={
                "name": "externalId",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        name: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingTransactionFeeType(BaseTransactionFeeType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ClaimDelayRepaySetType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "originTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "destinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "departureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "arrivalDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ConfirmationInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    value_document_retrieval_information: Optional[
        "ConfirmationInformationType.ValueDocumentRetrievalInformation"
    ] = field(
        default=None,
        metadata={
            "name": "valueDocumentRetrievalInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    selected_confirmation_option: SelectedConfirmationOptionType | None = field(
        default=None,
        metadata={
            "name": "selectedConfirmationOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    selected_ticket_language: str | None = field(
        default=None,
        metadata={
            "name": "selectedTicketLanguage",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ValueDocumentRetrievalInformation:
        customer: Optional[
            "ConfirmationInformationType.ValueDocumentRetrievalInformation.Customer"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card_number: str | None = field(
            default=None,
            metadata={
                "name": "creditCardNumber",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        expiration_date: XmlPeriod | None = field(
            default=None,
            metadata={
                "name": "expirationDate",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class Customer:
            name_last: str | None = field(
                default=None,
                metadata={
                    "name": "nameLast",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            name_first: str | None = field(
                default=None,
                metadata={
                    "name": "nameFirst",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            name_middle: str | None = field(
                default=None,
                metadata={
                    "name": "nameMiddle",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )


@dataclass(frozen=True)
class DelayRepaySetType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    ticketable_fare_idref: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    delay_refund_eligibility: DelayRefundEligibilityType | None = field(
        default=None,
        metadata={
            "name": "delayRefundEligibility",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    reason: ReasonType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    delay_repay_applied: bool | None = field(
        default=None,
        metadata={
            "name": "delayRepayApplied",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ReservationRequestType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    fare_code_locator: str | None = field(
        default=None,
        metadata={
            "name": "fareCodeLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    seats: SeatLocationListType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    seat_preferences: Optional["ReservationRequestType.SeatPreferences"] = field(
        default=None,
        metadata={
            "name": "seatPreferences",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class SeatPreferences:
        seat_preference: list[SeatPreferenceType] = field(
            default_factory=list,
            metadata={
                "name": "seatPreference",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class IntermediateTravelPoint:
    class Meta:
        name = "intermediateTravelPoint"
        target_namespace = "http://railgds.net/ws/booking"

    travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "travelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    scheduled_arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "scheduledArrivalDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    scheduled_departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "scheduledDepartureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    updated_arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "updatedArrivalDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    updated_departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "updatedDepartureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    status_reason: str | None = field(
        default=None,
        metadata={
            "name": "statusReason",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    platform: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    status: IntermediateTravelPointStatusEnumeration | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    activity: IntermediateTravelPointActivityEnumeration | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: IntermediateTravelPointTypeEnumeration | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class BaseCreditCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    expiration_year_month: XmlPeriod | None = field(
        default=None,
        metadata={
            "name": "expirationYearMonth",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    cardholder_name: str | None = field(
        default=None,
        metadata={
            "name": "cardholderName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    billing_address: AddressType | None = field(
        default=None,
        metadata={
            "name": "billingAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    site_card: bool | None = field(
        default=None,
        metadata={
            "name": "siteCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: BaseCreditCardTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class BaseDebitCardType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    start_year_month: XmlPeriod | None = field(
        default=None,
        metadata={
            "name": "startYearMonth",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    expiration_year_month: XmlPeriod | None = field(
        default=None,
        metadata={
            "name": "expirationYearMonth",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    cardholder_name: str | None = field(
        default=None,
        metadata={
            "name": "cardholderName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    billing_address: AddressType | None = field(
        default=None,
        metadata={
            "name": "billingAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: BaseDebitCardTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class BaseResponseType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    request_status: RequestStatusType | None = field(
        default=None,
        metadata={
            "name": "requestStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    conversation_token: str | None = field(
        default=None,
        metadata={
            "name": "conversationToken",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class BaseTravelPointPairType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "originTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "destinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class CancellationOptionType(BaseCancellationOptionType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    penalty: Optional["CancellationOptionType.Penalty"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    penalty_cost: Optional["CancellationOptionType.PenaltyCost"] = field(
        default=None,
        metadata={
            "name": "penaltyCost",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class Penalty:
        total: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        breakdown: Optional["CancellationOptionType.Penalty.Breakdown"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Breakdown:
            component: list["CancellationOptionType.Penalty.Breakdown.Component"] = (
                field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
            )

            @dataclass(frozen=True)
            class Component(MoneyType):
                type_value: ComponentType | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                        "required": True,
                    },
                )

    @dataclass(frozen=True)
    class PenaltyCost:
        total: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        breakdown: Optional["CancellationOptionType.PenaltyCost.Breakdown"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Breakdown:
            component: list[
                "CancellationOptionType.PenaltyCost.Breakdown.Component"
            ] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )

            @dataclass(frozen=True)
            class Component(MoneyType):
                type_value: ComponentType | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                        "required": True,
                    },
                )


@dataclass(frozen=True)
class CarrierRestrictionsType1:
    class Meta:
        name = "CarrierRestrictionsType"
        target_namespace = "http://railgds.net/ws/commontypes"

    carrier_restriction: list[CarrierRestrictionType1] = field(
        default_factory=list,
        metadata={
            "name": "carrierRestriction",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ConsumptionRulesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    age_break_consumption_rule: list[AgeBreakConsumptionRuleType] = field(
        default_factory=list,
        metadata={
            "name": "ageBreakConsumptionRule",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    total_passengers_consumption_rule: list[TotalPassengersConsumptionRuleType] = field(
        default_factory=list,
        metadata={
            "name": "totalPassengersConsumptionRule",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    travel_card_zone_consumption_rule: list[TravelCardZoneConsumptionRuleType] = field(
        default_factory=list,
        metadata={
            "name": "travelCardZoneConsumptionRule",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    plus_bus_zone_consumption_rule: list[PlusBusZoneConsumptionRuleType] = field(
        default_factory=list,
        metadata={
            "name": "plusBusZoneConsumptionRule",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class CustomerType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    title: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    name_first: str | None = field(
        default=None,
        metadata={
            "name": "nameFirst",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 0,
        },
    )
    name_middle: str | None = field(
        default=None,
        metadata={
            "name": "nameMiddle",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    name_last: str | None = field(
        default=None,
        metadata={
            "name": "nameLast",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_length": 0,
        },
    )
    suffix: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    dob: XmlDate | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    gender: GenderType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    residence_information: ResidenceInformationType | None = field(
        default=None,
        metadata={
            "name": "residenceInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    place_of_birth_information: PlaceOfBirthInformationType | None = field(
        default=None,
        metadata={
            "name": "placeOfBirthInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    address: AddressType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    contact_information: Optional["CustomerType.ContactInformation"] = field(
        default=None,
        metadata={
            "name": "contactInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    age_at_time_of_travel: int | None = field(
        default=None,
        metadata={
            "name": "ageAtTimeOfTravel",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    loyalty_cards: Optional["CustomerType.LoyaltyCards"] = field(
        default=None,
        metadata={
            "name": "loyaltyCards",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class ContactInformation:
        contact: list[CustomerContactType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class LoyaltyCards:
        loyalty_card: list[PassengerLoyaltyCardType] = field(
            default_factory=list,
            metadata={
                "name": "loyaltyCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class EquipmentTypeRestrictionsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    equipment_type: EquipmentTypeType | None = field(
        default=None,
        metadata={
            "name": "equipmentType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    type_value: EquipmentTypeRestrictionsTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ExchangeOptionType(BaseExchangeOptionType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    penalty: Optional["ExchangeOptionType.Penalty"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    penalty_cost: Optional["ExchangeOptionType.PenaltyCost"] = field(
        default=None,
        metadata={
            "name": "penaltyCost",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    exchange_breakdown: Optional["ExchangeOptionType.ExchangeBreakdown"] = field(
        default=None,
        metadata={
            "name": "exchangeBreakdown",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Penalty:
        total: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        breakdown: Optional["ExchangeOptionType.Penalty.Breakdown"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Breakdown:
            component: list["ExchangeOptionType.Penalty.Breakdown.Component"] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )

            @dataclass(frozen=True)
            class Component(MoneyType):
                type_value: ComponentType | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                        "required": True,
                    },
                )

    @dataclass(frozen=True)
    class PenaltyCost:
        total: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        breakdown: Optional["ExchangeOptionType.PenaltyCost.Breakdown"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Breakdown:
            component: list["ExchangeOptionType.PenaltyCost.Breakdown.Component"] = (
                field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
            )

            @dataclass(frozen=True)
            class Component(MoneyType):
                type_value: ComponentType | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                        "required": True,
                    },
                )

    @dataclass(frozen=True)
    class ExchangeBreakdown:
        new_products_total: MoneyType | None = field(
            default=None,
            metadata={
                "name": "newProductsTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        new_fees_total: MoneyType | None = field(
            default=None,
            metadata={
                "name": "newFeesTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        reversed_revenue_total: MoneyType | None = field(
            default=None,
            metadata={
                "name": "reversedRevenueTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        revenue_total: MoneyType | None = field(
            default=None,
            metadata={
                "name": "revenueTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        receipt_total: MoneyType | None = field(
            default=None,
            metadata={
                "name": "receiptTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        exchanged_loss_total: MoneyType | None = field(
            default=None,
            metadata={
                "name": "exchangedLossTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


@dataclass(frozen=True)
class FareCodeType:
    """:ivar service_class:

    :ivar travel_segment_idref: :ivar sub_segment_idref: :ivar cabin_class:
    :ivar rewards_eligible: :ivar fare_class: :ivar fare_display_name: :ivar
    open_return: :ivar fare_return_expiration_date_time: :ivar overbooked: :ivar
    reservable: :ivar reservation_requested: :ivar fare_start_date_time: :ivar
    fare_expiration_date_time: :ivar seat_assignment: :ivar seats: :ivar
    seats_available: :ivar seat_preferences: :ivar amenities: :ivar services:
    :ivar fare_applicabilities: :ivar optional_prices_requested: :ivar code:
    :ivar fare_code_id: This attribute should be required but it will     remain
    optional for backwards compatibility.
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    service_class: ServiceClassType | None = field(
        default=None,
        metadata={
            "name": "serviceClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    sub_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "subSegmentIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cabin_class: str | None = field(
        default=None,
        metadata={
            "name": "cabinClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    rewards_eligible: YesNoType | None = field(
        default=None,
        metadata={
            "name": "rewardsEligible",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_class: str | None = field(
        default=None,
        metadata={
            "name": "fareClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_display_name: str | None = field(
        default=None,
        metadata={
            "name": "fareDisplayName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    open_return: YesNoType | None = field(
        default=None,
        metadata={
            "name": "openReturn",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_return_expiration_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "fareReturnExpirationDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    overbooked: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    reservable: ReservableType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    reservation_requested: YesNoType | None = field(
        default=None,
        metadata={
            "name": "reservationRequested",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_start_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "fareStartDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_expiration_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "fareExpirationDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seat_assignment: SeatAssignmentType | None = field(
        default=None,
        metadata={
            "name": "seatAssignment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seats: SeatLocationListType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seats_available: int | None = field(
        default=None,
        metadata={
            "name": "seatsAvailable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seat_preferences: Optional["FareCodeType.SeatPreferences"] = field(
        default=None,
        metadata={
            "name": "seatPreferences",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    amenities: Optional["FareCodeType.Amenities"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    services: Optional["FareCodeType.Services"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_applicabilities: Optional["FareCodeType.FareApplicabilities"] = field(
        default=None,
        metadata={
            "name": "fareApplicabilities",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    optional_prices_requested: Optional["FareCodeType.OptionalPricesRequested"] = field(
        default=None,
        metadata={
            "name": "optionalPricesRequested",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    code: object | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    fare_code_id: str | None = field(
        default=None,
        metadata={
            "name": "fareCodeID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class SeatPreferences:
        seat_preference: list[SeatPreferenceType] = field(
            default_factory=list,
            metadata={
                "name": "seatPreference",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Amenities:
        amenity: list[AmenityType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Services:
        service: list["FareCodeType.Services.Service"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Service:
            value: str = field(
                default="",
                metadata={
                    "required": True,
                },
            )
            category: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            supplement_code: str | None = field(
                default=None,
                metadata={
                    "name": "supplementCode",
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class FareApplicabilities:
        fare_applicability: list[
            "FareCodeType.FareApplicabilities.FareApplicability"
        ] = field(
            default_factory=list,
            metadata={
                "name": "fareApplicability",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class FareApplicability:
            fare_applicability_text: str | None = field(
                default=None,
                metadata={
                    "name": "fareApplicabilityText",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            outbound: FareApplicabilityRestrictionType | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            return_value: FareApplicabilityRestrictionType | None = field(
                default=None,
                metadata={
                    "name": "return",
                    "type": "Attribute",
                },
            )
            type_value: FareApplicabilityBasisType | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class OptionalPricesRequested:
        optional_price_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "optionalPriceIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class FareTerminalPointType(TravelPointType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    unknown_fare_mapping: bool | None = field(
        default=None,
        metadata={
            "name": "unknownFareMapping",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class FeesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    fee: list[FeeType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class PaymentRequirementsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    acceptable_forms_of_payment: Optional[
        "PaymentRequirementsType.AcceptableFormsOfPayment"
    ] = field(
        default=None,
        metadata={
            "name": "acceptableFormsOfPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    credit_card_surcharge_fees: Optional[
        "PaymentRequirementsType.CreditCardSurchargeFees"
    ] = field(
        default=None,
        metadata={
            "name": "creditCardSurchargeFees",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    confirmation_upon_add_payment: bool | None = field(
        default=None,
        metadata={
            "name": "confirmationUponAddPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class AcceptableFormsOfPayment:
        form_of_payment: list[FormOfPaymentType] = field(
            default_factory=list,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class CreditCardSurchargeFees:
        credit_card_surcharge_fee: list[CreditCardSurchargeFeeType] = field(
            default_factory=list,
            metadata={
                "name": "creditCardSurchargeFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PromotionsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    promotion: list[PromotionType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class QueryTravelPassType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    code: TravelPassCodeType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    start_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "startDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ResponseSummatedFareFilterType(RequestSummatedFareFilterType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    summated_fare_filter_id: int | None = field(
        default=None,
        metadata={
            "name": "summatedFareFilterId",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class RevisionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    reason: RevisionReasonType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    revised_departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "revisedDepartureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    revised_arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "revisedArrivalDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    revised_origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "revisedOriginTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    revised_destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "revisedDestinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    travel_segment_idref: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentIDRef",
            "type": "Attribute",
            "required": True,
        },
    )
    status: RevisionTypeStatus | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class RoutingRestrictionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    routing_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "routingTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    type_value: RoutingRestrictionTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class RulesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    rule: list[RuleType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class SelectedCancellationOptionType(BaseCancellationOptionType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"


@dataclass(frozen=True)
class SelectedExchangeOptionType(BaseExchangeOptionType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"


@dataclass(frozen=True)
class ShippingInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    shipping_name: str | None = field(
        default=None,
        metadata={
            "name": "shippingName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    shipping_address: AddressType | None = field(
        default=None,
        metadata={
            "name": "shippingAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class SplitTicketingRequestType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    automatic_split_at_calling_stations: object | None = field(
        default=None,
        metadata={
            "name": "automaticSplitAtCallingStations",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    automatic_split_at_interchanges: object | None = field(
        default=None,
        metadata={
            "name": "automaticSplitAtInterchanges",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    excluded_fares: Optional["SplitTicketingRequestType.ExcludedFares"] = field(
        default=None,
        metadata={
            "name": "excludedFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    summated_fare_filters: Optional["SplitTicketingRequestType.SummatedFareFilters"] = (
        field(
            default=None,
            metadata={
                "name": "summatedFareFilters",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    max_splits: int | None = field(
        default=None,
        metadata={
            "name": "maxSplits",
            "type": "Attribute",
            "required": True,
        },
    )
    max_summated_fares: int | None = field(
        default=None,
        metadata={
            "name": "maxSummatedFares",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ExcludedFares:
        ticket_code: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketCode",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class SummatedFareFilters:
        summated_fare_filter: list[RequestSummatedFareFilterType] = field(
            default_factory=list,
            metadata={
                "name": "summatedFareFilter",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class SubSegmentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "originTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "destinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "departureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "arrivalDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    sub_segment_id: str | None = field(
        default=None,
        metadata={
            "name": "subSegmentID",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class SummatedFareTypes:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    summated_fare: list["SummatedFareTypes.SummatedFare"] = field(
        default_factory=list,
        metadata={
            "name": "summatedFare",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )

    @dataclass(frozen=True)
    class SummatedFare:
        total_price: TotalPriceType | None = field(
            default=None,
            metadata={
                "name": "totalPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        outward_fares: Optional["SummatedFareTypes.SummatedFare.OutwardFares"] = field(
            default=None,
            metadata={
                "name": "outwardFares",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        return_fares: Optional["SummatedFareTypes.SummatedFare.ReturnFares"] = field(
            default=None,
            metadata={
                "name": "returnFares",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        outward_leg_solutions: Optional[
            "SummatedFareTypes.SummatedFare.OutwardLegSolutions"
        ] = field(
            default=None,
            metadata={
                "name": "outwardLegSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        return_leg_solutions: Optional[
            "SummatedFareTypes.SummatedFare.ReturnLegSolutions"
        ] = field(
            default=None,
            metadata={
                "name": "returnLegSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        summated_fare_filter_ids: str | None = field(
            default=None,
            metadata={
                "name": "summatedFareFilterIds",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        summated_fare_id: int | None = field(
            default=None,
            metadata={
                "name": "summatedFareId",
                "type": "Attribute",
            },
        )

        @dataclass(frozen=True)
        class OutwardFares:
            fare: list[str] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class ReturnFares:
            fare: list[str] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class OutwardLegSolutions:
            leg_solution_idref: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "legSolutionIDRef",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class ReturnLegSolutions:
            leg_solution_idref: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "legSolutionIDRef",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )


@dataclass(frozen=True)
class SupplementType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number_of_units: int | None = field(
        default=None,
        metadata={
            "name": "numberOfUnits",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    price: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    applicable_fare_code_idrefs: Optional["SupplementType.ApplicableFareCodeIdrefs"] = (
        field(
            default=None,
            metadata={
                "name": "applicableFareCodeIDRefs",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    travel_segments: Optional["SupplementType.TravelSegments"] = field(
        default=None,
        metadata={
            "name": "travelSegments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    passenger_idrefs: Optional["SupplementType.PassengerIdrefs"] = field(
        default=None,
        metadata={
            "name": "passengerIDRefs",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seat_assignment: SeatAssignmentType | None = field(
        default=None,
        metadata={
            "name": "seatAssignment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    category: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ApplicableFareCodeIdrefs:
        applicable_fare_code_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "applicableFareCodeIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class TravelSegments:
        travel_segment_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "travelSegmentIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class PassengerIdrefs:
        passenger_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "passengerIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class TaxesType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    total_price: MoneyType | None = field(
        default=None,
        metadata={
            "name": "totalPrice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    tax: list[TaxType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class TravelInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    information: list[InformationType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class TravelPointPairType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "originTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "destinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    departure_date_time_window: DateTimeWindowType | None = field(
        default=None,
        metadata={
            "name": "departureDateTimeWindow",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    arrival_date_time_window: DateTimeWindowType | None = field(
        default=None,
        metadata={
            "name": "arrivalDateTimeWindow",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class ValueDocumentCouponType(CouponTypeAbstract):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    coupon_received_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "couponReceivedDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    unique_ticket_number: str | None = field(
        default=None,
        metadata={
            "name": "uniqueTicketNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    origin: TravelPointType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    destination: TravelPointType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    refund_approved_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "refundApprovedDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    authorization: Optional["ValueDocumentCouponType.Authorization"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "departureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticket_type_code: str | None = field(
        default=None,
        metadata={
            "name": "ticketTypeCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticket_type: str | None = field(
        default=None,
        metadata={
            "name": "ticketType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    number_adults: str | None = field(
        default=None,
        metadata={
            "name": "numberAdults",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    number_children: str | None = field(
        default=None,
        metadata={
            "name": "numberChildren",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    railcard_printing_name: str | None = field(
        default=None,
        metadata={
            "name": "railcardPrintingName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketable_fare_idref: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    type_value: ValueDocumentCouponTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    is_releasable: bool | None = field(
        default=None,
        metadata={
            "name": "isReleasable",
            "type": "Attribute",
        },
    )
    released_at: str | None = field(
        default=None,
        metadata={
            "name": "releasedAt",
            "type": "Attribute",
        },
    )
    return_start_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "returnStartDateTime",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class Authorization:
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        code: str | None = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )


@dataclass(frozen=True)
class ValueDocumentTicketType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    barcode: Optional["ValueDocumentTicketType.Barcode"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    data: Optional["ValueDocumentTicketType.Data"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cabin_class: str | None = field(
        default=None,
        metadata={
            "name": "cabinClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    ticket_type: str | None = field(
        default=None,
        metadata={
            "name": "ticketType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    out_return_indicator: str | None = field(
        default=None,
        metadata={
            "name": "outReturnIndicator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    issuing_system_id: str | None = field(
        default=None,
        metadata={
            "name": "issuingSystemID",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    issuing_system_unique_eticket_number: str | None = field(
        default=None,
        metadata={
            "name": "issuingSystemUniqueEticketNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    check_sum: str | None = field(
        default=None,
        metadata={
            "name": "checkSum",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    departure_time: str | None = field(
        default=None,
        metadata={
            "name": "departureTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    origin: TravelPointType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    origin_name: str | None = field(
        default=None,
        metadata={
            "name": "originName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination: TravelPointType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination_name: str | None = field(
        default=None,
        metadata={
            "name": "destinationName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    departure_date: str | None = field(
        default=None,
        metadata={
            "name": "departureDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    reservations: Optional["ValueDocumentTicketType.Reservations"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    adult_child_indicator: str | None = field(
        default=None,
        metadata={
            "name": "adultChildIndicator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    customer_name: str | None = field(
        default=None,
        metadata={
            "name": "customerName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    document_idtype: str | None = field(
        default=None,
        metadata={
            "name": "documentIDType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    document_idnumber: str | None = field(
        default=None,
        metadata={
            "name": "documentIDNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    route_description: str | None = field(
        default=None,
        metadata={
            "name": "routeDescription",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    price: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    restriction_code: str | None = field(
        default=None,
        metadata={
            "name": "restrictionCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_expiry_date: str | None = field(
        default=None,
        metadata={
            "name": "fareExpiryDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    passenger_idref: str | None = field(
        default=None,
        metadata={
            "name": "passengerIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketable_fare_idref: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class Reservations:
        reservation: list[ValueDocumentTicketReservationType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Barcode:
        value: bytes | None = field(
            default=None,
            metadata={
                "required": True,
                "format": "base64",
            },
        )
        type_value: str | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class Data:
        value: bytes | None = field(
            default=None,
            metadata={
                "required": True,
                "format": "base64",
            },
        )
        type_value: str | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass(frozen=True)
class WarningsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    warning: list[WarningType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ExchangeSetsType:
    class Meta:
        name = "exchangeSetsType"
        target_namespace = "http://railgds.net/ws/commontypes"

    exchange_set: list[ExchangeSetType] = field(
        default_factory=list,
        metadata={
            "name": "exchangeSet",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class MarketingCarrierRefType:
    class Meta:
        name = "marketingCarrierRefType"
        target_namespace = "http://railgds.net/ws/commontypes"

    ticketing_details: Optional["MarketingCarrierRefType.TicketingDetails"] = field(
        default=None,
        metadata={
            "name": "ticketingDetails",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    reference_code: object | None = field(
        default=None,
        metadata={
            "name": "referenceCode",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class TicketingDetails:
        ticketing_detail: list[TicketingDetailType] = field(
            default_factory=list,
            metadata={
                "name": "ticketingDetail",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class AddPaymentCreditCardType(BaseCreditCardType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    validation_number: str | None = field(
        default=None,
        metadata={
            "name": "validationNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AddPaymentDebitCardType(BaseDebitCardType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    issue_number: str | None = field(
        default=None,
        metadata={
            "name": "issueNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    validation_number: str | None = field(
        default=None,
        metadata={
            "name": "validationNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AuthenticatePayerResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    three_dee_secure_authenticate_payer: Optional[
        "AuthenticatePayerResponseType.ThreeDeeSecureAuthenticatePayer"
    ] = field(
        default=None,
        metadata={
            "name": "threeDeeSecureAuthenticatePayer",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ThreeDeeSecureAuthenticatePayer:
        is_enrolled: bool | None = field(
            default=None,
            metadata={
                "name": "isEnrolled",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        processor: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        access_control_server_url: str | None = field(
            default=None,
            metadata={
                "name": "accessControlServerUrl",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        payer_authentication_request: str | None = field(
            default=None,
            metadata={
                "name": "payerAuthenticationRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class AuthenticatePayerV2ChallengeRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AuthenticatePayerV2ChallengeResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    ds_trans_id: str | None = field(
        default=None,
        metadata={
            "name": "dsTransId",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    eci: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    authentication_status: str | None = field(
        default=None,
        metadata={
            "name": "authenticationStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    authentication_value: str | None = field(
        default=None,
        metadata={
            "name": "authenticationValue",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class AuthenticatePayerV2ResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    authentication_status: AuthenticatePayerV2AuthenticationStatusType | None = field(
        default=None,
        metadata={
            "name": "authenticationStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    authentication_value: str | None = field(
        default=None,
        metadata={
            "name": "authenticationValue",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    ds_trans_id: str | None = field(
        default=None,
        metadata={
            "name": "dsTransId",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    eci: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    cardholder_response_info: str | None = field(
        default=None,
        metadata={
            "name": "cardholderResponseInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    challenge: Optional["AuthenticatePayerV2ResponseType.Challenge"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Challenge:
        request_url: str | None = field(
            default=None,
            metadata={
                "name": "requestUrl",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        encoded_creq: str | None = field(
            default=None,
            metadata={
                "name": "encodedCreq",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class AuthenticatePayerV2VersionResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    securev2supported: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    method_url: str | None = field(
        default=None,
        metadata={
            "name": "methodURL",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    method_data: str | None = field(
        default=None,
        metadata={
            "name": "methodData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class BaseAddOrderRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    notes: Optional["BaseAddOrderRequestType.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order_notes: Optional["BaseAddOrderRequestType.OrderNotes"] = field(
        default=None,
        metadata={
            "name": "orderNotes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Notes:
        note: list[BookingNoteType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class OrderNotes:
        order_note: list[OrderNoteType] = field(
            default_factory=list,
            metadata={
                "name": "orderNote",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class BaseBookingRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    notes: Optional["BaseBookingRequestType.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order_notes: Optional["BaseBookingRequestType.OrderNotes"] = field(
        default=None,
        metadata={
            "name": "orderNotes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Notes:
        note: list[BookingNoteType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class OrderNotes:
        order_note: list[AddedOrderNoteType] = field(
            default_factory=list,
            metadata={
                "name": "orderNote",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class DelayRefundType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    delay_repay_sets: Optional["DelayRefundType.DelayRepaySets"] = field(
        default=None,
        metadata={
            "name": "delayRepaySets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class DelayRepaySets:
        delay_repay_set: list[DelayRepaySetType] = field(
            default_factory=list,
            metadata={
                "name": "delayRepaySet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class DelayRepayRefundResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_status: RefundStatusType | None = field(
        default=None,
        metadata={
            "name": "refundStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class DelayRepaySetRequestType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    ticketable_fare_locators: Optional[
        "DelayRepaySetRequestType.TicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "ticketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    claim: ClaimDelayRepaySetType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    delay_repay_set_id: str | None = field(
        default=None,
        metadata={
            "name": "delayRepaySetID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class TicketableFareLocators:
        ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class DeleteCardholderInfoRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class DeleteCardholderInfoResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DeletePaymentTokenRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    account_holder_first_name: str | None = field(
        default=None,
        metadata={
            "name": "accountHolderFirstName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    account_holder_last_name: str | None = field(
        default=None,
        metadata={
            "name": "accountHolderLastName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    force_delete: bool | None = field(
        default=None,
        metadata={
            "name": "forceDelete",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class DeletePaymentTokenResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class GeneratePaymentTokenResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ReservationShoppingQueryType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    travel_point_pairs: Optional["ReservationShoppingQueryType.TravelPointPairs"] = (
        field(
            default=None,
            metadata={
                "name": "travelPointPairs",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
    )

    @dataclass(frozen=True)
    class TravelPointPairs:
        travel_point_pair: list[TravelPointPairType] = field(
            default_factory=list,
            metadata={
                "name": "travelPointPair",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class ReservationTicketableFare:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    reservation_requests: Optional["ReservationTicketableFare.ReservationRequests"] = (
        field(
            default=None,
            metadata={
                "name": "reservationRequests",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )
    ticketable_fare_id: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareID",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ReservationRequests:
        reservation_request: list[ReservationRequestType] = field(
            default_factory=list,
            metadata={
                "name": "reservationRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class RetrieveBookingRecordRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    supply_channel_record_locator: str | None = field(
        default=None,
        metadata={
            "name": "supplyChannelRecordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    value_document_locator: str | None = field(
        default=None,
        metadata={
            "name": "valueDocumentLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    orders: Optional["RetrieveBookingRecordRequestType.Orders"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["RetrieveBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Orders:
        order: list["RetrieveBookingRecordRequestType.Orders.Order"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Order:
            alternative_ticket_pickup_location: TravelPointType | None = field(
                default=None,
                metadata={
                    "name": "alternativeTicketPickupLocation",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            order_number: str | None = field(
                default=None,
                metadata={
                    "name": "orderNumber",
                    "type": "Attribute",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class ResponseSpec:
        include_order_details: bool | None = field(
            default=None,
            metadata={
                "name": "includeOrderDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_order_costs: bool | None = field(
            default=None,
            metadata={
                "name": "includeOrderCosts",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_passenger_details: bool | None = field(
            default=None,
            metadata={
                "name": "includePassengerDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_financials: bool | None = field(
            default=None,
            metadata={
                "name": "includeFinancials",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_payment_requirements: bool | None = field(
            default=None,
            metadata={
                "name": "includePaymentRequirements",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_ticketing_options: bool | None = field(
            default=None,
            metadata={
                "name": "includeTicketingOptions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_notes: bool | None = field(
            default=None,
            metadata={
                "name": "includeNotes",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_fulfillment_information: bool | None = field(
            default=None,
            metadata={
                "name": "includeFulfillmentInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "includeReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class RetrieveCancellationSummaryRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    ticketable_fare_locators: Optional[
        "RetrieveCancellationSummaryRequestType.TicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "ticketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class TicketableFareLocators:
        ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class SearchBookingsRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    search_filter: Optional["SearchBookingsRequestType.SearchFilter"] = field(
        default=None,
        metadata={
            "name": "searchFilter",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    page_number: int | None = field(
        default=None,
        metadata={
            "name": "pageNumber",
            "type": "Attribute",
        },
    )
    page_size: int | None = field(
        default=None,
        metadata={
            "name": "pageSize",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class SearchFilter:
        departure_date_time: Optional[
            "SearchBookingsRequestType.SearchFilter.DepartureDateTime"
        ] = field(
            default=None,
            metadata={
                "name": "departureDateTime",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        order_statuses: Optional[
            "SearchBookingsRequestType.SearchFilter.OrderStatuses"
        ] = field(
            default=None,
            metadata={
                "name": "orderStatuses",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fare_classes: Optional["SearchBookingsRequestType.SearchFilter.FareClasses"] = (
            field(
                default=None,
                metadata={
                    "name": "fareClasses",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        passenger_custom_informations: CustomInformationType | None = field(
            default=None,
            metadata={
                "name": "passengerCustomInformations",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        passenger_details: Optional[
            "SearchBookingsRequestType.SearchFilter.PassengerDetails"
        ] = field(
            default=None,
            metadata={
                "name": "passengerDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        search_type: SearchBookFilterType | None = field(
            default=None,
            metadata={
                "name": "searchType",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class DepartureDateTime:
            start: XmlDateTime | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            end: XmlDateTime | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )

        @dataclass(frozen=True)
        class OrderStatuses:
            order_status: list[OrderStatusFilterType] = field(
                default_factory=list,
                metadata={
                    "name": "orderStatus",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class FareClasses:
            fare_class: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "fareClass",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class PassengerDetails:
            passenger_first_name: str | None = field(
                default=None,
                metadata={
                    "name": "passengerFirstName",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            passenger_last_name: str | None = field(
                default=None,
                metadata={
                    "name": "passengerLastName",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            email_address: str | None = field(
                default=None,
                metadata={
                    "name": "emailAddress",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )


@dataclass(frozen=True)
class CancellationSummaryType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    cancellation_options: Optional["CancellationSummaryType.CancellationOptions"] = (
        field(
            default=None,
            metadata={
                "name": "cancellationOptions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    price_reversals: Optional["CancellationSummaryType.PriceReversals"] = field(
        default=None,
        metadata={
            "name": "priceReversals",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    is_cancellable: bool | None = field(
        default=None,
        metadata={
            "name": "isCancellable",
            "type": "Attribute",
            "required": True,
        },
    )
    is_partially_cancellable: bool | None = field(
        default=None,
        metadata={
            "name": "isPartiallyCancellable",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class CancellationOptions:
        cancellation_option: list[CancellationOptionType] = field(
            default_factory=list,
            metadata={
                "name": "cancellationOption",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class PriceReversals:
        total: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        breakdown: Optional["CancellationSummaryType.PriceReversals.Breakdown"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Breakdown:
            component: list[
                "CancellationSummaryType.PriceReversals.Breakdown.Component"
            ] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class Component:
                amount: MoneyType | None = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "required": True,
                    },
                )
                type_value: str | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                    },
                )


@dataclass(frozen=True)
class CreditCardType(BaseCreditCardType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    payment_processor_info: PaymentProcessorInfoType | None = field(
        default=None,
        metadata={
            "name": "paymentProcessorInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class DebitCardType(BaseDebitCardType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    payment_processor_info: PaymentProcessorInfoType | None = field(
        default=None,
        metadata={
            "name": "paymentProcessorInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ExchangeSummaryType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    exchange_options: Optional["ExchangeSummaryType.ExchangeOptions"] = field(
        default=None,
        metadata={
            "name": "exchangeOptions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    payment_requirements: PaymentRequirementsType | None = field(
        default=None,
        metadata={
            "name": "paymentRequirements",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class ExchangeOptions:
        exchange_option: list[ExchangeOptionType] = field(
            default_factory=list,
            metadata={
                "name": "exchangeOption",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class OptionalPriceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    price: Optional["OptionalPriceType.Price"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    applicable_travel_segments: Optional[
        "OptionalPriceType.ApplicableTravelSegments"
    ] = field(
        default=None,
        metadata={
            "name": "applicableTravelSegments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    applicable_passenger_idrefs: Optional[
        "OptionalPriceType.ApplicablePassengerIdrefs"
    ] = field(
        default=None,
        metadata={
            "name": "applicablePassengerIDRefs",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    supplement_availabilities: Optional[
        "OptionalPriceType.SupplementAvailabilities"
    ] = field(
        default=None,
        metadata={
            "name": "supplementAvailabilities",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    rules: RulesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_codes: Optional["OptionalPriceType.FareCodes"] = field(
        default=None,
        metadata={
            "name": "fareCodes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_qualifier_idref: str | None = field(
        default=None,
        metadata={
            "name": "fareQualifierIDRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketing_options_available: TicketingOptionsAvailableType | None = field(
        default=None,
        metadata={
            "name": "ticketingOptionsAvailable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    consumption_rules: ConsumptionRulesType | None = field(
        default=None,
        metadata={
            "name": "consumptionRules",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    maximum_bookable_quantity: int | None = field(
        default=None,
        metadata={
            "name": "maximumBookableQuantity",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    optional_price_id: str | None = field(
        default=None,
        metadata={
            "name": "optionalPriceID",
            "type": "Attribute",
        },
    )
    quantity: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    category: OptionalPriceTypeCategory | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class Price(MoneyType):
        type_value: PriceType2 | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )
        supplement_category: str | None = field(
            default=None,
            metadata={
                "name": "supplementCategory",
                "type": "Attribute",
            },
        )
        supplement_code: str | None = field(
            default=None,
            metadata={
                "name": "supplementCode",
                "type": "Attribute",
            },
        )

    @dataclass(frozen=True)
    class ApplicableTravelSegments:
        travel_segment_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "travelSegmentIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )
        min_quantity: int | None = field(
            default=None,
            metadata={
                "name": "minQuantity",
                "type": "Attribute",
            },
        )
        max_quantity: int | None = field(
            default=None,
            metadata={
                "name": "maxQuantity",
                "type": "Attribute",
            },
        )

    @dataclass(frozen=True)
    class ApplicablePassengerIdrefs:
        applicable_passenger_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "applicablePassengerIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )
        min_quantity: int | None = field(
            default=None,
            metadata={
                "name": "minQuantity",
                "type": "Attribute",
            },
        )
        max_quantity: int | None = field(
            default=None,
            metadata={
                "name": "maxQuantity",
                "type": "Attribute",
            },
        )

    @dataclass(frozen=True)
    class SupplementAvailabilities:
        supplement_availability: list[SupplementAvailabilityType] = field(
            default_factory=list,
            metadata={
                "name": "supplementAvailability",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class FareCodes:
        fare_code: list[OptionalPriceFareCodeType] = field(
            default_factory=list,
            metadata={
                "name": "fareCode",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PassengerType(CustomerType):
    """:ivar travel_documents:

    :ivar order_references: Will only be returned if the     includeOrderDetails
    flag is true in the request :ivar customer_reference: Will only be returned
    if the     includeOrderDetails flag is true in the request :ivar
    custom_information: Element is only valid for update booking     requests
    and retrieve booking responses. :ivar smart_card_number: Unsupported :ivar
    passenger_id: This attribute should be required but it will     remain
    optional for backwards compatibility.
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    travel_documents: Optional["PassengerType.TravelDocuments"] = field(
        default=None,
        metadata={
            "name": "travelDocuments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    order_references: Optional["PassengerType.OrderReferences"] = field(
        default=None,
        metadata={
            "name": "orderReferences",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    customer_reference: Optional["PassengerType.CustomerReference"] = field(
        default=None,
        metadata={
            "name": "customerReference",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    custom_information: CustomInformationType | None = field(
        default=None,
        metadata={
            "name": "customInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    smart_card_number: str | None = field(
        default=None,
        metadata={
            "name": "smartCardNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "pattern": r"[0-9]{0,18}",
        },
    )
    passenger_id: str | None = field(
        default=None,
        metadata={
            "name": "passengerID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class TravelDocuments:
        travel_document: list[TravelDocumentType] = field(
            default_factory=list,
            metadata={
                "name": "travelDocument",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class OrderReferences:
        order_idref: list[str] = field(
            default_factory=list,
            metadata={
                "name": "orderIDRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class CustomerReference:
        crm_number: str | None = field(
            default=None,
            metadata={
                "name": "crmNumber",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        username: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        customer_number: str | None = field(
            default=None,
            metadata={
                "name": "customerNumber",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        customer_source: str | None = field(
            default=None,
            metadata={
                "name": "customerSource",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        campaign_reference: str | None = field(
            default=None,
            metadata={
                "name": "campaignReference",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


@dataclass(frozen=True)
class ResponseSummatedFareFilterTypes:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    summated_fare_filter: list[ResponseSummatedFareFilterType] = field(
        default_factory=list,
        metadata={
            "name": "summatedFareFilter",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class RoutingRestrictionsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    routing_restriction: list[RoutingRestrictionType] = field(
        default_factory=list,
        metadata={
            "name": "routingRestriction",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class TicketingOptionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    description: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fee: RefundableMoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    marketing_carrier_refs: Optional["TicketingOptionType.MarketingCarrierRefs"] = (
        field(
            default=None,
            metadata={
                "name": "marketingCarrierRefs",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    code: TicketingOptionTypeCode | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    departure_station: bool | None = field(
        default=None,
        metadata={
            "name": "departureStation",
            "type": "Attribute",
        },
    )
    destination: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    redelivery_allowed: bool | None = field(
        default=None,
        metadata={
            "name": "redeliveryAllowed",
            "type": "Attribute",
        },
    )
    agent_email: str | None = field(
        default=None,
        metadata={
            "name": "agentEmail",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class MarketingCarrierRefs:
        marketing_carrier_ref: list[MarketingCarrierRefType] = field(
            default_factory=list,
            metadata={
                "name": "marketingCarrierRef",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class TravelPointPairDateType(BaseTravelPointPairType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    start_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "startDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    end_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "endDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class TravelSegmentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "originTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "destinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    departure_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "departureDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "arrivalDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    service_origins: SegmentServiceListType | None = field(
        default=None,
        metadata={
            "name": "serviceOrigins",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    service_destinations: SegmentServiceListType | None = field(
        default=None,
        metadata={
            "name": "serviceDestinations",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    designator: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    marketing_carrier: CarrierType | None = field(
        default=None,
        metadata={
            "name": "marketingCarrier",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    operating_carrier: CarrierType | None = field(
        default=None,
        metadata={
            "name": "operatingCarrier",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    supplier_equipment_type: SupplierEquipmentTypeType | None = field(
        default=None,
        metadata={
            "name": "supplierEquipmentType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    distance: DistanceType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    duration: XmlDuration | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    on_time_percentage: float | None = field(
        default=None,
        metadata={
            "name": "onTimePercentage",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    amenities: Optional["TravelSegmentType.Amenities"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cross_border_info: bool | None = field(
        default=None,
        metadata={
            "name": "crossBorderInfo",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    supplier_record_locator: str | None = field(
        default=None,
        metadata={
            "name": "supplierRecordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    equipment_type: EquipmentTypeType | None = field(
        default=None,
        metadata={
            "name": "equipmentType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    carbon_data: UnitCarbonType | None = field(
        default=None,
        metadata={
            "name": "carbonData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    via_travel_points: Optional["TravelSegmentType.ViaTravelPoints"] = field(
        default=None,
        metadata={
            "name": "viaTravelPoints",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    marketing_service_name: str | None = field(
        default=None,
        metadata={
            "name": "marketingServiceName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    marketing_information: MarketingInformationType | None = field(
        default=None,
        metadata={
            "name": "marketingInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seat_map_information: SeatMapInformationType | None = field(
        default=None,
        metadata={
            "name": "seatMapInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    schedule_confirmed: bool | None = field(
        default=None,
        metadata={
            "name": "scheduleConfirmed",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    avg_train_loading: Optional["TravelSegmentType.AvgTrainLoading"] = field(
        default=None,
        metadata={
            "name": "avgTrainLoading",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    travel_information: TravelInformationType | None = field(
        default=None,
        metadata={
            "name": "travelInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    sequence: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        },
    )
    travel_segment_id: str | None = field(
        default=None,
        metadata={
            "name": "travelSegmentID",
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    leg_grouping: str | None = field(
        default=None,
        metadata={
            "name": "legGrouping",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class Amenities:
        amenity: list[AmenityType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ViaTravelPoints:
        via_travel_point: list[TravelPointType] = field(
            default_factory=list,
            metadata={
                "name": "viaTravelPoint",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class AvgTrainLoading:
        origin: int | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        destination: int | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        max: int | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )


@dataclass(frozen=True)
class ValueDocumentEticketPdfType(ValueDocumentTicketType):
    class Meta:
        name = "ValueDocumentETicketPdfType"
        target_namespace = "http://railgds.net/ws/commontypes"

    barcode_data: Optional["ValueDocumentEticketPdfType.BarcodeData"] = field(
        default=None,
        metadata={
            "name": "barcodeData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    bidirectional: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    format: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    bar_code_types: BarCodeTypes | None = field(
        default=None,
        metadata={
            "name": "barCodeTypes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    standard: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )

    @dataclass(frozen=True)
    class BarcodeData:
        value: bytes | None = field(
            default=None,
            metadata={
                "required": True,
                "format": "base64",
            },
        )
        type_value: str | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass(frozen=True)
class ValueDocumentEticketType(ValueDocumentTicketType):
    class Meta:
        name = "ValueDocumentETicketType"
        target_namespace = "http://railgds.net/ws/commontypes"

    bidirectional: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    format: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    date_of_birth: XmlDate | None = field(
        default=None,
        metadata={
            "name": "dateOfBirth",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    bar_code_types: BarCodeTypes | None = field(
        default=None,
        metadata={
            "name": "barCodeTypes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    standard: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class ValueDocumentMticketType(ValueDocumentTicketType):
    class Meta:
        name = "ValueDocumentMTicketType"
        target_namespace = "http://railgds.net/ws/commontypes"

    bidirectional: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    standard: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class AbstractPaymentRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    payment: Optional["AbstractPaymentRequestType.Payment"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Payment:
        form_of_payment: FormOfPaymentType | None = field(
            default=None,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card: AddPaymentCreditCardType | None = field(
            default=None,
            metadata={
                "name": "creditCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        check: CheckType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        on_account: OnAccountType | None = field(
            default=None,
            metadata={
                "name": "onAccount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        debit_card: AddPaymentDebitCardType | None = field(
            default=None,
            metadata={
                "name": "debitCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        voucher: list[AddPaymentVoucherType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        e_check: BaseEcheckType | None = field(
            default=None,
            metadata={
                "name": "eCheck",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        amount: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card_surcharge_fee: CreditCardSurchargeFeeType | None = field(
            default=None,
            metadata={
                "name": "creditCardSurchargeFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class AdjustCostAndRevenueRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    ticketable_fares: Optional["AdjustCostAndRevenueRequestType.TicketableFares"] = (
        field(
            default=None,
            metadata={
                "name": "ticketableFares",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
    )
    response_spec: Optional["AdjustCostAndRevenueRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class TicketableFares:
        ticketable_fare: list[AdjustCostAndRevenueTicketableFareType] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFare",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class AuthenticatePayerV2VersionRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    payment: Optional["AuthenticatePayerV2VersionRequestType.Payment"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Payment:
        form_of_payment: TokenPaymentType | None = field(
            default=None,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card: AuthenticatePayerV2CreditCardType | None = field(
            default=None,
            metadata={
                "name": "creditCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        debit_card: AuthenticatePayerV2DebitCardType | None = field(
            default=None,
            metadata={
                "name": "debitCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BaseReservationRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class CancelBookingRecordRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    ticketable_fare_locators: Optional[
        "CancelBookingRecordRequestType.TicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "ticketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    expected_cancellation_fee: MoneyType | None = field(
        default=None,
        metadata={
            "name": "expectedCancellationFee",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    parameters: Optional["CancelBookingRecordRequestType.Parameters"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["CancelBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    cancellation_reason: CancellationReasonType | None = field(
        default=None,
        metadata={
            "name": "cancellationReason",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_information: RefundInformationType | None = field(
        default=None,
        metadata={
            "name": "refundInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    selected_cancellation_option: SelectedCancellationOptionType | None = field(
        default=None,
        metadata={
            "name": "selectedCancellationOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    release_seat: bool | None = field(
        default=None,
        metadata={
            "name": "releaseSeat",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class TicketableFareLocators:
        ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Parameters:
        always_accept_cancellation_fee: bool | None = field(
            default=None,
            metadata={
                "name": "alwaysAcceptCancellationFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        void: bool | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        void_override: VoidOverrideType | None = field(
            default=None,
            metadata={
                "name": "voidOverride",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ClaimValueDocumentRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ClaimValueDocumentRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    barcode_type: str | None = field(
        default=None,
        metadata={
            "name": "barcodeType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        pdf_per_coupon: bool | None = field(
            default=None,
            metadata={
                "name": "pdfPerCoupon",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_eticket_pdf_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnETicketPdfDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class DelayRepayRefundRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    delay_repay_sets: Optional["DelayRepayRefundRequestType.DelayRepaySets"] = field(
        default=None,
        metadata={
            "name": "delayRepaySets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    refund_details: RefundDetailsType | None = field(
        default=None,
        metadata={
            "name": "refundDetails",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class DelayRepaySets:
        delay_repay_set: list[DelayRepaySetRequestType] = field(
            default_factory=list,
            metadata={
                "name": "delayRepaySet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class ExchangePassengersType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    passenger: list[PassengerType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ExchangePaymentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    form_of_payment: FormOfPaymentType | None = field(
        default=None,
        metadata={
            "name": "formOfPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    credit_card: AddPaymentCreditCardType | None = field(
        default=None,
        metadata={
            "name": "creditCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    check: CheckType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    on_account: OnAccountType | None = field(
        default=None,
        metadata={
            "name": "onAccount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    debit_card: AddPaymentDebitCardType | None = field(
        default=None,
        metadata={
            "name": "debitCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    voucher: AddPaymentVoucherType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    e_check: BaseEcheckType | None = field(
        default=None,
        metadata={
            "name": "eCheck",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    amount: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    credit_card_surcharge_fee: CreditCardSurchargeFeeType | None = field(
        default=None,
        metadata={
            "name": "creditCardSurchargeFee",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ExchangeSearchTravelPointPairType(TravelPointPairType):
    """:ivar carrier_restrictions: carrierRestrictions have been deprecated.

    They have been replaced by     ExchangeShoppingQuery.CarrierRestrictions.
    :ivar equipment_type_restrictions: :ivar routing_restrictions: :ivar
    minimum_connection_time: :ivar maximum_connection_time: :ivar
    maximum_permitted_connections: :ivar maximum_transit_time:
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    carrier_restrictions: Optional[
        "ExchangeSearchTravelPointPairType.CarrierRestrictions"
    ] = field(
        default=None,
        metadata={
            "name": "carrierRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    equipment_type_restrictions: Optional[
        "ExchangeSearchTravelPointPairType.EquipmentTypeRestrictions"
    ] = field(
        default=None,
        metadata={
            "name": "equipmentTypeRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    routing_restrictions: RoutingRestrictionsType | None = field(
        default=None,
        metadata={
            "name": "routingRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    minimum_connection_time: XmlDuration | None = field(
        default=None,
        metadata={
            "name": "minimumConnectionTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    maximum_connection_time: XmlDuration | None = field(
        default=None,
        metadata={
            "name": "maximumConnectionTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    maximum_permitted_connections: int | None = field(
        default=None,
        metadata={
            "name": "maximumPermittedConnections",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    maximum_transit_time: XmlDuration | None = field(
        default=None,
        metadata={
            "name": "maximumTransitTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class CarrierRestrictions:
        carrier_restriction: list[
            "ExchangeSearchTravelPointPairType.CarrierRestrictions.CarrierRestriction"
        ] = field(
            default_factory=list,
            metadata={
                "name": "carrierRestriction",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class CarrierRestriction:
            carrier: CarrierType | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            type_value: CarrierRestrictionType2 | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Attribute",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class EquipmentTypeRestrictions:
        equipment_type_restriction: list[
            "ExchangeSearchTravelPointPairType.EquipmentTypeRestrictions.EquipmentTypeRestriction"
        ] = field(
            default_factory=list,
            metadata={
                "name": "equipmentTypeRestriction",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class EquipmentTypeRestriction:
            equipment_type: EquipmentTypeType | None = field(
                default=None,
                metadata={
                    "name": "equipmentType",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            type_value: EquipmentTypeRestrictionType | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Attribute",
                    "required": True,
                },
            )


@dataclass(frozen=True)
class FulfillmentInformationType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    ticket_option: TicketingOptionType | None = field(
        default=None,
        metadata={
            "name": "ticketOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    shipping_name: str | None = field(
        default=None,
        metadata={
            "name": "shippingName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    shipping_address: AddressType | None = field(
        default=None,
        metadata={
            "name": "shippingAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    phone_number: FulfillmentPhoneNumberType | None = field(
        default=None,
        metadata={
            "name": "phoneNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    pickup_location: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "pickupLocation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    back_office_fulfillment_type: BackOfficeFulfillmentType | None = field(
        default=None,
        metadata={
            "name": "backOfficeFulfillmentType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class GeneratePaymentTokenRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    payment: Optional["GeneratePaymentTokenRequestType.Payment"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Payment:
        form_of_payment: TokenPaymentType | None = field(
            default=None,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card: AddPaymentCreditCardType | None = field(
            default=None,
            metadata={
                "name": "creditCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        debit_card: AddPaymentDebitCardType | None = field(
            default=None,
            metadata={
                "name": "debitCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        customer_ip_address: str | None = field(
            default=None,
            metadata={
                "name": "customerIpAddress",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class GetIntermediateTravelPointsResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    intermediate_travel_points_lists: Optional[
        "GetIntermediateTravelPointsResponseType.IntermediateTravelPointsLists"
    ] = field(
        default=None,
        metadata={
            "name": "intermediateTravelPointsLists",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class IntermediateTravelPointsLists:
        intermediate_travel_points_list: list[
            "GetIntermediateTravelPointsResponseType.IntermediateTravelPointsLists.IntermediateTravelPointsList"
        ] = field(
            default_factory=list,
            metadata={
                "name": "intermediateTravelPointsList",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class IntermediateTravelPointsList:
            travel_segment: TravelSegmentType | None = field(
                default=None,
                metadata={
                    "name": "travelSegment",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            intermediate_travel_points: Optional[
                "GetIntermediateTravelPointsResponseType.IntermediateTravelPointsLists.IntermediateTravelPointsList.IntermediateTravelPoints"
            ] = field(
                default=None,
                metadata={
                    "name": "intermediateTravelPoints",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

            @dataclass(frozen=True)
            class IntermediateTravelPoints:
                intermediate_travel_point: list[IntermediateTravelPoint] = field(
                    default_factory=list,
                    metadata={
                        "name": "intermediateTravelPoint",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "min_occurs": 1,
                    },
                )


@dataclass(frozen=True)
class RecordFinancialTransactionRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    refunds: Optional["RecordFinancialTransactionRequestType.Refunds"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["RecordFinancialTransactionRequestType.ResponseSpec"] = (
        field(
            default=None,
            metadata={
                "name": "responseSpec",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )

    @dataclass(frozen=True)
    class Refunds:
        refund: list["RecordFinancialTransactionRequestType.Refunds.Refund"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Refund:
            receipt_number: str | None = field(
                default=None,
                metadata={
                    "name": "receiptNumber",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            refund_amount: MoneyType | None = field(
                default=None,
                metadata={
                    "name": "refundAmount",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            refund_reason: str | None = field(
                default=None,
                metadata={
                    "name": "refundReason",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            payment_processor_info: PaymentProcessorInfoType | None = field(
                default=None,
                metadata={
                    "name": "paymentProcessorInfo",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class RedeliverValueDocumentRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    email_address: str | None = field(
        default=None,
        metadata={
            "name": "emailAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    phone_number: FulfillmentPhoneNumberType | None = field(
        default=None,
        metadata={
            "name": "phoneNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["RedeliverValueDocumentRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class RefundBookingRecordRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    response_spec: Optional["RefundBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    receipt_number: str | None = field(
        default=None,
        metadata={
            "name": "receiptNumber",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    refund_amount: MoneyType | None = field(
        default=None,
        metadata={
            "name": "refundAmount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    refund_reason: str | None = field(
        default=None,
        metadata={
            "name": "refundReason",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    external_payment: ExternalPaymentType | None = field(
        default=None,
        metadata={
            "name": "externalPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ReservationChangeSetType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    leg_grouping: OneOrTwoType | None = field(
        default=None,
        metadata={
            "name": "legGrouping",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    ticketable_fare_locators: Optional[
        "ReservationChangeSetType.TicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "ticketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    reservation_shopping_query: ReservationShoppingQueryType | None = field(
        default=None,
        metadata={
            "name": "reservationShoppingQuery",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    reservation_change_set_id: str | None = field(
        default=None,
        metadata={
            "name": "reservationChangeSetID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class TicketableFareLocators:
        ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class RetrieveCancellationSummaryResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    orders: Optional["RetrieveCancellationSummaryResponseType.Orders"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Orders:
        order: list["RetrieveCancellationSummaryResponseType.Orders.Order"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Order:
            cancellation_summary: CancellationSummaryType | None = field(
                default=None,
                metadata={
                    "name": "cancellationSummary",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            void_summary: VoidSummaryType | None = field(
                default=None,
                metadata={
                    "name": "voidSummary",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            order_id: object | None = field(
                default=None,
                metadata={
                    "name": "orderID",
                    "type": "Attribute",
                    "required": True,
                },
            )


@dataclass(frozen=True)
class ReturnValueDocumentRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    value_document_locator: str | None = field(
        default=None,
        metadata={
            "name": "valueDocumentLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    receive_coupons: Optional["ReturnValueDocumentRequestType.ReceiveCoupons"] = field(
        default=None,
        metadata={
            "name": "receiveCoupons",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    authorize_refund: Optional["ReturnValueDocumentRequestType.AuthorizeRefund"] = (
        field(
            default=None,
            metadata={
                "name": "authorizeRefund",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )
    force_cancel: str | None = field(
        default=None,
        metadata={
            "name": "forceCancel",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ReturnValueDocumentRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class ReceiveCoupons:
        coupons: Optional["ReturnValueDocumentRequestType.ReceiveCoupons.Coupons"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
        )
        return_type: ReceiveCouponsReturnType | None = field(
            default=None,
            metadata={
                "name": "returnType",
                "type": "Attribute",
                "required": True,
            },
        )

        @dataclass(frozen=True)
        class Coupons:
            coupon: list[
                "ReturnValueDocumentRequestType.ReceiveCoupons.Coupons.Coupon"
            ] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class Coupon(CouponTypeAbstract):
                unique_ticket_number: str | None = field(
                    default=None,
                    metadata={
                        "name": "uniqueTicketNumber",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                coupon_received_date: XmlDate | None = field(
                    default=None,
                    metadata={
                        "name": "couponReceivedDate",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "required": True,
                    },
                )
                origin: TravelPointType | None = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                destination: TravelPointType | None = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                type_value: CouponType | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                    },
                )

    @dataclass(frozen=True)
    class AuthorizeRefund:
        coupons: Optional["ReturnValueDocumentRequestType.AuthorizeRefund.Coupons"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
        )
        reverse_revenue: Optional[
            "ReturnValueDocumentRequestType.AuthorizeRefund.ReverseRevenue"
        ] = field(
            default=None,
            metadata={
                "name": "reverseRevenue",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        reverse_cost: Optional[
            "ReturnValueDocumentRequestType.AuthorizeRefund.ReverseCost"
        ] = field(
            default=None,
            metadata={
                "name": "reverseCost",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        cancellation_penalty: MoneyType | None = field(
            default=None,
            metadata={
                "name": "cancellationPenalty",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class Coupons:
            coupon: list[
                "ReturnValueDocumentRequestType.AuthorizeRefund.Coupons.Coupon"
            ] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class Coupon(CouponTypeAbstract):
                unique_ticket_number: str | None = field(
                    default=None,
                    metadata={
                        "name": "uniqueTicketNumber",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                refund_approved_date: XmlDate | None = field(
                    default=None,
                    metadata={
                        "name": "refundApprovedDate",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "required": True,
                    },
                )
                authorization: Optional[
                    "ReturnValueDocumentRequestType.AuthorizeRefund.Coupons.Coupon.Authorization"
                ] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "required": True,
                    },
                )

                @dataclass(frozen=True)
                class Authorization:
                    value: str = field(
                        default="",
                        metadata={
                            "required": True,
                        },
                    )
                    code: str | None = field(
                        default=None,
                        metadata={
                            "type": "Attribute",
                        },
                    )

        @dataclass(frozen=True)
        class ReverseRevenue:
            amount: MoneyType | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            description: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )

        @dataclass(frozen=True)
        class ReverseCost:
            amount: MoneyType | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            description: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )


@dataclass(frozen=True)
class SearchBookingsResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_records: Optional["SearchBookingsResponseType.BookingRecords"] = field(
        default=None,
        metadata={
            "name": "bookingRecords",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    total_pages: int | None = field(
        default=None,
        metadata={
            "name": "totalPages",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class BookingRecords:
        booking_record: list[
            "SearchBookingsResponseType.BookingRecords.BookingRecord"
        ] = field(
            default_factory=list,
            metadata={
                "name": "bookingRecord",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class BookingRecord:
            context: ContextType | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            passengers: Optional[
                "SearchBookingsResponseType.BookingRecords.BookingRecord.Passengers"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            departure_date: XmlDate | None = field(
                default=None,
                metadata={
                    "name": "departureDate",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            orders: Optional[
                "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            record_locator: object | None = field(
                default=None,
                metadata={
                    "name": "recordLocator",
                    "type": "Attribute",
                    "required": True,
                },
            )
            status: BookingRecordStatus | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )

            @dataclass(frozen=True)
            class Passengers:
                passenger: list[PassengerType] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class Orders:
                order: list[
                    "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order"
                ] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "min_occurs": 1,
                    },
                )

                @dataclass(frozen=True)
                class Order:
                    value_document_locator: str | None = field(
                        default=None,
                        metadata={
                            "name": "valueDocumentLocator",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                        },
                    )
                    date_booked: XmlDate | None = field(
                        default=None,
                        metadata={
                            "name": "dateBooked",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "required": True,
                        },
                    )
                    date_cancelled: XmlDateTime | None = field(
                        default=None,
                        metadata={
                            "name": "dateCancelled",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                        },
                    )
                    travel_segments: Optional[
                        "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TravelSegments"
                    ] = field(
                        default=None,
                        metadata={
                            "name": "travelSegments",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                        },
                    )
                    ticketable_fares: Optional[
                        "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TicketableFares"
                    ] = field(
                        default=None,
                        metadata={
                            "name": "ticketableFares",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "required": True,
                        },
                    )
                    order_id: str | None = field(
                        default=None,
                        metadata={
                            "name": "orderID",
                            "type": "Attribute",
                            "required": True,
                        },
                    )
                    status: OrderStatus | None = field(
                        default=None,
                        metadata={
                            "type": "Attribute",
                            "required": True,
                        },
                    )

                    @dataclass(frozen=True)
                    class TravelSegments:
                        travel_segment: list[TravelSegmentType] = field(
                            default_factory=list,
                            metadata={
                                "name": "travelSegment",
                                "type": "Element",
                                "namespace": "http://railgds.net/ws/booking",
                                "min_occurs": 1,
                            },
                        )

                    @dataclass(frozen=True)
                    class TicketableFares:
                        ticketable_fare: list[
                            "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TicketableFares.TicketableFare"
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "ticketableFare",
                                "type": "Element",
                                "namespace": "http://railgds.net/ws/booking",
                                "min_occurs": 1,
                            },
                        )

                        @dataclass(frozen=True)
                        class TicketableFare:  # noqa: WPS220
                            total_price: TotalPriceType | None = field(
                                default=None,
                                metadata={
                                    "name": "totalPrice",
                                    "type": "Element",
                                    "namespace": "http://railgds.net/ws/booking",
                                    "required": True,
                                },
                            )
                            passenger_references: Optional[
                                "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TicketableFares.TicketableFare.PassengerReferences"
                            ] = field(
                                default=None,
                                metadata={
                                    "name": "passengerReferences",
                                    "type": "Element",
                                    "namespace": "http://railgds.net/ws/booking",
                                    "required": True,
                                },
                            )
                            fare_origin: FareTerminalPointType | None = field(
                                default=None,
                                metadata={
                                    "name": "fareOrigin",
                                    "type": "Element",
                                    "namespace": "http://railgds.net/ws/booking",
                                },
                            )
                            fare_destination: FareTerminalPointType | None = field(
                                default=None,
                                metadata={
                                    "name": "fareDestination",
                                    "type": "Element",
                                    "namespace": "http://railgds.net/ws/booking",
                                },
                            )
                            ticketable_fare_id: str | None = field(
                                default=None,
                                metadata={
                                    "name": "ticketableFareID",
                                    "type": "Attribute",
                                },
                            )

                            @dataclass(frozen=True)
                            class PassengerReferences:  # noqa: WPS220
                                passenger_reference: list[
                                    "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TicketableFares.TicketableFare.PassengerReferences.PassengerReference"
                                ] = field(
                                    default_factory=list,
                                    metadata={
                                        "name": "passengerReference",
                                        "type": "Element",
                                        "namespace": "http://railgds.net/ws/booking",
                                        "min_occurs": 1,
                                    },
                                )

                                @dataclass(frozen=True)
                                class PassengerReference:  # noqa: WPS220
                                    passenger_idref: str | None = field(
                                        default=None,
                                        metadata={
                                            "name": "passengerIDRef",
                                            "type": "Element",
                                            "namespace": "http://railgds.net/ws/booking",
                                            "required": True,
                                        },
                                    )
                                    passenger_type_code: str | None = field(
                                        default=None,
                                        metadata={
                                            "name": "passengerTypeCode",
                                            "type": "Element",
                                            "namespace": "http://railgds.net/ws/booking",
                                            "required": True,
                                        },
                                    )
                                    fare_codes: Optional[
                                        "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TicketableFares.TicketableFare.PassengerReferences.PassengerReference.FareCodes"
                                    ] = field(
                                        default=None,
                                        metadata={
                                            "name": "fareCodes",
                                            "type": "Element",
                                            "namespace": "http://railgds.net/ws/booking",
                                            "required": True,
                                        },
                                    )
                                    ticket_identifier: Optional[
                                        "SearchBookingsResponseType.BookingRecords.BookingRecord.Orders.Order.TicketableFares.TicketableFare.PassengerReferences.PassengerReference.TicketIdentifier"
                                    ] = field(
                                        default=None,
                                        metadata={
                                            "name": "ticketIdentifier",
                                            "type": "Element",
                                            "namespace": "http://railgds.net/ws/booking",
                                        },
                                    )

                                    @dataclass(frozen=True)
                                    class FareCodes:  # noqa: WPS220
                                        fare_code: list[FareCodeType] = field(
                                            default_factory=list,
                                            metadata={
                                                "name": "fareCode",
                                                "type": "Element",
                                                "namespace": "http://railgds.net/ws/booking",
                                                "min_occurs": 1,
                                            },
                                        )

                                    @dataclass(frozen=True)
                                    class TicketIdentifier:  # noqa: WPS220
                                        type_value: str | None = field(
                                            default=None,
                                            metadata={
                                                "name": "type",
                                                "type": "Attribute",
                                            },
                                        )
                                        value: str | None = field(
                                            default=None,
                                            metadata={
                                                "type": "Attribute",
                                            },
                                        )


@dataclass(frozen=True)
class TravelPassExchangeSearchTravelPointPairType(TravelPointPairDateType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    carrier_restrictions: CarrierRestrictionsType1 | None = field(
        default=None,
        metadata={
            "name": "carrierRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    routing_restrictions: RoutingRestrictionsType | None = field(
        default=None,
        metadata={
            "name": "routingRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ValidateDelayRepayRefundStatusRequestType(BaseBookingRequestType):
    """ValidateDelayRepayRefundStatusRequestType is functionality under development and
    subject to change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    delay_repay_sets: Optional[
        "ValidateDelayRepayRefundStatusRequestType.DelayRepaySets"
    ] = field(
        default=None,
        metadata={
            "name": "delayRepaySets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    parameters: ParametersValidateDelayRepayRefundStatusRequestType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class DelayRepaySets:
        delay_repay_set: list[DelayRepaySetRequestType] = field(
            default_factory=list,
            metadata={
                "name": "delayRepaySet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class ValidateDelayRepayRefundStatusResponseType(BaseResponseType):
    """ValidateDelayRepayRefundStatusResponseType is functionality under development
    and subject to change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    delay_refund: DelayRefundType | None = field(
        default=None,
        metadata={
            "name": "delayRefund",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class AuthenticatePayerResponse(AuthenticatePayerResponseType):
    class Meta:
        name = "authenticatePayerResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerV2ChallengeRequest(AuthenticatePayerV2ChallengeRequestType):
    class Meta:
        name = "authenticatePayerV2ChallengeRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerV2ChallengeResponse(AuthenticatePayerV2ChallengeResponseType):
    class Meta:
        name = "authenticatePayerV2ChallengeResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerV2Response(AuthenticatePayerV2ResponseType):
    class Meta:
        name = "authenticatePayerV2Response"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerV2VersionResponse(AuthenticatePayerV2VersionResponseType):
    class Meta:
        name = "authenticatePayerV2VersionResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DelayRepayRefundResponse(DelayRepayRefundResponseType):
    class Meta:
        name = "delayRepayRefundResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DeleteCardholderInfoRequest(DeleteCardholderInfoRequestType):
    class Meta:
        name = "deleteCardholderInfoRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DeleteCardholderInfoResponse(DeleteCardholderInfoResponseType):
    class Meta:
        name = "deleteCardholderInfoResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DeletePaymentTokenRequest(DeletePaymentTokenRequestType):
    class Meta:
        name = "deletePaymentTokenRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DeletePaymentTokenResponse(DeletePaymentTokenResponseType):
    class Meta:
        name = "deletePaymentTokenResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class GeneratePaymentTokenResponse(GeneratePaymentTokenResponseType):
    class Meta:
        name = "generatePaymentTokenResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveBookingRecordRequest(RetrieveBookingRecordRequestType):
    class Meta:
        name = "retrieveBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveCancellationSummaryRequest(RetrieveCancellationSummaryRequestType):
    class Meta:
        name = "retrieveCancellationSummaryRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class SearchBookingsRequest(SearchBookingsRequestType):
    class Meta:
        name = "searchBookingsRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class LegSolutionType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    number_of_connections: int | None = field(
        default=None,
        metadata={
            "name": "numberOfConnections",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    service_alerts: Optional["LegSolutionType.ServiceAlerts"] = field(
        default=None,
        metadata={
            "name": "serviceAlerts",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    travel_segments: Optional["LegSolutionType.TravelSegments"] = field(
        default=None,
        metadata={
            "name": "travelSegments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    sub_segments: Optional["LegSolutionType.SubSegments"] = field(
        default=None,
        metadata={
            "name": "subSegments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    overtaken_journey: bool | None = field(
        default=None,
        metadata={
            "name": "overtakenJourney",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    duration: XmlDuration | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    carbon_data_comparison: CarbonDataComparisonType | None = field(
        default=None,
        metadata={
            "name": "carbonDataComparison",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    routing_restrictions: RoutingRestrictionsType | None = field(
        default=None,
        metadata={
            "name": "routingRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    passenger_information_required: Optional[
        "LegSolutionType.PassengerInformationRequired"
    ] = field(
        default=None,
        metadata={
            "name": "passengerInformationRequired",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    available_seat_preferences: Optional["LegSolutionType.AvailableSeatPreferences"] = (
        field(
            default=None,
            metadata={
                "name": "availableSeatPreferences",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    loyalty_cards: Optional["LegSolutionType.LoyaltyCards"] = field(
        default=None,
        metadata={
            "name": "loyaltyCards",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    is_not_bookable: Optional["LegSolutionType.IsNotBookable"] = field(
        default=None,
        metadata={
            "name": "isNotBookable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    revisions: Optional["LegSolutionType.Revisions"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    leg_solution_id: str | None = field(
        default=None,
        metadata={
            "name": "legSolutionID",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ServiceAlerts:
        service_alert: list[ServiceAlertType] = field(
            default_factory=list,
            metadata={
                "name": "serviceAlert",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class TravelSegments:
        travel_segment: list[TravelSegmentType] = field(
            default_factory=list,
            metadata={
                "name": "travelSegment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class SubSegments:
        sub_segment: list[SubSegmentType] = field(
            default_factory=list,
            metadata={
                "name": "subSegment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class PassengerInformationRequired:
        passenger_information: list[PassengerInformationType] = field(
            default_factory=list,
            metadata={
                "name": "passengerInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class AvailableSeatPreferences:
        available_seat_preference: list[AvailableSeatPreferenceType] = field(
            default_factory=list,
            metadata={
                "name": "availableSeatPreference",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class LoyaltyCards:
        loyalty_card: list[LoyaltyCardType] = field(
            default_factory=list,
            metadata={
                "name": "loyaltyCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class IsNotBookable:
        reason: IsNotBookableReason | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class Revisions:
        revision: list[RevisionType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PassTicketableFareType:
    """:ivar total_price:

    :ivar passenger_references: :ivar prices: :ivar optional_prices: :ivar
    costs: :ivar commissions: :ivar commission_amount: :ivar rules: :ivar
    fare_qualifiers: :ivar cancel_eligibility: :ivar cancel_fee: :ivar
    ticketing_options_available: :ivar fare_origin: :ivar fare_origin_terminals:
    :ivar fare_destination: :ivar fare_destination_terminals: :ivar
    fare_start_date: :ivar fare_expiration_date: :ivar fare_days_of_travel:
    :ivar ticketable_fare_id: This attribute should be required but it     will
    remain optional for backwards compatibility.
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    total_price: TotalPriceType | None = field(
        default=None,
        metadata={
            "name": "totalPrice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    passenger_references: Optional["PassTicketableFareType.PassengerReferences"] = (
        field(
            default=None,
            metadata={
                "name": "passengerReferences",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
    )
    prices: Optional["PassTicketableFareType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    optional_prices: Optional["PassTicketableFareType.OptionalPrices"] = field(
        default=None,
        metadata={
            "name": "optionalPrices",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    costs: Optional["PassTicketableFareType.Costs"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    commissions: Optional["PassTicketableFareType.Commissions"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    commission_amount: MoneyType | None = field(
        default=None,
        metadata={
            "name": "commissionAmount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    rules: RulesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_qualifiers: Optional["PassTicketableFareType.FareQualifiers"] = field(
        default=None,
        metadata={
            "name": "fareQualifiers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cancel_eligibility: bool | None = field(
        default=None,
        metadata={
            "name": "cancelEligibility",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cancel_fee: MoneyType | None = field(
        default=None,
        metadata={
            "name": "cancelFee",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketing_options_available: Optional[
        "PassTicketableFareType.TicketingOptionsAvailable"
    ] = field(
        default=None,
        metadata={
            "name": "ticketingOptionsAvailable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_origin: FareTerminalPointType | None = field(
        default=None,
        metadata={
            "name": "fareOrigin",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_origin_terminals: Optional["PassTicketableFareType.FareOriginTerminals"] = (
        field(
            default=None,
            metadata={
                "name": "fareOriginTerminals",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    fare_destination: FareTerminalPointType | None = field(
        default=None,
        metadata={
            "name": "fareDestination",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_destination_terminals: Optional[
        "PassTicketableFareType.FareDestinationTerminals"
    ] = field(
        default=None,
        metadata={
            "name": "fareDestinationTerminals",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_start_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "fareStartDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_expiration_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "fareExpirationDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_days_of_travel: int | None = field(
        default=None,
        metadata={
            "name": "fareDaysOfTravel",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketable_fare_id: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class PassengerReferences:
        passenger_reference: list[
            "PassTicketableFareType.PassengerReferences.PassengerReference"
        ] = field(
            default_factory=list,
            metadata={
                "name": "passengerReference",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class PassengerReference:
            passenger_idref: str | None = field(
                default=None,
                metadata={
                    "name": "passengerIDRef",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
            passenger_type_code: str | None = field(
                default=None,
                metadata={
                    "name": "passengerTypeCode",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
            fare_codes: Optional[
                "PassTicketableFareType.PassengerReferences.PassengerReference.FareCodes"
            ] = field(
                default=None,
                metadata={
                    "name": "fareCodes",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
            fare_qualifier_idref: str | None = field(
                default=None,
                metadata={
                    "name": "fareQualifierIDRef",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )

            @dataclass(frozen=True)
            class FareCodes:
                fare_code: list[PassFareCodeType] = field(
                    default_factory=list,
                    metadata={
                        "name": "fareCode",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

    @dataclass(frozen=True)
    class Prices:
        price: list[PriceType1] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class OptionalPrices:
        optional_price: list[OptionalPriceType] = field(
            default_factory=list,
            metadata={
                "name": "optionalPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Costs:
        cost: list[CostType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Commissions:
        commission: list[CommissionType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class FareQualifiers:
        fare_qualifier: list[FareQualifierType] = field(
            default_factory=list,
            metadata={
                "name": "fareQualifier",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class TicketingOptionsAvailable:
        tod: bool | None = field(
            default=None,
            metadata={
                "name": "TOD",
                "type": "Attribute",
                "required": True,
            },
        )
        etk: bool | None = field(
            default=None,
            metadata={
                "name": "ETK",
                "type": "Attribute",
                "required": True,
            },
        )
        pah: bool | None = field(
            default=None,
            metadata={
                "name": "PAH",
                "type": "Attribute",
                "required": True,
            },
        )
        prn: bool | None = field(
            default=None,
            metadata={
                "name": "PRN",
                "type": "Attribute",
            },
        )
        eml: bool | None = field(
            default=None,
            metadata={
                "name": "EML",
                "type": "Attribute",
            },
        )
        departure_station_tod: bool | None = field(
            default=None,
            metadata={
                "name": "DEPARTURE_STATION_TOD",
                "type": "Attribute",
                "required": True,
            },
        )
        sms: bool | None = field(
            default=None,
            metadata={
                "name": "SMS",
                "type": "Attribute",
            },
        )
        xvd: bool | None = field(
            default=None,
            metadata={
                "name": "XVD",
                "type": "Attribute",
            },
        )
        mvd: bool | None = field(
            default=None,
            metadata={
                "name": "MVD",
                "type": "Attribute",
            },
        )
        sct: bool | None = field(
            default=None,
            metadata={
                "name": "SCT",
                "type": "Attribute",
            },
        )
        mtd: bool | None = field(
            default=None,
            metadata={
                "name": "MTD",
                "type": "Attribute",
            },
        )

    @dataclass(frozen=True)
    class FareOriginTerminals:
        fare_origin_terminal: list[FareTerminalPointType] = field(
            default_factory=list,
            metadata={
                "name": "fareOriginTerminal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class FareDestinationTerminals:
        fare_destination_terminal: list[FareTerminalPointType] = field(
            default_factory=list,
            metadata={
                "name": "fareDestinationTerminal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PaymentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    form_of_payment: FormOfPaymentType | None = field(
        default=None,
        metadata={
            "name": "formOfPayment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    credit_card: CreditCardType | None = field(
        default=None,
        metadata={
            "name": "creditCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    check: CheckType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    on_account: OnAccountType | None = field(
        default=None,
        metadata={
            "name": "onAccount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    debit_card: DebitCardType | None = field(
        default=None,
        metadata={
            "name": "debitCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    voucher: VoucherType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    e_check: EcheckType | None = field(
        default=None,
        metadata={
            "name": "eCheck",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    amount: MoneyType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    type_value: PaymentTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class QueryTravelPointPairPassType(TravelPointPairDateType):
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    carrier_restrictions: CarrierRestrictionsType1 | None = field(
        default=None,
        metadata={
            "name": "carrierRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    routing_restrictions: RoutingRestrictionsType | None = field(
        default=None,
        metadata={
            "name": "routingRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class TicketableFareType:
    """:ivar total_price:

    :ivar passenger_references:
    :ivar campaign:
    :ivar prices:
    :ivar supplements:
    :ivar optional_prices:
    :ivar costs:
    :ivar commissions:
    :ivar commission_amount:
    :ivar rules:
    :ivar fare_qualifiers:
    :ivar cancel_eligibility:
    :ivar cancel_fee:
    :ivar ticketing_options_available:
    :ivar fare_origin:
    :ivar fare_origin_terminals:
    :ivar fare_destination:
    :ivar fare_destination_terminals:
    :ivar seats_available:
    :ivar passenger_information_required_overrides:
    :ivar marketing_carrier_ref:
    :ivar travel_passes:
    :ivar outward_fare_expiration_date:
    :ivar return_fare_expiration_date:
    :ivar expiration_additional_time:
    :ivar fare_days_of_travel:
    :ivar warnings:
    :ivar ticketable_fare_id: This attribute should be required but it
        will remain optional for backwards compatibility.
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    total_price: TotalPriceType | None = field(
        default=None,
        metadata={
            "name": "totalPrice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    passenger_references: Optional["TicketableFareType.PassengerReferences"] = field(
        default=None,
        metadata={
            "name": "passengerReferences",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    campaign: CampaignFareType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    prices: Optional["TicketableFareType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    supplements: Optional["TicketableFareType.Supplements"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    optional_prices: Optional["TicketableFareType.OptionalPrices"] = field(
        default=None,
        metadata={
            "name": "optionalPrices",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    costs: Optional["TicketableFareType.Costs"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    commissions: Optional["TicketableFareType.Commissions"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    commission_amount: MoneyType | None = field(
        default=None,
        metadata={
            "name": "commissionAmount",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    rules: RulesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_qualifiers: Optional["TicketableFareType.FareQualifiers"] = field(
        default=None,
        metadata={
            "name": "fareQualifiers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cancel_eligibility: bool | None = field(
        default=None,
        metadata={
            "name": "cancelEligibility",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    cancel_fee: MoneyType | None = field(
        default=None,
        metadata={
            "name": "cancelFee",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketing_options_available: Optional[
        "TicketableFareType.TicketingOptionsAvailable"
    ] = field(
        default=None,
        metadata={
            "name": "ticketingOptionsAvailable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_origin: FareTerminalPointType | None = field(
        default=None,
        metadata={
            "name": "fareOrigin",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_origin_terminals: Optional["TicketableFareType.FareOriginTerminals"] = field(
        default=None,
        metadata={
            "name": "fareOriginTerminals",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_destination: FareTerminalPointType | None = field(
        default=None,
        metadata={
            "name": "fareDestination",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_destination_terminals: Optional[
        "TicketableFareType.FareDestinationTerminals"
    ] = field(
        default=None,
        metadata={
            "name": "fareDestinationTerminals",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    seats_available: int | None = field(
        default=None,
        metadata={
            "name": "seatsAvailable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    passenger_information_required_overrides: Optional[
        "TicketableFareType.PassengerInformationRequiredOverrides"
    ] = field(
        default=None,
        metadata={
            "name": "passengerInformationRequiredOverrides",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    marketing_carrier_ref: str | None = field(
        default=None,
        metadata={
            "name": "marketingCarrierRef",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    travel_passes: Optional["TicketableFareType.TravelPasses"] = field(
        default=None,
        metadata={
            "name": "travelPasses",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    outward_fare_expiration_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "outwardFareExpirationDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    return_fare_expiration_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "returnFareExpirationDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    expiration_additional_time: str | None = field(
        default=None,
        metadata={
            "name": "expirationAdditionalTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_days_of_travel: int | None = field(
        default=None,
        metadata={
            "name": "fareDaysOfTravel",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    warnings: WarningsType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketable_fare_id: str | None = field(
        default=None,
        metadata={
            "name": "ticketableFareID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class PassengerReferences:
        passenger_reference: list[
            "TicketableFareType.PassengerReferences.PassengerReference"
        ] = field(
            default_factory=list,
            metadata={
                "name": "passengerReference",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class PassengerReference:
            """:ivar passenger_idref:

            :ivar passenger_type_code: :ivar fare_codes: :ivar
            passenger_fare_qualifiers: passengerFareQualifiers     have been
            deprecated. They have been replaced by     loyaltyCards. :ivar
            fare_qualifier_idref:
            """

            passenger_idref: str | None = field(
                default=None,
                metadata={
                    "name": "passengerIDRef",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
            passenger_type_code: str | None = field(
                default=None,
                metadata={
                    "name": "passengerTypeCode",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
            fare_codes: Optional[
                "TicketableFareType.PassengerReferences.PassengerReference.FareCodes"
            ] = field(
                default=None,
                metadata={
                    "name": "fareCodes",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "required": True,
                },
            )
            passenger_fare_qualifiers: Optional[
                "TicketableFareType.PassengerReferences.PassengerReference.PassengerFareQualifiers"
            ] = field(
                default=None,
                metadata={
                    "name": "passengerFareQualifiers",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            fare_qualifier_idref: str | None = field(
                default=None,
                metadata={
                    "name": "fareQualifierIDRef",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )

            @dataclass(frozen=True)
            class FareCodes:
                fare_code: list[FareCodeType] = field(
                    default_factory=list,
                    metadata={
                        "name": "fareCode",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class PassengerFareQualifiers:
                passenger_fare_qualifier: list[PassengerFareQualifierType] = field(
                    default_factory=list,
                    metadata={
                        "name": "passengerFareQualifier",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

    @dataclass(frozen=True)
    class Prices:
        price: list[PriceType1] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Supplements:
        supplement: list[SupplementType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class OptionalPrices:
        optional_price: list[OptionalPriceType] = field(
            default_factory=list,
            metadata={
                "name": "optionalPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Costs:
        cost: list[CostType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Commissions:
        commission: list[CommissionType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class FareQualifiers:
        fare_qualifier: list[FareQualifierType] = field(
            default_factory=list,
            metadata={
                "name": "fareQualifier",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class TicketingOptionsAvailable:
        tod: bool | None = field(
            default=None,
            metadata={
                "name": "TOD",
                "type": "Attribute",
                "required": True,
            },
        )
        etk: bool | None = field(
            default=None,
            metadata={
                "name": "ETK",
                "type": "Attribute",
                "required": True,
            },
        )
        pah: bool | None = field(
            default=None,
            metadata={
                "name": "PAH",
                "type": "Attribute",
                "required": True,
            },
        )
        prn: bool | None = field(
            default=None,
            metadata={
                "name": "PRN",
                "type": "Attribute",
            },
        )
        eml: bool | None = field(
            default=None,
            metadata={
                "name": "EML",
                "type": "Attribute",
            },
        )
        departure_station_tod: bool | None = field(
            default=None,
            metadata={
                "name": "DEPARTURE_STATION_TOD",
                "type": "Attribute",
                "required": True,
            },
        )
        sms: bool | None = field(
            default=None,
            metadata={
                "name": "SMS",
                "type": "Attribute",
            },
        )
        xvd: bool | None = field(
            default=None,
            metadata={
                "name": "XVD",
                "type": "Attribute",
            },
        )
        sct: bool | None = field(
            default=None,
            metadata={
                "name": "SCT",
                "type": "Attribute",
            },
        )
        mtd: bool | None = field(
            default=None,
            metadata={
                "name": "MTD",
                "type": "Attribute",
            },
        )
        mvd: bool | None = field(
            default=None,
            metadata={
                "name": "MVD",
                "type": "Attribute",
            },
        )

    @dataclass(frozen=True)
    class FareOriginTerminals:
        fare_origin_terminal: list[FareTerminalPointType] = field(
            default_factory=list,
            metadata={
                "name": "fareOriginTerminal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class FareDestinationTerminals:
        fare_destination_terminal: list[FareTerminalPointType] = field(
            default_factory=list,
            metadata={
                "name": "fareDestinationTerminal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class PassengerInformationRequiredOverrides:
        passenger_information: list[PassengerInformationType] = field(
            default_factory=list,
            metadata={
                "name": "passengerInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class TravelPasses:
        travel_pass: list[TravelPassType] = field(
            default_factory=list,
            metadata={
                "name": "travelPass",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class ValueDocumentType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    value_document_locator: str | None = field(
        default=None,
        metadata={
            "name": "valueDocumentLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    retrieval_customer: str | None = field(
        default=None,
        metadata={
            "name": "retrievalCustomer",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    retrieval_masked_credit_card: str | None = field(
        default=None,
        metadata={
            "name": "retrievalMaskedCreditCard",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    retrieval_code: str | None = field(
        default=None,
        metadata={
            "name": "retrievalCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    coupons: Optional["ValueDocumentType.Coupons"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    url: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    urls: Optional["ValueDocumentType.Urls"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    selected_ticket_language: str | None = field(
        default=None,
        metadata={
            "name": "selectedTicketLanguage",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    issued_location: str | None = field(
        default=None,
        metadata={
            "name": "issuedLocation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    issued_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "issuedDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    data: Optional["ValueDocumentType.Data"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    e_tickets: Optional["ValueDocumentType.ETickets"] = field(
        default=None,
        metadata={
            "name": "eTickets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    m_tickets: Optional["ValueDocumentType.MTickets"] = field(
        default=None,
        metadata={
            "name": "mTickets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    e_ticket_pdfs: Optional["ValueDocumentType.ETicketPdfs"] = field(
        default=None,
        metadata={
            "name": "eTicketPdfs",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    status: ValueDocumentTypeStatus | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Coupons:
        coupon: list[ValueDocumentCouponType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Urls:
        url: list[str] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Data:
        value: bytes | None = field(
            default=None,
            metadata={
                "required": True,
                "format": "base64",
            },
        )
        type_value: str | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class ETickets:
        e_ticket: list[ValueDocumentEticketType] = field(
            default_factory=list,
            metadata={
                "name": "eTicket",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class MTickets:
        m_ticket: list[ValueDocumentMticketType] = field(
            default_factory=list,
            metadata={
                "name": "mTicket",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ETicketPdfs:
        e_ticket_pdf: list[ValueDocumentEticketPdfType] = field(
            default_factory=list,
            metadata={
                "name": "eTicketPdf",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class AddPaymentRequestType(AbstractPaymentRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    parameters: Optional["AddPaymentRequestType.Parameters"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    confirmation_information: ConfirmationInformationType | None = field(
        default=None,
        metadata={
            "name": "confirmationInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["AddPaymentRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    customer_ip_address: str | None = field(
        default=None,
        metadata={
            "name": "customerIpAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    three_dee_authenticate_payer: Optional[
        "AddPaymentRequestType.ThreeDeeAuthenticatePayer"
    ] = field(
        default=None,
        metadata={
            "name": "threeDeeAuthenticatePayer",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    three_dee_authenticate_payer_v2: Optional[
        "AddPaymentRequestType.ThreeDeeAuthenticatePayerV2"
    ] = field(
        default=None,
        metadata={
            "name": "threeDeeAuthenticatePayerV2",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Parameters:
        confirm_booking: bool | None = field(
            default=None,
            metadata={
                "name": "confirmBooking",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class ThreeDeeAuthenticatePayer:
        payer_authentication_response: str | None = field(
            default=None,
            metadata={
                "name": "payerAuthenticationResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class ThreeDeeAuthenticatePayerV2:
        ds_trans_id: str | None = field(
            default=None,
            metadata={
                "name": "dsTransId",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        authentication_value: str | None = field(
            default=None,
            metadata={
                "name": "authenticationValue",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        eci: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class AuthenticatePayerRequestType(AbstractPaymentRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    customer_ip_address: str | None = field(
        default=None,
        metadata={
            "name": "customerIpAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["AuthenticatePayerRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class AuthenticatePayerV2RequestType(AbstractPaymentRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    customer_ip_address: str | None = field(
        default=None,
        metadata={
            "name": "customerIpAddress",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    authentication_source: str | None = field(
        default=None,
        metadata={
            "name": "authenticationSource",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    customer_name: str | None = field(
        default=None,
        metadata={
            "name": "customerName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    customer_email: str | None = field(
        default=None,
        metadata={
            "name": "customerEmail",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    customer_phone: FulfillmentPhoneNumberType | None = field(
        default=None,
        metadata={
            "name": "customerPhone",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    browser_session_information: Optional[
        "AuthenticatePayerV2RequestType.BrowserSessionInformation"
    ] = field(
        default=None,
        metadata={
            "name": "browserSessionInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    api_customer_app_information: Optional[
        "AuthenticatePayerV2RequestType.ApiCustomerAppInformation"
    ] = field(
        default=None,
        metadata={
            "name": "apiCustomerAppInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class BrowserSessionInformation:
        accept_header: str | None = field(
            default=None,
            metadata={
                "name": "acceptHeader",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        color_depth: AuthenticatePayerV2BrowserColorDepthType | None = field(
            default=None,
            metadata={
                "name": "colorDepth",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        ip_address: str | None = field(
            default=None,
            metadata={
                "name": "ipAddress",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        java_enabled: bool | None = field(
            default=None,
            metadata={
                "name": "javaEnabled",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        java_script_enabled: bool | None = field(
            default=None,
            metadata={
                "name": "javaScriptEnabled",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        language: str | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        screen_height: str | None = field(
            default=None,
            metadata={
                "name": "screenHeight",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        screen_width: str | None = field(
            default=None,
            metadata={
                "name": "screenWidth",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        challenge_window_size: (
            AuthenticatePayerV2BrowserChallengeWindowSizeType | None
        ) = field(
            default=None,
            metadata={
                "name": "challengeWindowSize",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        local_time: str | None = field(
            default=None,
            metadata={
                "name": "localTime",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        user_agent: str | None = field(
            default=None,
            metadata={
                "name": "userAgent",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class ApiCustomerAppInformation:
        merchant_contact_url: str | None = field(
            default=None,
            metadata={
                "name": "merchantContactUrl",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )


@dataclass(frozen=True)
class BookingAuthenticatePayerRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_response: AuthenticatePayerResponse | None = field(
            default=None,
            metadata={
                "name": "authenticatePayerResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingAuthenticatePayerRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingAuthenticatePayerRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingAuthenticatePayerV2ChallengeRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerV2ChallengeRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_v2_challenge_request: (
            AuthenticatePayerV2ChallengeRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "authenticatePayerV2ChallengeRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingAuthenticatePayerV2ChallengeRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerV2ChallengeRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_v2_challenge_response: (
            AuthenticatePayerV2ChallengeResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "authenticatePayerV2ChallengeResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional[
            "BookingAuthenticatePayerV2ChallengeRequestOutput.Body.Fault"
        ] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingAuthenticatePayerV2ChallengeRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingAuthenticatePayerV2RequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerV2RequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_v2_response: AuthenticatePayerV2Response | None = field(
            default=None,
            metadata={
                "name": "authenticatePayerV2Response",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingAuthenticatePayerV2RequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingAuthenticatePayerV2RequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingAuthenticatePayerV2VersionOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerV2VersionOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_v2_version_response: (
            AuthenticatePayerV2VersionResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "authenticatePayerV2VersionResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingAuthenticatePayerV2VersionOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingAuthenticatePayerV2VersionOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingDelayRepayRefundOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingDelayRepayRefundOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        delay_repay_refund_response: DelayRepayRefundResponse | None = field(
            default=None,
            metadata={
                "name": "delayRepayRefundResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingDelayRepayRefundOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingDelayRepayRefundOutput.Body.Fault.Detail"] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingDeleteCardholderInfoInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingDeleteCardholderInfoInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        delete_cardholder_info_request: DeleteCardholderInfoRequest | None = field(
            default=None,
            metadata={
                "name": "deleteCardholderInfoRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingDeleteCardholderInfoOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingDeleteCardholderInfoOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        delete_cardholder_info_response: DeleteCardholderInfoResponse | None = field(
            default=None,
            metadata={
                "name": "deleteCardholderInfoResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingDeleteCardholderInfoOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingDeleteCardholderInfoOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingDeletePaymentTokenRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingDeletePaymentTokenRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        delete_payment_token_request: DeletePaymentTokenRequest | None = field(
            default=None,
            metadata={
                "name": "deletePaymentTokenRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingDeletePaymentTokenRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingDeletePaymentTokenRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        delete_payment_token_response: DeletePaymentTokenResponse | None = field(
            default=None,
            metadata={
                "name": "deletePaymentTokenResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingDeletePaymentTokenRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingDeletePaymentTokenRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingGeneratePaymentTokenRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingGeneratePaymentTokenRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        generate_payment_token_response: GeneratePaymentTokenResponse | None = field(
            default=None,
            metadata={
                "name": "generatePaymentTokenResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingGeneratePaymentTokenRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingGeneratePaymentTokenRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRetrieveBookingRecordRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveBookingRecordRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_booking_record_request: RetrieveBookingRecordRequest | None = field(
            default=None,
            metadata={
                "name": "retrieveBookingRecordRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingRetrieveCancellationSummaryRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveCancellationSummaryRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_cancellation_summary_request: (
            RetrieveCancellationSummaryRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "retrieveCancellationSummaryRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingSearchBookingsRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingSearchBookingsRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        search_bookings_request: SearchBookingsRequest | None = field(
            default=None,
            metadata={
                "name": "searchBookingsRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class CancelReservationRequestType(BaseReservationRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    reservation_type: ReservationTypeEnum | None = field(
        default=None,
        metadata={
            "name": "reservationType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    leg_grouping: OneOrTwoType | None = field(
        default=None,
        metadata={
            "name": "legGrouping",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    ticketable_fares: list[TicketableFareLocatorsType] = field(
        default_factory=list,
        metadata={
            "name": "ticketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class ClaimValueDocumentResultType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    result: RequestStatusType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    claim_value_document_url: str | None = field(
        default=None,
        metadata={
            "name": "claimValueDocumentUrl",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    value_document: ValueDocumentType | None = field(
        default=None,
        metadata={
            "name": "valueDocument",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ConfirmBookingRecordRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    confirmation_information: ConfirmationInformationType | None = field(
        default=None,
        metadata={
            "name": "confirmationInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ConfirmBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    return_claim_value_document: bool | None = field(
        default=None,
        metadata={
            "name": "returnClaimValueDocument",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ExchangeShoppingQuery:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    travel_point_pairs: Optional["ExchangeShoppingQuery.TravelPointPairs"] = field(
        default=None,
        metadata={
            "name": "travelPointPairs",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    carrier_restrictions: Optional["ExchangeShoppingQuery.CarrierRestrictions"] = field(
        default=None,
        metadata={
            "name": "carrierRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fare_qualifiers: Optional["ExchangeShoppingQuery.FareQualifiers"] = field(
        default=None,
        metadata={
            "name": "fareQualifiers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fare_filter: ExchangeShoppingQueryFareFilter | None = field(
        default=None,
        metadata={
            "name": "fareFilter",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class TravelPointPairs:
        travel_point_pair: list[ExchangeSearchTravelPointPairType] = field(
            default_factory=list,
            metadata={
                "name": "travelPointPair",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class CarrierRestrictions:
        carrier_restriction: list[
            "ExchangeShoppingQuery.CarrierRestrictions.CarrierRestriction"
        ] = field(
            default_factory=list,
            metadata={
                "name": "carrierRestriction",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )
        type_value: CarrierRestrictionsType2 | None = field(
            default=None,
            metadata={
                "name": "type",
                "type": "Attribute",
                "required": True,
            },
        )

        @dataclass(frozen=True)
        class CarrierRestriction:
            code: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class FareQualifiers:
        fare_qualifier: list[FareQualifierType] = field(
            default_factory=list,
            metadata={
                "name": "fareQualifier",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class IntermediateTravelPointsQueryType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    order: Optional["IntermediateTravelPointsQueryType.Order"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    leg_solution: LegSolutionType | None = field(
        default=None,
        metadata={
            "name": "legSolution",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Order:
        record_locator: str | None = field(
            default=None,
            metadata={
                "name": "recordLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        order_locator: str | None = field(
            default=None,
            metadata={
                "name": "orderLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )


@dataclass(frozen=True)
class ProcessReservationRequestType(BaseReservationRequestType):
    """ProcessReservationRequestType is functionality under development and subject to
    change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    ticketable_fares: Optional["ProcessReservationRequestType.TicketableFares"] = field(
        default=None,
        metadata={
            "name": "ticketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    travel_segments: Optional["ProcessReservationRequestType.TravelSegments"] = field(
        default=None,
        metadata={
            "name": "travelSegments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    payment: Optional["ProcessReservationRequestType.Payment"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ProcessReservationRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class TicketableFares:
        ticketable_fare: list[ReservationTicketableFare] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFare",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class TravelSegments:
        travel_segment: list[TravelSegmentType] = field(
            default_factory=list,
            metadata={
                "name": "travelSegment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Payment:
        form_of_payment: FormOfPaymentType | None = field(
            default=None,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card: AddPaymentCreditCardType | None = field(
            default=None,
            metadata={
                "name": "creditCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        check: CheckType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        on_account: OnAccountType | None = field(
            default=None,
            metadata={
                "name": "onAccount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        debit_card: AddPaymentDebitCardType | None = field(
            default=None,
            metadata={
                "name": "debitCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        voucher: AddPaymentVoucherType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        e_check: BaseEcheckType | None = field(
            default=None,
            metadata={
                "name": "eCheck",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        amount: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card_surcharge_fee: CreditCardSurchargeFeeType | None = field(
            default=None,
            metadata={
                "name": "creditCardSurchargeFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ReservationShoppingRequestType(BaseReservationRequestType):
    """ReservationShoppingRequestType is functionality under development and subject to
    change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    reservation_change_sets: Optional[
        "ReservationShoppingRequestType.ReservationChangeSets"
    ] = field(
        default=None,
        metadata={
            "name": "reservationChangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ReservationChangeSets:
        reservation_change_set: list[ReservationChangeSetType] = field(
            default_factory=list,
            metadata={
                "name": "reservationChangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class TravelPassExchangeShoppingQuery:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    travel_point_pair: TravelPassExchangeSearchTravelPointPairType | None = field(
        default=None,
        metadata={
            "name": "travelPointPair",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    fare_qualifiers: Optional["TravelPassExchangeShoppingQuery.FareQualifiers"] = field(
        default=None,
        metadata={
            "name": "fareQualifiers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class FareQualifiers:
        fare_qualifier: list[FareQualifierType] = field(
            default_factory=list,
            metadata={
                "name": "fareQualifier",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class AdjustCostAndRevenueRequest(AdjustCostAndRevenueRequestType):
    class Meta:
        name = "adjustCostAndRevenueRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerV2VersionRequest(AuthenticatePayerV2VersionRequestType):
    class Meta:
        name = "authenticatePayerV2VersionRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class CancelBookingRecordRequest(CancelBookingRecordRequestType):
    class Meta:
        name = "cancelBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ClaimValueDocumentRequest(ClaimValueDocumentRequestType):
    class Meta:
        name = "claimValueDocumentRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class DelayRepayRefundRequest(DelayRepayRefundRequestType):
    class Meta:
        name = "delayRepayRefundRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class GeneratePaymentTokenRequest(GeneratePaymentTokenRequestType):
    class Meta:
        name = "generatePaymentTokenRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class GetIntermediateTravelPointsResponse(GetIntermediateTravelPointsResponseType):
    class Meta:
        name = "getIntermediateTravelPointsResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RecordFinancialTransactionRequest(RecordFinancialTransactionRequestType):
    class Meta:
        name = "recordFinancialTransactionRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RedeliverValueDocumentRequest(RedeliverValueDocumentRequestType):
    class Meta:
        name = "redeliverValueDocumentRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RefundBookingRecordRequest(RefundBookingRecordRequestType):
    class Meta:
        name = "refundBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveCancellationSummaryResponse(RetrieveCancellationSummaryResponseType):
    class Meta:
        name = "retrieveCancellationSummaryResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ReturnValueDocumentRequest(ReturnValueDocumentRequestType):
    class Meta:
        name = "returnValueDocumentRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class SearchBookingsResponse(SearchBookingsResponseType):
    class Meta:
        name = "searchBookingsResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ValidateDelayRepayRefundStatusRequest(ValidateDelayRepayRefundStatusRequestType):
    class Meta:
        name = "validateDelayRepayRefundStatusRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ValidateDelayRepayRefundStatusResponse(
    ValidateDelayRepayRefundStatusResponseType,
):
    class Meta:
        name = "validateDelayRepayRefundStatusResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class LegSolutionsType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    leg_solution: list[LegSolutionType] = field(
        default_factory=list,
        metadata={
            "name": "legSolution",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )


@dataclass(frozen=True)
class OrderType:
    """:ivar supply_channel_record_locator:

    :ivar supplier_locator: :ivar date_booked: :ivar date_cancelled: :ivar
    service_alerts: :ivar hold_expiration: :ivar fulfillment_information: :ivar
    refund_eligibility: refundEligibility is deprecated. Please     use
    cancellationSummary instead. :ivar cancellation_summary: :ivar void_summary:
    :ivar rules: :ivar shipment_tracking_information: :ivar cancellation_reason:
    :ivar internal_cancellation_reason: :ivar available_ticket_languages: :ivar
    is_inventory_canceled: :ivar delayed_refund_available_date_time: :ivar
    order_id: :ivar status: :ivar original_order_id:
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    supply_channel_record_locator: str | None = field(
        default=None,
        metadata={
            "name": "supplyChannelRecordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    supplier_locator: str | None = field(
        default=None,
        metadata={
            "name": "supplierLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    date_booked: XmlDate | None = field(
        default=None,
        metadata={
            "name": "dateBooked",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    date_cancelled: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "dateCancelled",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    service_alerts: Optional["OrderType.ServiceAlerts"] = field(
        default=None,
        metadata={
            "name": "serviceAlerts",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    hold_expiration: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "holdExpiration",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    fulfillment_information: Optional["OrderType.FulfillmentInformation"] = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    refund_eligibility: Optional["OrderType.RefundEligibility"] = field(
        default=None,
        metadata={
            "name": "refundEligibility",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    cancellation_summary: CancellationSummaryType | None = field(
        default=None,
        metadata={
            "name": "cancellationSummary",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    void_summary: VoidSummaryType | None = field(
        default=None,
        metadata={
            "name": "voidSummary",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    rules: RulesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    shipment_tracking_information: Optional["OrderType.ShipmentTrackingInformation"] = (
        field(
            default=None,
            metadata={
                "name": "shipmentTrackingInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    cancellation_reason: CancellationReasonType | None = field(
        default=None,
        metadata={
            "name": "cancellationReason",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    internal_cancellation_reason: str | None = field(
        default=None,
        metadata={
            "name": "internalCancellationReason",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    available_ticket_languages: Optional["OrderType.AvailableTicketLanguages"] = field(
        default=None,
        metadata={
            "name": "availableTicketLanguages",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    is_inventory_canceled: bool | None = field(
        default=None,
        metadata={
            "name": "isInventoryCanceled",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    delayed_refund_available_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "delayedRefundAvailableDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    order_id: str | None = field(
        default=None,
        metadata={
            "name": "orderID",
            "type": "Attribute",
            "required": True,
        },
    )
    status: OrderTypeStatus | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    original_order_id: str | None = field(
        default=None,
        metadata={
            "name": "originalOrderID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class ServiceAlerts:
        service_alert: list[ServiceAlertType] = field(
            default_factory=list,
            metadata={
                "name": "serviceAlert",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class FulfillmentInformation:
        """:ivar selected_ticketing_option:

        :ivar shipping_name: :ivar shipping_address: :ivar value_document: :ivar
        phone_number: :ivar pickup_location: Unsupported :ivar
        back_office_fulfillment_type:
        """

        selected_ticketing_option: TicketingOptionType | None = field(
            default=None,
            metadata={
                "name": "selectedTicketingOption",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        shipping_name: str | None = field(
            default=None,
            metadata={
                "name": "shippingName",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        shipping_address: AddressType | None = field(
            default=None,
            metadata={
                "name": "shippingAddress",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        value_document: ValueDocumentType | None = field(
            default=None,
            metadata={
                "name": "valueDocument",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        phone_number: FulfillmentPhoneNumberType | None = field(
            default=None,
            metadata={
                "name": "phoneNumber",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        pickup_location: TravelPointType | None = field(
            default=None,
            metadata={
                "name": "pickupLocation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        back_office_fulfillment_type: BackOfficeFulfillmentType | None = field(
            default=None,
            metadata={
                "name": "backOfficeFulfillmentType",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

    @dataclass(frozen=True)
    class RefundEligibility:
        penalty: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        penalty_breakdown: Optional["OrderType.RefundEligibility.PenaltyBreakdown"] = (
            field(
                default=None,
                metadata={
                    "name": "penaltyBreakdown",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
        )
        eligible: bool | None = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            },
        )
        cancel_required_for_refund: bool | None = field(
            default=None,
            metadata={
                "name": "cancelRequiredForRefund",
                "type": "Attribute",
            },
        )

        @dataclass(frozen=True)
        class PenaltyBreakdown:
            penalty_item: list[
                "OrderType.RefundEligibility.PenaltyBreakdown.PenaltyItem"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "penaltyItem",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class PenaltyItem(MoneyType):
                type_value: PenaltyItemType | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                        "required": True,
                    },
                )

    @dataclass(frozen=True)
    class ShipmentTrackingInformation:
        shipment_tracking: list[ShipmentTrackingType] = field(
            default_factory=list,
            metadata={
                "name": "shipmentTracking",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class AvailableTicketLanguages:
        language: list[str] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PassPriceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    total_price: TotalPriceType | None = field(
        default=None,
        metadata={
            "name": "totalPrice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    ticketable_fares: Optional["PassPriceType.TicketableFares"] = field(
        default=None,
        metadata={
            "name": "ticketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    fare_merchandising_rank: int | None = field(
        default=None,
        metadata={
            "name": "fareMerchandisingRank",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    hold_expiration: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "holdExpiration",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    price_id: str | None = field(
        default=None,
        metadata={
            "name": "priceID",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class TicketableFares:
        ticketable_fare: list[PassTicketableFareType] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFare",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class PointToPointPriceType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    total_price: TotalPriceType | None = field(
        default=None,
        metadata={
            "name": "totalPrice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    restrictive_fare_class: str | None = field(
        default=None,
        metadata={
            "name": "restrictiveFareClass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    ticketable_fares: Optional["PointToPointPriceType.TicketableFares"] = field(
        default=None,
        metadata={
            "name": "ticketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    leg_references: LegReferencesType | None = field(
        default=None,
        metadata={
            "name": "legReferences",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    fare_merchandising_rank: int | None = field(
        default=None,
        metadata={
            "name": "fareMerchandisingRank",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    hold_expiration: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "holdExpiration",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    compatible_prices: CompatiblePricesType | None = field(
        default=None,
        metadata={
            "name": "compatiblePrices",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    add_on_fare_qualifiers: Optional["PointToPointPriceType.AddOnFareQualifiers"] = (
        field(
            default=None,
            metadata={
                "name": "addOnFareQualifiers",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
    )
    price_id: str | None = field(
        default=None,
        metadata={
            "name": "priceID",
            "type": "Attribute",
            "required": True,
        },
    )
    availability_check_bypassed: bool | None = field(
        default=None,
        metadata={
            "name": "availabilityCheckBypassed",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class TicketableFares:
        ticketable_fare: list[TicketableFareType] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFare",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class AddOnFareQualifiers:
        fare_qualifier: list[FareQualifierType] = field(
            default_factory=list,
            metadata={
                "name": "fareQualifier",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class AddOrderToBookingRecordRequestType(BaseAddOrderRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order: Optional["AddOrderToBookingRecordRequestType.Order"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["AddOrderToBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    supplier_notes: SupplierNoteType | None = field(
        default=None,
        metadata={
            "name": "supplierNotes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    campaign: CampaignType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Order:
        passengers: Optional["AddOrderToBookingRecordRequestType.Order.Passengers"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
        )
        leg_solutions: LegSolutionsType | None = field(
            default=None,
            metadata={
                "name": "legSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        prices: Optional["AddOrderToBookingRecordRequestType.Order.Prices"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        parameters: Optional["AddOrderToBookingRecordRequestType.Order.Parameters"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        outward_journey_and_fare_signatures: JourneyAndFareSignaturesType | None = (
            field(
                default=None,
                metadata={
                    "name": "outwardJourneyAndFareSignatures",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        return_journey_and_fare_signatures: JourneyAndFareSignaturesType | None = field(
            default=None,
            metadata={
                "name": "returnJourneyAndFareSignatures",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        rail_card_signatures: str | None = field(
            default=None,
            metadata={
                "name": "railCardSignatures",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        total_price: MoneyType | None = field(
            default=None,
            metadata={
                "name": "totalPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class Passengers:
            passenger: list[PassengerType] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Prices:
            point_to_point_price: list[PointToPointPriceType] = field(
                default_factory=list,
                metadata={
                    "name": "pointToPointPrice",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Parameters:
            price_acceptance: Optional[
                "AddOrderToBookingRecordRequestType.Order.Parameters.PriceAcceptance"
            ] = field(
                default=None,
                metadata={
                    "name": "priceAcceptance",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            shop_ancillary: bool | None = field(
                default=None,
                metadata={
                    "name": "shopAncillary",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

            @dataclass(frozen=True)
            class PriceAcceptance:
                accept_any: bool | None = field(
                    default=None,
                    metadata={
                        "name": "acceptAny",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                accept_higher: PriceAcceptanceType | None = field(
                    default=None,
                    metadata={
                        "name": "acceptHigher",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                accept_lower: PriceAcceptanceType | None = field(
                    default=None,
                    metadata={
                        "name": "acceptLower",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingRequestExchangeSetType(BaseRequestExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    leg_solutions: LegSolutionsType | None = field(
        default=None,
        metadata={
            "name": "legSolutions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    prices: Optional["BookingRequestExchangeSetType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Prices:
        point_to_point_price: list[PointToPointPriceType] = field(
            default_factory=list,
            metadata={
                "name": "pointToPointPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class BookingRequestTravelPassExchangeSetType(BaseRequestExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    travel_point_pair: QueryTravelPointPairPassType | None = field(
        default=None,
        metadata={
            "name": "travelPointPair",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    prices: Optional["BookingRequestTravelPassExchangeSetType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Prices:
        travel_pass_price: list[PassPriceType] = field(
            default_factory=list,
            metadata={
                "name": "travelPassPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class BookingAdjustCostAndRevenueRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAdjustCostAndRevenueRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        adjust_cost_and_revenue_request: AdjustCostAndRevenueRequest | None = field(
            default=None,
            metadata={
                "name": "adjustCostAndRevenueRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


class BookingAuthenticatePayerV2ChallengeRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAuthenticatePayerV2ChallengeRequestInput
    output = BookingAuthenticatePayerV2ChallengeRequestOutput


@dataclass(frozen=True)
class BookingAuthenticatePayerV2VersionInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerV2VersionInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_v2_version_request: (
            AuthenticatePayerV2VersionRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "authenticatePayerV2VersionRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingCancelBookingRecordRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingCancelBookingRecordRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        cancel_booking_record_request: CancelBookingRecordRequest | None = field(
            default=None,
            metadata={
                "name": "cancelBookingRecordRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingClaimValueDocumentRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingClaimValueDocumentRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        claim_value_document_request: ClaimValueDocumentRequest | None = field(
            default=None,
            metadata={
                "name": "claimValueDocumentRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingDelayRepayRefundInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingDelayRepayRefundInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        delay_repay_refund_request: DelayRepayRefundRequest | None = field(
            default=None,
            metadata={
                "name": "delayRepayRefundRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


class BookingDeleteCardholderInfo:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingDeleteCardholderInfoInput
    output = BookingDeleteCardholderInfoOutput


class BookingDeletePaymentTokenRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingDeletePaymentTokenRequestInput
    output = BookingDeletePaymentTokenRequestOutput


@dataclass(frozen=True)
class BookingGeneratePaymentTokenRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingGeneratePaymentTokenRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        generate_payment_token_request: GeneratePaymentTokenRequest | None = field(
            default=None,
            metadata={
                "name": "generatePaymentTokenRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingGetIntermediateTravelPointsOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingGetIntermediateTravelPointsOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        get_intermediate_travel_points_response: (
            GetIntermediateTravelPointsResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "getIntermediateTravelPointsResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingGetIntermediateTravelPointsOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingGetIntermediateTravelPointsOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRecordFinancialTransactionRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRecordFinancialTransactionRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        record_financial_transaction_request: (
            RecordFinancialTransactionRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "recordFinancialTransactionRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingRedeliverValueDocumentRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRedeliverValueDocumentRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        redeliver_value_document_request: RedeliverValueDocumentRequest | None = field(
            default=None,
            metadata={
                "name": "redeliverValueDocumentRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingRefundBookingRecordRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRefundBookingRecordRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        refund_booking_record_request: RefundBookingRecordRequest | None = field(
            default=None,
            metadata={
                "name": "refundBookingRecordRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingRetrieveCancellationSummaryRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveCancellationSummaryRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_cancellation_summary_response: (
            RetrieveCancellationSummaryResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "retrieveCancellationSummaryResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional[
            "BookingRetrieveCancellationSummaryRequestOutput.Body.Fault"
        ] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRetrieveCancellationSummaryRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingReturnValueDocumentRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingReturnValueDocumentRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        return_value_document_request: ReturnValueDocumentRequest | None = field(
            default=None,
            metadata={
                "name": "returnValueDocumentRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingSearchBookingsRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingSearchBookingsRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        search_bookings_response: SearchBookingsResponse | None = field(
            default=None,
            metadata={
                "name": "searchBookingsResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingSearchBookingsRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingSearchBookingsRequestOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingValidateDelayRepayRefundStatusRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingValidateDelayRepayRefundStatusRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        validate_delay_repay_refund_status_request: (
            ValidateDelayRepayRefundStatusRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "validateDelayRepayRefundStatusRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingValidateDelayRepayRefundStatusRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingValidateDelayRepayRefundStatusRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        validate_delay_repay_refund_status_response: (
            ValidateDelayRepayRefundStatusResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "validateDelayRepayRefundStatusResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional[
            "BookingValidateDelayRepayRefundStatusRequestOutput.Body.Fault"
        ] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingValidateDelayRepayRefundStatusRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class ExchangeSearchRequestExchangeSetType(BaseRequestExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    exchange_shopping_query: ExchangeShoppingQuery | None = field(
        default=None,
        metadata={
            "name": "exchangeShoppingQuery",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ExchangeSearchResponseExchangeSetType(BaseExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    exchanged_ticketable_fares: Optional[
        "ExchangeSearchResponseExchangeSetType.ExchangedTicketableFares"
    ] = field(
        default=None,
        metadata={
            "name": "exchangedTicketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    cancelled_ticketable_fares: Optional[
        "ExchangeSearchResponseExchangeSetType.CancelledTicketableFares"
    ] = field(
        default=None,
        metadata={
            "name": "cancelledTicketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    exchanged_travel_segments: Optional[
        "ExchangeSearchResponseExchangeSetType.ExchangedTravelSegments"
    ] = field(
        default=None,
        metadata={
            "name": "exchangedTravelSegments",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    leg_solutions: LegSolutionsType | None = field(
        default=None,
        metadata={
            "name": "legSolutions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    prices: Optional["ExchangeSearchResponseExchangeSetType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ExchangedTicketableFares:
        exchanged_ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "exchangedTicketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class CancelledTicketableFares:
        cancelled_ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "cancelledTicketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ExchangedTravelSegments:
        exchanged_travel_segment_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "exchangedTravelSegmentLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Prices:
        point_to_point_price: list[PointToPointPriceType] = field(
            default_factory=list,
            metadata={
                "name": "pointToPointPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class GetIntermediateTravelPointsRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    intermediate_travel_points_query: IntermediateTravelPointsQueryType | None = field(
        default=None,
        metadata={
            "name": "intermediateTravelPointsQuery",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class ReservationChangeShoppingSetType:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    leg_grouping: OneOrTwoType | None = field(
        default=None,
        metadata={
            "name": "legGrouping",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    ticketable_fare_locators: Optional[
        "ReservationChangeShoppingSetType.TicketableFareLocators"
    ] = field(
        default=None,
        metadata={
            "name": "ticketableFareLocators",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    leg_solutions: LegSolutionsType | None = field(
        default=None,
        metadata={
            "name": "legSolutions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    prices: Optional["ReservationChangeShoppingSetType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: Optional["ReservationChangeShoppingSetType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    reservation_change_set_id: str | None = field(
        default=None,
        metadata={
            "name": "reservationChangeSetID",
            "type": "Attribute",
        },
    )

    @dataclass(frozen=True)
    class TicketableFareLocators:
        ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "ticketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Prices:
        point_to_point_price: list[PointToPointPriceType] = field(
            default_factory=list,
            metadata={
                "name": "pointToPointPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list[PassengerType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class ReservationSearchResponseType(BaseResponseType):
    """ReservationSearchResponseType is functionality under development and subject to
    change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    passengers: Optional["ReservationSearchResponseType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order: Optional["ReservationSearchResponseType.Order"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list[PassengerType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Order(OrderType):
        travel_segments: Optional[
            "ReservationSearchResponseType.Order.TravelSegments"
        ] = field(
            default=None,
            metadata={
                "name": "travelSegments",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        sub_segments: Optional["ReservationSearchResponseType.Order.SubSegments"] = (
            field(
                default=None,
                metadata={
                    "name": "subSegments",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        ticketable_fares: Optional[
            "ReservationSearchResponseType.Order.TicketableFares"
        ] = field(
            default=None,
            metadata={
                "name": "ticketableFares",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        supply_channel_passengers: Optional[
            "ReservationSearchResponseType.Order.SupplyChannelPassengers"
        ] = field(
            default=None,
            metadata={
                "name": "supplyChannelPassengers",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        reservable_ticketable_fares: Optional[
            "ReservationSearchResponseType.Order.ReservableTicketableFares"
        ] = field(
            default=None,
            metadata={
                "name": "reservableTicketableFares",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        combined_ticketable_fare_sets: Optional[
            "ReservationSearchResponseType.Order.CombinedTicketableFareSets"
        ] = field(
            default=None,
            metadata={
                "name": "combinedTicketableFareSets",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class TravelSegments:
            travel_segment: list[TravelSegmentType] = field(
                default_factory=list,
                metadata={
                    "name": "travelSegment",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

        @dataclass(frozen=True)
        class SubSegments:
            sub_segment: list[SubSegmentType] = field(
                default_factory=list,
                metadata={
                    "name": "subSegment",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class TicketableFares:
            ticketable_fare: list[TicketableFareType] = field(
                default_factory=list,
                metadata={
                    "name": "ticketableFare",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class SupplyChannelPassengers:
            supply_channel_passenger_reference: list[
                SupplyChannelPassengerReferenceType
            ] = field(
                default_factory=list,
                metadata={
                    "name": "supplyChannelPassengerReference",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class ReservableTicketableFares:
            reservable_ticketable_fare: list[ReservableTicketableFareType] = field(
                default_factory=list,
                metadata={
                    "name": "reservableTicketableFare",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class CombinedTicketableFareSets:
            combined_ticketable_fare_set: list[CombinedTicketableFareSetType] = field(
                default_factory=list,
                metadata={
                    "name": "combinedTicketableFareSet",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                    "max_occurs": 2,
                },
            )


@dataclass(frozen=True)
class ReservationShoppingResponseType(BaseResponseType):
    """ReservationShoppingResponseType is functionality under development and subject
    to change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    results: Optional["ReservationShoppingResponseType.Results"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Results:
        leg_solutions: LegSolutionsType | None = field(
            default=None,
            metadata={
                "name": "legSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        available_seat_preferences: Optional[
            "ReservationShoppingResponseType.Results.AvailableSeatPreferences"
        ] = field(
            default=None,
            metadata={
                "name": "availableSeatPreferences",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        prices: Optional["ReservationShoppingResponseType.Results.Prices"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        passengers: Optional["ReservationShoppingResponseType.Results.Passengers"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
        )

        @dataclass(frozen=True)
        class AvailableSeatPreferences:
            available_seat_preference: list[AvailableSeatPreferenceType] = field(
                default_factory=list,
                metadata={
                    "name": "availableSeatPreference",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Prices:
            point_to_point_price: list[PointToPointPriceType] = field(
                default_factory=list,
                metadata={
                    "name": "pointToPointPrice",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

        @dataclass(frozen=True)
        class Passengers:
            passenger: list[PassengerType] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )


@dataclass(frozen=True)
class TravelPassExchangeSearchRequestExchangeSetType(BaseRequestExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    travel_pass_exchange_shopping_query: TravelPassExchangeShoppingQuery | None = field(
        default=None,
        metadata={
            "name": "travelPassExchangeShoppingQuery",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )


@dataclass(frozen=True)
class TravelPassExchangeSearchResponseExchangeSetType(BaseExchangeSetType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    exchanged_ticketable_fares: Optional[
        "TravelPassExchangeSearchResponseExchangeSetType.ExchangedTicketableFares"
    ] = field(
        default=None,
        metadata={
            "name": "exchangedTicketableFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    prices: Optional["TravelPassExchangeSearchResponseExchangeSetType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class ExchangedTicketableFares:
        exchanged_ticketable_fare_locator: list[str] = field(
            default_factory=list,
            metadata={
                "name": "exchangedTicketableFareLocator",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Prices:
        travel_pass_price: list[PassPriceType] = field(
            default_factory=list,
            metadata={
                "name": "travelPassPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class TravelPassQuery:
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    travel_point_pair: QueryTravelPointPairPassType | None = field(
        default=None,
        metadata={
            "name": "travelPointPair",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    travel_pass: QueryTravelPassType | None = field(
        default=None,
        metadata={
            "name": "travelPass",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    pass_prices: Optional["TravelPassQuery.PassPrices"] = field(
        default=None,
        metadata={
            "name": "passPrices",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    pass_issue_type: IssueType | None = field(
        default=None,
        metadata={
            "name": "passIssueType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class PassPrices:
        travel_pass_price: list[PassPriceType] = field(
            default_factory=list,
            metadata={
                "name": "travelPassPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class UpdateBookingRecordRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    service_fees: FeesType | None = field(
        default=None,
        metadata={
            "name": "serviceFees",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    promotions: PromotionsType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    remove_promotion: bool | None = field(
        default=None,
        metadata={
            "name": "removePromotion",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    remove_selected_ticketing_option: object | None = field(
        default=None,
        metadata={
            "name": "removeSelectedTicketingOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    custom_information: CustomInformationType | None = field(
        default=None,
        metadata={
            "name": "customInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    shipment_tracking: ShipmentTrackingType | None = field(
        default=None,
        metadata={
            "name": "shipmentTracking",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order: Optional["UpdateBookingRecordRequestType.Order"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passengers: Optional["UpdateBookingRecordRequestType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["UpdateBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    external_identification: ExternalIdentificationType | None = field(
        default=None,
        metadata={
            "name": "externalIdentification",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    allow_any_card_for_collection: bool | None = field(
        default=None,
        metadata={
            "name": "allowAnyCardForCollection",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    supplier_notes: SupplierNoteType | None = field(
        default=None,
        metadata={
            "name": "supplierNotes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Order:
        passengers: Optional["UpdateBookingRecordRequestType.Order.Passengers"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        leg_solutions: LegSolutionsType | None = field(
            default=None,
            metadata={
                "name": "legSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        prices: Optional["UpdateBookingRecordRequestType.Order.Prices"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        parameters: Optional["UpdateBookingRecordRequestType.Order.Parameters"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class Passengers:
            passenger: list[PassengerType] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Prices:
            point_to_point_price: list[PointToPointPriceType] = field(
                default_factory=list,
                metadata={
                    "name": "pointToPointPrice",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Parameters:
            price_acceptance: Optional[
                "UpdateBookingRecordRequestType.Order.Parameters.PriceAcceptance"
            ] = field(
                default=None,
                metadata={
                    "name": "priceAcceptance",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            shop_ancillary: bool | None = field(
                default=None,
                metadata={
                    "name": "shopAncillary",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

            @dataclass(frozen=True)
            class PriceAcceptance:
                accept_any: bool | None = field(
                    default=None,
                    metadata={
                        "name": "acceptAny",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                accept_higher: PriceAcceptanceType | None = field(
                    default=None,
                    metadata={
                        "name": "acceptHigher",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                accept_lower: PriceAcceptanceType | None = field(
                    default=None,
                    metadata={
                        "name": "acceptLower",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list[PassengerType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ValidateBookingRecordInformationResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record_information: Optional[
        "ValidateBookingRecordInformationResponseType.BookingRecordInformation"
    ] = field(
        default=None,
        metadata={
            "name": "bookingRecordInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class BookingRecordInformation:
        order_information_set: Optional[
            "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet"
        ] = field(
            default=None,
            metadata={
                "name": "orderInformationSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        payment_requirements: PaymentRequirementsType | None = field(
            default=None,
            metadata={
                "name": "paymentRequirements",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        service_fee_allowed: bool | None = field(
            default=None,
            metadata={
                "name": "serviceFeeAllowed",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        credit_card_surcharge_fee_applicable: bool | None = field(
            default=None,
            metadata={
                "name": "creditCardSurchargeFeeApplicable",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        campaign: CampaignResponseType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class OrderInformationSet:
            order_information: list[
                "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "orderInformation",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class OrderInformation:
                passengers: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.Passengers"
                ] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                leg_solutions: LegSolutionsType | None = field(
                    default=None,
                    metadata={
                        "name": "legSolutions",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                prices: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.Prices"
                ] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                travel_segments: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.TravelSegments"
                ] = field(
                    default=None,
                    metadata={
                        "name": "travelSegments",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                sub_segments: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.SubSegments"
                ] = field(
                    default=None,
                    metadata={
                        "name": "subSegments",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                ticketing_options: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.TicketingOptions"
                ] = field(
                    default=None,
                    metadata={
                        "name": "ticketingOptions",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "required": True,
                    },
                )
                confirmation_options: ConfirmationOptionsType | None = field(
                    default=None,
                    metadata={
                        "name": "confirmationOptions",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                confirmation_information_required: bool | None = field(
                    default=None,
                    metadata={
                        "name": "confirmationInformationRequired",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "required": True,
                    },
                )
                confirmation_information_required_overrides: (
                    ConfirmationInformationRequiredOverrideType | None
                ) = field(
                    default=None,
                    metadata={
                        "name": "confirmationInformationRequiredOverrides",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                payment_card_required_for_confirmation_information: bool | None = field(
                    default=None,
                    metadata={
                        "name": "paymentCardRequiredForConfirmationInformation",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "required": True,
                    },
                )
                available_ticket_languages: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.AvailableTicketLanguages"
                ] = field(
                    default=None,
                    metadata={
                        "name": "availableTicketLanguages",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                external_booking_url: str | None = field(
                    default=None,
                    metadata={
                        "name": "externalBookingUrl",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                commercial_agent_name: str | None = field(
                    default=None,
                    metadata={
                        "name": "commercialAgentName",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )
                passenger_information_required: Optional[
                    "ValidateBookingRecordInformationResponseType.BookingRecordInformation.OrderInformationSet.OrderInformation.PassengerInformationRequired"
                ] = field(
                    default=None,
                    metadata={
                        "name": "passengerInformationRequired",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )

                @dataclass(frozen=True)
                class TravelSegments:
                    travel_segment: list[TravelSegmentType] = field(
                        default_factory=list,
                        metadata={
                            "name": "travelSegment",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                        },
                    )

                @dataclass(frozen=True)
                class SubSegments:
                    booked_sub_segment: list[SubSegmentType] = field(
                        default_factory=list,
                        metadata={
                            "name": "bookedSubSegment",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "min_occurs": 1,
                        },
                    )

                @dataclass(frozen=True)
                class TicketingOptions:
                    ticketing_option: list[TicketingOptionType] = field(
                        default_factory=list,
                        metadata={
                            "name": "ticketingOption",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "min_occurs": 1,
                        },
                    )

                @dataclass(frozen=True)
                class AvailableTicketLanguages:
                    language: list[str] = field(
                        default_factory=list,
                        metadata={
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "min_occurs": 1,
                        },
                    )

                @dataclass(frozen=True)
                class PassengerInformationRequired:
                    passenger_information: list[PassengerInformationType] = field(
                        default_factory=list,
                        metadata={
                            "name": "passengerInformation",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "min_occurs": 1,
                        },
                    )

                @dataclass(frozen=True)
                class Passengers:
                    passenger: list[PassengerType] = field(
                        default_factory=list,
                        metadata={
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "min_occurs": 1,
                        },
                    )

                @dataclass(frozen=True)
                class Prices:
                    point_to_point_price: list[PointToPointPriceType] = field(
                        default_factory=list,
                        metadata={
                            "name": "pointToPointPrice",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/booking",
                            "min_occurs": 1,
                        },
                    )


@dataclass(frozen=True)
class AddPaymentRequest(AddPaymentRequestType):
    class Meta:
        name = "addPaymentRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerRequest(AuthenticatePayerRequestType):
    class Meta:
        name = "authenticatePayerRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AuthenticatePayerV2Request(AuthenticatePayerV2RequestType):
    class Meta:
        name = "authenticatePayerV2Request"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class CancelReservationRequest(CancelReservationRequestType):
    class Meta:
        name = "cancelReservationRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ConfirmBookingRecordRequest(ConfirmBookingRecordRequestType):
    class Meta:
        name = "confirmBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessReservationRequest(ProcessReservationRequestType):
    class Meta:
        name = "processReservationRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ReservationShoppingRequest(ReservationShoppingRequestType):
    class Meta:
        name = "reservationShoppingRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class BookingRecordType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    updateable: UpdateableBookingType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    booking_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "bookingDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    departure_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "departureDate",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    number_of_orders: int | None = field(
        default=None,
        metadata={
            "name": "numberOfOrders",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    revenue_total: MoneyType | None = field(
        default=None,
        metadata={
            "name": "revenueTotal",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    receipts_total: MoneyType | None = field(
        default=None,
        metadata={
            "name": "receiptsTotal",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    passengers: Optional["BookingRecordType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    orders: Optional["BookingRecordType.Orders"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    payment_requirements: Optional["BookingRecordType.PaymentRequirements"] = field(
        default=None,
        metadata={
            "name": "paymentRequirements",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    service_fee_allowed: bool | None = field(
        default=None,
        metadata={
            "name": "serviceFeeAllowed",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    credit_card_surcharge_fee_applicable: bool | None = field(
        default=None,
        metadata={
            "name": "creditCardSurchargeFeeApplicable",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    financials: Optional["BookingRecordType.Financials"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    external_identification: ExternalIdentificationType | None = field(
        default=None,
        metadata={
            "name": "externalIdentification",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    custom_information: CustomInformationType | None = field(
        default=None,
        metadata={
            "name": "customInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
        },
    )
    record_locator: object | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Attribute",
            "required": True,
        },
    )
    status: BookingRecordTypeStatus | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list[PassengerType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Orders:
        order: list["BookingRecordType.Orders.Order"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Order(OrderType):
            updateable: UpdateableOrderType | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            travel_segments: Optional[
                "BookingRecordType.Orders.Order.TravelSegments"
            ] = field(
                default=None,
                metadata={
                    "name": "travelSegments",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            sub_segments: Optional["BookingRecordType.Orders.Order.SubSegments"] = (
                field(
                    default=None,
                    metadata={
                        "name": "subSegments",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
            )
            carbon_data_comparisons: Optional[
                "BookingRecordType.Orders.Order.CarbonDataComparisons"
            ] = field(
                default=None,
                metadata={
                    "name": "carbonDataComparisons",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            ticketable_fares: Optional[
                "BookingRecordType.Orders.Order.TicketableFares"
            ] = field(
                default=None,
                metadata={
                    "name": "ticketableFares",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            ticketing_options: Optional[
                "BookingRecordType.Orders.Order.TicketingOptions"
            ] = field(
                default=None,
                metadata={
                    "name": "ticketingOptions",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            financials: Optional["BookingRecordType.Orders.Order.Financials"] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            supply_channel_passengers: Optional[
                "BookingRecordType.Orders.Order.SupplyChannelPassengers"
            ] = field(
                default=None,
                metadata={
                    "name": "supplyChannelPassengers",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            order_notes: Optional["BookingRecordType.Orders.Order.OrderNotes"] = field(
                default=None,
                metadata={
                    "name": "orderNotes",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            confirmation_information_required: bool | None = field(
                default=None,
                metadata={
                    "name": "confirmationInformationRequired",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            payment_card_required_for_confirmation_information: bool | None = field(
                default=None,
                metadata={
                    "name": "paymentCardRequiredForConfirmationInformation",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            confirmation_information_required_overrides: (
                ConfirmationInformationRequiredOverrideType | None
            ) = field(
                default=None,
                metadata={
                    "name": "confirmationInformationRequiredOverrides",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            confirmation_options: ConfirmationOptionsType | None = field(
                default=None,
                metadata={
                    "name": "confirmationOptions",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            selected_confirmation_option: SelectedConfirmationOptionType | None = field(
                default=None,
                metadata={
                    "name": "selectedConfirmationOption",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            commercial_agent_name: str | None = field(
                default=None,
                metadata={
                    "name": "commercialAgentName",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            exchangeable_ticketable_fare_locators: (
                ExchangeableTicketableFareLocatorsType | None
            ) = field(
                default=None,
                metadata={
                    "name": "exchangeableTicketableFareLocators",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            exchange_sets: ExchangeSetsType | None = field(
                default=None,
                metadata={
                    "name": "exchangeSets",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            voidable_ticketable_fare_locators: (
                VoidableTicketableFareLocatorsType | None
            ) = field(
                default=None,
                metadata={
                    "name": "voidableTicketableFareLocators",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            supplier_notes: SupplierNoteType | None = field(
                default=None,
                metadata={
                    "name": "supplierNotes",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            reservable_ticketable_fares: Optional[
                "BookingRecordType.Orders.Order.ReservableTicketableFares"
            ] = field(
                default=None,
                metadata={
                    "name": "reservableTicketableFares",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            combined_ticketable_fare_sets: Optional[
                "BookingRecordType.Orders.Order.CombinedTicketableFareSets"
            ] = field(
                default=None,
                metadata={
                    "name": "combinedTicketableFareSets",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            revisions: Optional["BookingRecordType.Orders.Order.Revisions"] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )
            available_seat_preferences: Optional[
                "BookingRecordType.Orders.Order.AvailableSeatPreferences"
            ] = field(
                default=None,
                metadata={
                    "name": "availableSeatPreferences",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                },
            )

            @dataclass(frozen=True)
            class TravelSegments:
                travel_segment: list[TravelSegmentType] = field(
                    default_factory=list,
                    metadata={
                        "name": "travelSegment",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )

            @dataclass(frozen=True)
            class SubSegments:
                sub_segment: list[SubSegmentType] = field(
                    default_factory=list,
                    metadata={
                        "name": "subSegment",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class CarbonDataComparisons:
                carbon_data_comparison: list[CarbonDataComparisonType] = field(
                    default_factory=list,
                    metadata={
                        "name": "carbonDataComparison",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )

            @dataclass(frozen=True)
            class TicketableFares:
                ticketable_fare: list[TicketableFareType] = field(
                    default_factory=list,
                    metadata={
                        "name": "ticketableFare",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class TicketingOptions:
                ticketing_option: list[TicketingOptionType] = field(
                    default_factory=list,
                    metadata={
                        "name": "ticketingOption",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class Financials:
                total_price: MoneyType | None = field(
                    default=None,
                    metadata={
                        "name": "totalPrice",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "required": True,
                    },
                )
                base_price: MoneyType | None = field(
                    default=None,
                    metadata={
                        "name": "basePrice",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                upgrade_price: MoneyType | None = field(
                    default=None,
                    metadata={
                        "name": "upgradePrice",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                accommodation_price: MoneyType | None = field(
                    default=None,
                    metadata={
                        "name": "accommodationPrice",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                taxes: MoneyType | None = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                fees: MoneyType | None = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                commission_amount: MoneyType | None = field(
                    default=None,
                    metadata={
                        "name": "commissionAmount",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )

            @dataclass(frozen=True)
            class SupplyChannelPassengers:
                supply_channel_passenger_reference: list[
                    SupplyChannelPassengerReferenceType
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "supplyChannelPassengerReference",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class OrderNotes:
                order_note: list[OrderNoteType] = field(
                    default_factory=list,
                    metadata={
                        "name": "orderNote",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class ReservableTicketableFares:
                reservable_ticketable_fare: list[ReservableTicketableFareType] = field(
                    default_factory=list,
                    metadata={
                        "name": "reservableTicketableFare",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class CombinedTicketableFareSets:
                combined_ticketable_fare_set: list[CombinedTicketableFareSetType] = (
                    field(
                        default_factory=list,
                        metadata={
                            "name": "combinedTicketableFareSet",
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/commontypes",
                            "min_occurs": 1,
                            "max_occurs": 2,
                        },
                    )
                )

            @dataclass(frozen=True)
            class Revisions:
                revision: list[RevisionType] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

            @dataclass(frozen=True)
            class AvailableSeatPreferences:
                available_seat_preference: list[AvailableSeatPreferenceType] = field(
                    default_factory=list,
                    metadata={
                        "name": "availableSeatPreference",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "min_occurs": 1,
                    },
                )

    @dataclass(frozen=True)
    class PaymentRequirements:
        payment_due: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "paymentDue",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        payment_information: PaymentRequirementsPaymentInformation | None = field(
            default=None,
            metadata={
                "name": "paymentInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        next_deposit_due: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "nextDepositDue",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        minimum_deposit_amount: MoneyType | None = field(
            default=None,
            metadata={
                "name": "minimumDepositAmount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        acceptable_forms_of_payment: Optional[
            "BookingRecordType.PaymentRequirements.AcceptableFormsOfPayment"
        ] = field(
            default=None,
            metadata={
                "name": "acceptableFormsOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
                "required": True,
            },
        )
        credit_card_surcharge_fees: Optional[
            "BookingRecordType.PaymentRequirements.CreditCardSurchargeFees"
        ] = field(
            default=None,
            metadata={
                "name": "creditCardSurchargeFees",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        refund_is_processed_on_cancel: bool | None = field(
            default=None,
            metadata={
                "name": "refundIsProcessedOnCancel",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        confirmation_upon_add_payment: bool | None = field(
            default=None,
            metadata={
                "name": "confirmationUponAddPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        confirmation_information_required: bool | None = field(
            default=None,
            metadata={
                "name": "confirmationInformationRequired",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        payment_card_required_for_confirmation_information: bool | None = field(
            default=None,
            metadata={
                "name": "paymentCardRequiredForConfirmationInformation",
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class AcceptableFormsOfPayment:
            form_of_payment: list[FormOfPaymentType] = field(
                default_factory=list,
                metadata={
                    "name": "formOfPayment",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class CreditCardSurchargeFees:
            credit_card_surcharge_fee: list[CreditCardSurchargeFeeType] = field(
                default_factory=list,
                metadata={
                    "name": "creditCardSurchargeFee",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

    @dataclass(frozen=True)
    class Financials:
        prices: Optional["BookingRecordType.Financials.Prices"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )
        payments: Optional["BookingRecordType.Financials.Payments"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/commontypes",
            },
        )

        @dataclass(frozen=True)
        class Prices:
            price: list["BookingRecordType.Financials.Prices.Price"] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class Price:
                order_idref: str | None = field(
                    default=None,
                    metadata={
                        "name": "orderIDRef",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                amount: MoneyType | None = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                        "required": True,
                    },
                )
                posting_date: XmlDate | None = field(
                    default=None,
                    metadata={
                        "name": "postingDate",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                posting_time: XmlTime | None = field(
                    default=None,
                    metadata={
                        "name": "postingTime",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                commission: Optional[
                    "BookingRecordType.Financials.Prices.Price.Commission"
                ] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                price_id: str | None = field(
                    default=None,
                    metadata={
                        "name": "priceID",
                        "type": "Attribute",
                        "required": True,
                    },
                )
                type_value: str | None = field(
                    default=None,
                    metadata={
                        "name": "type",
                        "type": "Attribute",
                    },
                )
                supplement_code: str | None = field(
                    default=None,
                    metadata={
                        "name": "supplementCode",
                        "type": "Attribute",
                    },
                )
                price_description: str | None = field(
                    default=None,
                    metadata={
                        "name": "priceDescription",
                        "type": "Attribute",
                    },
                )

                @dataclass(frozen=True)
                class Commission:
                    amount: MoneyType | None = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "namespace": "http://railgds.net/ws/commontypes",
                        },
                    )
                    commissionable: bool | None = field(
                        default=None,
                        metadata={
                            "type": "Attribute",
                        },
                    )

        @dataclass(frozen=True)
        class Payments:
            payment: list["BookingRecordType.Financials.Payments.Payment"] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/commontypes",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class Payment(PaymentType):
                price_idref: str | None = field(
                    default=None,
                    metadata={
                        "name": "priceIDRef",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                balance_amount: MoneyType | None = field(
                    default=None,
                    metadata={
                        "name": "balanceAmount",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                posting_date: XmlDate | None = field(
                    default=None,
                    metadata={
                        "name": "postingDate",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                posting_time: XmlTime | None = field(
                    default=None,
                    metadata={
                        "name": "postingTime",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                receipt_number: str | None = field(
                    default=None,
                    metadata={
                        "name": "receiptNumber",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                reference_receipt_number: str | None = field(
                    default=None,
                    metadata={
                        "name": "referenceReceiptNumber",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )
                external_payment: ExternalPaymentType | None = field(
                    default=None,
                    metadata={
                        "name": "externalPayment",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/commontypes",
                    },
                )


@dataclass(frozen=True)
class LegType:
    class Meta:
        target_namespace = "http://railgds.net/ws/commontypes"

    origin_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "originTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    destination_travel_point: TravelPointType | None = field(
        default=None,
        metadata={
            "name": "destinationTravelPoint",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    leg_solutions: LegSolutionsType | None = field(
        default=None,
        metadata={
            "name": "legSolutions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/commontypes",
            "required": True,
        },
    )
    leg_id: str | None = field(
        default=None,
        metadata={
            "name": "legID",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AddOrderToBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class AddPaymentResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    payment_token: str | None = field(
        default=None,
        metadata={
            "name": "paymentToken",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passenger_rights: PassengerRightsType | None = field(
        default=None,
        metadata={
            "name": "passengerRights",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class AdjustCostAndRevenueResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class BookingAddPaymentRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAddPaymentRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        add_payment_request: AddPaymentRequest | None = field(
            default=None,
            metadata={
                "name": "addPaymentRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingAuthenticatePayerRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_request: AuthenticatePayerRequest | None = field(
            default=None,
            metadata={
                "name": "authenticatePayerRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingAuthenticatePayerV2RequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAuthenticatePayerV2RequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        authenticate_payer_v2_request: AuthenticatePayerV2Request | None = field(
            default=None,
            metadata={
                "name": "authenticatePayerV2Request",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


class BookingAuthenticatePayerV2Version:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAuthenticatePayerV2VersionInput
    output = BookingAuthenticatePayerV2VersionOutput


@dataclass(frozen=True)
class BookingCancelReservationInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingCancelReservationInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        cancel_reservation_request: CancelReservationRequest | None = field(
            default=None,
            metadata={
                "name": "cancelReservationRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingConfirmBookingRecordRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingConfirmBookingRecordRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        confirm_booking_record_request: ConfirmBookingRecordRequest | None = field(
            default=None,
            metadata={
                "name": "confirmBookingRecordRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


class BookingDelayRepayRefund:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingDelayRepayRefundInput
    output = BookingDelayRepayRefundOutput


class BookingGeneratePaymentTokenRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingGeneratePaymentTokenRequestInput
    output = BookingGeneratePaymentTokenRequestOutput


@dataclass(frozen=True)
class BookingProcessReservationInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessReservationInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_reservation_request: ProcessReservationRequest | None = field(
            default=None,
            metadata={
                "name": "processReservationRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingReservationShoppingInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingReservationShoppingInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        reservation_shopping_request: ReservationShoppingRequest | None = field(
            default=None,
            metadata={
                "name": "reservationShoppingRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


class BookingRetrieveCancellationSummaryRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRetrieveCancellationSummaryRequestInput
    output = BookingRetrieveCancellationSummaryRequestOutput


class BookingSearchBookingsRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingSearchBookingsRequestInput
    output = BookingSearchBookingsRequestOutput


class BookingValidateDelayRepayRefundStatusRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingValidateDelayRepayRefundStatusRequestInput
    output = BookingValidateDelayRepayRefundStatusRequestOutput


@dataclass(frozen=True)
class CancelBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    refund_status: RequestStatusType | None = field(
        default=None,
        metadata={
            "name": "refundStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class CancelReservationResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ClaimValueDocumentResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    value_document: ValueDocumentType | None = field(
        default=None,
        metadata={
            "name": "valueDocument",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passenger_rights: PassengerRightsType | None = field(
        default=None,
        metadata={
            "name": "passengerRights",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ConfirmBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    claim_value_document_result: ClaimValueDocumentResultType | None = field(
        default=None,
        metadata={
            "name": "claimValueDocumentResult",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passenger_rights: PassengerRightsType | None = field(
        default=None,
        metadata={
            "name": "passengerRights",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class CreateBookingRecordRequestType(BaseBookingRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    passengers: Optional["CreateBookingRecordRequestType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    leg_solutions: LegSolutionsType | None = field(
        default=None,
        metadata={
            "name": "legSolutions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    prices: Optional["CreateBookingRecordRequestType.Prices"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    summated_fares: SummatedFareTypes | None = field(
        default=None,
        metadata={
            "name": "summatedFares",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    split_ticketing: SplitTicketingRequestType | None = field(
        default=None,
        metadata={
            "name": "splitTicketing",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    travel_pass_query: TravelPassQuery | None = field(
        default=None,
        metadata={
            "name": "travelPassQuery",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    transaction_fees: Optional["CreateBookingRecordRequestType.TransactionFees"] = (
        field(
            default=None,
            metadata={
                "name": "transactionFees",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )
    parameters: Optional["CreateBookingRecordRequestType.Parameters"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["CreateBookingRecordRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    external_identification: ExternalIdentificationType | None = field(
        default=None,
        metadata={
            "name": "externalIdentification",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fare_qualifiers: Optional["CreateBookingRecordRequestType.FareQualifiers"] = field(
        default=None,
        metadata={
            "name": "fareQualifiers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    agency_identifier: str | None = field(
        default=None,
        metadata={
            "name": "agencyIdentifier",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    outward_journey_and_fare_signatures: JourneyAndFareSignaturesType | None = field(
        default=None,
        metadata={
            "name": "outwardJourneyAndFareSignatures",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    return_journey_and_fare_signatures: JourneyAndFareSignaturesType | None = field(
        default=None,
        metadata={
            "name": "returnJourneyAndFareSignatures",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    rail_card_signatures: str | None = field(
        default=None,
        metadata={
            "name": "railCardSignatures",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    total_price: MoneyType | None = field(
        default=None,
        metadata={
            "name": "totalPrice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    nre_handoff_basket_request: Optional[
        "CreateBookingRecordRequestType.NreHandoffBasketRequest"
    ] = field(
        default=None,
        metadata={
            "name": "nreHandoffBasketRequest",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    campaign: CampaignType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list[PassengerType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Prices:
        point_to_point_price: list[PointToPointPriceType] = field(
            default_factory=list,
            metadata={
                "name": "pointToPointPrice",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class TransactionFees:
        transaction_fee: list[BookingTransactionFeeType] = field(
            default_factory=list,
            metadata={
                "name": "transactionFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Parameters:
        price_acceptance: Optional[
            "CreateBookingRecordRequestType.Parameters.PriceAcceptance"
        ] = field(
            default=None,
            metadata={
                "name": "priceAcceptance",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fare_acceptance: Optional[
            "CreateBookingRecordRequestType.Parameters.FareAcceptance"
        ] = field(
            default=None,
            metadata={
                "name": "fareAcceptance",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        shop_ancillary: bool | None = field(
            default=None,
            metadata={
                "name": "shopAncillary",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class PriceAcceptance:
            accept_any: bool | None = field(
                default=None,
                metadata={
                    "name": "acceptAny",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            accept_higher: PriceAcceptanceType | None = field(
                default=None,
                metadata={
                    "name": "acceptHigher",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
            accept_lower: PriceAcceptanceType | None = field(
                default=None,
                metadata={
                    "name": "acceptLower",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

        @dataclass(frozen=True)
        class FareAcceptance:
            type_value: FareAcceptanceType | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_pricing_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnPricingDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_optional_prices: Optional[
            "CreateBookingRecordRequestType.ResponseSpec.IncludeOptionalPrices"
        ] = field(
            default=None,
            metadata={
                "name": "includeOptionalPrices",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class IncludeOptionalPrices:
            reservations: bool | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            accommodations: bool | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            onboard_services: bool | None = field(
                default=None,
                metadata={
                    "name": "onboardServices",
                    "type": "Attribute",
                    "required": True,
                },
            )
            local_services: bool | None = field(
                default=None,
                metadata={
                    "name": "localServices",
                    "type": "Attribute",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class FareQualifiers:
        fare_qualifier: list[FareQualifierType] = field(
            default_factory=list,
            metadata={
                "name": "fareQualifier",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class NreHandoffBasketRequest:
        request_id: str | None = field(
            default=None,
            metadata={
                "name": "RequestID",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        request_meta_data: object | None = field(
            default=None,
            metadata={
                "name": "RequestMetaData",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        purchase_ticket_request: list[object] = field(
            default_factory=list,
            metadata={
                "name": "PurchaseTicketRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )
        basket_total: int | None = field(
            default=None,
            metadata={
                "name": "BasketTotal",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )


@dataclass(frozen=True)
class CreateBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    last_hold_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "lastHoldDateTime",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passenger_rights: PassengerRightsType | None = field(
        default=None,
        metadata={
            "name": "passengerRights",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ExchangeSearchRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    exchange_sets: Optional["ExchangeSearchRequestType.ExchangeSets"] = field(
        default=None,
        metadata={
            "name": "exchangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: Optional["ExchangeSearchRequestType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ExchangeSearchRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    equipment_type_restrictions: Optional[
        "ExchangeSearchRequestType.EquipmentTypeRestrictions"
    ] = field(
        default=None,
        metadata={
            "name": "equipmentTypeRestrictions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    interchange_adjustment: Optional[
        "ExchangeSearchRequestType.InterchangeAdjustment"
    ] = field(
        default=None,
        metadata={
            "name": "interchangeAdjustment",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    reduce_transfers: Optional["ExchangeSearchRequestType.ReduceTransfers"] = field(
        default=None,
        metadata={
            "name": "reduceTransfers",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ExchangeSets:
        exchange_set: list[ExchangeSearchRequestExchangeSetType] = field(
            default_factory=list,
            metadata={
                "name": "exchangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list["ExchangeSearchRequestType.Passengers.Passenger"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class Passenger:
            passenger_id: str | None = field(
                default=None,
                metadata={
                    "name": "passengerID",
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class ResponseSpec:
        include_commissions: bool | None = field(
            default=None,
            metadata={
                "name": "includeCommissions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        intermediate_points: ResponseSpecIntermediatePoints | None = field(
            default=None,
            metadata={
                "name": "intermediatePoints",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        valid_fare_types: ResponseSpecValidFareTypes | None = field(
            default=None,
            metadata={
                "name": "validFareTypes",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        maximum_number_of_solutions: int | None = field(
            default=None,
            metadata={
                "name": "maximumNumberOfSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        product_type: ResponseSpecProductType | None = field(
            default=None,
            metadata={
                "name": "productType",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_rules: bool | None = field(
            default=None,
            metadata={
                "name": "includeRules",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_optional_prices: Optional[
            "ExchangeSearchRequestType.ResponseSpec.IncludeOptionalPrices"
        ] = field(
            default=None,
            metadata={
                "name": "includeOptionalPrices",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class IncludeOptionalPrices:
            reservations: bool | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            accommodations: bool | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            onboard_services: bool | None = field(
                default=None,
                metadata={
                    "name": "onboardServices",
                    "type": "Attribute",
                    "required": True,
                },
            )
            local_services: bool | None = field(
                default=None,
                metadata={
                    "name": "localServices",
                    "type": "Attribute",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class EquipmentTypeRestrictions:
        equipment_type_restriction: list[
            "ExchangeSearchRequestType.EquipmentTypeRestrictions.EquipmentTypeRestriction"
        ] = field(
            default_factory=list,
            metadata={
                "name": "equipmentTypeRestriction",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

        @dataclass(frozen=True)
        class EquipmentTypeRestriction:
            code: EquipmentTypeRestrictionCode | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            type_value: EquipmentTypeRestrictionType | None = field(
                default=None,
                metadata={
                    "name": "type",
                    "type": "Attribute",
                    "required": True,
                },
            )

    @dataclass(frozen=True)
    class InterchangeAdjustment:
        add_minutes: int | None = field(
            default=None,
            metadata={
                "name": "addMinutes",
                "type": "Attribute",
                "required": True,
            },
        )

    @dataclass(frozen=True)
    class ReduceTransfers:
        set_reduction: bool | None = field(
            default=None,
            metadata={
                "name": "setReduction",
                "type": "Attribute",
            },
        )
        subtract_minutes: int | None = field(
            default=None,
            metadata={
                "name": "subtractMinutes",
                "type": "Attribute",
            },
        )


@dataclass(frozen=True)
class ExchangeSearchResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    results: Optional["ExchangeSearchResponseType.Results"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Results:
        exchange_sets: Optional["ExchangeSearchResponseType.Results.ExchangeSets"] = (
            field(
                default=None,
                metadata={
                    "name": "exchangeSets",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
        )
        passengers: Optional["ExchangeSearchResponseType.Results.Passengers"] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )

        @dataclass(frozen=True)
        class ExchangeSets:
            exchange_set: list[ExchangeSearchResponseExchangeSetType] = field(
                default_factory=list,
                metadata={
                    "name": "exchangeSet",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Passengers:
            passenger: list[PassengerSpecType] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )


@dataclass(frozen=True)
class ProcessExchangeRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    notes: Optional["ProcessExchangeRequestType.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order_notes: Optional["ProcessExchangeRequestType.OrderNotes"] = field(
        default=None,
        metadata={
            "name": "orderNotes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    exchange_sets: Optional["ProcessExchangeRequestType.ExchangeSets"] = field(
        default=None,
        metadata={
            "name": "exchangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: ExchangePassengersType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    selected_exchange_option: SelectedExchangeOptionType | None = field(
        default=None,
        metadata={
            "name": "selectedExchangeOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    payment: Optional["ProcessExchangeRequestType.Payment"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    additional_payments: Optional["ProcessExchangeRequestType.AdditionalPayments"] = (
        field(
            default=None,
            metadata={
                "name": "additionalPayments",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )
    service_fees: FeesType | None = field(
        default=None,
        metadata={
            "name": "serviceFees",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ProcessExchangeRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Notes:
        note: list[BookingNoteType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class OrderNotes:
        order_note: list[AddedOrderNoteType] = field(
            default_factory=list,
            metadata={
                "name": "orderNote",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ExchangeSets:
        exchange_set: list[BookingRequestExchangeSetType] = field(
            default_factory=list,
            metadata={
                "name": "exchangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Payment:
        form_of_payment: FormOfPaymentType | None = field(
            default=None,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card: AddPaymentCreditCardType | None = field(
            default=None,
            metadata={
                "name": "creditCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        check: CheckType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        on_account: OnAccountType | None = field(
            default=None,
            metadata={
                "name": "onAccount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        debit_card: AddPaymentDebitCardType | None = field(
            default=None,
            metadata={
                "name": "debitCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        voucher: AddPaymentVoucherType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        e_check: BaseEcheckType | None = field(
            default=None,
            metadata={
                "name": "eCheck",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        amount: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card_surcharge_fee: CreditCardSurchargeFeeType | None = field(
            default=None,
            metadata={
                "name": "creditCardSurchargeFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class AdditionalPayments:
        payment: list[ExchangePaymentType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
                "max_occurs": 3,
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ProcessExchangeResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ProcessReservationResponseType(BaseResponseType):
    """ProcessReservationResponseType is functionality under development and subject to
    change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ProcessReservationShoppingRequestType(BaseReservationRequestType):
    """ProcessReservationShoppingRequestType is functionality under development and
    subject to change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    reservation_type: ReservationType | None = field(
        default=None,
        metadata={
            "name": "reservationType",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    reservation_change_sets: Optional[
        "ProcessReservationShoppingRequestType.ReservationChangeSets"
    ] = field(
        default=None,
        metadata={
            "name": "reservationChangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ReservationChangeSets:
        reservation_change_set: list[ReservationChangeShoppingSetType] = field(
            default_factory=list,
            metadata={
                "name": "reservationChangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class ProcessReservationShoppingResponseType(BaseResponseType):
    """ProcessReservationShoppingResponseType is functionality under development and
    subject to change.

    Do not implement against this specification
    """

    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ProcessTravelPassExchangeRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    order_notes: AddedOrderNotesType | None = field(
        default=None,
        metadata={
            "name": "orderNotes",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    travel_pass_exchange_sets: Optional[
        "ProcessTravelPassExchangeRequestType.TravelPassExchangeSets"
    ] = field(
        default=None,
        metadata={
            "name": "travelPassExchangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: ExchangePassengersType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    selected_exchange_option: SelectedExchangeOptionType | None = field(
        default=None,
        metadata={
            "name": "selectedExchangeOption",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    payment: Optional["ProcessTravelPassExchangeRequestType.Payment"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    service_fees: FeesType | None = field(
        default=None,
        metadata={
            "name": "serviceFees",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["ProcessTravelPassExchangeRequestType.ResponseSpec"] = (
        field(
            default=None,
            metadata={
                "name": "responseSpec",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )

    @dataclass(frozen=True)
    class TravelPassExchangeSets:
        travel_pass_exchange_set: list[BookingRequestTravelPassExchangeSetType] = field(
            default_factory=list,
            metadata={
                "name": "travelPassExchangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Payment:
        form_of_payment: FormOfPaymentType | None = field(
            default=None,
            metadata={
                "name": "formOfPayment",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card: AddPaymentCreditCardType | None = field(
            default=None,
            metadata={
                "name": "creditCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        check: CheckType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        on_account: OnAccountType | None = field(
            default=None,
            metadata={
                "name": "onAccount",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        debit_card: AddPaymentDebitCardType | None = field(
            default=None,
            metadata={
                "name": "debitCard",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        voucher: AddPaymentVoucherType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        e_check: BaseEcheckType | None = field(
            default=None,
            metadata={
                "name": "eCheck",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        amount: MoneyType | None = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        credit_card_surcharge_fee: CreditCardSurchargeFeeType | None = field(
            default=None,
            metadata={
                "name": "creditCardSurchargeFee",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class RecordFinancialTransactionResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class RedeliverValueDocumentResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    delivery_status: Optional["RedeliverValueDocumentResponseType.DeliveryStatus"] = (
        field(
            default=None,
            metadata={
                "name": "deliveryStatus",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
    )
    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class DeliveryStatus:
        direct_delivery_requested: bool | None = field(
            default=None,
            metadata={
                "name": "directDeliveryRequested",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        value_document_url: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentUrl"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentURL",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_pdf: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentPdf"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentPDF",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_etickets: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentEtickets"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentETickets",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_eticket_pdfs: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentEticketPdfs"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentETicketPdfs",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_mtickets: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentMtickets"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentMTickets",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_urls: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentUrls"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentURLS",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_etickets_with_urls: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentEticketsWithUrls"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentETicketsWithUrls",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        value_document_eticket_barcode_pdfs: Optional[
            "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentEticketBarcodePdfs"
        ] = field(
            default=None,
            metadata={
                "name": "valueDocumentETicketBarcodePdfs",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )

        @dataclass(frozen=True)
        class ValueDocumentEticketBarcodePdfs:
            e_ticket_pdfs: list[ValueDocumentEticketPdfType] = field(
                default_factory=list,
                metadata={
                    "name": "eTicketPdfs",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )

        @dataclass(frozen=True)
        class ValueDocumentUrl:
            value: str = field(
                default="",
                metadata={
                    "required": True,
                },
            )
            expiration_date_time: XmlDateTime | None = field(
                default=None,
                metadata={
                    "name": "expirationDateTime",
                    "type": "Attribute",
                },
            )

        @dataclass(frozen=True)
        class ValueDocumentPdf:
            value: bytes | None = field(
                default=None,
                metadata={
                    "required": True,
                    "format": "base64",
                },
            )
            encoding: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )

        @dataclass(frozen=True)
        class ValueDocumentEtickets:
            e_tickets: list[ValueDocumentEticketType] = field(
                default_factory=list,
                metadata={
                    "name": "eTickets",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class ValueDocumentEticketPdfs:
            e_ticket_pdfs: list[ValueDocumentEticketPdfType] = field(
                default_factory=list,
                metadata={
                    "name": "eTicketPdfs",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class ValueDocumentMtickets:
            m_tickets: list[ValueDocumentMticketType] = field(
                default_factory=list,
                metadata={
                    "name": "mTickets",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class ValueDocumentUrls:
            value_document_url: list[
                "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentUrls.ValueDocumentUrl"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "valueDocumentURL",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class ValueDocumentUrl:
                value: str = field(
                    default="",
                    metadata={
                        "required": True,
                    },
                )
                expiration_date_time: XmlDateTime | None = field(
                    default=None,
                    metadata={
                        "name": "expirationDateTime",
                        "type": "Attribute",
                    },
                )

        @dataclass(frozen=True)
        class ValueDocumentEticketsWithUrls:
            value_document_urls: Optional[
                "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentEticketsWithUrls.ValueDocumentUrls"
            ] = field(
                default=None,
                metadata={
                    "name": "valueDocumentURLS",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "required": True,
                },
            )
            e_tickets: list[ValueDocumentEticketType] = field(
                default_factory=list,
                metadata={
                    "name": "eTickets",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

            @dataclass(frozen=True)
            class ValueDocumentUrls:
                value_document_url: list[
                    "RedeliverValueDocumentResponseType.DeliveryStatus.ValueDocumentEticketsWithUrls.ValueDocumentUrls.ValueDocumentUrl"
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "valueDocumentURL",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                        "min_occurs": 1,
                    },
                )

                @dataclass(frozen=True)
                class ValueDocumentUrl:
                    value: str = field(
                        default="",
                        metadata={
                            "required": True,
                        },
                    )
                    expiration_date_time: XmlDateTime | None = field(
                        default=None,
                        metadata={
                            "name": "expirationDateTime",
                            "type": "Attribute",
                        },
                    )


@dataclass(frozen=True)
class RefundBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class RetrieveBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: Optional["RetrieveBookingRecordResponseType.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passenger_rights: PassengerRightsType | None = field(
        default=None,
        metadata={
            "name": "passengerRights",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Notes:
        note: list[BookingNoteType] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class RetrieveExchangeSummaryRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    exchange_sets: Optional["RetrieveExchangeSummaryRequestType.ExchangeSets"] = field(
        default=None,
        metadata={
            "name": "exchangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: ExchangePassengersType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    service_fees: FeesType | None = field(
        default=None,
        metadata={
            "name": "serviceFees",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    response_spec: Optional["RetrieveExchangeSummaryRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class ExchangeSets:
        exchange_set: list[BookingRequestExchangeSetType] = field(
            default_factory=list,
            metadata={
                "name": "exchangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class RetrieveExchangeSummaryResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    exchange_summary: ExchangeSummaryType | None = field(
        default=None,
        metadata={
            "name": "exchangeSummary",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    leg_solutions: LegSolutionsType | None = field(
        default=None,
        metadata={
            "name": "legSolutions",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class RetrieveTravelPassExchangeSummaryRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    travel_pass_exchange_sets: Optional[
        "RetrieveTravelPassExchangeSummaryRequestType.TravelPassExchangeSets"
    ] = field(
        default=None,
        metadata={
            "name": "travelPassExchangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: ExchangePassengersType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    service_fees: FeesType | None = field(
        default=None,
        metadata={
            "name": "serviceFees",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    fulfillment_information: FulfillmentInformationType | None = field(
        default=None,
        metadata={
            "name": "fulfillmentInformation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    response_spec: Optional[
        "RetrieveTravelPassExchangeSummaryRequestType.ResponseSpec"
    ] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class TravelPassExchangeSets:
        travel_pass_exchange_set: list[BookingRequestTravelPassExchangeSetType] = field(
            default_factory=list,
            metadata={
                "name": "travelPassExchangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class ResponseSpec:
        return_reservation_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnReservationDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class RetrieveTravelPassExchangeSummaryResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    exchange_summary: ExchangeSummaryType | None = field(
        default=None,
        metadata={
            "name": "exchangeSummary",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class ReturnValueDocumentResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class TravelPassExchangeSearchRequestType(AuditableRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    record_locator: str | None = field(
        default=None,
        metadata={
            "name": "recordLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    order_locator: str | None = field(
        default=None,
        metadata={
            "name": "orderLocator",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    travel_pass_exchange_sets: Optional[
        "TravelPassExchangeSearchRequestType.TravelPassExchangeSets"
    ] = field(
        default=None,
        metadata={
            "name": "travelPassExchangeSets",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
            "required": True,
        },
    )
    passengers: Optional["TravelPassExchangeSearchRequestType.Passengers"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    response_spec: Optional["TravelPassExchangeSearchRequestType.ResponseSpec"] = field(
        default=None,
        metadata={
            "name": "responseSpec",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class TravelPassExchangeSets:
        travel_pass_exchange_set: list[
            TravelPassExchangeSearchRequestExchangeSetType
        ] = field(
            default_factory=list,
            metadata={
                "name": "travelPassExchangeSet",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "min_occurs": 1,
            },
        )

    @dataclass(frozen=True)
    class Passengers:
        passenger: list["TravelPassExchangeSearchRequestType.Passengers.Passenger"] = (
            field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )
        )

        @dataclass(frozen=True)
        class Passenger:
            passenger_id: str | None = field(
                default=None,
                metadata={
                    "name": "passengerID",
                    "type": "Attribute",
                },
            )

    @dataclass(frozen=True)
    class ResponseSpec:
        include_commissions: bool | None = field(
            default=None,
            metadata={
                "name": "includeCommissions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        valid_fare_types: ResponseSpecValidFareTypes | None = field(
            default=None,
            metadata={
                "name": "validFareTypes",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        maximum_number_of_solutions: int | None = field(
            default=None,
            metadata={
                "name": "maximumNumberOfSolutions",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        include_rules: bool | None = field(
            default=None,
            metadata={
                "name": "includeRules",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        return_carbon_data_comparisons_details: bool | None = field(
            default=None,
            metadata={
                "name": "returnCarbonDataComparisonsDetails",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class TravelPassExchangeSearchResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    results: Optional["TravelPassExchangeSearchResponseType.Results"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )

    @dataclass(frozen=True)
    class Results:
        travel_pass_exchange_sets: Optional[
            "TravelPassExchangeSearchResponseType.Results.TravelPassExchangeSets"
        ] = field(
            default=None,
            metadata={
                "name": "travelPassExchangeSets",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )
        passengers: Optional[
            "TravelPassExchangeSearchResponseType.Results.Passengers"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "required": True,
            },
        )

        @dataclass(frozen=True)
        class TravelPassExchangeSets:
            travel_pass_exchange_set: list[
                TravelPassExchangeSearchResponseExchangeSetType
            ] = field(
                default_factory=list,
                metadata={
                    "name": "travelPassExchangeSet",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )

        @dataclass(frozen=True)
        class Passengers:
            passenger: list[PassengerSpecType] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "min_occurs": 1,
                },
            )


@dataclass(frozen=True)
class UpdateBookingRecordResponseType(BaseResponseType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"

    booking_record: BookingRecordType | None = field(
        default=None,
        metadata={
            "name": "bookingRecord",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    notes: BookingNotesType | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )
    passenger_rights: PassengerRightsType | None = field(
        default=None,
        metadata={
            "name": "passengerRights",
            "type": "Element",
            "namespace": "http://railgds.net/ws/booking",
        },
    )


@dataclass(frozen=True)
class AddOrderToBookingRecordRequest(AddOrderToBookingRecordRequestType):
    class Meta:
        name = "addOrderToBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class GetIntermediateTravelPointsRequest(GetIntermediateTravelPointsRequestType):
    class Meta:
        name = "getIntermediateTravelPointsRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ReservationSearchResponse(ReservationSearchResponseType):
    class Meta:
        name = "reservationSearchResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ReservationShoppingResponse(ReservationShoppingResponseType):
    class Meta:
        name = "reservationShoppingResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class UpdateBookingRecordRequest(UpdateBookingRecordRequestType):
    class Meta:
        name = "updateBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ValidateBookingRecordInformationResponse(
    ValidateBookingRecordInformationResponseType,
):
    class Meta:
        name = "validateBookingRecordInformationResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class BookingAddOrderToBookingRecordRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAddOrderToBookingRecordRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        add_order_to_booking_record_request: AddOrderToBookingRecordRequest | None = (
            field(
                default=None,
                metadata={
                    "name": "addOrderToBookingRecordRequest",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )


class BookingAuthenticatePayerRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAuthenticatePayerRequestInput
    output = BookingAuthenticatePayerRequestOutput


class BookingAuthenticatePayerV2Request:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAuthenticatePayerV2RequestInput
    output = BookingAuthenticatePayerV2RequestOutput


@dataclass(frozen=True)
class BookingGetIntermediateTravelPointsInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingGetIntermediateTravelPointsInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        get_intermediate_travel_points_request: (
            GetIntermediateTravelPointsRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "getIntermediateTravelPointsRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingReservationShoppingOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingReservationShoppingOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        reservation_shopping_response: ReservationShoppingResponse | None = field(
            default=None,
            metadata={
                "name": "reservationShoppingResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingReservationShoppingOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingReservationShoppingOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingUpdateBookingRecordRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingUpdateBookingRecordRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        update_booking_record_request: UpdateBookingRecordRequest | None = field(
            default=None,
            metadata={
                "name": "updateBookingRecordRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingValidateBookingRecordInformationRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingValidateBookingRecordInformationRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        validate_booking_record_information_response: (
            ValidateBookingRecordInformationResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "validateBookingRecordInformationResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional[
            "BookingValidateBookingRecordInformationRequestOutput.Body.Fault"
        ] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingValidateBookingRecordInformationRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class ValidateBookingRecordInformationRequestType(CreateBookingRecordRequestType):
    class Meta:
        target_namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AddOrderToBookingRecordResponse(AddOrderToBookingRecordResponseType):
    class Meta:
        name = "addOrderToBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AddPaymentResponse(AddPaymentResponseType):
    class Meta:
        name = "addPaymentResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class AdjustCostAndRevenueResponse(AdjustCostAndRevenueResponseType):
    class Meta:
        name = "adjustCostAndRevenueResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class CancelBookingRecordResponse(CancelBookingRecordResponseType):
    class Meta:
        name = "cancelBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class CancelReservationResponse(CancelReservationResponseType):
    class Meta:
        name = "cancelReservationResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ClaimValueDocumentResponse(ClaimValueDocumentResponseType):
    class Meta:
        name = "claimValueDocumentResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ConfirmBookingRecordResponse(ConfirmBookingRecordResponseType):
    class Meta:
        name = "confirmBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class CreateBookingRecordRequest(CreateBookingRecordRequestType):
    class Meta:
        name = "createBookingRecordRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class CreateBookingRecordResponse(CreateBookingRecordResponseType):
    class Meta:
        name = "createBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ExchangeSearchRequest(ExchangeSearchRequestType):
    class Meta:
        name = "exchangeSearchRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ExchangeSearchResponse(ExchangeSearchResponseType):
    class Meta:
        name = "exchangeSearchResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessExchangeRequest(ProcessExchangeRequestType):
    class Meta:
        name = "processExchangeRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessExchangeResponse(ProcessExchangeResponseType):
    class Meta:
        name = "processExchangeResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessReservationResponse(ProcessReservationResponseType):
    class Meta:
        name = "processReservationResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessReservationShoppingRequest(ProcessReservationShoppingRequestType):
    class Meta:
        name = "processReservationShoppingRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessReservationShoppingResponse(ProcessReservationShoppingResponseType):
    class Meta:
        name = "processReservationShoppingResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessTravelPassExchangeRequest(ProcessTravelPassExchangeRequestType):
    class Meta:
        name = "processTravelPassExchangeRequest"
        nillable = True
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ProcessTravelPassExchangeResponse(ProcessExchangeResponseType):
    class Meta:
        name = "processTravelPassExchangeResponse"
        nillable = True
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RecordFinancialTransactionResponse(RecordFinancialTransactionResponseType):
    class Meta:
        name = "recordFinancialTransactionResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RedeliverValueDocumentResponse(RedeliverValueDocumentResponseType):
    class Meta:
        name = "redeliverValueDocumentResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RefundBookingRecordResponse(RefundBookingRecordResponseType):
    class Meta:
        name = "refundBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveBookingRecordResponse(RetrieveBookingRecordResponseType):
    class Meta:
        name = "retrieveBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveExchangeSummaryRequest(RetrieveExchangeSummaryRequestType):
    class Meta:
        name = "retrieveExchangeSummaryRequest"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveExchangeSummaryResponse(RetrieveExchangeSummaryResponseType):
    class Meta:
        name = "retrieveExchangeSummaryResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveTravelPassExchangeSummaryRequest(
    RetrieveTravelPassExchangeSummaryRequestType,
):
    class Meta:
        name = "retrieveTravelPassExchangeSummaryRequest"
        nillable = True
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class RetrieveTravelPassExchangeSummaryResponse(
    RetrieveTravelPassExchangeSummaryResponseType,
):
    class Meta:
        name = "retrieveTravelPassExchangeSummaryResponse"
        nillable = True
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class ReturnValueDocumentResponse(ReturnValueDocumentResponseType):
    class Meta:
        name = "returnValueDocumentResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class TravelPassExchangeSearchRequest(TravelPassExchangeSearchRequestType):
    class Meta:
        name = "travelPassExchangeSearchRequest"
        nillable = True
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class TravelPassExchangeSearchResponse(TravelPassExchangeSearchResponseType):
    class Meta:
        name = "travelPassExchangeSearchResponse"
        nillable = True
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class UpdateBookingRecordResponse(UpdateBookingRecordResponseType):
    class Meta:
        name = "updateBookingRecordResponse"
        namespace = "http://railgds.net/ws/booking"


@dataclass(frozen=True)
class BookingAddOrderToBookingRecordRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAddOrderToBookingRecordRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        add_order_to_booking_record_response: AddOrderToBookingRecordResponse | None = (
            field(
                default=None,
                metadata={
                    "name": "addOrderToBookingRecordResponse",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        fault: Optional["BookingAddOrderToBookingRecordRequestOutput.Body.Fault"] = (
            field(
                default=None,
                metadata={
                    "name": "Fault",
                    "type": "Element",
                },
            )
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingAddOrderToBookingRecordRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingAddPaymentRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAddPaymentRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        add_payment_response: AddPaymentResponse | None = field(
            default=None,
            metadata={
                "name": "addPaymentResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingAddPaymentRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingAddPaymentRequestOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingAdjustCostAndRevenueRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingAdjustCostAndRevenueRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        adjust_cost_and_revenue_response: AdjustCostAndRevenueResponse | None = field(
            default=None,
            metadata={
                "name": "adjustCostAndRevenueResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingAdjustCostAndRevenueRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingAdjustCostAndRevenueRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingCancelBookingRecordRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingCancelBookingRecordRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        cancel_booking_record_response: CancelBookingRecordResponse | None = field(
            default=None,
            metadata={
                "name": "cancelBookingRecordResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingCancelBookingRecordRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingCancelBookingRecordRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingCancelReservationOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingCancelReservationOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        cancel_reservation_response: CancelReservationResponse | None = field(
            default=None,
            metadata={
                "name": "cancelReservationResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingCancelReservationOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingCancelReservationOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingClaimValueDocumentRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingClaimValueDocumentRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        claim_value_document_response: ClaimValueDocumentResponse | None = field(
            default=None,
            metadata={
                "name": "claimValueDocumentResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingClaimValueDocumentRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingClaimValueDocumentRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingConfirmBookingRecordRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingConfirmBookingRecordRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        confirm_booking_record_response: ConfirmBookingRecordResponse | None = field(
            default=None,
            metadata={
                "name": "confirmBookingRecordResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingConfirmBookingRecordRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingConfirmBookingRecordRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingCreateBookingRecordInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingCreateBookingRecordInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        create_booking_record_request: CreateBookingRecordRequest | None = field(
            default=None,
            metadata={
                "name": "createBookingRecordRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingCreateBookingRecordOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingCreateBookingRecordOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        create_booking_record_response: CreateBookingRecordResponse | None = field(
            default=None,
            metadata={
                "name": "createBookingRecordResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingCreateBookingRecordOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingCreateBookingRecordOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingExchangeSearchInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingExchangeSearchInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        exchange_search_request: ExchangeSearchRequest | None = field(
            default=None,
            metadata={
                "name": "exchangeSearchRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingExchangeSearchOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingExchangeSearchOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        exchange_search_response: ExchangeSearchResponse | None = field(
            default=None,
            metadata={
                "name": "exchangeSearchResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingExchangeSearchOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )


class BookingGetIntermediateTravelPoints:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingGetIntermediateTravelPointsInput
    output = BookingGetIntermediateTravelPointsOutput


@dataclass(frozen=True)
class BookingProcessExchangeInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessExchangeInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_exchange_request: ProcessExchangeRequest | None = field(
            default=None,
            metadata={
                "name": "processExchangeRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingProcessExchangeOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessExchangeOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_exchange_response: ProcessExchangeResponse | None = field(
            default=None,
            metadata={
                "name": "processExchangeResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingProcessExchangeOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingProcessExchangeOutput.Body.Fault.Detail"] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingProcessReservationShoppingInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessReservationShoppingInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_reservation_shopping_request: (
            ProcessReservationShoppingRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "processReservationShoppingRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


@dataclass(frozen=True)
class BookingProcessReservationShoppingOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessReservationShoppingOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_reservation_shopping_response: (
            ProcessReservationShoppingResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "processReservationShoppingResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingProcessReservationShoppingOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingProcessReservationShoppingOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingProcessReservationOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessReservationOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_reservation_response: ProcessReservationResponse | None = field(
            default=None,
            metadata={
                "name": "processReservationResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingProcessReservationOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional["BookingProcessReservationOutput.Body.Fault.Detail"] = (
                field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "",
                    },
                )
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingProcessTravelPassExchangeInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessTravelPassExchangeInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_travel_pass_exchange_request: (
            ProcessTravelPassExchangeRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "processTravelPassExchangeRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "nillable": True,
            },
        )


@dataclass(frozen=True)
class BookingProcessTravelPassExchangeOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingProcessTravelPassExchangeOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        process_travel_pass_exchange_response: (
            ProcessTravelPassExchangeResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "processTravelPassExchangeResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "nillable": True,
            },
        )
        fault: Optional["BookingProcessTravelPassExchangeOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingProcessTravelPassExchangeOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRecordFinancialTransactionRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRecordFinancialTransactionRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        record_financial_transaction_response: (
            RecordFinancialTransactionResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "recordFinancialTransactionResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingRecordFinancialTransactionRequestOutput.Body.Fault"] = (
            field(
                default=None,
                metadata={
                    "name": "Fault",
                    "type": "Element",
                },
            )
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRecordFinancialTransactionRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRedeliverValueDocumentRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRedeliverValueDocumentRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        redeliver_value_document_response: RedeliverValueDocumentResponse | None = (
            field(
                default=None,
                metadata={
                    "name": "redeliverValueDocumentResponse",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        fault: Optional["BookingRedeliverValueDocumentRequestOutput.Body.Fault"] = (
            field(
                default=None,
                metadata={
                    "name": "Fault",
                    "type": "Element",
                },
            )
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRedeliverValueDocumentRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRefundBookingRecordRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRefundBookingRecordRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        refund_booking_record_response: RefundBookingRecordResponse | None = field(
            default=None,
            metadata={
                "name": "refundBookingRecordResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingRefundBookingRecordRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRefundBookingRecordRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


class BookingReservationShopping:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingReservationShoppingInput
    output = BookingReservationShoppingOutput


@dataclass(frozen=True)
class BookingRetrieveBookingRecordRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveBookingRecordRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_booking_record_response: RetrieveBookingRecordResponse | None = field(
            default=None,
            metadata={
                "name": "retrieveBookingRecordResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingRetrieveBookingRecordRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRetrieveBookingRecordRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRetrieveExchangeSummaryInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveExchangeSummaryInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_exchange_summary_request: RetrieveExchangeSummaryRequest | None = (
            field(
                default=None,
                metadata={
                    "name": "retrieveExchangeSummaryRequest",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )


@dataclass(frozen=True)
class BookingRetrieveExchangeSummaryOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveExchangeSummaryOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_exchange_summary_response: RetrieveExchangeSummaryResponse | None = (
            field(
                default=None,
                metadata={
                    "name": "retrieveExchangeSummaryResponse",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                },
            )
        )
        fault: Optional["BookingRetrieveExchangeSummaryOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRetrieveExchangeSummaryOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingRetrieveTravelPassExchangeSummaryInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveTravelPassExchangeSummaryInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_travel_pass_exchange_summary_request: (
            RetrieveTravelPassExchangeSummaryRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "retrieveTravelPassExchangeSummaryRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "nillable": True,
            },
        )


@dataclass(frozen=True)
class BookingRetrieveTravelPassExchangeSummaryOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingRetrieveTravelPassExchangeSummaryOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        retrieve_travel_pass_exchange_summary_response: (
            RetrieveTravelPassExchangeSummaryResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "retrieveTravelPassExchangeSummaryResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "nillable": True,
            },
        )
        fault: Optional["BookingRetrieveTravelPassExchangeSummaryOutput.Body.Fault"] = (
            field(
                default=None,
                metadata={
                    "name": "Fault",
                    "type": "Element",
                },
            )
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingRetrieveTravelPassExchangeSummaryOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingReturnValueDocumentRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingReturnValueDocumentRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        return_value_document_response: ReturnValueDocumentResponse | None = field(
            default=None,
            metadata={
                "name": "returnValueDocumentResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingReturnValueDocumentRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingReturnValueDocumentRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class BookingTravelPassExchangeSearchInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingTravelPassExchangeSearchInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        travel_pass_exchange_search_request: TravelPassExchangeSearchRequest | None = (
            field(
                default=None,
                metadata={
                    "name": "travelPassExchangeSearchRequest",
                    "type": "Element",
                    "namespace": "http://railgds.net/ws/booking",
                    "nillable": True,
                },
            )
        )


@dataclass(frozen=True)
class BookingTravelPassExchangeSearchOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingTravelPassExchangeSearchOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        travel_pass_exchange_search_response: (
            TravelPassExchangeSearchResponse | None
        ) = field(
            default=None,
            metadata={
                "name": "travelPassExchangeSearchResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
                "nillable": True,
            },
        )
        fault: Optional["BookingTravelPassExchangeSearchOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )


@dataclass(frozen=True)
class BookingUpdateBookingRecordRequestOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingUpdateBookingRecordRequestOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        update_booking_record_response: UpdateBookingRecordResponse | None = field(
            default=None,
            metadata={
                "name": "updateBookingRecordResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )
        fault: Optional["BookingUpdateBookingRecordRequestOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass(frozen=True)
        class Fault:
            faultcode: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: str | None = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[
                "BookingUpdateBookingRecordRequestOutput.Body.Fault.Detail"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

            @dataclass(frozen=True)
            class Detail:
                booking_services_exception: BookingServicesException | None = field(
                    default=None,
                    metadata={
                        "name": "BookingServicesException",
                        "type": "Element",
                        "namespace": "http://railgds.net/ws/booking",
                    },
                )


@dataclass(frozen=True)
class ValidateBookingRecordInformationRequest(
    ValidateBookingRecordInformationRequestType,
):
    class Meta:
        name = "validateBookingRecordInformationRequest"
        namespace = "http://railgds.net/ws/booking"


class BookingAddOrderToBookingRecordRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAddOrderToBookingRecordRequestInput
    output = BookingAddOrderToBookingRecordRequestOutput


class BookingAddPaymentRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAddPaymentRequestInput
    output = BookingAddPaymentRequestOutput


class BookingAdjustCostAndRevenueRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingAdjustCostAndRevenueRequestInput
    output = BookingAdjustCostAndRevenueRequestOutput


class BookingCancelBookingRecordRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingCancelBookingRecordRequestInput
    output = BookingCancelBookingRecordRequestOutput


class BookingCancelReservation:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingCancelReservationInput
    output = BookingCancelReservationOutput


class BookingClaimValueDocumentRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingClaimValueDocumentRequestInput
    output = BookingClaimValueDocumentRequestOutput


class BookingConfirmBookingRecordRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingConfirmBookingRecordRequestInput
    output = BookingConfirmBookingRecordRequestOutput


class BookingCreateBookingRecord:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingCreateBookingRecordInput
    output = BookingCreateBookingRecordOutput


class BookingExchangeSearch:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingExchangeSearchInput
    output = BookingExchangeSearchOutput


class BookingProcessExchange:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingProcessExchangeInput
    output = BookingProcessExchangeOutput


class BookingProcessReservation:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingProcessReservationInput
    output = BookingProcessReservationOutput


class BookingProcessReservationShopping:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingProcessReservationShoppingInput
    output = BookingProcessReservationShoppingOutput


class BookingProcessTravelPassExchange:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingProcessTravelPassExchangeInput
    output = BookingProcessTravelPassExchangeOutput


class BookingRecordFinancialTransactionRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRecordFinancialTransactionRequestInput
    output = BookingRecordFinancialTransactionRequestOutput


class BookingRedeliverValueDocumentRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRedeliverValueDocumentRequestInput
    output = BookingRedeliverValueDocumentRequestOutput


class BookingRefundBookingRecordRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRefundBookingRecordRequestInput
    output = BookingRefundBookingRecordRequestOutput


class BookingRetrieveBookingRecordRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRetrieveBookingRecordRequestInput
    output = BookingRetrieveBookingRecordRequestOutput


class BookingRetrieveExchangeSummary:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRetrieveExchangeSummaryInput
    output = BookingRetrieveExchangeSummaryOutput


class BookingRetrieveTravelPassExchangeSummary:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingRetrieveTravelPassExchangeSummaryInput
    output = BookingRetrieveTravelPassExchangeSummaryOutput


class BookingReturnValueDocumentRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingReturnValueDocumentRequestInput
    output = BookingReturnValueDocumentRequestOutput


class BookingTravelPassExchangeSearch:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingTravelPassExchangeSearchInput
    output = BookingTravelPassExchangeSearchOutput


class BookingUpdateBookingRecordRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingUpdateBookingRecordRequestInput
    output = BookingUpdateBookingRecordRequestOutput


@dataclass(frozen=True)
class BookingValidateBookingRecordInformationRequestInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/booking"

    body: Optional["BookingValidateBookingRecordInformationRequestInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Body:
        validate_booking_record_information_request: (
            ValidateBookingRecordInformationRequest | None
        ) = field(
            default=None,
            metadata={
                "name": "validateBookingRecordInformationRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/booking",
            },
        )


class BookingValidateBookingRecordInformationRequest:
    style = "document"
    location = "http://xml-cert-nex.railgds.net/booking-ws/services/Booking/v2"
    transport = "http://schemas.xmlsoap.org/soap/http"
    input = BookingValidateBookingRecordInformationRequestInput
    output = BookingValidateBookingRecordInformationRequestOutput
