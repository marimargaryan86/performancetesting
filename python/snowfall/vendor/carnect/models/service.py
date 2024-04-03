from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlDateTime, XmlDuration, XmlPeriod

__NAMESPACE__ = "http://www.opentravel.org/OTA/2003/05"


class ActionType(Enum):
    ADD_UPDATE = "Add-Update"
    CANCEL = "Cancel"
    DELETE = "Delete"
    ADD = "Add"
    REPLACE = "Replace"


class AdditionalQualificationMethod(Enum):
    RT_AIRLINE_TICKET = "RT_AirlineTicket"
    CREDIT_CARD = "CreditCard"
    PASSPORT_AND_RETURN_TKT = "PassportAndReturnTkt"


class AddressTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class AddressTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class AdvanceBookingOffsetDropTime(Enum):
    BEFORE_ARRIVAL = "BeforeArrival"
    AFTER_BOOKING = "AfterBooking"
    AFTER_CONFIRMATION = "AfterConfirmation"


@dataclass
class ArrayOfAcceptablePaymentCardsInfoTypeAcceptablePaymentCard:
    acceptable_payment_card: list[
        "ArrayOfAcceptablePaymentCardsInfoTypeAcceptablePaymentCard.AcceptablePaymentCard"
    ] = field(
        default_factory=list,
        metadata={
            "name": "AcceptablePaymentCard",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class AcceptablePaymentCard:
        card_type: str | None = field(
            default=None,
            metadata={
                "name": "CardType",
                "type": "Attribute",
            },
        )
        card_name: str | None = field(
            default=None,
            metadata={
                "name": "CardName",
                "type": "Attribute",
            },
        )
        usage_percentage: Decimal | None = field(
            default=None,
            metadata={
                "name": "UsagePercentage",
                "type": "Attribute",
            },
        )
        usage_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "UsageAmount",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfOperationScheduleTypeOperationTime:
    operation_time: list["ArrayOfOperationScheduleTypeOperationTime.OperationTime"] = (
        field(
            default_factory=list,
            metadata={
                "name": "OperationTime",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
    )

    @dataclass
    class OperationTime:
        mon: bool | None = field(
            default=None,
            metadata={
                "name": "Mon",
                "type": "Attribute",
            },
        )
        tue: bool | None = field(
            default=None,
            metadata={
                "name": "Tue",
                "type": "Attribute",
            },
        )
        weds: bool | None = field(
            default=None,
            metadata={
                "name": "Weds",
                "type": "Attribute",
            },
        )
        thur: bool | None = field(
            default=None,
            metadata={
                "name": "Thur",
                "type": "Attribute",
            },
        )
        fri: bool | None = field(
            default=None,
            metadata={
                "name": "Fri",
                "type": "Attribute",
            },
        )
        sat: bool | None = field(
            default=None,
            metadata={
                "name": "Sat",
                "type": "Attribute",
            },
        )
        sun: bool | None = field(
            default=None,
            metadata={
                "name": "Sun",
                "type": "Attribute",
            },
        )
        start: str | None = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: str | None = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: str | None = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )
        additional_operation_info_code: str | None = field(
            default=None,
            metadata={
                "name": "AdditionalOperationInfoCode",
                "type": "Attribute",
            },
        )
        frequency: str | None = field(
            default=None,
            metadata={
                "name": "Frequency",
                "type": "Attribute",
            },
        )
        text: str | None = field(
            default=None,
            metadata={
                "name": "Text",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfString:
    additional_person_name: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AdditionalPersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleAvailRqadditionalInfoTypeCoveragePref:
    class Meta:
        name = "ArrayOfVehicleAvailRQAdditionalInfoTypeCoveragePref"

    coverage_pref: list[object] = field(
        default_factory=list,
        metadata={
            "name": "CoveragePref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleChargeTypeTaxAmount:
    tax_amount: list["ArrayOfVehicleChargeTypeTaxAmount.TaxAmount"] = field(
        default_factory=list,
        metadata={
            "name": "TaxAmount",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class TaxAmount:
        total: Decimal | None = field(
            default=None,
            metadata={
                "name": "Total",
                "type": "Attribute",
                "required": True,
            },
        )
        currency_code: str | None = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        tax_code: str | None = field(
            default=None,
            metadata={
                "name": "TaxCode",
                "type": "Attribute",
            },
        )
        percentage: Decimal | None = field(
            default=None,
            metadata={
                "name": "Percentage",
                "type": "Attribute",
            },
        )
        description: str | None = field(
            default=None,
            metadata={
                "name": "Description",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleReservationRqadditionalInfoTypeCoveragePref:
    class Meta:
        name = "ArrayOfVehicleReservationRQAdditionalInfoTypeCoveragePref"

    coverage_pref: list[object] = field(
        default_factory=list,
        metadata={
            "name": "CoveragePref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


class BankAcctTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class BankAcctTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class CalculationApplicability(Enum):
    FROM_PICKUP_LOCATION = "FromPickupLocation"
    FROM_DROPOFF_LOCATION = "FromDropoffLocation"
    BEFORE_PICKUP = "BeforePickup"
    AFTER_DROPOFF = "AfterDropoff"


class CancelRuleTypeType(Enum):
    REFUND = "Refund"
    CHARGE = "Charge"
    FORFEITURE = "Forfeiture"


@dataclass
class CompanyNameType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    company_short_name: str | None = field(
        default=None,
        metadata={
            "name": "CompanyShortName",
            "type": "Attribute",
        },
    )
    travel_sector: str | None = field(
        default=None,
        metadata={
            "name": "TravelSector",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: str | None = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )
    division: str | None = field(
        default=None,
        metadata={
            "name": "Division",
            "type": "Attribute",
        },
    )
    department: str | None = field(
        default=None,
        metadata={
            "name": "Department",
            "type": "Attribute",
        },
    )


class ContactPersonTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class ContactPersonTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


@dataclass
class CountryNameType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )


@dataclass
class CoverageType:
    details: list["CoveragePricedType"] = field(
        default_factory=list,
        metadata={
            "name": "Details",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    coverage_type: str | None = field(
        default=None,
        metadata={
            "name": "CoverageType",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )


class CustomerTypeGender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class DayOfWeekType(Enum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"


class DeadlineOffsetDropTime(Enum):
    BEFORE_ARRIVAL = "BeforeArrival"
    AFTER_BOOKING = "AfterBooking"
    AFTER_CONFIRMATION = "AfterConfirmation"


class DirectBillTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class DirectBillTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class DistanceUnitNameType(Enum):
    MILE = "Mile"
    KM = "Km"
    BLOCK = "Block"


class DocumentTypeGender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class DocumentTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class DocumentTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class EmailTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class EmailTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


@dataclass
class EmployeeInfoType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    employee_id: str | None = field(
        default=None,
        metadata={
            "name": "EmployeeId",
            "type": "Attribute",
        },
    )
    employee_level: str | None = field(
        default=None,
        metadata={
            "name": "EmployeeLevel",
            "type": "Attribute",
        },
    )
    employee_title: str | None = field(
        default=None,
        metadata={
            "name": "EmployeeTitle",
            "type": "Attribute",
        },
    )
    employee_status: str | None = field(
        default=None,
        metadata={
            "name": "EmployeeStatus",
            "type": "Attribute",
        },
    )


class EquipmentRestrictionType(Enum):
    ONE_WAY_ONLY = "OneWayOnly"
    ROUND_TRIP_ONLY = "RoundTripOnly"
    ANY_RESERVATION = "AnyReservation"


@dataclass
class FormattedTextTextType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    formatted: bool | None = field(
        default=None,
        metadata={
            "name": "Formatted",
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


@dataclass
class FreeTextType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


class IncludeExcludeType(Enum):
    INCLUDE = "Include"
    EXCLUDE = "Exclude"
    REQUIRED = "Required"
    ALLOWED = "Allowed"


@dataclass
class InformationHeader1:
    class Meta:
        name = "InformationHeader"

    successfully: bool | None = field(
        default=None,
        metadata={
            "name": "Successfully",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    processing_time: float | None = field(
        default=None,
        metadata={
            "name": "ProcessingTime",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    any_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##any",
        },
    )


class InventoryStatusType(Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    ON_REQUEST = "OnRequest"
    CONFIRMED = "Confirmed"
    ALL = "All"
    WAITLIST = "Waitlist"
    SUPPLIER_BOOKED = "SupplierBooked"


class ItemSearchCriterionTypeImportanceType(Enum):
    MANDATORY = "Mandatory"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class LocationDetailRequirementAddlDriverInfoType(Enum):
    INCLUDED_AUTHORIZED = "IncludedAuthorized"
    ADDITIONAL_AUTHORIZED = "AdditionalAuthorized"
    FEES = "Fees"
    MISCELLANEOUS = "Miscellaneous"


class LocationDetailRequirementAgeInfoType(Enum):
    MINIMUM_AGE = "MinimumAge"
    MINIMUM_AGE_EXCEPTIONS = "MinimumAgeExceptions"
    MISCELLANEOUS = "Miscellaneous"


class LocationDetailRequirementInfoType(Enum):
    ONE_WAY_RENTAL = "OneWayRental"
    GEOGRAPHIC = "Geographic"
    DROP_OFF = "DropOff"
    LICENSE = "License"
    INSURANCE = "Insurance"
    ELIGIBILITY = "Eligibility"
    MISCELLANEOUS = "Miscellaneous"


class LocationDetailShuttleInfoType(Enum):
    TRANSPORTATION = "Transportation"
    FREQUENCY = "Frequency"
    PICKUP_INFO = "PickupInfo"
    DISTANCE = "Distance"
    ELAPSED_TIME = "ElapsedTime"
    FEE = "Fee"
    MISCELLANEOUS = "Miscellaneous"
    HOURS = "Hours"


class LocationDetailVehicleInfoType(Enum):
    GENERAL_INFORMATION = "GeneralInformation"
    DISCLAIMER = "Disclaimer"
    ADVANCED_BOOKING = "AdvancedBooking"
    NON_SMOKING_VEHICLES = "NonSmokingVehicles"
    SPECIALITY_VEHICLES = "SpecialityVehicles"


@dataclass
class LocationType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    location_code: str | None = field(
        default=None,
        metadata={
            "name": "LocationCode",
            "type": "Attribute",
        },
    )
    code_context: str = field(
        default="",
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )


class LoyaltyCertificateFormat(Enum):
    PAPER = "Paper"
    ELECTRONIC = "Electronic"


@dataclass
class MonetaryRuleType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    amount: Decimal | None = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Attribute",
        },
    )
    rule_type: str | None = field(
        default=None,
        metadata={
            "name": "RuleType",
            "type": "Attribute",
        },
    )
    percent: Decimal | None = field(
        default=None,
        metadata={
            "name": "Percent",
            "type": "Attribute",
        },
    )
    date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "DateTime",
            "type": "Attribute",
        },
    )
    payment_type: str | None = field(
        default=None,
        metadata={
            "name": "PaymentType",
            "type": "Attribute",
        },
    )


class OtaVehRateRuleRqrentalInfoRateQualifierRatePeriod(Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    WEEKEND_DAY = "WeekendDay"
    OTHER = "Other"
    PACKAGE = "Package"
    BUNDLE = "Bundle"
    TOTAL = "Total"


class OffLocationServiceIdType(Enum):
    CUST_PICK_UP = "CustPickUp"
    VEH_DELIVERY = "VehDelivery"
    CUST_DROP_OFF = "CustDropOff"
    VEH_COLLECTION = "VehCollection"
    EXCHANGE = "Exchange"


class OnLocationServiceIdType(Enum):
    COMPUTER_DRIVING_DIRECTIONS = "ComputerDrivingDirections"
    EXPRESS_RETURN_SERVICE = "ExpressReturnService"
    SPECIAL_NEEDS = "SpecialNeeds"
    FREQUENT_RENTER = "FrequentRenter"
    MISCELLANEOUS = "Miscellaneous"


@dataclass
class OtaResponse:
    pass


class PaymentCardTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class PaymentCardTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class PaymentFormTypePaymentTransactionTypeCode(Enum):
    CHARGE = "charge"
    RESERVE = "reserve"


class PaymentFormTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class PaymentFormTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class PersonNameTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class PersonNameTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class PickupReturnRuleRuleType(Enum):
    EARLIEST_PICKUP = "EarliestPickup"
    LATEST_PICKUP = "LatestPickup"
    LATEST_RETURN = "LatestReturn"


class PingRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class PingRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class PingRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class PingRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class PreferLevelType(Enum):
    REQUIRED = "Required"
    ONLY = "Only"
    PREFERRED = "Preferred"
    NO_PREFERENCE = "NoPreference"


class RateDepositOffsetDropTime(Enum):
    BEFORE_ARRIVAL = "BeforeArrival"
    AFTER_BOOKING = "AfterBooking"
    AFTER_CONFIRMATION = "AfterConfirmation"


class RateGuaranteeOffsetDropTime(Enum):
    BEFORE_ARRIVAL = "BeforeArrival"
    AFTER_BOOKING = "AfterBooking"
    AFTER_CONFIRMATION = "AfterConfirmation"


class RateQualifierTypeRatePeriod(Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    WEEKEND_DAY = "WeekendDay"
    OTHER = "Other"
    PACKAGE = "Package"
    BUNDLE = "Bundle"
    TOTAL = "Total"


class RateQueryType(Enum):
    CACHE = "Cache"
    CASH = "Cash"
    VERIFICATION = "Verification"
    LIVE = "Live"
    DIRECT_CONNECTION = "DirectConnection"
    NO_PREFERENCE = "NoPreference"


class RateRestrictionsOneWayPolicy(Enum):
    ONE_WAY_ALLOWED = "OneWayAllowed"
    ONE_WAY_NOT_ALLOWED = "OneWayNotAllowed"
    RESTRICTED_ONE_WAY = "RestrictedOneWay"


class RelatedTravelerTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class RelatedTravelerTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class RentalPaymentPrefType(Enum):
    GUARANTEE = "guarantee"
    PAYMENT = "payment"


@dataclass
class StateProvType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    state_code: str | None = field(
        default=None,
        metadata={
            "name": "StateCode",
            "type": "Attribute",
        },
    )


@dataclass
class StreetNmbrType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    po_box: str | None = field(
        default=None,
        metadata={
            "name": "PO_Box",
            "type": "Attribute",
        },
    )


@dataclass
class SuccessType:
    pass


@dataclass
class TpaExtensionsType:
    class Meta:
        name = "TPA_ExtensionsType"

    any_element: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
        },
    )


class TimeUnitType(Enum):
    YEAR = "Year"
    MONTH = "Month"
    WEEK = "Week"
    DAY = "Day"
    HOUR = "Hour"
    SECOND = "Second"
    FULL_DURATION = "FullDuration"


class TransactionActionType(Enum):
    BOOK = "Book"
    QUOTE = "Quote"
    HOLD = "Hold"
    INITIATE = "Initiate"
    IGNORE = "Ignore"
    MODIFY = "Modify"
    COMMIT = "Commit"
    CANCEL = "Cancel"
    COMMIT_OVERRIDE_EDITS = "CommitOverrideEdits"


class TransactionStatusType(Enum):
    PENDING = "Pending"
    CANCELLED = "Cancelled"
    MODIFIED = "Modified"
    COMMITTED = "Committed"
    IGNORED = "Ignored"
    ON_HOLD = "On Hold"
    UNSUCCESSFUL = "Unsuccessful"


class UrlTypeShareMarketInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class UrlTypeShareSynchInd(Enum):
    YES = "Yes"
    NO = "No"
    INHERIT = "Inherit"


class VehAvailRateRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehAvailRateRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehAvailRateRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehAvailRateRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehCancelResRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehCancelResRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehCancelResRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehCancelResRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehLocDetailRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehLocDetailRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehLocDetailRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehLocDetailRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehLocationSearchRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehLocationSearchRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehLocationSearchRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehLocationSearchRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehRateRuleRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehRateRuleRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehRateRuleRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehRateRuleRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehResRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehResRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehResRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehResRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehRetResRqTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehRetResRqTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehRetResRsTarget(Enum):
    TEST = "Test"
    PRODUCTION = "Production"


class VehRetResRsTransactionStatusCode(Enum):
    START = "Start"
    END = "End"
    ROLLBACK = "Rollback"
    IN_SERIES = "InSeries"
    CONTINUATION = "Continuation"
    SUBSEQUENT = "Subsequent"


class VehicleAvailRqcoreTypeRateQualifierRatePeriod(Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    WEEKEND_DAY = "WeekendDay"
    OTHER = "Other"
    PACKAGE = "Package"
    BUNDLE = "Bundle"
    TOTAL = "Total"


class VehicleCoreTypeDriveType(Enum):
    AWD = "AWD"
    VALUE_4_WD = "4WD"
    UNSPECIFIED = "Unspecified"


class VehicleCoreTypeFuelType(Enum):
    UNSPECIFIED = "Unspecified"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"
    LPG_COMPRESSED_GAS = "LPG_CompressedGas"
    HYDROGEN = "Hydrogen"
    MULTI_FUEL = "MultiFuel"
    PETROL = "Petrol"
    ETHANOL = "Ethanol"


@dataclass
class VehicleEquipmentCoreType:
    equip_type: str | None = field(
        default=None,
        metadata={
            "name": "EquipType",
            "type": "Attribute",
        },
    )
    quantity: int | None = field(
        default=None,
        metadata={
            "name": "Quantity",
            "type": "Attribute",
        },
    )


class VehiclePeriodUnitNameType(Enum):
    RENTAL_PERIOD = "RentalPeriod"
    YEAR = "Year"
    MONTH = "Month"
    WEEK = "Week"
    DAY = "Day"
    HOUR = "Hour"
    WEEKEND = "Weekend"
    BUNDLE = "Bundle"
    PACKAGE = "Package"


class VehicleTransmissionType(Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"


@dataclass
class VehicleWhereAtFacilityType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    location: str | None = field(
        default=None,
        metadata={
            "name": "Location",
            "type": "Attribute",
        },
    )


class VendorLocationCounterLocInfo(Enum):
    WALK_TO_CAR = "WalkToCar"
    SHUTTLE_TO_CAR = "ShuttleToCar"


@dataclass
class AddressType:
    street_nmbr: Optional["AddressType.StreetNmbr"] = field(
        default=None,
        metadata={
            "name": "StreetNmbr",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    bldg_room: list["AddressType.BldgRoom"] = field(
        default_factory=list,
        metadata={
            "name": "BldgRoom",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address_line: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AddressLine",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    city_name: str | None = field(
        default=None,
        metadata={
            "name": "CityName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    postal_code: str | None = field(
        default=None,
        metadata={
            "name": "PostalCode",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    county: str | None = field(
        default=None,
        metadata={
            "name": "County",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    state_prov: StateProvType | None = field(
        default=None,
        metadata={
            "name": "StateProv",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    country_name: CountryNameType | None = field(
        default=None,
        metadata={
            "name": "CountryName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    formatted_ind: bool = field(
        default=False,
        metadata={
            "name": "FormattedInd",
            "type": "Attribute",
        },
    )
    share_synch_ind: AddressTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: AddressTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    type: str | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )

    @dataclass
    class StreetNmbr(StreetNmbrType):
        street_nmbr_suffix: str | None = field(
            default=None,
            metadata={
                "name": "StreetNmbrSuffix",
                "type": "Attribute",
            },
        )
        street_direction: str | None = field(
            default=None,
            metadata={
                "name": "StreetDirection",
                "type": "Attribute",
            },
        )
        rural_route_nmbr: str | None = field(
            default=None,
            metadata={
                "name": "RuralRouteNmbr",
                "type": "Attribute",
            },
        )

    @dataclass
    class BldgRoom:
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        bldg_name_indicator: bool | None = field(
            default=None,
            metadata={
                "name": "BldgNameIndicator",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfMonetaryRuleType:
    payment_rule: list[MonetaryRuleType] = field(
        default_factory=list,
        metadata={
            "name": "PaymentRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfOtaVehRateRuleRqrentalInfoSpecialEquipPref:
    class Meta:
        name = "ArrayOfOTA_VehRateRuleRQRentalInfoSpecialEquipPref"

    special_equip_pref: list[
        "ArrayOfOtaVehRateRuleRqrentalInfoSpecialEquipPref.SpecialEquipPref"
    ] = field(
        default_factory=list,
        metadata={
            "name": "SpecialEquipPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class SpecialEquipPref:
        action: ActionType | None = field(
            default=None,
            metadata={
                "name": "Action",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfRateQualifierTypeRateComment:
    rate_comment: list["ArrayOfRateQualifierTypeRateComment.RateComment"] = field(
        default_factory=list,
        metadata={
            "name": "RateComment",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class RateComment(FormattedTextTextType):
        name: str | None = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleAvailRqcoreTypeSpecialEquipPref:
    class Meta:
        name = "ArrayOfVehicleAvailRQCoreTypeSpecialEquipPref"

    special_equip_pref: list[
        "ArrayOfVehicleAvailRqcoreTypeSpecialEquipPref.SpecialEquipPref"
    ] = field(
        default_factory=list,
        metadata={
            "name": "SpecialEquipPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class SpecialEquipPref:
        action: ActionType | None = field(
            default=None,
            metadata={
                "name": "Action",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleLocationAdditionalDetailsTypeOneWayDropLocation:
    one_way_drop_location: list[
        "ArrayOfVehicleLocationAdditionalDetailsTypeOneWayDropLocation.OneWayDropLocation"
    ] = field(
        default_factory=list,
        metadata={
            "name": "OneWayDropLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class OneWayDropLocation(LocationType):
        extended_location_code: str | None = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )


@dataclass
class BankAcctType:
    bank_acct_name: str | None = field(
        default=None,
        metadata={
            "name": "BankAcctName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: BankAcctTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: BankAcctTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    bank_id: str | None = field(
        default=None,
        metadata={
            "name": "BankID",
            "type": "Attribute",
        },
    )
    acct_type: str | None = field(
        default=None,
        metadata={
            "name": "AcctType",
            "type": "Attribute",
        },
    )
    bank_acct_number: str | None = field(
        default=None,
        metadata={
            "name": "BankAcctNumber",
            "type": "Attribute",
        },
    )
    checks_accepted_ind: bool | None = field(
        default=None,
        metadata={
            "name": "ChecksAcceptedInd",
            "type": "Attribute",
        },
    )


@dataclass
class CompanyNamePrefType(CompanyNameType):
    prefer_level: PreferLevelType = field(
        default=PreferLevelType.PREFERRED,
        metadata={
            "name": "PreferLevel",
            "type": "Attribute",
        },
    )


@dataclass
class EmailType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    share_synch_ind: EmailTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: EmailTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    default_ind: bool = field(
        default=False,
        metadata={
            "name": "DefaultInd",
            "type": "Attribute",
        },
    )
    email_type: str | None = field(
        default=None,
        metadata={
            "name": "EmailType",
            "type": "Attribute",
        },
    )
    rph: str | None = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )


@dataclass
class ErrorType(FreeTextType):
    type: str | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    short_text: str | None = field(
        default=None,
        metadata={
            "name": "ShortText",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    doc_url: str | None = field(
        default=None,
        metadata={
            "name": "DocURL",
            "type": "Attribute",
        },
    )
    status: str | None = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    tag: str | None = field(
        default=None,
        metadata={
            "name": "Tag",
            "type": "Attribute",
        },
    )
    record_id: str | None = field(
        default=None,
        metadata={
            "name": "RecordID",
            "type": "Attribute",
        },
    )
    node_list: str | None = field(
        default=None,
        metadata={
            "name": "NodeList",
            "type": "Attribute",
        },
    )


@dataclass
class OperationScheduleType:
    operation_times: ArrayOfOperationScheduleTypeOperationTime | None = field(
        default=None,
        metadata={
            "name": "OperationTimes",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    start: str | None = field(
        default=None,
        metadata={
            "name": "Start",
            "type": "Attribute",
        },
    )
    duration: str | None = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    end: str | None = field(
        default=None,
        metadata={
            "name": "End",
            "type": "Attribute",
        },
    )


@dataclass
class ParagraphType:
    text: list[FormattedTextTextType] = field(
        default_factory=list,
        metadata={
            "name": "Text",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    image: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Image",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: list[str] = field(
        default_factory=list,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    list_item: list["ParagraphType.ListItem"] = field(
        default_factory=list,
        metadata={
            "name": "ListItem",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )
    paragraph_number: int | None = field(
        default=None,
        metadata={
            "name": "ParagraphNumber",
            "type": "Attribute",
        },
    )
    create_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "CreateDateTime",
            "type": "Attribute",
        },
    )
    creator_id: str | None = field(
        default=None,
        metadata={
            "name": "CreatorID",
            "type": "Attribute",
        },
    )
    last_modify_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "LastModifyDateTime",
            "type": "Attribute",
        },
    )
    last_modifier_id: str | None = field(
        default=None,
        metadata={
            "name": "LastModifierID",
            "type": "Attribute",
        },
    )
    purge_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "PurgeDate",
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )

    @dataclass
    class ListItem(FormattedTextTextType):
        list_item: int | None = field(
            default=None,
            metadata={
                "name": "ListItem",
                "type": "Attribute",
            },
        )


@dataclass
class PaymentRulesType:
    payment_rule: list[MonetaryRuleType] = field(
        default_factory=list,
        metadata={
            "name": "PaymentRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class PersonNameType:
    name_prefix: list[str] = field(
        default_factory=list,
        metadata={
            "name": "NamePrefix",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    given_name: list[str] = field(
        default_factory=list,
        metadata={
            "name": "GivenName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    middle_name: list[str] = field(
        default_factory=list,
        metadata={
            "name": "MiddleName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    surname_prefix: str | None = field(
        default=None,
        metadata={
            "name": "SurnamePrefix",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    surname: str | None = field(
        default=None,
        metadata={
            "name": "Surname",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    name_suffix: list[str] = field(
        default_factory=list,
        metadata={
            "name": "NameSuffix",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    name_title: list[str] = field(
        default_factory=list,
        metadata={
            "name": "NameTitle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: PersonNameTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: PersonNameTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    name_type: str | None = field(
        default=None,
        metadata={
            "name": "NameType",
            "type": "Attribute",
        },
    )


@dataclass
class PingRq:
    class Meta:
        name = "PingRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    echo_data: str | None = field(
        default=None,
        metadata={
            "name": "EchoData",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: PingRqTarget = field(
        default=PingRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: PingRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class UrlType:
    class Meta:
        name = "URL_Type"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    share_synch_ind: UrlTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: UrlTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    type: str | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    default_ind: bool = field(
        default=False,
        metadata={
            "name": "DefaultInd",
            "type": "Attribute",
        },
    )


@dataclass
class UniqueIdType:
    class Meta:
        name = "UniqueID_Type"

    company_name: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "CompanyName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: str | None = field(
        default=None,
        metadata={
            "name": "URL",
            "type": "Attribute",
        },
    )
    type: str | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    instance: str | None = field(
        default=None,
        metadata={
            "name": "Instance",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Attribute",
        },
    )
    id_context: str | None = field(
        default=None,
        metadata={
            "name": "ID_Context",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleArrivalDetailsType:
    arrival_location: LocationType | None = field(
        default=None,
        metadata={
            "name": "ArrivalLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    marketing_company: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "MarketingCompany",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    operating_company: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "OperatingCompany",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    transportation_code: str | None = field(
        default=None,
        metadata={
            "name": "TransportationCode",
            "type": "Attribute",
        },
    )
    number: str | None = field(
        default=None,
        metadata={
            "name": "Number",
            "type": "Attribute",
        },
    )
    arrival_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "ArrivalDateTime",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleCancelRqadditionalInfoType:
    class Meta:
        name = "VehicleCancelRQAdditionalInfoType"

    cust_loyalty: Optional["VehicleCancelRqadditionalInfoType.CustLoyalty"] = field(
        default=None,
        metadata={
            "name": "CustLoyalty",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: object | None = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_info: Optional["VehicleCancelRqadditionalInfoType.RentalInfo"] = field(
        default=None,
        metadata={
            "name": "RentalInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class CustLoyalty:
        program_id: str | None = field(
            default=None,
            metadata={
                "name": "ProgramID",
                "type": "Attribute",
            },
        )
        membership_id: str | None = field(
            default=None,
            metadata={
                "name": "MembershipID",
                "type": "Attribute",
            },
        )
        travel_sector: str | None = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        rph: str | None = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )
        vendor_code: list[str] = field(
            default_factory=list,
            metadata={
                "name": "VendorCode",
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass
    class RentalInfo:
        pick_up_location: LocationType | None = field(
            default=None,
            metadata={
                "name": "PickUpLocation",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        return_location: LocationType | None = field(
            default=None,
            metadata={
                "name": "ReturnLocation",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        pick_up_date_time: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "PickUpDateTime",
                "type": "Attribute",
            },
        )
        return_date_time: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "ReturnDateTime",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleChargeType:
    tax_amounts: ArrayOfVehicleChargeTypeTaxAmount | None = field(
        default=None,
        metadata={
            "name": "TaxAmounts",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    min_max: Optional["VehicleChargeType.MinMax"] = field(
        default=None,
        metadata={
            "name": "MinMax",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    calculation: list["VehicleChargeType.Calculation"] = field(
        default_factory=list,
        metadata={
            "name": "Calculation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    currency_code: str | None = field(
        default=None,
        metadata={
            "name": "CurrencyCode",
            "type": "Attribute",
        },
    )
    amount: Decimal | None = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Attribute",
        },
    )
    tax_inclusive: bool | None = field(
        default=None,
        metadata={
            "name": "TaxInclusive",
            "type": "Attribute",
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    guaranteed_ind: bool | None = field(
        default=None,
        metadata={
            "name": "GuaranteedInd",
            "type": "Attribute",
        },
    )
    included_in_rate: bool = field(
        default=False,
        metadata={
            "name": "IncludedInRate",
            "type": "Attribute",
        },
    )
    included_in_est_total_ind: bool | None = field(
        default=None,
        metadata={
            "name": "IncludedInEstTotalInd",
            "type": "Attribute",
        },
    )

    @dataclass
    class MinMax:
        max_charge: Decimal | None = field(
            default=None,
            metadata={
                "name": "MaxCharge",
                "type": "Attribute",
            },
        )
        min_charge: Decimal | None = field(
            default=None,
            metadata={
                "name": "MinCharge",
                "type": "Attribute",
            },
        )
        max_charge_days: int | None = field(
            default=None,
            metadata={
                "name": "MaxChargeDays",
                "type": "Attribute",
            },
        )

    @dataclass
    class Calculation:
        unit_charge: Decimal | None = field(
            default=None,
            metadata={
                "name": "UnitCharge",
                "type": "Attribute",
            },
        )
        unit_name: str | None = field(
            default=None,
            metadata={
                "name": "UnitName",
                "type": "Attribute",
            },
        )
        quantity: int | None = field(
            default=None,
            metadata={
                "name": "Quantity",
                "type": "Attribute",
            },
        )
        percentage: Decimal | None = field(
            default=None,
            metadata={
                "name": "Percentage",
                "type": "Attribute",
            },
        )
        applicability: CalculationApplicability | None = field(
            default=None,
            metadata={
                "name": "Applicability",
                "type": "Attribute",
            },
        )
        max_quantity: int | None = field(
            default=None,
            metadata={
                "name": "MaxQuantity",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleCoreType:
    veh_type: Optional["VehicleCoreType.VehType"] = field(
        default=None,
        metadata={
            "name": "VehType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_class: Optional["VehicleCoreType.VehClass"] = field(
        default=None,
        metadata={
            "name": "VehClass",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    air_condition_ind: bool | None = field(
        default=None,
        metadata={
            "name": "AirConditionInd",
            "type": "Attribute",
        },
    )
    transmission_type: VehicleTransmissionType | None = field(
        default=None,
        metadata={
            "name": "TransmissionType",
            "type": "Attribute",
        },
    )
    fuel_type: VehicleCoreTypeFuelType | None = field(
        default=None,
        metadata={
            "name": "FuelType",
            "type": "Attribute",
        },
    )
    drive_type: VehicleCoreTypeDriveType | None = field(
        default=None,
        metadata={
            "name": "DriveType",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehType:
        vehicle_category: str | None = field(
            default=None,
            metadata={
                "name": "VehicleCategory",
                "type": "Attribute",
            },
        )
        door_count: str | None = field(
            default=None,
            metadata={
                "name": "DoorCount",
                "type": "Attribute",
            },
        )

    @dataclass
    class VehClass:
        size: str | None = field(
            default=None,
            metadata={
                "name": "Size",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleEquipmentType:
    description: str | None = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    equip_type: str | None = field(
        default=None,
        metadata={
            "name": "EquipType",
            "type": "Attribute",
        },
    )
    quantity: int | None = field(
        default=None,
        metadata={
            "name": "Quantity",
            "type": "Attribute",
        },
    )
    restriction: EquipmentRestrictionType | None = field(
        default=None,
        metadata={
            "name": "Restriction",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRentalCoreType:
    pick_up_location: list["VehicleRentalCoreType.PickUpLocation"] = field(
        default_factory=list,
        metadata={
            "name": "PickUpLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    return_location: Optional["VehicleRentalCoreType.ReturnLocation"] = field(
        default=None,
        metadata={
            "name": "ReturnLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "PickUpDateTime",
            "type": "Attribute",
        },
    )
    return_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "ReturnDateTime",
            "type": "Attribute",
        },
    )
    start_charges_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "StartChargesDateTime",
            "type": "Attribute",
        },
    )
    stop_charges_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "StopChargesDateTime",
            "type": "Attribute",
        },
    )
    one_way_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "OneWayIndicator",
            "type": "Attribute",
        },
    )
    multi_island_rental_days: int | None = field(
        default=None,
        metadata={
            "name": "MultiIslandRentalDays",
            "type": "Attribute",
        },
    )
    quantity: int | None = field(
        default=None,
        metadata={
            "name": "Quantity",
            "type": "Attribute",
        },
    )
    dist_unit_name: DistanceUnitNameType | None = field(
        default=None,
        metadata={
            "name": "DistUnitName",
            "type": "Attribute",
        },
    )

    @dataclass
    class PickUpLocation(LocationType):
        extended_location_code: str | None = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: str | None = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )

    @dataclass
    class ReturnLocation(LocationType):
        extended_location_code: str | None = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: str | None = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleResRsadditionalInfoType:
    class Meta:
        name = "VehicleResRSAdditionalInfoType"

    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleReservationRqcoreTypeSpecialEquipPrefsSpecialEquipPref(
    VehicleEquipmentCoreType,
):
    class Meta:
        name = "VehicleReservationRQCoreTypeSpecialEquipPrefsSpecialEquipPref"

    prefer_level: PreferLevelType = field(
        default=PreferLevelType.PREFERRED,
        metadata={
            "name": "PreferLevel",
            "type": "Attribute",
        },
    )
    action: ActionType | None = field(
        default=None,
        metadata={
            "name": "Action",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRetrieveResRsadditionalInfoType:
    class Meta:
        name = "VehicleRetrieveResRSAdditionalInfoType"

    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleSpecialReqPrefType:
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    prefer_level: PreferLevelType = field(
        default=PreferLevelType.PREFERRED,
        metadata={
            "name": "PreferLevel",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleTourInfoType:
    tour_operator: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "TourOperator",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_number: str | None = field(
        default=None,
        metadata={
            "name": "TourNumber",
            "type": "Attribute",
        },
    )


@dataclass
class WarningType(FreeTextType):
    type: str | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    short_text: str | None = field(
        default=None,
        metadata={
            "name": "ShortText",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    doc_url: str | None = field(
        default=None,
        metadata={
            "name": "DocURL",
            "type": "Attribute",
        },
    )
    status: str | None = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    tag: str | None = field(
        default=None,
        metadata={
            "name": "Tag",
            "type": "Attribute",
        },
    )
    record_id: str | None = field(
        default=None,
        metadata={
            "name": "RecordID",
            "type": "Attribute",
        },
    )


@dataclass
class InformationHeader(InformationHeader1):
    class Meta:
        name = "informationHeader"
        namespace = "http://www.opentravel.org/OTA/2003/05"


@dataclass
class AddressInfoType(AddressType):
    default_ind: bool = field(
        default=False,
        metadata={
            "name": "DefaultInd",
            "type": "Attribute",
        },
    )
    use_type: str | None = field(
        default=None,
        metadata={
            "name": "UseType",
            "type": "Attribute",
        },
    )
    rph: str | None = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfErrorType:
    error: list[ErrorType] = field(
        default_factory=list,
        metadata={
            "name": "Error",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleCoreType:
    vehicle: list[VehicleCoreType] = field(
        default_factory=list,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfWarningType:
    warning: list[WarningType] = field(
        default_factory=list,
        metadata={
            "name": "Warning",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class CancelInfoRqtype:
    class Meta:
        name = "CancelInfoRQType"

    unique_id: list[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cancel_type: TransactionActionType | None = field(
        default=None,
        metadata={
            "name": "CancelType",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class CoveragePricedType:
    coverage: CoverageType | None = field(
        default=None,
        metadata={
            "name": "Coverage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    charge: VehicleChargeType | None = field(
        default=None,
        metadata={
            "name": "Charge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    required: bool = field(
        default=False,
        metadata={
            "name": "Required",
            "type": "Attribute",
        },
    )


@dataclass
class DocumentType:
    doc_holder_name: str | None = field(
        default=None,
        metadata={
            "name": "DocHolderName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    doc_holder_formatted_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "DocHolderFormattedName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    doc_limitations: list[str] = field(
        default_factory=list,
        metadata={
            "name": "DocLimitations",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional_person_names: ArrayOfString | None = field(
        default=None,
        metadata={
            "name": "AdditionalPersonNames",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: DocumentTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: DocumentTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    doc_issue_authority: str | None = field(
        default=None,
        metadata={
            "name": "DocIssueAuthority",
            "type": "Attribute",
        },
    )
    doc_issue_location: str | None = field(
        default=None,
        metadata={
            "name": "DocIssueLocation",
            "type": "Attribute",
        },
    )
    doc_id: str | None = field(
        default=None,
        metadata={
            "name": "DocID",
            "type": "Attribute",
        },
    )
    doc_type: str | None = field(
        default=None,
        metadata={
            "name": "DocType",
            "type": "Attribute",
        },
    )
    gender: DocumentTypeGender | None = field(
        default=None,
        metadata={
            "name": "Gender",
            "type": "Attribute",
        },
    )
    birth_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "BirthDate",
            "type": "Attribute",
        },
    )
    effective_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "EffectiveDate",
            "type": "Attribute",
        },
    )
    expire_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "ExpireDate",
            "type": "Attribute",
        },
    )
    doc_issue_state_prov: str | None = field(
        default=None,
        metadata={
            "name": "DocIssueStateProv",
            "type": "Attribute",
        },
    )
    doc_issue_country: str | None = field(
        default=None,
        metadata={
            "name": "DocIssueCountry",
            "type": "Attribute",
        },
    )
    birth_country: str | None = field(
        default=None,
        metadata={
            "name": "BirthCountry",
            "type": "Attribute",
        },
    )
    doc_holder_nationality: str | None = field(
        default=None,
        metadata={
            "name": "DocHolderNationality",
            "type": "Attribute",
        },
    )


@dataclass
class FormattedTextSubSectionType:
    paragraph: list[ParagraphType] = field(
        default_factory=list,
        metadata={
            "name": "Paragraph",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    sub_title: str | None = field(
        default=None,
        metadata={
            "name": "SubTitle",
            "type": "Attribute",
        },
    )
    sub_code: str | None = field(
        default=None,
        metadata={
            "name": "SubCode",
            "type": "Attribute",
        },
    )
    sub_section_number: int | None = field(
        default=None,
        metadata={
            "name": "SubSectionNumber",
            "type": "Attribute",
        },
    )


@dataclass
class ItemSearchCriterionType:
    position: Optional["ItemSearchCriterionType.Position"] = field(
        default=None,
        metadata={
            "name": "Position",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: Optional["ItemSearchCriterionType.Address"] = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: object | None = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    ref_point: list["ItemSearchCriterionType.RefPoint"] = field(
        default_factory=list,
        metadata={
            "name": "RefPoint",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    code_ref: Optional["ItemSearchCriterionType.CodeRef"] = field(
        default=None,
        metadata={
            "name": "CodeRef",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    hotel_ref: Optional["ItemSearchCriterionType.HotelRef"] = field(
        default=None,
        metadata={
            "name": "HotelRef",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    radius: Optional["ItemSearchCriterionType.Radius"] = field(
        default=None,
        metadata={
            "name": "Radius",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    exact_match: bool | None = field(
        default=None,
        metadata={
            "name": "ExactMatch",
            "type": "Attribute",
        },
    )
    importance_type: ItemSearchCriterionTypeImportanceType | None = field(
        default=None,
        metadata={
            "name": "ImportanceType",
            "type": "Attribute",
        },
    )
    ranking: int | None = field(
        default=None,
        metadata={
            "name": "Ranking",
            "type": "Attribute",
        },
    )

    @dataclass
    class Position:
        latitude: str | None = field(
            default=None,
            metadata={
                "name": "Latitude",
                "type": "Attribute",
            },
        )
        longitude: str | None = field(
            default=None,
            metadata={
                "name": "Longitude",
                "type": "Attribute",
            },
        )
        altitude: str | None = field(
            default=None,
            metadata={
                "name": "Altitude",
                "type": "Attribute",
            },
        )
        altitude_unit_of_measure_code: str | None = field(
            default=None,
            metadata={
                "name": "AltitudeUnitOfMeasureCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class Address(AddressType):
        same_country_ind: bool | None = field(
            default=None,
            metadata={
                "name": "SameCountryInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class RefPoint:
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        state_prov: str | None = field(
            default=None,
            metadata={
                "name": "StateProv",
                "type": "Attribute",
            },
        )
        country_code: str | None = field(
            default=None,
            metadata={
                "name": "CountryCode",
                "type": "Attribute",
            },
        )
        uri: str | None = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )
        ref_point_type: str | None = field(
            default=None,
            metadata={
                "name": "RefPointType",
                "type": "Attribute",
            },
        )
        name: str | None = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )
        city_name: str | None = field(
            default=None,
            metadata={
                "name": "CityName",
                "type": "Attribute",
            },
        )

    @dataclass
    class CodeRef(LocationType):
        vicinity_code: str | None = field(
            default=None,
            metadata={
                "name": "VicinityCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class HotelRef:
        chain_code: str | None = field(
            default=None,
            metadata={
                "name": "ChainCode",
                "type": "Attribute",
            },
        )
        brand_code: str | None = field(
            default=None,
            metadata={
                "name": "BrandCode",
                "type": "Attribute",
            },
        )
        hotel_code: str | None = field(
            default=None,
            metadata={
                "name": "HotelCode",
                "type": "Attribute",
            },
        )
        hotel_city_code: str | None = field(
            default=None,
            metadata={
                "name": "HotelCityCode",
                "type": "Attribute",
            },
        )
        hotel_name: str | None = field(
            default=None,
            metadata={
                "name": "HotelName",
                "type": "Attribute",
            },
        )
        hotel_code_context: str | None = field(
            default=None,
            metadata={
                "name": "HotelCodeContext",
                "type": "Attribute",
            },
        )
        chain_name: str | None = field(
            default=None,
            metadata={
                "name": "ChainName",
                "type": "Attribute",
            },
        )
        brand_name: str | None = field(
            default=None,
            metadata={
                "name": "BrandName",
                "type": "Attribute",
            },
        )
        segment_category_code: str | None = field(
            default=None,
            metadata={
                "name": "SegmentCategoryCode",
                "type": "Attribute",
            },
        )
        property_class_code: str | None = field(
            default=None,
            metadata={
                "name": "PropertyClassCode",
                "type": "Attribute",
            },
        )
        architectural_style_code: str | None = field(
            default=None,
            metadata={
                "name": "ArchitecturalStyleCode",
                "type": "Attribute",
            },
        )
        supplier_integration_level: int | None = field(
            default=None,
            metadata={
                "name": "SupplierIntegrationLevel",
                "type": "Attribute",
            },
        )

    @dataclass
    class Radius:
        distance: str | None = field(
            default=None,
            metadata={
                "name": "Distance",
                "type": "Attribute",
            },
        )
        distance_measure: str | None = field(
            default=None,
            metadata={
                "name": "DistanceMeasure",
                "type": "Attribute",
            },
        )
        direction: str | None = field(
            default=None,
            metadata={
                "name": "Direction",
                "type": "Attribute",
            },
        )
        distance_max: str | None = field(
            default=None,
            metadata={
                "name": "DistanceMax",
                "type": "Attribute",
            },
        )


@dataclass
class OffLocationServiceCoreType:
    address: Optional["OffLocationServiceCoreType.Address"] = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    type: OffLocationServiceIdType | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass
    class Address(AddressType):
        site_id: str | None = field(
            default=None,
            metadata={
                "name": "SiteID",
                "type": "Attribute",
            },
        )
        site_name: str | None = field(
            default=None,
            metadata={
                "name": "SiteName",
                "type": "Attribute",
            },
        )


@dataclass
class OperationSchedulesType:
    operation_schedule: list[OperationScheduleType] = field(
        default_factory=list,
        metadata={
            "name": "OperationSchedule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    start: str | None = field(
        default=None,
        metadata={
            "name": "Start",
            "type": "Attribute",
        },
    )
    duration: str | None = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    end: str | None = field(
        default=None,
        metadata={
            "name": "End",
            "type": "Attribute",
        },
    )


@dataclass
class PaymentCardType:
    card_holder_name: str | None = field(
        default=None,
        metadata={
            "name": "CardHolderName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    card_issuer_name: Optional["PaymentCardType.CardIssuerName"] = field(
        default=None,
        metadata={
            "name": "CardIssuerName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: AddressType | None = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: PaymentCardTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: PaymentCardTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    card_type: str | None = field(
        default=None,
        metadata={
            "name": "CardType",
            "type": "Attribute",
        },
    )
    card_code: str | None = field(
        default=None,
        metadata={
            "name": "CardCode",
            "type": "Attribute",
        },
    )
    card_number: str | None = field(
        default=None,
        metadata={
            "name": "CardNumber",
            "type": "Attribute",
        },
    )
    series_code: str | None = field(
        default=None,
        metadata={
            "name": "SeriesCode",
            "type": "Attribute",
        },
    )
    effective_date: str | None = field(
        default=None,
        metadata={
            "name": "EffectiveDate",
            "type": "Attribute",
        },
    )
    expire_date: str | None = field(
        default=None,
        metadata={
            "name": "ExpireDate",
            "type": "Attribute",
        },
    )
    masked_card_number: str | None = field(
        default=None,
        metadata={
            "name": "MaskedCardNumber",
            "type": "Attribute",
        },
    )
    card_holder_rph: str | None = field(
        default=None,
        metadata={
            "name": "CardHolderRPH",
            "type": "Attribute",
        },
    )
    extend_payment_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "ExtendPaymentIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class CardIssuerName:
        bank_id: str | None = field(
            default=None,
            metadata={
                "name": "BankID",
                "type": "Attribute",
            },
        )


@dataclass
class PingRs(OtaResponse):
    class Meta:
        name = "PingRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    echo_data: list[str] = field(
        default_factory=list,
        metadata={
            "name": "EchoData",
            "type": "Element",
            "sequential": True,
        },
    )
    errors: list[ErrorType] = field(
        default_factory=list,
        metadata={
            "name": "Errors",
            "type": "Element",
            "sequential": True,
        },
    )
    success: list[SuccessType] = field(
        default_factory=list,
        metadata={
            "name": "Success",
            "type": "Element",
            "sequential": True,
        },
    )
    warnings: list[WarningType] = field(
        default_factory=list,
        metadata={
            "name": "Warnings",
            "type": "Element",
            "sequential": True,
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: PingRsTarget = field(
        default=PingRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: PingRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class RateQualifierType:
    promo_desc: str | None = field(
        default=None,
        metadata={
            "name": "PromoDesc",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_comments: ArrayOfRateQualifierTypeRateComment | None = field(
        default=None,
        metadata={
            "name": "RateComments",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    travel_purpose: str | None = field(
        default=None,
        metadata={
            "name": "TravelPurpose",
            "type": "Attribute",
        },
    )
    rate_category: str | None = field(
        default=None,
        metadata={
            "name": "RateCategory",
            "type": "Attribute",
        },
    )
    corp_discount_nmbr: str | None = field(
        default=None,
        metadata={
            "name": "CorpDiscountNmbr",
            "type": "Attribute",
        },
    )
    rate_qualifier: str | None = field(
        default=None,
        metadata={
            "name": "RateQualifier",
            "type": "Attribute",
        },
    )
    rate_period: RateQualifierTypeRatePeriod | None = field(
        default=None,
        metadata={
            "name": "RatePeriod",
            "type": "Attribute",
        },
    )
    guaranteed_ind: bool | None = field(
        default=None,
        metadata={
            "name": "GuaranteedInd",
            "type": "Attribute",
        },
    )
    arrive_by_flight: bool = field(
        default=False,
        metadata={
            "name": "ArriveByFlight",
            "type": "Attribute",
        },
    )
    rate_authorization_code: str | None = field(
        default=None,
        metadata={
            "name": "RateAuthorizationCode",
            "type": "Attribute",
        },
    )
    vendor_rate_id: str | None = field(
        default=None,
        metadata={
            "name": "VendorRateID",
            "type": "Attribute",
        },
    )


@dataclass
class RelatedTravelerType:
    unique_id: UniqueIdType | None = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: RelatedTravelerTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: RelatedTravelerTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    relation: str | None = field(
        default=None,
        metadata={
            "name": "Relation",
            "type": "Attribute",
        },
    )


@dataclass
class ServiceSoapGetPingInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetPingInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        ping_rq: PingRq | None = field(
            default=None,
            metadata={
                "name": "PingRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class SourceType:
    requestor_id: Optional["SourceType.RequestorId"] = field(
        default=None,
        metadata={
            "name": "RequestorID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    position: Optional["SourceType.Position"] = field(
        default=None,
        metadata={
            "name": "Position",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    booking_channel: Optional["SourceType.BookingChannel"] = field(
        default=None,
        metadata={
            "name": "BookingChannel",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    agent_sine: str | None = field(
        default=None,
        metadata={
            "name": "AgentSine",
            "type": "Attribute",
        },
    )
    pseudo_city_code: str | None = field(
        default=None,
        metadata={
            "name": "PseudoCityCode",
            "type": "Attribute",
        },
    )
    isocountry: str | None = field(
        default=None,
        metadata={
            "name": "ISOCountry",
            "type": "Attribute",
        },
    )
    isocurrency: str | None = field(
        default=None,
        metadata={
            "name": "ISOCurrency",
            "type": "Attribute",
        },
    )
    agent_duty_code: str | None = field(
        default=None,
        metadata={
            "name": "AgentDutyCode",
            "type": "Attribute",
        },
    )
    airline_vendor_id: str | None = field(
        default=None,
        metadata={
            "name": "AirlineVendorID",
            "type": "Attribute",
        },
    )
    airport_code: str | None = field(
        default=None,
        metadata={
            "name": "AirportCode",
            "type": "Attribute",
        },
    )
    first_depart_point: str | None = field(
        default=None,
        metadata={
            "name": "FirstDepartPoint",
            "type": "Attribute",
        },
    )
    ersp_user_id: str | None = field(
        default=None,
        metadata={
            "name": "ERSP_UserID",
            "type": "Attribute",
        },
    )
    terminal_id: str | None = field(
        default=None,
        metadata={
            "name": "TerminalID",
            "type": "Attribute",
        },
    )

    @dataclass
    class RequestorId(UniqueIdType):
        message_password: str | None = field(
            default=None,
            metadata={
                "name": "MessagePassword",
                "type": "Attribute",
            },
        )

    @dataclass
    class Position:
        latitude: str | None = field(
            default=None,
            metadata={
                "name": "Latitude",
                "type": "Attribute",
            },
        )
        longitude: str | None = field(
            default=None,
            metadata={
                "name": "Longitude",
                "type": "Attribute",
            },
        )
        altitude: str | None = field(
            default=None,
            metadata={
                "name": "Altitude",
                "type": "Attribute",
            },
        )
        altitude_unit_of_measure_code: str | None = field(
            default=None,
            metadata={
                "name": "AltitudeUnitOfMeasureCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class BookingChannel:
        company_name: CompanyNameType | None = field(
            default=None,
            metadata={
                "name": "CompanyName",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: str | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )
        primary: bool | None = field(
            default=None,
            metadata={
                "name": "Primary",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleChargePurposeType(VehicleChargeType):
    purpose: str | None = field(
        default=None,
        metadata={
            "name": "Purpose",
            "type": "Attribute",
        },
    )
    rate_convert_ind: bool | None = field(
        default=None,
        metadata={
            "name": "RateConvertInd",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleEquipmentPricedType:
    equipment: VehicleEquipmentType | None = field(
        default=None,
        metadata={
            "name": "Equipment",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    charge: VehicleChargeType | None = field(
        default=None,
        metadata={
            "name": "Charge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    required: bool = field(
        default=False,
        metadata={
            "name": "Required",
            "type": "Attribute",
        },
    )


@dataclass
class VehiclePrefType(VehicleCoreType):
    type_pref: PreferLevelType | None = field(
        default=None,
        metadata={
            "name": "TypePref",
            "type": "Attribute",
        },
    )
    class_pref: PreferLevelType | None = field(
        default=None,
        metadata={
            "name": "ClassPref",
            "type": "Attribute",
        },
    )
    air_condition_pref: PreferLevelType | None = field(
        default=None,
        metadata={
            "name": "AirConditionPref",
            "type": "Attribute",
        },
    )
    transmission_pref: PreferLevelType | None = field(
        default=None,
        metadata={
            "name": "TransmissionPref",
            "type": "Attribute",
        },
    )
    vendor_car_type: str | None = field(
        default=None,
        metadata={
            "name": "VendorCarType",
            "type": "Attribute",
        },
    )
    vehicle_qty: int | None = field(
        default=None,
        metadata={
            "name": "VehicleQty",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: str | None = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRetrieveResRqadditionalInfoType:
    class Meta:
        name = "VehicleRetrieveResRQAdditionalInfoType"

    pick_up_location: LocationType | None = field(
        default=None,
        metadata={
            "name": "PickUpLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: object | None = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: EmailType | None = field(
        default=None,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "PickUpDateTime",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRetrieveResRqcoreType:
    class Meta:
        name = "VehicleRetrieveResRQCoreType"

    unique_id: UniqueIdType | None = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cust_loyalty: Optional["VehicleRetrieveResRqcoreType.CustLoyalty"] = field(
        default=None,
        metadata={
            "name": "CustLoyalty",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class CustLoyalty:
        program_id: str | None = field(
            default=None,
            metadata={
                "name": "ProgramID",
                "type": "Attribute",
            },
        )
        membership_id: str | None = field(
            default=None,
            metadata={
                "name": "MembershipID",
                "type": "Attribute",
            },
        )
        travel_sector: str | None = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        rph: str | None = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )
        vendor_code: list[str] = field(
            default_factory=list,
            metadata={
                "name": "VendorCode",
                "type": "Attribute",
                "tokens": True,
            },
        )


@dataclass
class VehicleType(VehicleCoreType):
    veh_make_model: Optional["VehicleType.VehMakeModel"] = field(
        default=None,
        metadata={
            "name": "VehMakeModel",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    picture_url: str | None = field(
        default=None,
        metadata={
            "name": "PictureURL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_identity: Optional["VehicleType.VehIdentity"] = field(
        default=None,
        metadata={
            "name": "VehIdentity",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    passenger_quantity: str | None = field(
        default=None,
        metadata={
            "name": "PassengerQuantity",
            "type": "Attribute",
        },
    )
    baggage_quantity: int | None = field(
        default=None,
        metadata={
            "name": "BaggageQuantity",
            "type": "Attribute",
        },
    )
    vendor_car_type: str | None = field(
        default=None,
        metadata={
            "name": "VendorCarType",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: str | None = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )
    unit_of_measure_quantity: Decimal | None = field(
        default=None,
        metadata={
            "name": "UnitOfMeasureQuantity",
            "type": "Attribute",
        },
    )
    unit_of_measure: str | None = field(
        default=None,
        metadata={
            "name": "UnitOfMeasure",
            "type": "Attribute",
        },
    )
    unit_of_measure_code: str | None = field(
        default=None,
        metadata={
            "name": "UnitOfMeasureCode",
            "type": "Attribute",
        },
    )
    start: str | None = field(
        default=None,
        metadata={
            "name": "Start",
            "type": "Attribute",
        },
    )
    duration: str | None = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    end: str | None = field(
        default=None,
        metadata={
            "name": "End",
            "type": "Attribute",
        },
    )
    odometer_unit_of_measure: DistanceUnitNameType | None = field(
        default=None,
        metadata={
            "name": "OdometerUnitOfMeasure",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehMakeModel:
        model_year: XmlPeriod | None = field(
            default=None,
            metadata={
                "name": "ModelYear",
                "type": "Attribute",
            },
        )
        name: str | None = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )

    @dataclass
    class VehIdentity:
        vehicle_asset_number: str | None = field(
            default=None,
            metadata={
                "name": "VehicleAssetNumber",
                "type": "Attribute",
            },
        )
        license_plate_number: str | None = field(
            default=None,
            metadata={
                "name": "LicensePlateNumber",
                "type": "Attribute",
            },
        )
        state_prov_code: str | None = field(
            default=None,
            metadata={
                "name": "StateProvCode",
                "type": "Attribute",
            },
        )
        country_code: str | None = field(
            default=None,
            metadata={
                "name": "CountryCode",
                "type": "Attribute",
            },
        )
        vehicle_id_number: str | None = field(
            default=None,
            metadata={
                "name": "VehicleID_Number",
                "type": "Attribute",
            },
        )
        vehicle_color: str | None = field(
            default=None,
            metadata={
                "name": "VehicleColor",
                "type": "Attribute",
            },
        )


@dataclass
class WrittenConfInstType:
    supplemental_data: ParagraphType | None = field(
        default=None,
        metadata={
            "name": "SupplementalData",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: EmailType | None = field(
        default=None,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    language_id: str | None = field(
        default=None,
        metadata={
            "name": "LanguageID",
            "type": "Attribute",
        },
    )
    addressee_name: str | None = field(
        default=None,
        metadata={
            "name": "AddresseeName",
            "type": "Attribute",
        },
    )
    address: str | None = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Attribute",
        },
    )
    telephone: str | None = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Attribute",
        },
    )
    confirm_ind: bool | None = field(
        default=None,
        metadata={
            "name": "ConfirmInd",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfCoveragePricedType:
    priced_coverage: list[CoveragePricedType] = field(
        default_factory=list,
        metadata={
            "name": "PricedCoverage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfSourceType:
    source: list[SourceType] = field(
        default_factory=list,
        metadata={
            "name": "Source",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleAvailRqcoreTypeVehPref:
    class Meta:
        name = "ArrayOfVehicleAvailRQCoreTypeVehPref"

    veh_pref: list["ArrayOfVehicleAvailRqcoreTypeVehPref.VehPref"] = field(
        default_factory=list,
        metadata={
            "name": "VehPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class VehPref(VehiclePrefType):
        up_sell_ind: bool | None = field(
            default=None,
            metadata={
                "name": "UpSellInd",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleChargePurposeType:
    vehicle_charge: list[VehicleChargePurposeType] = field(
        default_factory=list,
        metadata={
            "name": "VehicleCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleChargePurposeType1:
    fee: list[VehicleChargePurposeType] = field(
        default_factory=list,
        metadata={
            "name": "Fee",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleEquipmentPricedType:
    priced_equip: list[VehicleEquipmentPricedType] = field(
        default_factory=list,
        metadata={
            "name": "PricedEquip",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFeeVehicle:
    vehicle: list[
        "ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFeeVehicle.Vehicle"
    ] = field(
        default_factory=list,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Vehicle(VehicleType):
        include_exclude: IncludeExcludeType | None = field(
            default=None,
            metadata={
                "name": "IncludeExclude",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOffLocationServiceOffLocServiceCharge:
    off_loc_service_charge: list[
        "ArrayOfVehicleLocationServicesOfferedTypeOffLocationServiceOffLocServiceCharge.OffLocServiceCharge"
    ] = field(
        default_factory=list,
        metadata={
            "name": "OffLocServiceCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class OffLocServiceCharge(VehicleChargeType):
        vehicles: ArrayOfVehicleCoreType | None = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOnLocationServiceOnLocServiceCharge:
    on_loc_service_charge: list[
        "ArrayOfVehicleLocationServicesOfferedTypeOnLocationServiceOnLocServiceCharge.OnLocServiceCharge"
    ] = field(
        default_factory=list,
        metadata={
            "name": "OnLocServiceCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class OnLocServiceCharge(VehicleChargeType):
        vehicles: ArrayOfVehicleCoreType | None = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipmentEquipCharge:
    equip_charge: list[
        "ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipmentEquipCharge.EquipCharge"
    ] = field(
        default_factory=list,
        metadata={
            "name": "EquipCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class EquipCharge(VehicleChargeType):
        vehicles: ArrayOfVehicleCoreType | None = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class CancelRuleType:
    payment_card: PaymentCardType | None = field(
        default=None,
        metadata={
            "name": "PaymentCard",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cancel_by_date: str | None = field(
        default=None,
        metadata={
            "name": "CancelByDate",
            "type": "Attribute",
        },
    )
    amount: Decimal | None = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Attribute",
        },
    )
    percent: Decimal | None = field(
        default=None,
        metadata={
            "name": "Percent",
            "type": "Attribute",
        },
    )
    type: CancelRuleTypeType | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )


@dataclass
class ContactPersonType:
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: list["ContactPersonType.Telephone"] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: list[AddressInfoType] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: list[EmailType] = field(
        default_factory=list,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: list[UrlType] = field(
        default_factory=list,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    company_name: list[CompanyNameType] = field(
        default_factory=list,
        metadata={
            "name": "CompanyName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    employee_info: list[EmployeeInfoType] = field(
        default_factory=list,
        metadata={
            "name": "EmployeeInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: ContactPersonTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: ContactPersonTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    default_ind: bool = field(
        default=False,
        metadata={
            "name": "DefaultInd",
            "type": "Attribute",
        },
    )
    contact_type: str | None = field(
        default=None,
        metadata={
            "name": "ContactType",
            "type": "Attribute",
        },
    )
    relation: str | None = field(
        default=None,
        metadata={
            "name": "Relation",
            "type": "Attribute",
        },
    )
    emergency_flag: bool = field(
        default=False,
        metadata={
            "name": "EmergencyFlag",
            "type": "Attribute",
        },
    )
    rph: str | None = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )

    @dataclass
    class Telephone:
        rph: str | None = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )


@dataclass
class DirectBillType:
    company_name: Optional["DirectBillType.CompanyName"] = field(
        default=None,
        metadata={
            "name": "CompanyName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: AddressInfoType | None = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: DirectBillTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: DirectBillTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    direct_bill_id: str | None = field(
        default=None,
        metadata={
            "name": "DirectBill_ID",
            "type": "Attribute",
        },
    )
    billing_number: str | None = field(
        default=None,
        metadata={
            "name": "BillingNumber",
            "type": "Attribute",
        },
    )

    @dataclass
    class CompanyName(CompanyNameType):
        contact_name: str | None = field(
            default=None,
            metadata={
                "name": "ContactName",
                "type": "Attribute",
            },
        )


@dataclass
class FormattedTextType:
    sub_section: list[FormattedTextSubSectionType] = field(
        default_factory=list,
        metadata={
            "name": "SubSection",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    title: str | None = field(
        default=None,
        metadata={
            "name": "Title",
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


@dataclass
class OffLocationServiceType(OffLocationServiceCoreType):
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: object | None = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    spec_instructions: str | None = field(
        default=None,
        metadata={
            "name": "SpecInstructions",
            "type": "Attribute",
        },
    )


@dataclass
class ServiceSoapGetPingOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetPingOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetPingOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        ping_rs: PingRs | None = field(
            default=None,
            metadata={
                "name": "PingRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetPingOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleReservationSummaryType:
    conf_id: UniqueIdType | None = field(
        default=None,
        metadata={
            "name": "ConfID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_location: LocationType | None = field(
        default=None,
        metadata={
            "name": "PickUpLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    return_location: LocationType | None = field(
        default=None,
        metadata={
            "name": "ReturnLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle: VehicleType | None = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "PickUpDateTime",
            "type": "Attribute",
        },
    )
    return_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "ReturnDateTime",
            "type": "Attribute",
        },
    )


@dataclass
class AcceptablePaymentCardsInfoType:
    acceptable_payment_cards: (
        ArrayOfAcceptablePaymentCardsInfoTypeAcceptablePaymentCard | None
    ) = field(
        default=None,
        metadata={
            "name": "AcceptablePaymentCards",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    info: FormattedTextType | None = field(
        default=None,
        metadata={
            "name": "Info",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfCancelRuleType:
    cancel_rule: list[CancelRuleType] = field(
        default_factory=list,
        metadata={
            "name": "CancelRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfFormattedTextType:
    vendor_message: list[FormattedTextType] = field(
        default_factory=list,
        metadata={
            "name": "VendorMessage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleLocationAdditionalDetailsTypeShuttleShuttleInfo:
    shuttle_info: list[
        "ArrayOfVehicleLocationAdditionalDetailsTypeShuttleShuttleInfo.ShuttleInfo"
    ] = field(
        default_factory=list,
        metadata={
            "name": "ShuttleInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class ShuttleInfo(FormattedTextType):
        type: LocationDetailShuttleInfoType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFee:
    coverage_fee: list[
        "ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFee.CoverageFee"
    ] = field(
        default_factory=list,
        metadata={
            "name": "CoverageFee",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class CoverageFee:
        charge: VehicleChargeType | None = field(
            default=None,
            metadata={
                "name": "Charge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        vehicles: (
            ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFeeVehicle | None
        ) = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        deductible: Optional[
            "ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFee.CoverageFee.Deductible"
        ] = field(
            default=None,
            metadata={
                "name": "Deductible",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class Deductible:
            amount: Decimal | None = field(
                default=None,
                metadata={
                    "name": "Amount",
                    "type": "Attribute",
                },
            )
            liability_amount: Decimal | None = field(
                default=None,
                metadata={
                    "name": "LiabilityAmount",
                    "type": "Attribute",
                },
            )


@dataclass
class ArrayOfVehicleLocationRequirementsTypeAdditionalDriverAddlDriverInfo:
    addl_driver_info: list[
        "ArrayOfVehicleLocationRequirementsTypeAdditionalDriverAddlDriverInfo.AddlDriverInfo"
    ] = field(
        default_factory=list,
        metadata={
            "name": "AddlDriverInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class AddlDriverInfo(FormattedTextType):
        type: LocationDetailRequirementAddlDriverInfoType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationRequirementsTypeAgeAgeInfo:
    age_info: list["ArrayOfVehicleLocationRequirementsTypeAgeAgeInfo.AgeInfo"] = field(
        default_factory=list,
        metadata={
            "name": "AgeInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class AgeInfo(FormattedTextType):
        type: LocationDetailRequirementAgeInfoType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationRequirementsTypeRequirementInfo:
    requirement_info: list[
        "ArrayOfVehicleLocationRequirementsTypeRequirementInfo.RequirementInfo"
    ] = field(
        default_factory=list,
        metadata={
            "name": "RequirementInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class RequirementInfo(FormattedTextType):
        type: LocationDetailRequirementInfoType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOffLocationService:
    off_location_service: list[
        "ArrayOfVehicleLocationServicesOfferedTypeOffLocationService.OffLocationService"
    ] = field(
        default_factory=list,
        metadata={
            "name": "OffLocationService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class OffLocationService:
        off_loc_service_desc: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "OffLocServiceDesc",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        operation_schedules: OperationSchedulesType | None = field(
            default=None,
            metadata={
                "name": "OperationSchedules",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        off_loc_service_charges: (
            ArrayOfVehicleLocationServicesOfferedTypeOffLocationServiceOffLocServiceCharge
            | None
        ) = field(
            default=None,
            metadata={
                "name": "OffLocServiceCharges",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: OffLocationServiceIdType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOnLocationService:
    on_location_service: list[
        "ArrayOfVehicleLocationServicesOfferedTypeOnLocationService.OnLocationService"
    ] = field(
        default_factory=list,
        metadata={
            "name": "OnLocationService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class OnLocationService:
        on_loc_service_desc: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "OnLocServiceDesc",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        operation_schedules: OperationSchedulesType | None = field(
            default=None,
            metadata={
                "name": "OperationSchedules",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        on_loc_service_charges: (
            ArrayOfVehicleLocationServicesOfferedTypeOnLocationServiceOnLocServiceCharge
            | None
        ) = field(
            default=None,
            metadata={
                "name": "OnLocServiceCharges",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: OnLocationServiceIdType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipment:
    special_equipment: list[
        "ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipment.SpecialEquipment"
    ] = field(
        default_factory=list,
        metadata={
            "name": "SpecialEquipment",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class SpecialEquipment:
        equip_desc: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "EquipDesc",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        equip_charges: (
            ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipmentEquipCharge | None
        ) = field(
            default=None,
            metadata={
                "name": "EquipCharges",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: str | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleLocationVehiclesTypeVehicleInfo:
    vehicle_info: list["ArrayOfVehicleLocationVehiclesTypeVehicleInfo.VehicleInfo"] = (
        field(
            default_factory=list,
            metadata={
                "name": "VehicleInfo",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
    )

    @dataclass
    class VehicleInfo(FormattedTextType):
        type: LocationDetailVehicleInfoType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleReservationSummaryType:
    veh_res_summary: list[VehicleReservationSummaryType] = field(
        default_factory=list,
        metadata={
            "name": "VehResSummary",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class OffLocationServicePricedType:
    off_loc_service: OffLocationServiceType | None = field(
        default=None,
        metadata={
            "name": "OffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    charge: VehicleChargeType | None = field(
        default=None,
        metadata={
            "name": "Charge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class PaymentFormType:
    payment_card: PaymentCardType | None = field(
        default=None,
        metadata={
            "name": "PaymentCard",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    bank_acct: BankAcctType | None = field(
        default=None,
        metadata={
            "name": "BankAcct",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    direct_bill: DirectBillType | None = field(
        default=None,
        metadata={
            "name": "DirectBill",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    voucher: Optional["PaymentFormType.Voucher"] = field(
        default=None,
        metadata={
            "name": "Voucher",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    loyalty_redemption: Optional["PaymentFormType.LoyaltyRedemption"] = field(
        default=None,
        metadata={
            "name": "LoyaltyRedemption",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    misc_charge_order: Optional["PaymentFormType.MiscChargeOrder"] = field(
        default=None,
        metadata={
            "name": "MiscChargeOrder",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cash: Optional["PaymentFormType.Cash"] = field(
        default=None,
        metadata={
            "name": "Cash",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: PaymentFormTypeShareSynchInd | None = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: PaymentFormTypeShareMarketInd | None = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    cost_center_id: str | None = field(
        default=None,
        metadata={
            "name": "CostCenterID",
            "type": "Attribute",
        },
    )
    rph: str | None = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )
    payment_transaction_type_code: PaymentFormTypePaymentTransactionTypeCode | None = (
        field(
            default=None,
            metadata={
                "name": "PaymentTransactionTypeCode",
                "type": "Attribute",
            },
        )
    )

    @dataclass
    class Voucher:
        series_code: str | None = field(
            default=None,
            metadata={
                "name": "SeriesCode",
                "type": "Attribute",
            },
        )
        billing_number: str | None = field(
            default=None,
            metadata={
                "name": "BillingNumber",
                "type": "Attribute",
            },
        )
        supplier_identifier: str | None = field(
            default=None,
            metadata={
                "name": "SupplierIdentifier",
                "type": "Attribute",
            },
        )
        identifier: str | None = field(
            default=None,
            metadata={
                "name": "Identifier",
                "type": "Attribute",
            },
        )
        value_type: str | None = field(
            default=None,
            metadata={
                "name": "ValueType",
                "type": "Attribute",
            },
        )
        electronic_indicator: bool | None = field(
            default=None,
            metadata={
                "name": "ElectronicIndicator",
                "type": "Attribute",
            },
        )

    @dataclass
    class LoyaltyRedemption:
        loyalty_certificate: list[
            "PaymentFormType.LoyaltyRedemption.LoyaltyCertificate"
        ] = field(
            default_factory=list,
            metadata={
                "name": "LoyaltyCertificate",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        certificate_number: str | None = field(
            default=None,
            metadata={
                "name": "CertificateNumber",
                "type": "Attribute",
            },
        )
        member_number: str | None = field(
            default=None,
            metadata={
                "name": "MemberNumber",
                "type": "Attribute",
            },
        )
        program_name: str | None = field(
            default=None,
            metadata={
                "name": "ProgramName",
                "type": "Attribute",
            },
        )
        promotion_code: str | None = field(
            default=None,
            metadata={
                "name": "PromotionCode",
                "type": "Attribute",
            },
        )
        promotion_vendor_code: list[str] = field(
            default_factory=list,
            metadata={
                "name": "PromotionVendorCode",
                "type": "Attribute",
                "tokens": True,
            },
        )
        redemption_quantity: int | None = field(
            default=None,
            metadata={
                "name": "RedemptionQuantity",
                "type": "Attribute",
            },
        )

        @dataclass
        class LoyaltyCertificate:
            id_context: str | None = field(
                default=None,
                metadata={
                    "name": "ID_Context",
                    "type": "Attribute",
                },
            )
            nmbr_of_nights: int | None = field(
                default=None,
                metadata={
                    "name": "NmbrOfNights",
                    "type": "Attribute",
                },
            )
            format: LoyaltyCertificateFormat | None = field(
                default=None,
                metadata={
                    "name": "Format",
                    "type": "Attribute",
                },
            )
            status: str | None = field(
                default=None,
                metadata={
                    "name": "Status",
                    "type": "Attribute",
                },
            )

    @dataclass
    class MiscChargeOrder:
        ticket_number: str | None = field(
            default=None,
            metadata={
                "name": "TicketNumber",
                "type": "Attribute",
            },
        )

    @dataclass
    class Cash:
        cash_indicator: bool = field(
            default=True,
            metadata={
                "name": "CashIndicator",
                "type": "Attribute",
            },
        )


class ServiceSoapGetPing:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getPing"
    input = ServiceSoapGetPingInput
    output = ServiceSoapGetPingOutput


@dataclass
class VehCancelResRq:
    class Meta:
        name = "VehCancelResRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_cancel_rqcore: CancelInfoRqtype | None = field(
        default=None,
        metadata={
            "name": "VehCancelRQCore",
            "type": "Element",
        },
    )
    veh_cancel_rqinfo: VehicleCancelRqadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehCancelRQInfo",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehCancelResRqTarget = field(
        default=VehCancelResRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehCancelResRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: str | None = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )


@dataclass
class VehLocDetailRq:
    class Meta:
        name = "VehLocDetailRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    location: Optional["VehLocDetailRq.Location"] = field(
        default=None,
        metadata={
            "name": "Location",
            "type": "Element",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    response_filter: Optional["VehLocDetailRq.ResponseFilter"] = field(
        default=None,
        metadata={
            "name": "ResponseFilter",
            "type": "Element",
        },
    )
    date: Optional["VehLocDetailRq.Date"] = field(
        default=None,
        metadata={
            "name": "Date",
            "type": "Element",
        },
    )
    keyword: list["VehLocDetailRq.Keyword"] = field(
        default_factory=list,
        metadata={
            "name": "Keyword",
            "type": "Element",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehLocDetailRqTarget = field(
        default=VehLocDetailRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehLocDetailRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: str | None = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )

    @dataclass
    class Location(LocationType):
        extended_location_code: str | None = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class ResponseFilter:
        location_address_phone_indicator: bool = field(
            default=False,
            metadata={
                "name": "LocationAddressPhoneIndicator",
                "type": "Attribute",
            },
        )
        location_info_indicator: bool = field(
            default=False,
            metadata={
                "name": "LocationInfoIndicator",
                "type": "Attribute",
            },
        )
        vehicles_indicator: bool = field(
            default=False,
            metadata={
                "name": "VehiclesIndicator",
                "type": "Attribute",
            },
        )
        requirements_indicator: bool = field(
            default=False,
            metadata={
                "name": "RequirementsIndicator",
                "type": "Attribute",
            },
        )
        additional_fees_indicator: bool = field(
            default=False,
            metadata={
                "name": "AdditionalFeesIndicator",
                "type": "Attribute",
            },
        )
        liabilities_indicator: bool = field(
            default=False,
            metadata={
                "name": "LiabilitiesIndicator",
                "type": "Attribute",
            },
        )
        services_offered_indicator: bool = field(
            default=False,
            metadata={
                "name": "ServicesOfferedIndicator",
                "type": "Attribute",
            },
        )

    @dataclass
    class Date:
        pick_up_date_time: str | None = field(
            default=None,
            metadata={
                "name": "PickUpDateTime",
                "type": "Attribute",
            },
        )
        return_date_time: str | None = field(
            default=None,
            metadata={
                "name": "ReturnDateTime",
                "type": "Attribute",
            },
        )

    @dataclass
    class Keyword:
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )


@dataclass
class VehLocationSearchRq:
    class Meta:
        name = "VehLocationSearchRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_loc_search_criterion: list[ItemSearchCriterionType] = field(
        default_factory=list,
        metadata={
            "name": "VehLocSearchCriterion",
            "type": "Element",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehLocationSearchRqTarget = field(
        default=VehLocationSearchRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehLocationSearchRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    max_responses: int | None = field(
        default=None,
        metadata={
            "name": "MaxResponses",
            "type": "Attribute",
        },
    )
    req_resp_version: str | None = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )
    just_address_phone: bool = field(
        default=False,
        metadata={
            "name": "JustAddressPhone",
            "type": "Attribute",
        },
    )


@dataclass
class VehRateRuleRq:
    class Meta:
        name = "VehRateRuleRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    reference: UniqueIdType | None = field(
        default=None,
        metadata={
            "name": "Reference",
            "type": "Element",
        },
    )
    rental_info: Optional["VehRateRuleRq.RentalInfo"] = field(
        default=None,
        metadata={
            "name": "RentalInfo",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehRateRuleRqTarget = field(
        default=VehRateRuleRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehRateRuleRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    company_short_name: str | None = field(
        default=None,
        metadata={
            "name": "CompanyShortName",
            "type": "Attribute",
        },
    )
    travel_sector: str | None = field(
        default=None,
        metadata={
            "name": "TravelSector",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: str | None = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )

    @dataclass
    class RentalInfo:
        veh_rental_core: VehicleRentalCoreType | None = field(
            default=None,
            metadata={
                "name": "VehRentalCore",
                "type": "Element",
            },
        )
        vehicle_info: VehiclePrefType | None = field(
            default=None,
            metadata={
                "name": "VehicleInfo",
                "type": "Element",
            },
        )
        special_equip_prefs: (
            ArrayOfOtaVehRateRuleRqrentalInfoSpecialEquipPref | None
        ) = field(
            default=None,
            metadata={
                "name": "SpecialEquipPrefs",
                "type": "Element",
            },
        )
        cust_loyalty: list["VehRateRuleRq.RentalInfo.CustLoyalty"] = field(
            default_factory=list,
            metadata={
                "name": "CustLoyalty",
                "type": "Element",
            },
        )
        rate_qualifier: Optional["VehRateRuleRq.RentalInfo.RateQualifier"] = field(
            default=None,
            metadata={
                "name": "RateQualifier",
                "type": "Element",
            },
        )
        off_loc_service: OffLocationServiceType | None = field(
            default=None,
            metadata={
                "name": "OffLocService",
                "type": "Element",
            },
        )
        arrival_details: VehicleArrivalDetailsType | None = field(
            default=None,
            metadata={
                "name": "ArrivalDetails",
                "type": "Element",
            },
        )
        tour_info: VehicleTourInfoType | None = field(
            default=None,
            metadata={
                "name": "TourInfo",
                "type": "Element",
            },
        )
        customer_id: UniqueIdType | None = field(
            default=None,
            metadata={
                "name": "CustomerID",
                "type": "Element",
            },
        )
        tpa_extensions: TpaExtensionsType | None = field(
            default=None,
            metadata={
                "name": "TPA_Extensions",
                "type": "Element",
            },
        )

        @dataclass
        class CustLoyalty:
            program_id: str | None = field(
                default=None,
                metadata={
                    "name": "ProgramID",
                    "type": "Attribute",
                },
            )
            membership_id: str | None = field(
                default=None,
                metadata={
                    "name": "MembershipID",
                    "type": "Attribute",
                },
            )
            travel_sector: str | None = field(
                default=None,
                metadata={
                    "name": "TravelSector",
                    "type": "Attribute",
                },
            )
            rph: str | None = field(
                default=None,
                metadata={
                    "name": "RPH",
                    "type": "Attribute",
                },
            )
            vendor_code: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "VendorCode",
                    "type": "Attribute",
                    "tokens": True,
                },
            )

        @dataclass
        class RateQualifier:
            travel_purpose: str | None = field(
                default=None,
                metadata={
                    "name": "TravelPurpose",
                    "type": "Attribute",
                },
            )
            rate_category: str | None = field(
                default=None,
                metadata={
                    "name": "RateCategory",
                    "type": "Attribute",
                },
            )
            corp_discount_nmbr: str | None = field(
                default=None,
                metadata={
                    "name": "CorpDiscountNmbr",
                    "type": "Attribute",
                },
            )
            rate_qualifier: str | None = field(
                default=None,
                metadata={
                    "name": "RateQualifier",
                    "type": "Attribute",
                },
            )
            rate_period: OtaVehRateRuleRqrentalInfoRateQualifierRatePeriod | None = (
                field(
                    default=None,
                    metadata={
                        "name": "RatePeriod",
                        "type": "Attribute",
                    },
                )
            )
            guaranteed_ind: bool | None = field(
                default=None,
                metadata={
                    "name": "GuaranteedInd",
                    "type": "Attribute",
                },
            )
            rate_authorization_code: str | None = field(
                default=None,
                metadata={
                    "name": "RateAuthorizationCode",
                    "type": "Attribute",
                },
            )
            vendor_rate_id: str | None = field(
                default=None,
                metadata={
                    "name": "VendorRateID",
                    "type": "Attribute",
                },
            )
            rate_modified_ind: bool | None = field(
                default=None,
                metadata={
                    "name": "RateModifiedInd",
                    "type": "Attribute",
                },
            )


@dataclass
class VehRetResRq:
    class Meta:
        name = "VehRetResRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_ret_res_rqcore: VehicleRetrieveResRqcoreType | None = field(
        default=None,
        metadata={
            "name": "VehRetResRQCore",
            "type": "Element",
        },
    )
    veh_ret_res_rqinfo: VehicleRetrieveResRqadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehRetResRQInfo",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehRetResRqTarget = field(
        default=VehRetResRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehRetResRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: str | None = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailAdditionalInfoType:
    priced_coverages: ArrayOfCoveragePricedType | None = field(
        default=None,
        metadata={
            "name": "PricedCoverages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_rules: ArrayOfMonetaryRuleType | None = field(
        default=None,
        metadata={
            "name": "PaymentRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    chargeable_period: XmlDuration | None = field(
        default=None,
        metadata={
            "name": "ChargeablePeriod",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailRqcoreType:
    class Meta:
        name = "VehicleAvailRQCoreType"

    rate_query_parameter_type: str | None = field(
        default=None,
        metadata={
            "name": "RateQueryParameterType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_rental_core: VehicleRentalCoreType | None = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor_prefs: Optional["VehicleAvailRqcoreType.VendorPrefs"] = field(
        default=None,
        metadata={
            "name": "VendorPrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_prefs: ArrayOfVehicleAvailRqcoreTypeVehPref | None = field(
        default=None,
        metadata={
            "name": "VehPrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    driver_type: list["VehicleAvailRqcoreType.DriverType"] = field(
        default_factory=list,
        metadata={
            "name": "DriverType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_qualifier: list["VehicleAvailRqcoreType.RateQualifier"] = field(
        default_factory=list,
        metadata={
            "name": "RateQualifier",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_range: Optional["VehicleAvailRqcoreType.RateRange"] = field(
        default=None,
        metadata={
            "name": "RateRange",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_equip_prefs: ArrayOfVehicleAvailRqcoreTypeSpecialEquipPref | None = field(
        default=None,
        metadata={
            "name": "SpecialEquipPrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_query_type: RateQueryType | None = field(
        default=None,
        metadata={
            "name": "RateQueryType",
            "type": "Attribute",
            "required": True,
        },
    )
    status: InventoryStatusType | None = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    target_source: str | None = field(
        default=None,
        metadata={
            "name": "TargetSource",
            "type": "Attribute",
        },
    )

    @dataclass
    class VendorPrefs:
        vendor_pref: list["VehicleAvailRqcoreType.VendorPrefs.VendorPref"] = field(
            default_factory=list,
            metadata={
                "name": "VendorPref",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        participation_level_code: str | None = field(
            default=None,
            metadata={
                "name": "ParticipationLevelCode",
                "type": "Attribute",
            },
        )
        location_category: str | None = field(
            default=None,
            metadata={
                "name": "LocationCategory",
                "type": "Attribute",
            },
        )

        @dataclass
        class VendorPref(CompanyNamePrefType):
            corp_discount_nmbr: str | None = field(
                default=None,
                metadata={
                    "name": "CorpDiscountNmbr",
                    "type": "Attribute",
                },
            )

    @dataclass
    class DriverType:
        age: int | None = field(
            default=None,
            metadata={
                "name": "Age",
                "type": "Attribute",
            },
        )
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: str | None = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )
        uri: str | None = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateQualifier:
        travel_purpose: str | None = field(
            default=None,
            metadata={
                "name": "TravelPurpose",
                "type": "Attribute",
            },
        )
        rate_category: str | None = field(
            default=None,
            metadata={
                "name": "RateCategory",
                "type": "Attribute",
            },
        )
        corp_discount_nmbr: str | None = field(
            default=None,
            metadata={
                "name": "CorpDiscountNmbr",
                "type": "Attribute",
            },
        )
        rate_qualifier: str | None = field(
            default=None,
            metadata={
                "name": "RateQualifier",
                "type": "Attribute",
            },
        )
        rate_period: VehicleAvailRqcoreTypeRateQualifierRatePeriod | None = field(
            default=None,
            metadata={
                "name": "RatePeriod",
                "type": "Attribute",
            },
        )
        guaranteed_ind: bool | None = field(
            default=None,
            metadata={
                "name": "GuaranteedInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateRange:
        min_rate: Decimal | None = field(
            default=None,
            metadata={
                "name": "MinRate",
                "type": "Attribute",
            },
        )
        max_rate: Decimal | None = field(
            default=None,
            metadata={
                "name": "MaxRate",
                "type": "Attribute",
            },
        )
        fixed_rate: Decimal | None = field(
            default=None,
            metadata={
                "name": "FixedRate",
                "type": "Attribute",
            },
        )
        rate_time_unit: TimeUnitType | None = field(
            default=None,
            metadata={
                "name": "RateTimeUnit",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleLocationAdditionalFeesType:
    taxes: Optional["VehicleLocationAdditionalFeesType.Taxes"] = field(
        default=None,
        metadata={
            "name": "Taxes",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: Optional["VehicleLocationAdditionalFeesType.Fees"] = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    surcharges: Optional["VehicleLocationAdditionalFeesType.Surcharges"] = field(
        default=None,
        metadata={
            "name": "Surcharges",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    miscellaneous_charges: Optional[
        "VehicleLocationAdditionalFeesType.MiscellaneousCharges"
    ] = field(
        default=None,
        metadata={
            "name": "MiscellaneousCharges",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Taxes:
        tax: list["VehicleLocationAdditionalFeesType.Taxes.Tax"] = field(
            default_factory=list,
            metadata={
                "name": "Tax",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        start: str | None = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: str | None = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: str | None = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )

        @dataclass
        class Tax:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
            tax_code: str | None = field(
                default=None,
                metadata={
                    "name": "TaxCode",
                    "type": "Attribute",
                },
            )
            percentage: Decimal | None = field(
                default=None,
                metadata={
                    "name": "Percentage",
                    "type": "Attribute",
                },
            )

    @dataclass
    class Fees:
        fee: list["VehicleLocationAdditionalFeesType.Fees.Fee"] = field(
            default_factory=list,
            metadata={
                "name": "Fee",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class Fee(VehicleChargeType):
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

    @dataclass
    class Surcharges:
        surcharge: list["VehicleLocationAdditionalFeesType.Surcharges.Surcharge"] = (
            field(
                default_factory=list,
                metadata={
                    "name": "Surcharge",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
        )
        info: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        start: str | None = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: str | None = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: str | None = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )

        @dataclass
        class Surcharge(VehicleChargeType):
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

    @dataclass
    class MiscellaneousCharges:
        miscellaneous_charge: list[
            "VehicleLocationAdditionalFeesType.MiscellaneousCharges.MiscellaneousCharge"
        ] = field(
            default_factory=list,
            metadata={
                "name": "MiscellaneousCharge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class MiscellaneousCharge(VehicleChargeType):
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )


@dataclass
class VehicleLocationInformationType(FormattedTextType):
    type: str | None = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRentalRateType:
    rate_distance: list["VehicleRentalRateType.RateDistance"] = field(
        default_factory=list,
        metadata={
            "name": "RateDistance",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle_charges: ArrayOfVehicleChargePurposeType | None = field(
        default=None,
        metadata={
            "name": "VehicleCharges",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_qualifier: RateQualifierType | None = field(
        default=None,
        metadata={
            "name": "RateQualifier",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_restrictions: Optional["VehicleRentalRateType.RateRestrictions"] = field(
        default=None,
        metadata={
            "name": "RateRestrictions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_guarantee: Optional["VehicleRentalRateType.RateGuarantee"] = field(
        default=None,
        metadata={
            "name": "RateGuarantee",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pickup_return_rule: list["VehicleRentalRateType.PickupReturnRule"] = field(
        default_factory=list,
        metadata={
            "name": "PickupReturnRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class RateDistance:
        unlimited: bool | None = field(
            default=None,
            metadata={
                "name": "Unlimited",
                "type": "Attribute",
                "required": True,
            },
        )
        quantity: int | None = field(
            default=None,
            metadata={
                "name": "Quantity",
                "type": "Attribute",
            },
        )
        dist_unit_name: DistanceUnitNameType | None = field(
            default=None,
            metadata={
                "name": "DistUnitName",
                "type": "Attribute",
            },
        )
        vehicle_period_unit_name: VehiclePeriodUnitNameType | None = field(
            default=None,
            metadata={
                "name": "VehiclePeriodUnitName",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateRestrictions:
        minimum_age: int | None = field(
            default=None,
            metadata={
                "name": "MinimumAge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
                "required": True,
            },
        )
        maximum_age: int | None = field(
            default=None,
            metadata={
                "name": "MaximumAge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
                "required": True,
            },
        )
        no_show_fee_ind: bool | None = field(
            default=None,
            metadata={
                "name": "NoShowFeeInd",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
                "required": True,
            },
        )
        arrive_by_flight: bool = field(
            default=False,
            metadata={
                "name": "ArriveByFlight",
                "type": "Attribute",
            },
        )
        minimum_day_ind: bool | None = field(
            default=None,
            metadata={
                "name": "MinimumDayInd",
                "type": "Attribute",
            },
        )
        maximum_day_ind: bool | None = field(
            default=None,
            metadata={
                "name": "MaximumDayInd",
                "type": "Attribute",
            },
        )
        advanced_booking_ind: bool | None = field(
            default=None,
            metadata={
                "name": "AdvancedBookingInd",
                "type": "Attribute",
            },
        )
        restricted_mileage_ind: bool | None = field(
            default=None,
            metadata={
                "name": "RestrictedMileageInd",
                "type": "Attribute",
            },
        )
        corporate_rate_ind: bool | None = field(
            default=None,
            metadata={
                "name": "CorporateRateInd",
                "type": "Attribute",
            },
        )
        guarantee_req_ind: bool | None = field(
            default=None,
            metadata={
                "name": "GuaranteeReqInd",
                "type": "Attribute",
            },
        )
        maximum_vehicles_allowed: int | None = field(
            default=None,
            metadata={
                "name": "MaximumVehiclesAllowed",
                "type": "Attribute",
            },
        )
        overnight_ind: bool | None = field(
            default=None,
            metadata={
                "name": "OvernightInd",
                "type": "Attribute",
            },
        )
        one_way_policy: RateRestrictionsOneWayPolicy | None = field(
            default=None,
            metadata={
                "name": "OneWayPolicy",
                "type": "Attribute",
            },
        )
        cancellation_penalty_ind: bool | None = field(
            default=None,
            metadata={
                "name": "CancellationPenaltyInd",
                "type": "Attribute",
            },
        )
        modification_penalty_ind: bool | None = field(
            default=None,
            metadata={
                "name": "ModificationPenaltyInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateGuarantee:
        description: FormattedTextTextType | None = field(
            default=None,
            metadata={
                "name": "Description",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        absolute_deadline: str | None = field(
            default=None,
            metadata={
                "name": "AbsoluteDeadline",
                "type": "Attribute",
            },
        )
        offset_time_unit: TimeUnitType | None = field(
            default=None,
            metadata={
                "name": "OffsetTimeUnit",
                "type": "Attribute",
            },
        )
        offset_unit_multiplier: int | None = field(
            default=None,
            metadata={
                "name": "OffsetUnitMultiplier",
                "type": "Attribute",
            },
        )
        offset_drop_time: RateGuaranteeOffsetDropTime | None = field(
            default=None,
            metadata={
                "name": "OffsetDropTime",
                "type": "Attribute",
            },
        )

    @dataclass
    class PickupReturnRule:
        day_of_week: DayOfWeekType | None = field(
            default=None,
            metadata={
                "name": "DayOfWeek",
                "type": "Attribute",
            },
        )
        time: str | None = field(
            default=None,
            metadata={
                "name": "Time",
                "type": "Attribute",
            },
        )
        rule_type: PickupReturnRuleRuleType | None = field(
            default=None,
            metadata={
                "name": "RuleType",
                "type": "Attribute",
            },
        )


@dataclass
class VendorMessageType(FormattedTextType):
    info_type: str | None = field(
        default=None,
        metadata={
            "name": "InfoType",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfVehicleLocationInformationType:
    veh_rent_loc_info: list[VehicleLocationInformationType] = field(
        default_factory=list,
        metadata={
            "name": "VehRentLocInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleLocationLiabilitiesTypeCoverage:
    coverage: list["ArrayOfVehicleLocationLiabilitiesTypeCoverage.Coverage"] = field(
        default_factory=list,
        metadata={
            "name": "Coverage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Coverage:
        coverage_info: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "CoverageInfo",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        coverage_fees: (
            ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFee | None
        ) = field(
            default=None,
            metadata={
                "name": "CoverageFees",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: str | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )
        required_ind: bool | None = field(
            default=None,
            metadata={
                "name": "RequiredInd",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVendorMessageType:
    vendor_message: list[VendorMessageType] = field(
        default_factory=list,
        metadata={
            "name": "VendorMessage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class CancelInfoRstype:
    class Meta:
        name = "CancelInfoRSType"

    cancel_rules: ArrayOfCancelRuleType | None = field(
        default=None,
        metadata={
            "name": "CancelRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    unique_id: UniqueIdType | None = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class CustomerType:
    person_name: PersonNameType | None = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: list["CustomerType.Telephone"] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: list[EmailType] = field(
        default_factory=list,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: list["CustomerType.Address"] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: list[UrlType] = field(
        default_factory=list,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    citizen_country_name: list["CustomerType.CitizenCountryName"] = field(
        default_factory=list,
        metadata={
            "name": "CitizenCountryName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    phys_chall_name: list[str] = field(
        default_factory=list,
        metadata={
            "name": "PhysChallName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pet_info: list[str] = field(
        default_factory=list,
        metadata={
            "name": "PetInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_form: list[PaymentFormType] = field(
        default_factory=list,
        metadata={
            "name": "PaymentForm",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    related_traveler: list[RelatedTravelerType] = field(
        default_factory=list,
        metadata={
            "name": "RelatedTraveler",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    contact_person: list[ContactPersonType] = field(
        default_factory=list,
        metadata={
            "name": "ContactPerson",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    document: list[DocumentType] = field(
        default_factory=list,
        metadata={
            "name": "Document",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cust_loyalty: list["CustomerType.CustLoyalty"] = field(
        default_factory=list,
        metadata={
            "name": "CustLoyalty",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    employee_info: list[EmployeeInfoType] = field(
        default_factory=list,
        metadata={
            "name": "EmployeeInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    employer_info: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "EmployerInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    gender: CustomerTypeGender | None = field(
        default=None,
        metadata={
            "name": "Gender",
            "type": "Attribute",
        },
    )
    deceased: bool | None = field(
        default=None,
        metadata={
            "name": "Deceased",
            "type": "Attribute",
        },
    )
    lockout_type: str | None = field(
        default=None,
        metadata={
            "name": "LockoutType",
            "type": "Attribute",
        },
    )
    birth_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "BirthDate",
            "type": "Attribute",
        },
    )
    currency_code: str | None = field(
        default=None,
        metadata={
            "name": "CurrencyCode",
            "type": "Attribute",
        },
    )
    decimal_places: int | None = field(
        default=None,
        metadata={
            "name": "DecimalPlaces",
            "type": "Attribute",
        },
    )
    vip_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "VIP_Indicator",
            "type": "Attribute",
        },
    )
    text: str | None = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )

    @dataclass
    class Telephone:
        phone_tech_type: str | None = field(
            default=None,
            metadata={
                "name": "PhoneTechType",
                "type": "Attribute",
            },
        )
        phone_number: str | None = field(
            default=None,
            metadata={
                "name": "PhoneNumber",
                "type": "Attribute",
            },
        )
        effective_date: XmlDate | None = field(
            default=None,
            metadata={
                "name": "EffectiveDate",
                "type": "Attribute",
            },
        )
        expire_date: XmlDate | None = field(
            default=None,
            metadata={
                "name": "ExpireDate",
                "type": "Attribute",
            },
        )
        rph: str | None = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )

    @dataclass
    class Address(AddressInfoType):
        company_name: CompanyNameType | None = field(
            default=None,
            metadata={
                "name": "CompanyName",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        effective_date: XmlDate | None = field(
            default=None,
            metadata={
                "name": "EffectiveDate",
                "type": "Attribute",
            },
        )
        expire_date: XmlDate | None = field(
            default=None,
            metadata={
                "name": "ExpireDate",
                "type": "Attribute",
            },
        )

    @dataclass
    class CitizenCountryName:
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )

    @dataclass
    class CustLoyalty:
        program_id: str | None = field(
            default=None,
            metadata={
                "name": "ProgramID",
                "type": "Attribute",
            },
        )
        membership_id: str | None = field(
            default=None,
            metadata={
                "name": "MembershipID",
                "type": "Attribute",
            },
        )
        travel_sector: str | None = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        rph: str | None = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )
        vendor_code: list[str] = field(
            default_factory=list,
            metadata={
                "name": "VendorCode",
                "type": "Attribute",
                "tokens": True,
            },
        )


@dataclass
class PaymentDetailType(PaymentFormType):
    payment_amount: Optional["PaymentDetailType.PaymentAmount"] = field(
        default=None,
        metadata={
            "name": "PaymentAmount",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class PaymentAmount:
        amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "Amount",
                "type": "Attribute",
            },
        )
        approval_code: str | None = field(
            default=None,
            metadata={
                "name": "ApprovalCode",
                "type": "Attribute",
            },
        )


@dataclass
class ServiceSoapGetVehCancelReservationInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehCancelReservationInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_cancel_res_rq: VehCancelResRq | None = field(
            default=None,
            metadata={
                "name": "VehCancelResRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehLocDetailInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehLocDetailInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_loc_detail_rq: VehLocDetailRq | None = field(
            default=None,
            metadata={
                "name": "VehLocDetailRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehLocationSearchInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehLocationSearchInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_location_search_rq: VehLocationSearchRq | None = field(
            default=None,
            metadata={
                "name": "VehLocationSearchRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRateRuleInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehRateRuleInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_rate_rule_rq: VehRateRuleRq | None = field(
            default=None,
            metadata={
                "name": "VehRateRuleRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRetReservationInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehRetReservationInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_ret_res_rq: VehRetResRq | None = field(
            default=None,
            metadata={
                "name": "VehRetResRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleAvailCoreType:
    vehicle: VehicleType | None = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_rate: list[VehicleRentalRateType] = field(
        default_factory=list,
        metadata={
            "name": "RentalRate",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    total_charge: list["VehicleAvailCoreType.TotalCharge"] = field(
        default_factory=list,
        metadata={
            "name": "TotalCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_equips: ArrayOfVehicleEquipmentPricedType | None = field(
        default=None,
        metadata={
            "name": "PricedEquips",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: ArrayOfVehicleChargePurposeType1 | None = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    reference: Optional["VehicleAvailCoreType.Reference"] = field(
        default=None,
        metadata={
            "name": "Reference",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: Optional["VehicleAvailCoreType.Vendor"] = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor_location: Optional["VehicleAvailCoreType.VendorLocation"] = field(
        default=None,
        metadata={
            "name": "VendorLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    drop_off_location: Optional["VehicleAvailCoreType.DropOffLocation"] = field(
        default=None,
        metadata={
            "name": "DropOffLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    status: InventoryStatusType | None = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
            "required": True,
        },
    )
    is_alternate_ind: bool | None = field(
        default=None,
        metadata={
            "name": "IsAlternateInd",
            "type": "Attribute",
        },
    )

    @dataclass
    class TotalCharge:
        currency_code: str | None = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        rate_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )
        rate_convert_ind: bool | None = field(
            default=None,
            metadata={
                "name": "RateConvertInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class Reference(UniqueIdType):
        date_time: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "DateTime",
                "type": "Attribute",
            },
        )

    @dataclass
    class Vendor(CompanyNameType):
        participation_level_code: str | None = field(
            default=None,
            metadata={
                "name": "ParticipationLevelCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class VendorLocation(LocationType):
        extended_location_code: str | None = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: str | None = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )
        name: str | None = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )
        counter_loc_info: VendorLocationCounterLocInfo | None = field(
            default=None,
            metadata={
                "name": "CounterLocInfo",
                "type": "Attribute",
            },
        )

    @dataclass
    class DropOffLocation(LocationType):
        extended_location_code: str | None = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: str | None = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )
        name: str | None = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleLocationRequirementsType:
    age: Optional["VehicleLocationRequirementsType.Age"] = field(
        default=None,
        metadata={
            "name": "Age",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional_driver: Optional["VehicleLocationRequirementsType.AdditionalDriver"] = (
        field(
            default=None,
            metadata={
                "name": "AdditionalDriver",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
    )
    payment_options: Optional["VehicleLocationRequirementsType.PaymentOptions"] = field(
        default=None,
        metadata={
            "name": "PaymentOptions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    requirement_infos: ArrayOfVehicleLocationRequirementsTypeRequirementInfo | None = (
        field(
            default=None,
            metadata={
                "name": "RequirementInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Age:
        age_surcharge: list["VehicleLocationRequirementsType.Age.AgeSurcharge"] = field(
            default_factory=list,
            metadata={
                "name": "AgeSurcharge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        age_infos: ArrayOfVehicleLocationRequirementsTypeAgeAgeInfo | None = field(
            default=None,
            metadata={
                "name": "AgeInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        minimum_age: int | None = field(
            default=None,
            metadata={
                "name": "MinimumAge",
                "type": "Attribute",
            },
        )
        maximum_age: int | None = field(
            default=None,
            metadata={
                "name": "MaximumAge",
                "type": "Attribute",
            },
        )

        @dataclass
        class AgeSurcharge:
            age: str | None = field(
                default=None,
                metadata={
                    "name": "Age",
                    "type": "Attribute",
                },
            )
            amount: Decimal | None = field(
                default=None,
                metadata={
                    "name": "Amount",
                    "type": "Attribute",
                },
            )

    @dataclass
    class AdditionalDriver:
        addl_driver_infos: (
            ArrayOfVehicleLocationRequirementsTypeAdditionalDriverAddlDriverInfo | None
        ) = field(
            default=None,
            metadata={
                "name": "AddlDriverInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

    @dataclass
    class PaymentOptions:
        credit_card: AcceptablePaymentCardsInfoType | None = field(
            default=None,
            metadata={
                "name": "CreditCard",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        debit_card: AcceptablePaymentCardsInfoType | None = field(
            default=None,
            metadata={
                "name": "DebitCard",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        cash: Optional["VehicleLocationRequirementsType.PaymentOptions.Cash"] = field(
            default=None,
            metadata={
                "name": "Cash",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        voucher: Optional["VehicleLocationRequirementsType.PaymentOptions.Voucher"] = (
            field(
                default=None,
                metadata={
                    "name": "Voucher",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
        )
        bank_acct: Optional[
            "VehicleLocationRequirementsType.PaymentOptions.BankAcct"
        ] = field(
            default=None,
            metadata={
                "name": "BankAcct",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        direct_bill: Optional[
            "VehicleLocationRequirementsType.PaymentOptions.DirectBill"
        ] = field(
            default=None,
            metadata={
                "name": "DirectBill",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        loyalty_redemption: Optional[
            "VehicleLocationRequirementsType.PaymentOptions.LoyaltyRedemption"
        ] = field(
            default=None,
            metadata={
                "name": "LoyaltyRedemption",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        misc_charge_order: Optional[
            "VehicleLocationRequirementsType.PaymentOptions.MiscChargeOrder"
        ] = field(
            default=None,
            metadata={
                "name": "MiscChargeOrder",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        deposit: AcceptablePaymentCardsInfoType | None = field(
            default=None,
            metadata={
                "name": "Deposit",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        guarantee: AcceptablePaymentCardsInfoType | None = field(
            default=None,
            metadata={
                "name": "Guarantee",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        pre_payment: AcceptablePaymentCardsInfoType | None = field(
            default=None,
            metadata={
                "name": "PrePayment",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        payment_options_info: FormattedTextType | None = field(
            default=None,
            metadata={
                "name": "PaymentOptionsInfo",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class Cash:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class Voucher:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class BankAcct:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class DirectBill:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class LoyaltyRedemption:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class MiscChargeOrder:
            info: FormattedTextType | None = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )


@dataclass
class VehicleLocationServicesOfferedType:
    on_location_services: (
        ArrayOfVehicleLocationServicesOfferedTypeOnLocationService | None
    ) = field(
        default=None,
        metadata={
            "name": "OnLocationServices",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_location_services: (
        ArrayOfVehicleLocationServicesOfferedTypeOffLocationService | None
    ) = field(
        default=None,
        metadata={
            "name": "OffLocationServices",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_equipments: (
        ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipment | None
    ) = field(
        default=None,
        metadata={
            "name": "SpecialEquipments",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleLocationVehiclesType:
    vehicle_infos: ArrayOfVehicleLocationVehiclesTypeVehicleInfo | None = field(
        default=None,
        metadata={
            "name": "VehicleInfos",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle: list["VehicleLocationVehiclesType.Vehicle"] = field(
        default_factory=list,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Vehicle(VehicleType):
        text: list[FormattedTextType] = field(
            default_factory=list,
            metadata={
                "name": "Text",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        is_confirmable_ind: bool | None = field(
            default=None,
            metadata={
                "name": "IsConfirmableInd",
                "type": "Attribute",
            },
        )
        distance_unit: DistanceUnitNameType | None = field(
            default=None,
            metadata={
                "name": "DistanceUnit",
                "type": "Attribute",
            },
        )
        distance_per_fuel_unit: int | None = field(
            default=None,
            metadata={
                "name": "DistancePerFuelUnit",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleSegmentCoreType:
    conf_id: list[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "ConfID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_rental_core: VehicleRentalCoreType | None = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle: VehicleType | None = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_rate: VehicleRentalRateType | None = field(
        default=None,
        metadata={
            "name": "RentalRate",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_equips: ArrayOfVehicleEquipmentPricedType | None = field(
        default=None,
        metadata={
            "name": "PricedEquips",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: ArrayOfVehicleChargePurposeType1 | None = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    total_charge: Optional["VehicleSegmentCoreType.TotalCharge"] = field(
        default=None,
        metadata={
            "name": "TotalCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    index_number: int | None = field(
        default=None,
        metadata={
            "name": "IndexNumber",
            "type": "Attribute",
        },
    )

    @dataclass
    class TotalCharge:
        rate_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        currency_code: str | None = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )


@dataclass
class CustomerPrimaryAdditionalType:
    primary: Optional["CustomerPrimaryAdditionalType.Primary"] = field(
        default=None,
        metadata={
            "name": "Primary",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional: list["CustomerPrimaryAdditionalType.Additional"] = field(
        default_factory=list,
        metadata={
            "name": "Additional",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Primary(CustomerType):
        customer_id: UniqueIdType | None = field(
            default=None,
            metadata={
                "name": "CustomerID",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

    @dataclass
    class Additional(CustomerType):
        start: str | None = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: str | None = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: str | None = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )
        corp_discount_name: str | None = field(
            default=None,
            metadata={
                "name": "CorpDiscountName",
                "type": "Attribute",
            },
        )
        corp_discount_nmbr: str | None = field(
            default=None,
            metadata={
                "name": "CorpDiscountNmbr",
                "type": "Attribute",
            },
        )
        qualification_method: AdditionalQualificationMethod | None = field(
            default=None,
            metadata={
                "name": "QualificationMethod",
                "type": "Attribute",
            },
        )
        age: int | None = field(
            default=None,
            metadata={
                "name": "Age",
                "type": "Attribute",
            },
        )
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: str | None = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )
        uri: str | None = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleLocationAdditionalDetailsType:
    veh_rent_loc_infos: ArrayOfVehicleLocationInformationType | None = field(
        default=None,
        metadata={
            "name": "VehRentLocInfos",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    park_location: VehicleWhereAtFacilityType | None = field(
        default=None,
        metadata={
            "name": "ParkLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    counter_location: VehicleWhereAtFacilityType | None = field(
        default=None,
        metadata={
            "name": "CounterLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    operation_schedules: OperationSchedulesType | None = field(
        default=None,
        metadata={
            "name": "OperationSchedules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    shuttle: Optional["VehicleLocationAdditionalDetailsType.Shuttle"] = field(
        default=None,
        metadata={
            "name": "Shuttle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    one_way_drop_locations: (
        ArrayOfVehicleLocationAdditionalDetailsTypeOneWayDropLocation | None
    ) = field(
        default=None,
        metadata={
            "name": "OneWayDropLocations",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Shuttle:
        shuttle_infos: (
            ArrayOfVehicleLocationAdditionalDetailsTypeShuttleShuttleInfo | None
        ) = field(
            default=None,
            metadata={
                "name": "ShuttleInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        operation_schedules: OperationSchedulesType | None = field(
            default=None,
            metadata={
                "name": "OperationSchedules",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleLocationLiabilitiesType:
    coverages: ArrayOfVehicleLocationLiabilitiesTypeCoverage | None = field(
        default=None,
        metadata={
            "name": "Coverages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    info: FormattedTextType | None = field(
        default=None,
        metadata={
            "name": "Info",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleReservationRqadditionalInfoType:
    class Meta:
        name = "VehicleReservationRQAdditionalInfoType"

    special_req_pref: list[VehicleSpecialReqPrefType] = field(
        default_factory=list,
        metadata={
            "name": "SpecialReqPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    coverage_prefs: ArrayOfVehicleReservationRqadditionalInfoTypeCoveragePref | None = (
        field(
            default=None,
            metadata={
                "name": "CoveragePrefs",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
    )
    off_loc_service: list[OffLocationServiceType] = field(
        default_factory=list,
        metadata={
            "name": "OffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    arrival_details: VehicleArrivalDetailsType | None = field(
        default=None,
        metadata={
            "name": "ArrivalDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_payment_pref: list[
        "VehicleReservationRqadditionalInfoType.RentalPaymentPref"
    ] = field(
        default_factory=list,
        metadata={
            "name": "RentalPaymentPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    reference: Optional["VehicleReservationRqadditionalInfoType.Reference"] = field(
        default=None,
        metadata={
            "name": "Reference",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: VehicleTourInfoType | None = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    written_conf_inst: WrittenConfInstType | None = field(
        default=None,
        metadata={
            "name": "WrittenConfInst",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    luggage_qty: int | None = field(
        default=None,
        metadata={
            "name": "LuggageQty",
            "type": "Attribute",
        },
    )
    passenger_qty: int | None = field(
        default=None,
        metadata={
            "name": "PassengerQty",
            "type": "Attribute",
        },
    )
    smoking_allowed: bool = field(
        default=False,
        metadata={
            "name": "SmokingAllowed",
            "type": "Attribute",
        },
    )
    gas_pre_pay: bool = field(
        default=False,
        metadata={
            "name": "GasPrePay",
            "type": "Attribute",
        },
    )

    @dataclass
    class RentalPaymentPref(PaymentDetailType):
        payment_type: str | None = field(
            default=None,
            metadata={
                "name": "PaymentType",
                "type": "Attribute",
            },
        )
        type: RentalPaymentPrefType | None = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )

    @dataclass
    class Reference(UniqueIdType):
        date_time: XmlDateTime | None = field(
            default=None,
            metadata={
                "name": "DateTime",
                "type": "Attribute",
            },
        )
        amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "Amount",
                "type": "Attribute",
            },
        )
        currency_code: str | None = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        decimal_places: int | None = field(
            default=None,
            metadata={
                "name": "DecimalPlaces",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleAvailRqadditionalInfoType:
    class Meta:
        name = "VehicleAvailRQAdditionalInfoType"

    customer: CustomerPrimaryAdditionalType | None = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_req_pref: list[VehicleSpecialReqPrefType] = field(
        default_factory=list,
        metadata={
            "name": "SpecialReqPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    coverage_prefs: ArrayOfVehicleAvailRqadditionalInfoTypeCoveragePref | None = field(
        default=None,
        metadata={
            "name": "CoveragePrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_loc_service: list[OffLocationServiceType] = field(
        default_factory=list,
        metadata={
            "name": "OffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    arrival_details: VehicleArrivalDetailsType | None = field(
        default=None,
        metadata={
            "name": "ArrivalDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: VehicleTourInfoType | None = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    luggage_qty: int | None = field(
        default=None,
        metadata={
            "name": "LuggageQty",
            "type": "Attribute",
        },
    )
    passenger_qty: int | None = field(
        default=None,
        metadata={
            "name": "PassengerQty",
            "type": "Attribute",
        },
    )
    smoking_allowed: bool = field(
        default=False,
        metadata={
            "name": "SmokingAllowed",
            "type": "Attribute",
        },
    )
    gas_pre_pay: bool = field(
        default=False,
        metadata={
            "name": "GasPrePay",
            "type": "Attribute",
        },
    )
    single_quote: bool | None = field(
        default=None,
        metadata={
            "name": "SingleQuote",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailRsadditionalInfoType:
    class Meta:
        name = "VehicleAvailRSAdditionalInfoType"

    customer: CustomerPrimaryAdditionalType | None = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleLocationDetailsType:
    address: list[AddressInfoType] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: list["VehicleLocationDetailsType.Telephone"] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional_info: VehicleLocationAdditionalDetailsType | None = field(
        default=None,
        metadata={
            "name": "AdditionalInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    at_airport: bool | None = field(
        default=None,
        metadata={
            "name": "AtAirport",
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )
    code_context: str | None = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )
    extended_location_code: str | None = field(
        default=None,
        metadata={
            "name": "ExtendedLocationCode",
            "type": "Attribute",
        },
    )
    assoc_airport_loc_list: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AssocAirportLocList",
            "type": "Attribute",
            "tokens": True,
        },
    )

    @dataclass
    class Telephone:
        phone_tech_type: str | None = field(
            default=None,
            metadata={
                "name": "PhoneTechType",
                "type": "Attribute",
            },
        )
        phone_number: str | None = field(
            default=None,
            metadata={
                "name": "PhoneNumber",
                "type": "Attribute",
            },
        )
        rph: str | None = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleReservationRqcoreType:
    class Meta:
        name = "VehicleReservationRQCoreType"

    unique_id: list[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_rental_core: VehicleRentalCoreType | None = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    customer: CustomerPrimaryAdditionalType | None = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor_pref: CompanyNamePrefType | None = field(
        default=None,
        metadata={
            "name": "VendorPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_pref: VehiclePrefType | None = field(
        default=None,
        metadata={
            "name": "VehPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    driver_type: list["VehicleReservationRqcoreType.DriverType"] = field(
        default_factory=list,
        metadata={
            "name": "DriverType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_qualifier: RateQualifierType | None = field(
        default=None,
        metadata={
            "name": "RateQualifier",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: ArrayOfVehicleChargePurposeType1 | None = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle_charges: ArrayOfVehicleChargePurposeType | None = field(
        default=None,
        metadata={
            "name": "VehicleCharges",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_equip_prefs: Optional["VehicleReservationRqcoreType.SpecialEquipPrefs"] = (
        field(
            default=None,
            metadata={
                "name": "SpecialEquipPrefs",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
    )
    rate_distance: list["VehicleReservationRqcoreType.RateDistance"] = field(
        default_factory=list,
        metadata={
            "name": "RateDistance",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    total_charge: Optional["VehicleReservationRqcoreType.TotalCharge"] = field(
        default=None,
        metadata={
            "name": "TotalCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    queue: Optional["VehicleReservationRqcoreType.Queue"] = field(
        default=None,
        metadata={
            "name": "Queue",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    status: str | None = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )

    @dataclass
    class DriverType:
        age: int | None = field(
            default=None,
            metadata={
                "name": "Age",
                "type": "Attribute",
            },
        )
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: str | None = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )
        uri: str | None = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )

    @dataclass
    class SpecialEquipPrefs:
        special_equip_pref: list[
            VehicleReservationRqcoreTypeSpecialEquipPrefsSpecialEquipPref
        ] = field(
            default_factory=list,
            metadata={
                "name": "SpecialEquipPref",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        charge: VehicleChargeType | None = field(
            default=None,
            metadata={
                "name": "Charge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

    @dataclass
    class RateDistance:
        unlimited: bool | None = field(
            default=None,
            metadata={
                "name": "Unlimited",
                "type": "Attribute",
                "required": True,
            },
        )
        quantity: int | None = field(
            default=None,
            metadata={
                "name": "Quantity",
                "type": "Attribute",
            },
        )
        dist_unit_name: DistanceUnitNameType | None = field(
            default=None,
            metadata={
                "name": "DistUnitName",
                "type": "Attribute",
            },
        )
        vehicle_period_unit_name: VehiclePeriodUnitNameType | None = field(
            default=None,
            metadata={
                "name": "VehiclePeriodUnitName",
                "type": "Attribute",
            },
        )

    @dataclass
    class TotalCharge:
        rate_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )

    @dataclass
    class Queue:
        pseudo_city_code: str | None = field(
            default=None,
            metadata={
                "name": "PseudoCityCode",
                "type": "Attribute",
            },
        )
        queue_number: str | None = field(
            default=None,
            metadata={
                "name": "QueueNumber",
                "type": "Attribute",
            },
        )
        queue_category: str | None = field(
            default=None,
            metadata={
                "name": "QueueCategory",
                "type": "Attribute",
            },
        )
        system_code: str | None = field(
            default=None,
            metadata={
                "name": "SystemCode",
                "type": "Attribute",
            },
        )
        queue_id: str | None = field(
            default=None,
            metadata={
                "name": "QueueID",
                "type": "Attribute",
            },
        )


@dataclass
class VehAvailRateRq:
    class Meta:
        name = "VehAvailRateRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    customer_id: list[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "CustomerID",
            "type": "Element",
        },
    )
    veh_avail_rqcore: VehicleAvailRqcoreType | None = field(
        default=None,
        metadata={
            "name": "VehAvailRQCore",
            "type": "Element",
        },
    )
    veh_avail_rqinfo: VehicleAvailRqadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehAvailRQInfo",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehAvailRateRqTarget = field(
        default=VehAvailRateRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehAvailRateRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: str | None = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )
    max_responses: int | None = field(
        default=None,
        metadata={
            "name": "MaxResponses",
            "type": "Attribute",
        },
    )
    max_per_vendor_ind: bool | None = field(
        default=None,
        metadata={
            "name": "MaxPerVendorInd",
            "type": "Attribute",
        },
    )


@dataclass
class VehLocDetailRs(OtaResponse):
    class Meta:
        name = "VehLocDetailRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    location_detail: VehicleLocationDetailsType | None = field(
        default=None,
        metadata={
            "name": "LocationDetail",
            "type": "Element",
        },
    )
    vehicles: VehicleLocationVehiclesType | None = field(
        default=None,
        metadata={
            "name": "Vehicles",
            "type": "Element",
        },
    )
    requirements: VehicleLocationRequirementsType | None = field(
        default=None,
        metadata={
            "name": "Requirements",
            "type": "Element",
        },
    )
    additional_fees: VehicleLocationAdditionalFeesType | None = field(
        default=None,
        metadata={
            "name": "AdditionalFees",
            "type": "Element",
        },
    )
    liabilities: VehicleLocationLiabilitiesType | None = field(
        default=None,
        metadata={
            "name": "Liabilities",
            "type": "Element",
        },
    )
    services_offered: VehicleLocationServicesOfferedType | None = field(
        default=None,
        metadata={
            "name": "ServicesOffered",
            "type": "Element",
        },
    )
    date: Optional["VehLocDetailRs.Date"] = field(
        default=None,
        metadata={
            "name": "Date",
            "type": "Element",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehLocDetailRsTarget = field(
        default=VehLocDetailRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehLocDetailRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class Date:
        pick_up_date_time: str | None = field(
            default=None,
            metadata={
                "name": "PickUpDateTime",
                "type": "Attribute",
            },
        )
        return_date_time: str | None = field(
            default=None,
            metadata={
                "name": "ReturnDateTime",
                "type": "Attribute",
            },
        )


@dataclass
class VehRateRuleRs(OtaResponse):
    class Meta:
        name = "VehRateRuleRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_rental_core: Optional["VehRateRuleRs.VehRentalCore"] = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
        },
    )
    vehicle: Optional["VehRateRuleRs.Vehicle"] = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
        },
    )
    rental_rate: list["VehRateRuleRs.RentalRate"] = field(
        default_factory=list,
        metadata={
            "name": "RentalRate",
            "type": "Element",
        },
    )
    total_charge: Optional["VehRateRuleRs.TotalCharge"] = field(
        default=None,
        metadata={
            "name": "TotalCharge",
            "type": "Element",
        },
    )
    rate_rules: Optional["VehRateRuleRs.RateRules"] = field(
        default=None,
        metadata={
            "name": "RateRules",
            "type": "Element",
        },
    )
    priced_equips: ArrayOfVehicleEquipmentPricedType | None = field(
        default=None,
        metadata={
            "name": "PricedEquips",
            "type": "Element",
        },
    )
    fees: ArrayOfVehicleChargePurposeType1 | None = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
        },
    )
    priced_coverages: ArrayOfCoveragePricedType | None = field(
        default=None,
        metadata={
            "name": "PricedCoverages",
            "type": "Element",
        },
    )
    location_details: list["VehRateRuleRs.LocationDetails"] = field(
        default_factory=list,
        metadata={
            "name": "LocationDetails",
            "type": "Element",
        },
    )
    vendor_messages: ArrayOfVendorMessageType | None = field(
        default=None,
        metadata={
            "name": "VendorMessages",
            "type": "Element",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehRateRuleRsTarget = field(
        default=VehRateRuleRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehRateRuleRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehRentalCore(VehicleRentalCoreType):
        day_of_week: DayOfWeekType | None = field(
            default=None,
            metadata={
                "name": "DayOfWeek",
                "type": "Attribute",
            },
        )
        currency_code: str | None = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        company_short_name: str | None = field(
            default=None,
            metadata={
                "name": "CompanyShortName",
                "type": "Attribute",
            },
        )
        travel_sector: str | None = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        code: str | None = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: str | None = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )

    @dataclass
    class Vehicle(VehicleType):
        description: FormattedTextTextType | None = field(
            default=None,
            metadata={
                "name": "Description",
                "type": "Element",
            },
        )
        low_mileage: int | None = field(
            default=None,
            metadata={
                "name": "LowMileage",
                "type": "Attribute",
            },
        )
        high_mileage: int | None = field(
            default=None,
            metadata={
                "name": "HighMileage",
                "type": "Attribute",
            },
        )

    @dataclass
    class RentalRate(VehicleRentalRateType):
        written_conf_ind: bool | None = field(
            default=None,
            metadata={
                "name": "WrittenConfInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class TotalCharge:
        currency_code: str | None = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        rate_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Decimal | None = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateRules:
        advance_booking: Optional["VehRateRuleRs.RateRules.AdvanceBooking"] = field(
            default=None,
            metadata={
                "name": "AdvanceBooking",
                "type": "Element",
            },
        )
        pickup_return_rules: Optional["VehRateRuleRs.RateRules.PickupReturnRules"] = (
            field(
                default=None,
                metadata={
                    "name": "PickupReturnRules",
                    "type": "Element",
                },
            )
        )
        rate_guarantee: Optional["VehRateRuleRs.RateRules.RateGuarantee"] = field(
            default=None,
            metadata={
                "name": "RateGuarantee",
                "type": "Element",
            },
        )
        payment_rules: Optional["VehRateRuleRs.RateRules.PaymentRules"] = field(
            default=None,
            metadata={
                "name": "PaymentRules",
                "type": "Element",
            },
        )
        cancel_penalty_info: list["VehRateRuleRs.RateRules.CancelPenaltyInfo"] = field(
            default_factory=list,
            metadata={
                "name": "CancelPenaltyInfo",
                "type": "Element",
            },
        )
        rate_deposit: Optional["VehRateRuleRs.RateRules.RateDeposit"] = field(
            default=None,
            metadata={
                "name": "RateDeposit",
                "type": "Element",
            },
        )
        minimum_keep: XmlDuration | None = field(
            default=None,
            metadata={
                "name": "MinimumKeep",
                "type": "Attribute",
            },
        )
        maximum_keep: XmlDuration | None = field(
            default=None,
            metadata={
                "name": "MaximumKeep",
                "type": "Attribute",
            },
        )
        maximum_rental: XmlDuration | None = field(
            default=None,
            metadata={
                "name": "MaximumRental",
                "type": "Attribute",
            },
        )

        @dataclass
        class AdvanceBooking:
            absolute_deadline: str | None = field(
                default=None,
                metadata={
                    "name": "AbsoluteDeadline",
                    "type": "Attribute",
                },
            )
            offset_time_unit: TimeUnitType | None = field(
                default=None,
                metadata={
                    "name": "OffsetTimeUnit",
                    "type": "Attribute",
                },
            )
            offset_unit_multiplier: int | None = field(
                default=None,
                metadata={
                    "name": "OffsetUnitMultiplier",
                    "type": "Attribute",
                },
            )
            offset_drop_time: AdvanceBookingOffsetDropTime | None = field(
                default=None,
                metadata={
                    "name": "OffsetDropTime",
                    "type": "Attribute",
                },
            )
            required_ind: bool | None = field(
                default=None,
                metadata={
                    "name": "RequiredInd",
                    "type": "Attribute",
                },
            )

        @dataclass
        class PickupReturnRules:
            earliest_pickup: Optional[
                "VehRateRuleRs.RateRules.PickupReturnRules.EarliestPickup"
            ] = field(
                default=None,
                metadata={
                    "name": "EarliestPickup",
                    "type": "Element",
                },
            )
            latest_pickup: Optional[
                "VehRateRuleRs.RateRules.PickupReturnRules.LatestPickup"
            ] = field(
                default=None,
                metadata={
                    "name": "LatestPickup",
                    "type": "Element",
                },
            )
            latest_return: Optional[
                "VehRateRuleRs.RateRules.PickupReturnRules.LatestReturn"
            ] = field(
                default=None,
                metadata={
                    "name": "LatestReturn",
                    "type": "Element",
                },
            )

            @dataclass
            class EarliestPickup:
                day_of_week: DayOfWeekType | None = field(
                    default=None,
                    metadata={
                        "name": "DayOfWeek",
                        "type": "Attribute",
                    },
                )
                time: str | None = field(
                    default=None,
                    metadata={
                        "name": "Time",
                        "type": "Attribute",
                    },
                )

            @dataclass
            class LatestPickup:
                day_of_week: DayOfWeekType | None = field(
                    default=None,
                    metadata={
                        "name": "DayOfWeek",
                        "type": "Attribute",
                    },
                )
                time: str | None = field(
                    default=None,
                    metadata={
                        "name": "Time",
                        "type": "Attribute",
                    },
                )

            @dataclass
            class LatestReturn:
                day_of_week: DayOfWeekType | None = field(
                    default=None,
                    metadata={
                        "name": "DayOfWeek",
                        "type": "Attribute",
                    },
                )
                time: str | None = field(
                    default=None,
                    metadata={
                        "name": "Time",
                        "type": "Attribute",
                    },
                )

        @dataclass
        class RateGuarantee:
            description: FormattedTextTextType | None = field(
                default=None,
                metadata={
                    "name": "Description",
                    "type": "Element",
                },
            )
            absolute_deadline: str | None = field(
                default=None,
                metadata={
                    "name": "AbsoluteDeadline",
                    "type": "Attribute",
                },
            )
            offset_time_unit: TimeUnitType | None = field(
                default=None,
                metadata={
                    "name": "OffsetTimeUnit",
                    "type": "Attribute",
                },
            )
            offset_unit_multiplier: int | None = field(
                default=None,
                metadata={
                    "name": "OffsetUnitMultiplier",
                    "type": "Attribute",
                },
            )
            offset_drop_time: RateGuaranteeOffsetDropTime | None = field(
                default=None,
                metadata={
                    "name": "OffsetDropTime",
                    "type": "Attribute",
                },
            )

        @dataclass
        class PaymentRules(PaymentRulesType):
            acceptable_payments: list[
                "VehRateRuleRs.RateRules.PaymentRules.AcceptablePayments"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "AcceptablePayments",
                    "type": "Element",
                },
            )

            @dataclass
            class AcceptablePayments:
                acceptable_payment: list[
                    "VehRateRuleRs.RateRules.PaymentRules.AcceptablePayments.AcceptablePayment"
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "AcceptablePayment",
                        "type": "Element",
                    },
                )
                payment_type_code: str | None = field(
                    default=None,
                    metadata={
                        "name": "PaymentTypeCode",
                        "type": "Attribute",
                    },
                )

                @dataclass
                class AcceptablePayment:
                    credit_card_code: str | None = field(
                        default=None,
                        metadata={
                            "name": "CreditCardCode",
                            "type": "Attribute",
                        },
                    )

        @dataclass
        class CancelPenaltyInfo:
            deadline: list["VehRateRuleRs.RateRules.CancelPenaltyInfo.Deadline"] = (
                field(
                    default_factory=list,
                    metadata={
                        "name": "Deadline",
                        "type": "Element",
                    },
                )
            )
            penalty_fee: Optional[
                "VehRateRuleRs.RateRules.CancelPenaltyInfo.PenaltyFee"
            ] = field(
                default=None,
                metadata={
                    "name": "PenaltyFee",
                    "type": "Element",
                },
            )
            description: FormattedTextTextType | None = field(
                default=None,
                metadata={
                    "name": "Description",
                    "type": "Element",
                },
            )
            guarantee_required_ind: bool | None = field(
                default=None,
                metadata={
                    "name": "GuaranteeRequiredInd",
                    "type": "Attribute",
                },
            )
            modify_penalty_ind: bool | None = field(
                default=None,
                metadata={
                    "name": "ModifyPenaltyInd",
                    "type": "Attribute",
                },
            )

            @dataclass
            class Deadline:
                absolute_deadline: str | None = field(
                    default=None,
                    metadata={
                        "name": "AbsoluteDeadline",
                        "type": "Attribute",
                    },
                )
                offset_time_unit: TimeUnitType | None = field(
                    default=None,
                    metadata={
                        "name": "OffsetTimeUnit",
                        "type": "Attribute",
                    },
                )
                offset_unit_multiplier: int | None = field(
                    default=None,
                    metadata={
                        "name": "OffsetUnitMultiplier",
                        "type": "Attribute",
                    },
                )
                offset_drop_time: DeadlineOffsetDropTime | None = field(
                    default=None,
                    metadata={
                        "name": "OffsetDropTime",
                        "type": "Attribute",
                    },
                )

            @dataclass
            class PenaltyFee:
                amount: Decimal | None = field(
                    default=None,
                    metadata={
                        "name": "Amount",
                        "type": "Attribute",
                    },
                )

        @dataclass
        class RateDeposit:
            absolute_deadline: str | None = field(
                default=None,
                metadata={
                    "name": "AbsoluteDeadline",
                    "type": "Attribute",
                },
            )
            offset_time_unit: TimeUnitType | None = field(
                default=None,
                metadata={
                    "name": "OffsetTimeUnit",
                    "type": "Attribute",
                },
            )
            offset_unit_multiplier: int | None = field(
                default=None,
                metadata={
                    "name": "OffsetUnitMultiplier",
                    "type": "Attribute",
                },
            )
            offset_drop_time: RateDepositOffsetDropTime | None = field(
                default=None,
                metadata={
                    "name": "OffsetDropTime",
                    "type": "Attribute",
                },
            )
            deposit_required_ind: bool | None = field(
                default=None,
                metadata={
                    "name": "DepositRequiredInd",
                    "type": "Attribute",
                },
            )

    @dataclass
    class LocationDetails(VehicleLocationDetailsType):
        drop_off_indicator: bool | None = field(
            default=None,
            metadata={
                "name": "DropOffIndicator",
                "type": "Attribute",
            },
        )


@dataclass
class VehResRq:
    class Meta:
        name = "VehResRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: ArrayOfSourceType | None = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_res_rqcore: Optional["VehResRq.VehResRqcore"] = field(
        default=None,
        metadata={
            "name": "VehResRQCore",
            "type": "Element",
        },
    )
    veh_res_rqinfo: Optional["VehResRq.VehResRqinfo"] = field(
        default=None,
        metadata={
            "name": "VehResRQInfo",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehResRqTarget = field(
        default=VehResRqTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehResRqTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: str | None = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehResRqcore(VehicleReservationRqcoreType):
        option_change_indicator: bool | None = field(
            default=None,
            metadata={
                "name": "OptionChangeIndicator",
                "type": "Attribute",
            },
        )

    @dataclass
    class VehResRqinfo(VehicleReservationRqadditionalInfoType):
        res_status: TransactionActionType | None = field(
            default=None,
            metadata={
                "name": "ResStatus",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleAvailVendorInfoType:
    vendor_messages: ArrayOfVendorMessageType | None = field(
        default=None,
        metadata={
            "name": "VendorMessages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_loc_services: list[OffLocationServiceType] = field(
        default_factory=list,
        metadata={
            "name": "OffLocServices",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_rules: ArrayOfMonetaryRuleType | None = field(
        default=None,
        metadata={
            "name": "PaymentRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    location_details: list[VehicleLocationDetailsType] = field(
        default_factory=list,
        metadata={
            "name": "LocationDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: VehicleTourInfoType | None = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleMatchedLocationType:
    location_detail: VehicleLocationDetailsType | None = field(
        default=None,
        metadata={
            "name": "LocationDetail",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_loc_search_criterion: list[ItemSearchCriterionType] = field(
        default_factory=list,
        metadata={
            "name": "VehLocSearchCriterion",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    alternate_loc_ind: bool | None = field(
        default=None,
        metadata={
            "name": "AlternateLocInd",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleSegmentAdditionalInfoType:
    payment_rules: ArrayOfMonetaryRuleType | None = field(
        default=None,
        metadata={
            "name": "PaymentRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_payment_amount: list[PaymentDetailType] = field(
        default_factory=list,
        metadata={
            "name": "RentalPaymentAmount",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_coverages: ArrayOfCoveragePricedType | None = field(
        default=None,
        metadata={
            "name": "PricedCoverages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_off_loc_service: list[OffLocationServicePricedType] = field(
        default_factory=list,
        metadata={
            "name": "PricedOffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor_messages: ArrayOfFormattedTextType | None = field(
        default=None,
        metadata={
            "name": "VendorMessages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    location_details: list[VehicleLocationDetailsType] = field(
        default_factory=list,
        metadata={
            "name": "LocationDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: VehicleTourInfoType | None = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    written_conf_ind: bool | None = field(
        default=None,
        metadata={
            "name": "WrittenConfInd",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfVehicleMatchedLocationType:
    veh_matched_loc: list[VehicleMatchedLocationType] = field(
        default_factory=list,
        metadata={
            "name": "VehMatchedLoc",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ServiceSoapGetVehAvailRateInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehAvailRateInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_avail_rate_rq: VehAvailRateRq | None = field(
            default=None,
            metadata={
                "name": "VehAvailRateRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehLocDetailOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehLocDetailOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehLocDetailOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_loc_detail_rs: VehLocDetailRs | None = field(
            default=None,
            metadata={
                "name": "VehLocDetailRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehLocDetailOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRateRuleOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehRateRuleOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehRateRuleOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_rate_rule_rs: VehRateRuleRs | None = field(
            default=None,
            metadata={
                "name": "VehRateRuleRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehRateRuleOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehReservationInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehReservationInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_res_rq: VehResRq | None = field(
            default=None,
            metadata={
                "name": "VehResRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleReservationType:
    customer: CustomerPrimaryAdditionalType | None = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_segment_core: Optional["VehicleReservationType.VehSegmentCore"] = field(
        default=None,
        metadata={
            "name": "VehSegmentCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_segment_info: VehicleSegmentAdditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehSegmentInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    reservation_status: str | None = field(
        default=None,
        metadata={
            "name": "ReservationStatus",
            "type": "Attribute",
        },
    )
    create_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "CreateDateTime",
            "type": "Attribute",
        },
    )
    creator_id: str | None = field(
        default=None,
        metadata={
            "name": "CreatorID",
            "type": "Attribute",
        },
    )
    last_modify_date_time: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "LastModifyDateTime",
            "type": "Attribute",
        },
    )
    last_modifier_id: str | None = field(
        default=None,
        metadata={
            "name": "LastModifierID",
            "type": "Attribute",
        },
    )
    purge_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "PurgeDate",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehSegmentCore(VehicleSegmentCoreType):
        option_change_allowed_indicator: bool | None = field(
            default=None,
            metadata={
                "name": "OptionChangeAllowedIndicator",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleVendorAvailabilityType:
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_avails: Optional["VehicleVendorAvailabilityType.VehAvails"] = field(
        default=None,
        metadata={
            "name": "VehAvails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    info: VehicleAvailVendorInfoType | None = field(
        default=None,
        metadata={
            "name": "Info",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class VehAvails:
        veh_avail: list["VehicleVendorAvailabilityType.VehAvails.VehAvail"] = field(
            default_factory=list,
            metadata={
                "name": "VehAvail",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        rate_category: str | None = field(
            default=None,
            metadata={
                "name": "RateCategory",
                "type": "Attribute",
            },
        )

        @dataclass
        class VehAvail:
            veh_avail_core: VehicleAvailCoreType | None = field(
                default=None,
                metadata={
                    "name": "VehAvailCore",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
            veh_avail_info: VehicleAvailAdditionalInfoType | None = field(
                default=None,
                metadata={
                    "name": "VehAvailInfo",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
            advance_booking: Optional[
                "VehicleVendorAvailabilityType.VehAvails.VehAvail.AdvanceBooking"
            ] = field(
                default=None,
                metadata={
                    "name": "AdvanceBooking",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

            @dataclass
            class AdvanceBooking:
                absolute_deadline: str | None = field(
                    default=None,
                    metadata={
                        "name": "AbsoluteDeadline",
                        "type": "Attribute",
                    },
                )
                offset_time_unit: TimeUnitType | None = field(
                    default=None,
                    metadata={
                        "name": "OffsetTimeUnit",
                        "type": "Attribute",
                    },
                )
                offset_unit_multiplier: int | None = field(
                    default=None,
                    metadata={
                        "name": "OffsetUnitMultiplier",
                        "type": "Attribute",
                    },
                )
                offset_drop_time: AdvanceBookingOffsetDropTime | None = field(
                    default=None,
                    metadata={
                        "name": "OffsetDropTime",
                        "type": "Attribute",
                    },
                )
                rules_apply_ind: bool | None = field(
                    default=None,
                    metadata={
                        "name": "RulesApplyInd",
                        "type": "Attribute",
                    },
                )


@dataclass
class ArrayOfVehicleVendorAvailabilityType:
    veh_vendor_avail: list[VehicleVendorAvailabilityType] = field(
        default_factory=list,
        metadata={
            "name": "VehVendorAvail",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


class ServiceSoapGetVehLocDetail:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehLocDetail"
    input = ServiceSoapGetVehLocDetailInput
    output = ServiceSoapGetVehLocDetailOutput


class ServiceSoapGetVehRateRule:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehRateRule"
    input = ServiceSoapGetVehRateRuleInput
    output = ServiceSoapGetVehRateRuleOutput


@dataclass
class VehLocationSearchRs(OtaResponse):
    class Meta:
        name = "VehLocationSearchRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_matched_locs: ArrayOfVehicleMatchedLocationType | None = field(
        default=None,
        metadata={
            "name": "VehMatchedLocs",
            "type": "Element",
        },
    )
    vendor: CompanyNameType | None = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehLocationSearchRsTarget = field(
        default=VehLocationSearchRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehLocationSearchRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleCancelRsadditionalInfoType:
    class Meta:
        name = "VehicleCancelRSAdditionalInfoType"

    veh_reservation: VehicleReservationType | None = field(
        default=None,
        metadata={
            "name": "VehReservation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleResRscoreType:
    class Meta:
        name = "VehicleResRSCoreType"

    veh_reservation: VehicleReservationType | None = field(
        default=None,
        metadata={
            "name": "VehReservation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: TpaExtensionsType | None = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleRetrieveResRscoreType:
    class Meta:
        name = "VehicleRetrieveResRSCoreType"

    veh_reservation: VehicleReservationType | None = field(
        default=None,
        metadata={
            "name": "VehReservation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_res_summaries: ArrayOfVehicleReservationSummaryType | None = field(
        default=None,
        metadata={
            "name": "VehResSummaries",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ServiceSoapGetVehLocationSearchOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehLocationSearchOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehLocationSearchOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_location_search_rs: VehLocationSearchRs | None = field(
            default=None,
            metadata={
                "name": "VehLocationSearchRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehLocationSearchOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehCancelResRs(OtaResponse):
    class Meta:
        name = "VehCancelResRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_cancel_rscore: Optional["VehCancelResRs.VehCancelRscore"] = field(
        default=None,
        metadata={
            "name": "VehCancelRSCore",
            "type": "Element",
        },
    )
    veh_cancel_rsinfo: VehicleCancelRsadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehCancelRSInfo",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehCancelResRsTarget = field(
        default=VehCancelResRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehCancelResRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehCancelRscore(CancelInfoRstype):
        cancel_status: TransactionStatusType | None = field(
            default=None,
            metadata={
                "name": "CancelStatus",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class VehResRs(OtaResponse):
    class Meta:
        name = "VehResRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_res_rscore: Optional["VehResRs.VehResRscore"] = field(
        default=None,
        metadata={
            "name": "VehResRSCore",
            "type": "Element",
        },
    )
    veh_res_rsinfo: VehicleResRsadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehResRSInfo",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehResRsTarget = field(
        default=VehResRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehResRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehResRscore(VehicleResRscoreType):
        reservation_status: str | None = field(
            default=None,
            metadata={
                "name": "ReservationStatus",
                "type": "Attribute",
            },
        )


@dataclass
class VehRetResRs(OtaResponse):
    class Meta:
        name = "VehRetResRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_ret_res_rscore: VehicleRetrieveResRscoreType | None = field(
        default=None,
        metadata={
            "name": "VehRetResRSCore",
            "type": "Element",
        },
    )
    veh_ret_res_rsinfo: VehicleRetrieveResRsadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehRetResRSInfo",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehRetResRsTarget = field(
        default=VehRetResRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: Decimal | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehRetResRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailRscoreType:
    class Meta:
        name = "VehicleAvailRSCoreType"

    veh_rental_core: VehicleRentalCoreType | None = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_vendor_avails: ArrayOfVehicleVendorAvailabilityType | None = field(
        default=None,
        metadata={
            "name": "VehVendorAvails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ServiceSoapGetVehCancelReservationOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehCancelReservationOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehCancelReservationOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_cancel_res_rs: VehCancelResRs | None = field(
            default=None,
            metadata={
                "name": "VehCancelResRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehCancelReservationOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


class ServiceSoapGetVehLocationSearch:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehLocationSearch"
    input = ServiceSoapGetVehLocationSearchInput
    output = ServiceSoapGetVehLocationSearchOutput


@dataclass
class ServiceSoapGetVehReservationOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehReservationOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehReservationOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_res_rs: VehResRs | None = field(
            default=None,
            metadata={
                "name": "VehResRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehReservationOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRetReservationOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehRetReservationOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehRetReservationOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_ret_res_rs: VehRetResRs | None = field(
            default=None,
            metadata={
                "name": "VehRetResRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehRetReservationOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehAvailRateRs(OtaResponse):
    class Meta:
        name = "VehAvailRateRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: SuccessType | None = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: ArrayOfWarningType | None = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_avail_rscore: VehicleAvailRscoreType | None = field(
        default=None,
        metadata={
            "name": "VehAvailRSCore",
            "type": "Element",
        },
    )
    veh_avail_rsinfo: VehicleAvailRsadditionalInfoType | None = field(
        default=None,
        metadata={
            "name": "VehAvailRSInfo",
            "type": "Element",
        },
    )
    errors: ArrayOfErrorType | None = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: str | None = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
        },
    )
    target: VehAvailRateRsTarget = field(
        default=VehAvailRateRsTarget.PRODUCTION,
        metadata={
            "name": "Target",
            "type": "Attribute",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: str | None = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: int | None = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: VehAvailRateRsTransactionStatusCode | None = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: bool | None = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class ServiceSoapGetVehAvailRateOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["ServiceSoapGetVehAvailRateOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["ServiceSoapGetVehAvailRateOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body:
        veh_avail_rate_rs: VehAvailRateRs | None = field(
            default=None,
            metadata={
                "name": "VehAvailRateRS",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["ServiceSoapGetVehAvailRateOutput.Body.Fault"] = field(
            default=None,
            metadata={
                "name": "Fault",
                "type": "Element",
            },
        )

        @dataclass
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

    @dataclass
    class Header:
        information_header: InformationHeader | None = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


class ServiceSoapGetVehCancelReservation:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehCancelReservation"
    input = ServiceSoapGetVehCancelReservationInput
    output = ServiceSoapGetVehCancelReservationOutput


class ServiceSoapGetVehReservation:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehReservation"
    input = ServiceSoapGetVehReservationInput
    output = ServiceSoapGetVehReservationOutput


class ServiceSoapGetVehRetReservation:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehRetReservation"
    input = ServiceSoapGetVehRetReservationInput
    output = ServiceSoapGetVehRetReservationOutput


class ServiceSoapGetVehAvailRate:
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehAvailRate"
    input = ServiceSoapGetVehAvailRateInput
    output = ServiceSoapGetVehAvailRateOutput
