from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

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
class ArrayOfAcceptablePaymentCardsInfoTypeAcceptablePaymentCard(object):
    acceptable_payment_card: List[
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
    class AcceptablePaymentCard(object):
        card_type: Optional[str] = field(
            default=None,
            metadata={
                "name": "CardType",
                "type": "Attribute",
            },
        )
        card_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "CardName",
                "type": "Attribute",
            },
        )
        usage_percentage: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "UsagePercentage",
                "type": "Attribute",
            },
        )
        usage_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "UsageAmount",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfOperationScheduleTypeOperationTime(object):
    operation_time: List[
        "ArrayOfOperationScheduleTypeOperationTime.OperationTime"
    ] = field(
        default_factory=list,
        metadata={
            "name": "OperationTime",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class OperationTime(object):
        mon: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Mon",
                "type": "Attribute",
            },
        )
        tue: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Tue",
                "type": "Attribute",
            },
        )
        weds: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Weds",
                "type": "Attribute",
            },
        )
        thur: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Thur",
                "type": "Attribute",
            },
        )
        fri: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Fri",
                "type": "Attribute",
            },
        )
        sat: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Sat",
                "type": "Attribute",
            },
        )
        sun: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Sun",
                "type": "Attribute",
            },
        )
        start: Optional[str] = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: Optional[str] = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: Optional[str] = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )
        additional_operation_info_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "AdditionalOperationInfoCode",
                "type": "Attribute",
            },
        )
        frequency: Optional[str] = field(
            default=None,
            metadata={
                "name": "Frequency",
                "type": "Attribute",
            },
        )
        text: Optional[str] = field(
            default=None,
            metadata={
                "name": "Text",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfString(object):
    additional_person_name: List[str] = field(
        default_factory=list,
        metadata={
            "name": "AdditionalPersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleAvailRqadditionalInfoTypeCoveragePref(object):
    class Meta(object):
        name = "ArrayOfVehicleAvailRQAdditionalInfoTypeCoveragePref"

    coverage_pref: List[object] = field(
        default_factory=list,
        metadata={
            "name": "CoveragePref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleChargeTypeTaxAmount(object):
    tax_amount: List["ArrayOfVehicleChargeTypeTaxAmount.TaxAmount"] = field(
        default_factory=list,
        metadata={
            "name": "TaxAmount",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class TaxAmount(object):
        total: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "Total",
                "type": "Attribute",
                "required": True,
            },
        )
        currency_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        tax_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "TaxCode",
                "type": "Attribute",
            },
        )
        percentage: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "Percentage",
                "type": "Attribute",
            },
        )
        description: Optional[str] = field(
            default=None,
            metadata={
                "name": "Description",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleReservationRqadditionalInfoTypeCoveragePref(object):
    class Meta(object):
        name = "ArrayOfVehicleReservationRQAdditionalInfoTypeCoveragePref"

    coverage_pref: List[object] = field(
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
class CompanyNameType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    company_short_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "CompanyShortName",
            "type": "Attribute",
        },
    )
    travel_sector: Optional[str] = field(
        default=None,
        metadata={
            "name": "TravelSector",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )
    division: Optional[str] = field(
        default=None,
        metadata={
            "name": "Division",
            "type": "Attribute",
        },
    )
    department: Optional[str] = field(
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
class CountryNameType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )


@dataclass
class CoverageType(object):
    details: List["CoveragePricedType"] = field(
        default_factory=list,
        metadata={
            "name": "Details",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    coverage_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "CoverageType",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
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
class EmployeeInfoType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    employee_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "EmployeeId",
            "type": "Attribute",
        },
    )
    employee_level: Optional[str] = field(
        default=None,
        metadata={
            "name": "EmployeeLevel",
            "type": "Attribute",
        },
    )
    employee_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "EmployeeTitle",
            "type": "Attribute",
        },
    )
    employee_status: Optional[str] = field(
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
class FormattedTextTextType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    formatted: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Formatted",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


@dataclass
class FreeTextType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    language: Optional[str] = field(
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
class InformationHeader1(object):
    class Meta(object):
        name = "InformationHeader"

    successfully: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Successfully",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    processing_time: Optional[float] = field(
        default=None,
        metadata={
            "name": "ProcessingTime",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    any_attributes: Dict[str, str] = field(
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
class LocationType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    location_code: Optional[str] = field(
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
class MonetaryRuleType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    amount: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Attribute",
        },
    )
    rule_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "RuleType",
            "type": "Attribute",
        },
    )
    percent: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Percent",
            "type": "Attribute",
        },
    )
    date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "DateTime",
            "type": "Attribute",
        },
    )
    payment_type: Optional[str] = field(
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
class OtaResponse(object):
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
class StateProvType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    state_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "StateCode",
            "type": "Attribute",
        },
    )


@dataclass
class StreetNmbrType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    po_box: Optional[str] = field(
        default=None,
        metadata={
            "name": "PO_Box",
            "type": "Attribute",
        },
    )


@dataclass
class SuccessType(object):
    pass


@dataclass
class TpaExtensionsType(object):
    class Meta(object):
        name = "TPA_ExtensionsType"

    any_element: List[object] = field(
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
class VehicleEquipmentCoreType(object):
    equip_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "EquipType",
            "type": "Attribute",
        },
    )
    quantity: Optional[int] = field(
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
class VehicleWhereAtFacilityType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    location: Optional[str] = field(
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
class AddressType(object):
    street_nmbr: Optional["AddressType.StreetNmbr"] = field(
        default=None,
        metadata={
            "name": "StreetNmbr",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    bldg_room: List["AddressType.BldgRoom"] = field(
        default_factory=list,
        metadata={
            "name": "BldgRoom",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address_line: List[str] = field(
        default_factory=list,
        metadata={
            "name": "AddressLine",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    city_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "CityName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    postal_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "PostalCode",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    county: Optional[str] = field(
        default=None,
        metadata={
            "name": "County",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    state_prov: Optional[StateProvType] = field(
        default=None,
        metadata={
            "name": "StateProv",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    country_name: Optional[CountryNameType] = field(
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
    share_synch_ind: Optional[AddressTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[AddressTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    type: Optional[str] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )

    @dataclass
    class StreetNmbr(StreetNmbrType):
        street_nmbr_suffix: Optional[str] = field(
            default=None,
            metadata={
                "name": "StreetNmbrSuffix",
                "type": "Attribute",
            },
        )
        street_direction: Optional[str] = field(
            default=None,
            metadata={
                "name": "StreetDirection",
                "type": "Attribute",
            },
        )
        rural_route_nmbr: Optional[str] = field(
            default=None,
            metadata={
                "name": "RuralRouteNmbr",
                "type": "Attribute",
            },
        )

    @dataclass
    class BldgRoom(object):
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        bldg_name_indicator: Optional[bool] = field(
            default=None,
            metadata={
                "name": "BldgNameIndicator",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfMonetaryRuleType(object):
    payment_rule: List[MonetaryRuleType] = field(
        default_factory=list,
        metadata={
            "name": "PaymentRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfOtaVehRateRuleRqrentalInfoSpecialEquipPref(object):
    class Meta(object):
        name = "ArrayOfOTA_VehRateRuleRQRentalInfoSpecialEquipPref"

    special_equip_pref: List[
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
    class SpecialEquipPref(object):
        action: Optional[ActionType] = field(
            default=None,
            metadata={
                "name": "Action",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfRateQualifierTypeRateComment(object):
    rate_comment: List["ArrayOfRateQualifierTypeRateComment.RateComment"] = field(
        default_factory=list,
        metadata={
            "name": "RateComment",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class RateComment(FormattedTextTextType):
        name: Optional[str] = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleAvailRqcoreTypeSpecialEquipPref(object):
    class Meta(object):
        name = "ArrayOfVehicleAvailRQCoreTypeSpecialEquipPref"

    special_equip_pref: List[
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
    class SpecialEquipPref(object):
        action: Optional[ActionType] = field(
            default=None,
            metadata={
                "name": "Action",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleLocationAdditionalDetailsTypeOneWayDropLocation(object):
    one_way_drop_location: List[
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
        extended_location_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )


@dataclass
class BankAcctType(object):
    bank_acct_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "BankAcctName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[BankAcctTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[BankAcctTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    bank_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "BankID",
            "type": "Attribute",
        },
    )
    acct_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "AcctType",
            "type": "Attribute",
        },
    )
    bank_acct_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "BankAcctNumber",
            "type": "Attribute",
        },
    )
    checks_accepted_ind: Optional[bool] = field(
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
class EmailType(object):
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    share_synch_ind: Optional[EmailTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[EmailTypeShareMarketInd] = field(
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
    email_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "EmailType",
            "type": "Attribute",
        },
    )
    rph: Optional[str] = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )


@dataclass
class ErrorType(FreeTextType):
    type: Optional[str] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    short_text: Optional[str] = field(
        default=None,
        metadata={
            "name": "ShortText",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    doc_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocURL",
            "type": "Attribute",
        },
    )
    status: Optional[str] = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    tag: Optional[str] = field(
        default=None,
        metadata={
            "name": "Tag",
            "type": "Attribute",
        },
    )
    record_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "RecordID",
            "type": "Attribute",
        },
    )
    node_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "NodeList",
            "type": "Attribute",
        },
    )


@dataclass
class OperationScheduleType(object):
    operation_times: Optional[ArrayOfOperationScheduleTypeOperationTime] = field(
        default=None,
        metadata={
            "name": "OperationTimes",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    start: Optional[str] = field(
        default=None,
        metadata={
            "name": "Start",
            "type": "Attribute",
        },
    )
    duration: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    end: Optional[str] = field(
        default=None,
        metadata={
            "name": "End",
            "type": "Attribute",
        },
    )


@dataclass
class ParagraphType(object):
    text: List[FormattedTextTextType] = field(
        default_factory=list,
        metadata={
            "name": "Text",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    image: List[str] = field(
        default_factory=list,
        metadata={
            "name": "Image",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: List[str] = field(
        default_factory=list,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    list_item: List["ParagraphType.ListItem"] = field(
        default_factory=list,
        metadata={
            "name": "ListItem",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )
    paragraph_number: Optional[int] = field(
        default=None,
        metadata={
            "name": "ParagraphNumber",
            "type": "Attribute",
        },
    )
    create_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "CreateDateTime",
            "type": "Attribute",
        },
    )
    creator_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CreatorID",
            "type": "Attribute",
        },
    )
    last_modify_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "LastModifyDateTime",
            "type": "Attribute",
        },
    )
    last_modifier_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "LastModifierID",
            "type": "Attribute",
        },
    )
    purge_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "PurgeDate",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )

    @dataclass
    class ListItem(FormattedTextTextType):
        list_item: Optional[int] = field(
            default=None,
            metadata={
                "name": "ListItem",
                "type": "Attribute",
            },
        )


@dataclass
class PaymentRulesType(object):
    payment_rule: List[MonetaryRuleType] = field(
        default_factory=list,
        metadata={
            "name": "PaymentRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class PersonNameType(object):
    name_prefix: List[str] = field(
        default_factory=list,
        metadata={
            "name": "NamePrefix",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    given_name: List[str] = field(
        default_factory=list,
        metadata={
            "name": "GivenName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    middle_name: List[str] = field(
        default_factory=list,
        metadata={
            "name": "MiddleName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    surname_prefix: Optional[str] = field(
        default=None,
        metadata={
            "name": "SurnamePrefix",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    surname: Optional[str] = field(
        default=None,
        metadata={
            "name": "Surname",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    name_suffix: List[str] = field(
        default_factory=list,
        metadata={
            "name": "NameSuffix",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    name_title: List[str] = field(
        default_factory=list,
        metadata={
            "name": "NameTitle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[PersonNameTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[PersonNameTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    name_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "NameType",
            "type": "Attribute",
        },
    )


@dataclass
class PingRq(object):
    class Meta(object):
        name = "PingRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    echo_data: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoData",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[PingRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class UrlType(object):
    class Meta(object):
        name = "URL_Type"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    share_synch_ind: Optional[UrlTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[UrlTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    type: Optional[str] = field(
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
class UniqueIdType(object):
    class Meta(object):
        name = "UniqueID_Type"

    company_name: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "CompanyName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: Optional[str] = field(
        default=None,
        metadata={
            "name": "URL",
            "type": "Attribute",
        },
    )
    type: Optional[str] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    instance: Optional[str] = field(
        default=None,
        metadata={
            "name": "Instance",
            "type": "Attribute",
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Attribute",
        },
    )
    id_context: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID_Context",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleArrivalDetailsType(object):
    arrival_location: Optional[LocationType] = field(
        default=None,
        metadata={
            "name": "ArrivalLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    marketing_company: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "MarketingCompany",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    operating_company: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "OperatingCompany",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    transportation_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransportationCode",
            "type": "Attribute",
        },
    )
    number: Optional[str] = field(
        default=None,
        metadata={
            "name": "Number",
            "type": "Attribute",
        },
    )
    arrival_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ArrivalDateTime",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleCancelRqadditionalInfoType(object):
    class Meta(object):
        name = "VehicleCancelRQAdditionalInfoType"

    cust_loyalty: Optional["VehicleCancelRqadditionalInfoType.CustLoyalty"] = field(
        default=None,
        metadata={
            "name": "CustLoyalty",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: Optional[object] = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: Optional[CompanyNameType] = field(
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class CustLoyalty(object):
        program_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "ProgramID",
                "type": "Attribute",
            },
        )
        membership_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "MembershipID",
                "type": "Attribute",
            },
        )
        travel_sector: Optional[str] = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        rph: Optional[str] = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )
        vendor_code: List[str] = field(
            default_factory=list,
            metadata={
                "name": "VendorCode",
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass
    class RentalInfo(object):
        pick_up_location: Optional[LocationType] = field(
            default=None,
            metadata={
                "name": "PickUpLocation",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        return_location: Optional[LocationType] = field(
            default=None,
            metadata={
                "name": "ReturnLocation",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        pick_up_date_time: Optional[XmlDateTime] = field(
            default=None,
            metadata={
                "name": "PickUpDateTime",
                "type": "Attribute",
            },
        )
        return_date_time: Optional[XmlDateTime] = field(
            default=None,
            metadata={
                "name": "ReturnDateTime",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleChargeType(object):
    tax_amounts: Optional[ArrayOfVehicleChargeTypeTaxAmount] = field(
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
    calculation: List["VehicleChargeType.Calculation"] = field(
        default_factory=list,
        metadata={
            "name": "Calculation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    currency_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "CurrencyCode",
            "type": "Attribute",
        },
    )
    amount: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Attribute",
        },
    )
    tax_inclusive: Optional[bool] = field(
        default=None,
        metadata={
            "name": "TaxInclusive",
            "type": "Attribute",
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    guaranteed_ind: Optional[bool] = field(
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
    included_in_est_total_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "IncludedInEstTotalInd",
            "type": "Attribute",
        },
    )

    @dataclass
    class MinMax(object):
        max_charge: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "MaxCharge",
                "type": "Attribute",
            },
        )
        min_charge: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "MinCharge",
                "type": "Attribute",
            },
        )
        max_charge_days: Optional[int] = field(
            default=None,
            metadata={
                "name": "MaxChargeDays",
                "type": "Attribute",
            },
        )

    @dataclass
    class Calculation(object):
        unit_charge: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "UnitCharge",
                "type": "Attribute",
            },
        )
        unit_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "UnitName",
                "type": "Attribute",
            },
        )
        quantity: Optional[int] = field(
            default=None,
            metadata={
                "name": "Quantity",
                "type": "Attribute",
            },
        )
        percentage: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "Percentage",
                "type": "Attribute",
            },
        )
        applicability: Optional[CalculationApplicability] = field(
            default=None,
            metadata={
                "name": "Applicability",
                "type": "Attribute",
            },
        )
        max_quantity: Optional[int] = field(
            default=None,
            metadata={
                "name": "MaxQuantity",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleCoreType(object):
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
    air_condition_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "AirConditionInd",
            "type": "Attribute",
        },
    )
    transmission_type: Optional[VehicleTransmissionType] = field(
        default=None,
        metadata={
            "name": "TransmissionType",
            "type": "Attribute",
        },
    )
    fuel_type: Optional[VehicleCoreTypeFuelType] = field(
        default=None,
        metadata={
            "name": "FuelType",
            "type": "Attribute",
        },
    )
    drive_type: Optional[VehicleCoreTypeDriveType] = field(
        default=None,
        metadata={
            "name": "DriveType",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehType(object):
        vehicle_category: Optional[str] = field(
            default=None,
            metadata={
                "name": "VehicleCategory",
                "type": "Attribute",
            },
        )
        door_count: Optional[str] = field(
            default=None,
            metadata={
                "name": "DoorCount",
                "type": "Attribute",
            },
        )

    @dataclass
    class VehClass(object):
        size: Optional[str] = field(
            default=None,
            metadata={
                "name": "Size",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleEquipmentType(object):
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    equip_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "EquipType",
            "type": "Attribute",
        },
    )
    quantity: Optional[int] = field(
        default=None,
        metadata={
            "name": "Quantity",
            "type": "Attribute",
        },
    )
    restriction: Optional[EquipmentRestrictionType] = field(
        default=None,
        metadata={
            "name": "Restriction",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRentalCoreType(object):
    pick_up_location: List["VehicleRentalCoreType.PickUpLocation"] = field(
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
    pick_up_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "PickUpDateTime",
            "type": "Attribute",
        },
    )
    return_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ReturnDateTime",
            "type": "Attribute",
        },
    )
    start_charges_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "StartChargesDateTime",
            "type": "Attribute",
        },
    )
    stop_charges_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "StopChargesDateTime",
            "type": "Attribute",
        },
    )
    one_way_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "OneWayIndicator",
            "type": "Attribute",
        },
    )
    multi_island_rental_days: Optional[int] = field(
        default=None,
        metadata={
            "name": "MultiIslandRentalDays",
            "type": "Attribute",
        },
    )
    quantity: Optional[int] = field(
        default=None,
        metadata={
            "name": "Quantity",
            "type": "Attribute",
        },
    )
    dist_unit_name: Optional[DistanceUnitNameType] = field(
        default=None,
        metadata={
            "name": "DistUnitName",
            "type": "Attribute",
        },
    )

    @dataclass
    class PickUpLocation(LocationType):
        extended_location_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: Optional[str] = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )

    @dataclass
    class ReturnLocation(LocationType):
        extended_location_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: Optional[str] = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleResRsadditionalInfoType(object):
    class Meta(object):
        name = "VehicleResRSAdditionalInfoType"

    tpa_extensions: Optional[TpaExtensionsType] = field(
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
    class Meta(object):
        name = "VehicleReservationRQCoreTypeSpecialEquipPrefsSpecialEquipPref"

    prefer_level: PreferLevelType = field(
        default=PreferLevelType.PREFERRED,
        metadata={
            "name": "PreferLevel",
            "type": "Attribute",
        },
    )
    action: Optional[ActionType] = field(
        default=None,
        metadata={
            "name": "Action",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRetrieveResRsadditionalInfoType(object):
    class Meta(object):
        name = "VehicleRetrieveResRSAdditionalInfoType"

    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleSpecialReqPrefType(object):
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
class VehicleTourInfoType(object):
    tour_operator: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "TourOperator",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "TourNumber",
            "type": "Attribute",
        },
    )


@dataclass
class WarningType(FreeTextType):
    type: Optional[str] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )
    short_text: Optional[str] = field(
        default=None,
        metadata={
            "name": "ShortText",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    doc_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocURL",
            "type": "Attribute",
        },
    )
    status: Optional[str] = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    tag: Optional[str] = field(
        default=None,
        metadata={
            "name": "Tag",
            "type": "Attribute",
        },
    )
    record_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "RecordID",
            "type": "Attribute",
        },
    )


@dataclass
class InformationHeader(InformationHeader1):
    class Meta(object):
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
    use_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "UseType",
            "type": "Attribute",
        },
    )
    rph: Optional[str] = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfErrorType(object):
    error: List[ErrorType] = field(
        default_factory=list,
        metadata={
            "name": "Error",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleCoreType(object):
    vehicle: List[VehicleCoreType] = field(
        default_factory=list,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfWarningType(object):
    warning: List[WarningType] = field(
        default_factory=list,
        metadata={
            "name": "Warning",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class CancelInfoRqtype(object):
    class Meta(object):
        name = "CancelInfoRQType"

    unique_id: List[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cancel_type: Optional[TransactionActionType] = field(
        default=None,
        metadata={
            "name": "CancelType",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class CoveragePricedType(object):
    coverage: Optional[CoverageType] = field(
        default=None,
        metadata={
            "name": "Coverage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    charge: Optional[VehicleChargeType] = field(
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
class DocumentType(object):
    doc_holder_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocHolderName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    doc_holder_formatted_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "DocHolderFormattedName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    doc_limitations: List[str] = field(
        default_factory=list,
        metadata={
            "name": "DocLimitations",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional_person_names: Optional[ArrayOfString] = field(
        default=None,
        metadata={
            "name": "AdditionalPersonNames",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[DocumentTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[DocumentTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    doc_issue_authority: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocIssueAuthority",
            "type": "Attribute",
        },
    )
    doc_issue_location: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocIssueLocation",
            "type": "Attribute",
        },
    )
    doc_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocID",
            "type": "Attribute",
        },
    )
    doc_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocType",
            "type": "Attribute",
        },
    )
    gender: Optional[DocumentTypeGender] = field(
        default=None,
        metadata={
            "name": "Gender",
            "type": "Attribute",
        },
    )
    birth_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "BirthDate",
            "type": "Attribute",
        },
    )
    effective_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "EffectiveDate",
            "type": "Attribute",
        },
    )
    expire_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "ExpireDate",
            "type": "Attribute",
        },
    )
    doc_issue_state_prov: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocIssueStateProv",
            "type": "Attribute",
        },
    )
    doc_issue_country: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocIssueCountry",
            "type": "Attribute",
        },
    )
    birth_country: Optional[str] = field(
        default=None,
        metadata={
            "name": "BirthCountry",
            "type": "Attribute",
        },
    )
    doc_holder_nationality: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocHolderNationality",
            "type": "Attribute",
        },
    )


@dataclass
class FormattedTextSubSectionType(object):
    paragraph: List[ParagraphType] = field(
        default_factory=list,
        metadata={
            "name": "Paragraph",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    sub_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "SubTitle",
            "type": "Attribute",
        },
    )
    sub_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "SubCode",
            "type": "Attribute",
        },
    )
    sub_section_number: Optional[int] = field(
        default=None,
        metadata={
            "name": "SubSectionNumber",
            "type": "Attribute",
        },
    )


@dataclass
class ItemSearchCriterionType(object):
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
    telephone: Optional[object] = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    ref_point: List["ItemSearchCriterionType.RefPoint"] = field(
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
    exact_match: Optional[bool] = field(
        default=None,
        metadata={
            "name": "ExactMatch",
            "type": "Attribute",
        },
    )
    importance_type: Optional[ItemSearchCriterionTypeImportanceType] = field(
        default=None,
        metadata={
            "name": "ImportanceType",
            "type": "Attribute",
        },
    )
    ranking: Optional[int] = field(
        default=None,
        metadata={
            "name": "Ranking",
            "type": "Attribute",
        },
    )

    @dataclass
    class Position(object):
        latitude: Optional[str] = field(
            default=None,
            metadata={
                "name": "Latitude",
                "type": "Attribute",
            },
        )
        longitude: Optional[str] = field(
            default=None,
            metadata={
                "name": "Longitude",
                "type": "Attribute",
            },
        )
        altitude: Optional[str] = field(
            default=None,
            metadata={
                "name": "Altitude",
                "type": "Attribute",
            },
        )
        altitude_unit_of_measure_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "AltitudeUnitOfMeasureCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class Address(AddressType):
        same_country_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "SameCountryInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class RefPoint(object):
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        state_prov: Optional[str] = field(
            default=None,
            metadata={
                "name": "StateProv",
                "type": "Attribute",
            },
        )
        country_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CountryCode",
                "type": "Attribute",
            },
        )
        uri: Optional[str] = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )
        ref_point_type: Optional[str] = field(
            default=None,
            metadata={
                "name": "RefPointType",
                "type": "Attribute",
            },
        )
        name: Optional[str] = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )
        city_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "CityName",
                "type": "Attribute",
            },
        )

    @dataclass
    class CodeRef(LocationType):
        vicinity_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "VicinityCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class HotelRef(object):
        chain_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ChainCode",
                "type": "Attribute",
            },
        )
        brand_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "BrandCode",
                "type": "Attribute",
            },
        )
        hotel_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "HotelCode",
                "type": "Attribute",
            },
        )
        hotel_city_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "HotelCityCode",
                "type": "Attribute",
            },
        )
        hotel_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "HotelName",
                "type": "Attribute",
            },
        )
        hotel_code_context: Optional[str] = field(
            default=None,
            metadata={
                "name": "HotelCodeContext",
                "type": "Attribute",
            },
        )
        chain_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "ChainName",
                "type": "Attribute",
            },
        )
        brand_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "BrandName",
                "type": "Attribute",
            },
        )
        segment_category_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "SegmentCategoryCode",
                "type": "Attribute",
            },
        )
        property_class_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "PropertyClassCode",
                "type": "Attribute",
            },
        )
        architectural_style_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ArchitecturalStyleCode",
                "type": "Attribute",
            },
        )
        supplier_integration_level: Optional[int] = field(
            default=None,
            metadata={
                "name": "SupplierIntegrationLevel",
                "type": "Attribute",
            },
        )

    @dataclass
    class Radius(object):
        distance: Optional[str] = field(
            default=None,
            metadata={
                "name": "Distance",
                "type": "Attribute",
            },
        )
        distance_measure: Optional[str] = field(
            default=None,
            metadata={
                "name": "DistanceMeasure",
                "type": "Attribute",
            },
        )
        direction: Optional[str] = field(
            default=None,
            metadata={
                "name": "Direction",
                "type": "Attribute",
            },
        )
        distance_max: Optional[str] = field(
            default=None,
            metadata={
                "name": "DistanceMax",
                "type": "Attribute",
            },
        )


@dataclass
class OffLocationServiceCoreType(object):
    address: Optional["OffLocationServiceCoreType.Address"] = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    type: Optional[OffLocationServiceIdType] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass
    class Address(AddressType):
        site_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "SiteID",
                "type": "Attribute",
            },
        )
        site_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "SiteName",
                "type": "Attribute",
            },
        )


@dataclass
class OperationSchedulesType(object):
    operation_schedule: List[OperationScheduleType] = field(
        default_factory=list,
        metadata={
            "name": "OperationSchedule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    start: Optional[str] = field(
        default=None,
        metadata={
            "name": "Start",
            "type": "Attribute",
        },
    )
    duration: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    end: Optional[str] = field(
        default=None,
        metadata={
            "name": "End",
            "type": "Attribute",
        },
    )


@dataclass
class PaymentCardType(object):
    card_holder_name: Optional[str] = field(
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
    address: Optional[AddressType] = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[PaymentCardTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[PaymentCardTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    card_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "CardType",
            "type": "Attribute",
        },
    )
    card_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "CardCode",
            "type": "Attribute",
        },
    )
    card_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "CardNumber",
            "type": "Attribute",
        },
    )
    series_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "SeriesCode",
            "type": "Attribute",
        },
    )
    effective_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "EffectiveDate",
            "type": "Attribute",
        },
    )
    expire_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "ExpireDate",
            "type": "Attribute",
        },
    )
    masked_card_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaskedCardNumber",
            "type": "Attribute",
        },
    )
    card_holder_rph: Optional[str] = field(
        default=None,
        metadata={
            "name": "CardHolderRPH",
            "type": "Attribute",
        },
    )
    extend_payment_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "ExtendPaymentIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class CardIssuerName(object):
        bank_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "BankID",
                "type": "Attribute",
            },
        )


@dataclass
class PingRs(OtaResponse):
    class Meta(object):
        name = "PingRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    echo_data: List[str] = field(
        default_factory=list,
        metadata={
            "name": "EchoData",
            "type": "Element",
            "sequential": True,
        },
    )
    errors: List[ErrorType] = field(
        default_factory=list,
        metadata={
            "name": "Errors",
            "type": "Element",
            "sequential": True,
        },
    )
    success: List[SuccessType] = field(
        default_factory=list,
        metadata={
            "name": "Success",
            "type": "Element",
            "sequential": True,
        },
    )
    warnings: List[WarningType] = field(
        default_factory=list,
        metadata={
            "name": "Warnings",
            "type": "Element",
            "sequential": True,
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[PingRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class RateQualifierType(object):
    promo_desc: Optional[str] = field(
        default=None,
        metadata={
            "name": "PromoDesc",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_comments: Optional[ArrayOfRateQualifierTypeRateComment] = field(
        default=None,
        metadata={
            "name": "RateComments",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    travel_purpose: Optional[str] = field(
        default=None,
        metadata={
            "name": "TravelPurpose",
            "type": "Attribute",
        },
    )
    rate_category: Optional[str] = field(
        default=None,
        metadata={
            "name": "RateCategory",
            "type": "Attribute",
        },
    )
    corp_discount_nmbr: Optional[str] = field(
        default=None,
        metadata={
            "name": "CorpDiscountNmbr",
            "type": "Attribute",
        },
    )
    rate_qualifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "RateQualifier",
            "type": "Attribute",
        },
    )
    rate_period: Optional[RateQualifierTypeRatePeriod] = field(
        default=None,
        metadata={
            "name": "RatePeriod",
            "type": "Attribute",
        },
    )
    guaranteed_ind: Optional[bool] = field(
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
    rate_authorization_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "RateAuthorizationCode",
            "type": "Attribute",
        },
    )
    vendor_rate_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "VendorRateID",
            "type": "Attribute",
        },
    )


@dataclass
class RelatedTravelerType(object):
    unique_id: Optional[UniqueIdType] = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[RelatedTravelerTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[RelatedTravelerTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    relation: Optional[str] = field(
        default=None,
        metadata={
            "name": "Relation",
            "type": "Attribute",
        },
    )


@dataclass
class ServiceSoapGetPingInput(object):
    class Meta(object):
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
    class Body(object):
        ping_rq: Optional[PingRq] = field(
            default=None,
            metadata={
                "name": "PingRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class SourceType(object):
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
    agent_sine: Optional[str] = field(
        default=None,
        metadata={
            "name": "AgentSine",
            "type": "Attribute",
        },
    )
    pseudo_city_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "PseudoCityCode",
            "type": "Attribute",
        },
    )
    isocountry: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISOCountry",
            "type": "Attribute",
        },
    )
    isocurrency: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISOCurrency",
            "type": "Attribute",
        },
    )
    agent_duty_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "AgentDutyCode",
            "type": "Attribute",
        },
    )
    airline_vendor_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "AirlineVendorID",
            "type": "Attribute",
        },
    )
    airport_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "AirportCode",
            "type": "Attribute",
        },
    )
    first_depart_point: Optional[str] = field(
        default=None,
        metadata={
            "name": "FirstDepartPoint",
            "type": "Attribute",
        },
    )
    ersp_user_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ERSP_UserID",
            "type": "Attribute",
        },
    )
    terminal_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TerminalID",
            "type": "Attribute",
        },
    )

    @dataclass
    class RequestorId(UniqueIdType):
        message_password: Optional[str] = field(
            default=None,
            metadata={
                "name": "MessagePassword",
                "type": "Attribute",
            },
        )

    @dataclass
    class Position(object):
        latitude: Optional[str] = field(
            default=None,
            metadata={
                "name": "Latitude",
                "type": "Attribute",
            },
        )
        longitude: Optional[str] = field(
            default=None,
            metadata={
                "name": "Longitude",
                "type": "Attribute",
            },
        )
        altitude: Optional[str] = field(
            default=None,
            metadata={
                "name": "Altitude",
                "type": "Attribute",
            },
        )
        altitude_unit_of_measure_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "AltitudeUnitOfMeasureCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class BookingChannel(object):
        company_name: Optional[CompanyNameType] = field(
            default=None,
            metadata={
                "name": "CompanyName",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: Optional[str] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )
        primary: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Primary",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleChargePurposeType(VehicleChargeType):
    purpose: Optional[str] = field(
        default=None,
        metadata={
            "name": "Purpose",
            "type": "Attribute",
        },
    )
    rate_convert_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RateConvertInd",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleEquipmentPricedType(object):
    equipment: Optional[VehicleEquipmentType] = field(
        default=None,
        metadata={
            "name": "Equipment",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    charge: Optional[VehicleChargeType] = field(
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
    type_pref: Optional[PreferLevelType] = field(
        default=None,
        metadata={
            "name": "TypePref",
            "type": "Attribute",
        },
    )
    class_pref: Optional[PreferLevelType] = field(
        default=None,
        metadata={
            "name": "ClassPref",
            "type": "Attribute",
        },
    )
    air_condition_pref: Optional[PreferLevelType] = field(
        default=None,
        metadata={
            "name": "AirConditionPref",
            "type": "Attribute",
        },
    )
    transmission_pref: Optional[PreferLevelType] = field(
        default=None,
        metadata={
            "name": "TransmissionPref",
            "type": "Attribute",
        },
    )
    vendor_car_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "VendorCarType",
            "type": "Attribute",
        },
    )
    vehicle_qty: Optional[int] = field(
        default=None,
        metadata={
            "name": "VehicleQty",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRetrieveResRqadditionalInfoType(object):
    class Meta(object):
        name = "VehicleRetrieveResRQAdditionalInfoType"

    pick_up_location: Optional[LocationType] = field(
        default=None,
        metadata={
            "name": "PickUpLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: Optional[object] = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: Optional[EmailType] = field(
        default=None,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "PickUpDateTime",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRetrieveResRqcoreType(object):
    class Meta(object):
        name = "VehicleRetrieveResRQCoreType"

    unique_id: Optional[UniqueIdType] = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: Optional[PersonNameType] = field(
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class CustLoyalty(object):
        program_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "ProgramID",
                "type": "Attribute",
            },
        )
        membership_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "MembershipID",
                "type": "Attribute",
            },
        )
        travel_sector: Optional[str] = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        rph: Optional[str] = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )
        vendor_code: List[str] = field(
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
    picture_url: Optional[str] = field(
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
    passenger_quantity: Optional[str] = field(
        default=None,
        metadata={
            "name": "PassengerQuantity",
            "type": "Attribute",
        },
    )
    baggage_quantity: Optional[int] = field(
        default=None,
        metadata={
            "name": "BaggageQuantity",
            "type": "Attribute",
        },
    )
    vendor_car_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "VendorCarType",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )
    unit_of_measure_quantity: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "UnitOfMeasureQuantity",
            "type": "Attribute",
        },
    )
    unit_of_measure: Optional[str] = field(
        default=None,
        metadata={
            "name": "UnitOfMeasure",
            "type": "Attribute",
        },
    )
    unit_of_measure_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "UnitOfMeasureCode",
            "type": "Attribute",
        },
    )
    start: Optional[str] = field(
        default=None,
        metadata={
            "name": "Start",
            "type": "Attribute",
        },
    )
    duration: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    end: Optional[str] = field(
        default=None,
        metadata={
            "name": "End",
            "type": "Attribute",
        },
    )
    odometer_unit_of_measure: Optional[DistanceUnitNameType] = field(
        default=None,
        metadata={
            "name": "OdometerUnitOfMeasure",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehMakeModel(object):
        model_year: Optional[XmlPeriod] = field(
            default=None,
            metadata={
                "name": "ModelYear",
                "type": "Attribute",
            },
        )
        name: Optional[str] = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )

    @dataclass
    class VehIdentity(object):
        vehicle_asset_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "VehicleAssetNumber",
                "type": "Attribute",
            },
        )
        license_plate_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "LicensePlateNumber",
                "type": "Attribute",
            },
        )
        state_prov_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "StateProvCode",
                "type": "Attribute",
            },
        )
        country_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CountryCode",
                "type": "Attribute",
            },
        )
        vehicle_id_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "VehicleID_Number",
                "type": "Attribute",
            },
        )
        vehicle_color: Optional[str] = field(
            default=None,
            metadata={
                "name": "VehicleColor",
                "type": "Attribute",
            },
        )


@dataclass
class WrittenConfInstType(object):
    supplemental_data: Optional[ParagraphType] = field(
        default=None,
        metadata={
            "name": "SupplementalData",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: Optional[EmailType] = field(
        default=None,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    language_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "LanguageID",
            "type": "Attribute",
        },
    )
    addressee_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "AddresseeName",
            "type": "Attribute",
        },
    )
    address: Optional[str] = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Attribute",
        },
    )
    telephone: Optional[str] = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Attribute",
        },
    )
    confirm_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "ConfirmInd",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfCoveragePricedType(object):
    priced_coverage: List[CoveragePricedType] = field(
        default_factory=list,
        metadata={
            "name": "PricedCoverage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfSourceType(object):
    source: List[SourceType] = field(
        default_factory=list,
        metadata={
            "name": "Source",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleAvailRqcoreTypeVehPref(object):
    class Meta(object):
        name = "ArrayOfVehicleAvailRQCoreTypeVehPref"

    veh_pref: List["ArrayOfVehicleAvailRqcoreTypeVehPref.VehPref"] = field(
        default_factory=list,
        metadata={
            "name": "VehPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class VehPref(VehiclePrefType):
        up_sell_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "UpSellInd",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleChargePurposeType(object):
    vehicle_charge: List[VehicleChargePurposeType] = field(
        default_factory=list,
        metadata={
            "name": "VehicleCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleChargePurposeType1(object):
    fee: List[VehicleChargePurposeType] = field(
        default_factory=list,
        metadata={
            "name": "Fee",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleEquipmentPricedType(object):
    priced_equip: List[VehicleEquipmentPricedType] = field(
        default_factory=list,
        metadata={
            "name": "PricedEquip",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFeeVehicle(object):
    vehicle: List[
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
        include_exclude: Optional[IncludeExcludeType] = field(
            default=None,
            metadata={
                "name": "IncludeExclude",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOffLocationServiceOffLocServiceCharge(
    object,
):
    off_loc_service_charge: List[
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
        vehicles: Optional[ArrayOfVehicleCoreType] = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOnLocationServiceOnLocServiceCharge(
    object,
):
    on_loc_service_charge: List[
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
        vehicles: Optional[ArrayOfVehicleCoreType] = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipmentEquipCharge(object):
    equip_charge: List[
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
        vehicles: Optional[ArrayOfVehicleCoreType] = field(
            default=None,
            metadata={
                "name": "Vehicles",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class CancelRuleType(object):
    payment_card: Optional[PaymentCardType] = field(
        default=None,
        metadata={
            "name": "PaymentCard",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cancel_by_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "CancelByDate",
            "type": "Attribute",
        },
    )
    amount: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Attribute",
        },
    )
    percent: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Percent",
            "type": "Attribute",
        },
    )
    type: Optional[CancelRuleTypeType] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )


@dataclass
class ContactPersonType(object):
    person_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: List["ContactPersonType.Telephone"] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: List[AddressInfoType] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: List[EmailType] = field(
        default_factory=list,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: List[UrlType] = field(
        default_factory=list,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    company_name: List[CompanyNameType] = field(
        default_factory=list,
        metadata={
            "name": "CompanyName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    employee_info: List[EmployeeInfoType] = field(
        default_factory=list,
        metadata={
            "name": "EmployeeInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[ContactPersonTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[ContactPersonTypeShareMarketInd] = field(
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
    contact_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ContactType",
            "type": "Attribute",
        },
    )
    relation: Optional[str] = field(
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
    rph: Optional[str] = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )

    @dataclass
    class Telephone(object):
        rph: Optional[str] = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )


@dataclass
class DirectBillType(object):
    company_name: Optional["DirectBillType.CompanyName"] = field(
        default=None,
        metadata={
            "name": "CompanyName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: Optional[AddressInfoType] = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    share_synch_ind: Optional[DirectBillTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[DirectBillTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    direct_bill_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "DirectBill_ID",
            "type": "Attribute",
        },
    )
    billing_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "BillingNumber",
            "type": "Attribute",
        },
    )

    @dataclass
    class CompanyName(CompanyNameType):
        contact_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "ContactName",
                "type": "Attribute",
            },
        )


@dataclass
class FormattedTextType(object):
    sub_section: List[FormattedTextSubSectionType] = field(
        default_factory=list,
        metadata={
            "name": "SubSection",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    title: Optional[str] = field(
        default=None,
        metadata={
            "name": "Title",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


@dataclass
class OffLocationServiceType(OffLocationServiceCoreType):
    person_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: Optional[object] = field(
        default=None,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    spec_instructions: Optional[str] = field(
        default=None,
        metadata={
            "name": "SpecInstructions",
            "type": "Attribute",
        },
    )


@dataclass
class ServiceSoapGetPingOutput(object):
    class Meta(object):
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
    class Body(object):
        ping_rs: Optional[PingRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleReservationSummaryType(object):
    conf_id: Optional[UniqueIdType] = field(
        default=None,
        metadata={
            "name": "ConfID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_location: Optional[LocationType] = field(
        default=None,
        metadata={
            "name": "PickUpLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    return_location: Optional[LocationType] = field(
        default=None,
        metadata={
            "name": "ReturnLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    person_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle: Optional[VehicleType] = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pick_up_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "PickUpDateTime",
            "type": "Attribute",
        },
    )
    return_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ReturnDateTime",
            "type": "Attribute",
        },
    )


@dataclass
class AcceptablePaymentCardsInfoType(object):
    acceptable_payment_cards: Optional[
        ArrayOfAcceptablePaymentCardsInfoTypeAcceptablePaymentCard
    ] = field(
        default=None,
        metadata={
            "name": "AcceptablePaymentCards",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    info: Optional[FormattedTextType] = field(
        default=None,
        metadata={
            "name": "Info",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfCancelRuleType(object):
    cancel_rule: List[CancelRuleType] = field(
        default_factory=list,
        metadata={
            "name": "CancelRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfFormattedTextType(object):
    vendor_message: List[FormattedTextType] = field(
        default_factory=list,
        metadata={
            "name": "VendorMessage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleLocationAdditionalDetailsTypeShuttleShuttleInfo(object):
    shuttle_info: List[
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
        type: Optional[LocationDetailShuttleInfoType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFee(object):
    coverage_fee: List[
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
    class CoverageFee(object):
        charge: Optional[VehicleChargeType] = field(
            default=None,
            metadata={
                "name": "Charge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        vehicles: Optional[
            ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFeeVehicle
        ] = field(
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
        class Deductible(object):
            amount: Optional[Decimal] = field(
                default=None,
                metadata={
                    "name": "Amount",
                    "type": "Attribute",
                },
            )
            liability_amount: Optional[Decimal] = field(
                default=None,
                metadata={
                    "name": "LiabilityAmount",
                    "type": "Attribute",
                },
            )


@dataclass
class ArrayOfVehicleLocationRequirementsTypeAdditionalDriverAddlDriverInfo(object):
    addl_driver_info: List[
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
        type: Optional[LocationDetailRequirementAddlDriverInfoType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationRequirementsTypeAgeAgeInfo(object):
    age_info: List["ArrayOfVehicleLocationRequirementsTypeAgeAgeInfo.AgeInfo"] = field(
        default_factory=list,
        metadata={
            "name": "AgeInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class AgeInfo(FormattedTextType):
        type: Optional[LocationDetailRequirementAgeInfoType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationRequirementsTypeRequirementInfo(object):
    requirement_info: List[
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
        type: Optional[LocationDetailRequirementInfoType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOffLocationService(object):
    off_location_service: List[
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
    class OffLocationService(object):
        off_loc_service_desc: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "OffLocServiceDesc",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        operation_schedules: Optional[OperationSchedulesType] = field(
            default=None,
            metadata={
                "name": "OperationSchedules",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        off_loc_service_charges: Optional[
            ArrayOfVehicleLocationServicesOfferedTypeOffLocationServiceOffLocServiceCharge
        ] = field(
            default=None,
            metadata={
                "name": "OffLocServiceCharges",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: Optional[OffLocationServiceIdType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeOnLocationService(object):
    on_location_service: List[
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
    class OnLocationService(object):
        on_loc_service_desc: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "OnLocServiceDesc",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        operation_schedules: Optional[OperationSchedulesType] = field(
            default=None,
            metadata={
                "name": "OperationSchedules",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        on_loc_service_charges: Optional[
            ArrayOfVehicleLocationServicesOfferedTypeOnLocationServiceOnLocServiceCharge
        ] = field(
            default=None,
            metadata={
                "name": "OnLocServiceCharges",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: Optional[OnLocationServiceIdType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipment(object):
    special_equipment: List[
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
    class SpecialEquipment(object):
        equip_desc: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "EquipDesc",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        equip_charges: Optional[
            ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipmentEquipCharge
        ] = field(
            default=None,
            metadata={
                "name": "EquipCharges",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: Optional[str] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVehicleLocationVehiclesTypeVehicleInfo(object):
    vehicle_info: List[
        "ArrayOfVehicleLocationVehiclesTypeVehicleInfo.VehicleInfo"
    ] = field(
        default_factory=list,
        metadata={
            "name": "VehicleInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class VehicleInfo(FormattedTextType):
        type: Optional[LocationDetailVehicleInfoType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class ArrayOfVehicleReservationSummaryType(object):
    veh_res_summary: List[VehicleReservationSummaryType] = field(
        default_factory=list,
        metadata={
            "name": "VehResSummary",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class OffLocationServicePricedType(object):
    off_loc_service: Optional[OffLocationServiceType] = field(
        default=None,
        metadata={
            "name": "OffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    charge: Optional[VehicleChargeType] = field(
        default=None,
        metadata={
            "name": "Charge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class PaymentFormType(object):
    payment_card: Optional[PaymentCardType] = field(
        default=None,
        metadata={
            "name": "PaymentCard",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    bank_acct: Optional[BankAcctType] = field(
        default=None,
        metadata={
            "name": "BankAcct",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    direct_bill: Optional[DirectBillType] = field(
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
    share_synch_ind: Optional[PaymentFormTypeShareSynchInd] = field(
        default=None,
        metadata={
            "name": "ShareSynchInd",
            "type": "Attribute",
        },
    )
    share_market_ind: Optional[PaymentFormTypeShareMarketInd] = field(
        default=None,
        metadata={
            "name": "ShareMarketInd",
            "type": "Attribute",
        },
    )
    cost_center_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CostCenterID",
            "type": "Attribute",
        },
    )
    rph: Optional[str] = field(
        default=None,
        metadata={
            "name": "RPH",
            "type": "Attribute",
        },
    )
    payment_transaction_type_code: Optional[
        PaymentFormTypePaymentTransactionTypeCode
    ] = field(
        default=None,
        metadata={
            "name": "PaymentTransactionTypeCode",
            "type": "Attribute",
        },
    )

    @dataclass
    class Voucher(object):
        series_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "SeriesCode",
                "type": "Attribute",
            },
        )
        billing_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "BillingNumber",
                "type": "Attribute",
            },
        )
        supplier_identifier: Optional[str] = field(
            default=None,
            metadata={
                "name": "SupplierIdentifier",
                "type": "Attribute",
            },
        )
        identifier: Optional[str] = field(
            default=None,
            metadata={
                "name": "Identifier",
                "type": "Attribute",
            },
        )
        value_type: Optional[str] = field(
            default=None,
            metadata={
                "name": "ValueType",
                "type": "Attribute",
            },
        )
        electronic_indicator: Optional[bool] = field(
            default=None,
            metadata={
                "name": "ElectronicIndicator",
                "type": "Attribute",
            },
        )

    @dataclass
    class LoyaltyRedemption(object):
        loyalty_certificate: List[
            "PaymentFormType.LoyaltyRedemption.LoyaltyCertificate"
        ] = field(
            default_factory=list,
            metadata={
                "name": "LoyaltyCertificate",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        certificate_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "CertificateNumber",
                "type": "Attribute",
            },
        )
        member_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "MemberNumber",
                "type": "Attribute",
            },
        )
        program_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "ProgramName",
                "type": "Attribute",
            },
        )
        promotion_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "PromotionCode",
                "type": "Attribute",
            },
        )
        promotion_vendor_code: List[str] = field(
            default_factory=list,
            metadata={
                "name": "PromotionVendorCode",
                "type": "Attribute",
                "tokens": True,
            },
        )
        redemption_quantity: Optional[int] = field(
            default=None,
            metadata={
                "name": "RedemptionQuantity",
                "type": "Attribute",
            },
        )

        @dataclass
        class LoyaltyCertificate(object):
            id_context: Optional[str] = field(
                default=None,
                metadata={
                    "name": "ID_Context",
                    "type": "Attribute",
                },
            )
            nmbr_of_nights: Optional[int] = field(
                default=None,
                metadata={
                    "name": "NmbrOfNights",
                    "type": "Attribute",
                },
            )
            format: Optional[LoyaltyCertificateFormat] = field(
                default=None,
                metadata={
                    "name": "Format",
                    "type": "Attribute",
                },
            )
            status: Optional[str] = field(
                default=None,
                metadata={
                    "name": "Status",
                    "type": "Attribute",
                },
            )

    @dataclass
    class MiscChargeOrder(object):
        ticket_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "TicketNumber",
                "type": "Attribute",
            },
        )

    @dataclass
    class Cash(object):
        cash_indicator: bool = field(
            default=True,
            metadata={
                "name": "CashIndicator",
                "type": "Attribute",
            },
        )


class ServiceSoapGetPing(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getPing"
    input = ServiceSoapGetPingInput
    output = ServiceSoapGetPingOutput


@dataclass
class VehCancelResRq(object):
    class Meta(object):
        name = "VehCancelResRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_cancel_rqcore: Optional[CancelInfoRqtype] = field(
        default=None,
        metadata={
            "name": "VehCancelRQCore",
            "type": "Element",
        },
    )
    veh_cancel_rqinfo: Optional[VehicleCancelRqadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehCancelRQInfo",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehCancelResRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )


@dataclass
class VehLocDetailRq(object):
    class Meta(object):
        name = "VehLocDetailRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
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
    vendor: Optional[CompanyNameType] = field(
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
    keyword: List["VehLocDetailRq.Keyword"] = field(
        default_factory=list,
        metadata={
            "name": "Keyword",
            "type": "Element",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehLocDetailRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )

    @dataclass
    class Location(LocationType):
        extended_location_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class ResponseFilter(object):
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
    class Date(object):
        pick_up_date_time: Optional[str] = field(
            default=None,
            metadata={
                "name": "PickUpDateTime",
                "type": "Attribute",
            },
        )
        return_date_time: Optional[str] = field(
            default=None,
            metadata={
                "name": "ReturnDateTime",
                "type": "Attribute",
            },
        )

    @dataclass
    class Keyword(object):
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )


@dataclass
class VehLocationSearchRq(object):
    class Meta(object):
        name = "VehLocationSearchRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_loc_search_criterion: List[ItemSearchCriterionType] = field(
        default_factory=list,
        metadata={
            "name": "VehLocSearchCriterion",
            "type": "Element",
        },
    )
    vendor: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehLocationSearchRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    max_responses: Optional[int] = field(
        default=None,
        metadata={
            "name": "MaxResponses",
            "type": "Attribute",
        },
    )
    req_resp_version: Optional[str] = field(
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
class VehRateRuleRq(object):
    class Meta(object):
        name = "VehRateRuleRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    reference: Optional[UniqueIdType] = field(
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
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehRateRuleRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    company_short_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "CompanyShortName",
            "type": "Attribute",
        },
    )
    travel_sector: Optional[str] = field(
        default=None,
        metadata={
            "name": "TravelSector",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    code_context: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )

    @dataclass
    class RentalInfo(object):
        veh_rental_core: Optional[VehicleRentalCoreType] = field(
            default=None,
            metadata={
                "name": "VehRentalCore",
                "type": "Element",
            },
        )
        vehicle_info: Optional[VehiclePrefType] = field(
            default=None,
            metadata={
                "name": "VehicleInfo",
                "type": "Element",
            },
        )
        special_equip_prefs: Optional[
            ArrayOfOtaVehRateRuleRqrentalInfoSpecialEquipPref
        ] = field(
            default=None,
            metadata={
                "name": "SpecialEquipPrefs",
                "type": "Element",
            },
        )
        cust_loyalty: List["VehRateRuleRq.RentalInfo.CustLoyalty"] = field(
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
        off_loc_service: Optional[OffLocationServiceType] = field(
            default=None,
            metadata={
                "name": "OffLocService",
                "type": "Element",
            },
        )
        arrival_details: Optional[VehicleArrivalDetailsType] = field(
            default=None,
            metadata={
                "name": "ArrivalDetails",
                "type": "Element",
            },
        )
        tour_info: Optional[VehicleTourInfoType] = field(
            default=None,
            metadata={
                "name": "TourInfo",
                "type": "Element",
            },
        )
        customer_id: Optional[UniqueIdType] = field(
            default=None,
            metadata={
                "name": "CustomerID",
                "type": "Element",
            },
        )
        tpa_extensions: Optional[TpaExtensionsType] = field(
            default=None,
            metadata={
                "name": "TPA_Extensions",
                "type": "Element",
            },
        )

        @dataclass
        class CustLoyalty(object):
            program_id: Optional[str] = field(
                default=None,
                metadata={
                    "name": "ProgramID",
                    "type": "Attribute",
                },
            )
            membership_id: Optional[str] = field(
                default=None,
                metadata={
                    "name": "MembershipID",
                    "type": "Attribute",
                },
            )
            travel_sector: Optional[str] = field(
                default=None,
                metadata={
                    "name": "TravelSector",
                    "type": "Attribute",
                },
            )
            rph: Optional[str] = field(
                default=None,
                metadata={
                    "name": "RPH",
                    "type": "Attribute",
                },
            )
            vendor_code: List[str] = field(
                default_factory=list,
                metadata={
                    "name": "VendorCode",
                    "type": "Attribute",
                    "tokens": True,
                },
            )

        @dataclass
        class RateQualifier(object):
            travel_purpose: Optional[str] = field(
                default=None,
                metadata={
                    "name": "TravelPurpose",
                    "type": "Attribute",
                },
            )
            rate_category: Optional[str] = field(
                default=None,
                metadata={
                    "name": "RateCategory",
                    "type": "Attribute",
                },
            )
            corp_discount_nmbr: Optional[str] = field(
                default=None,
                metadata={
                    "name": "CorpDiscountNmbr",
                    "type": "Attribute",
                },
            )
            rate_qualifier: Optional[str] = field(
                default=None,
                metadata={
                    "name": "RateQualifier",
                    "type": "Attribute",
                },
            )
            rate_period: Optional[
                OtaVehRateRuleRqrentalInfoRateQualifierRatePeriod
            ] = field(
                default=None,
                metadata={
                    "name": "RatePeriod",
                    "type": "Attribute",
                },
            )
            guaranteed_ind: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "GuaranteedInd",
                    "type": "Attribute",
                },
            )
            rate_authorization_code: Optional[str] = field(
                default=None,
                metadata={
                    "name": "RateAuthorizationCode",
                    "type": "Attribute",
                },
            )
            vendor_rate_id: Optional[str] = field(
                default=None,
                metadata={
                    "name": "VendorRateID",
                    "type": "Attribute",
                },
            )
            rate_modified_ind: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "RateModifiedInd",
                    "type": "Attribute",
                },
            )


@dataclass
class VehRetResRq(object):
    class Meta(object):
        name = "VehRetResRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    veh_ret_res_rqcore: Optional[VehicleRetrieveResRqcoreType] = field(
        default=None,
        metadata={
            "name": "VehRetResRQCore",
            "type": "Element",
        },
    )
    veh_ret_res_rqinfo: Optional[VehicleRetrieveResRqadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehRetResRQInfo",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehRetResRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailAdditionalInfoType(object):
    priced_coverages: Optional[ArrayOfCoveragePricedType] = field(
        default=None,
        metadata={
            "name": "PricedCoverages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_rules: Optional[ArrayOfMonetaryRuleType] = field(
        default=None,
        metadata={
            "name": "PaymentRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    chargeable_period: Optional[XmlDuration] = field(
        default=None,
        metadata={
            "name": "ChargeablePeriod",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailRqcoreType(object):
    class Meta(object):
        name = "VehicleAvailRQCoreType"

    rate_query_parameter_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "RateQueryParameterType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_rental_core: Optional[VehicleRentalCoreType] = field(
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
    veh_prefs: Optional[ArrayOfVehicleAvailRqcoreTypeVehPref] = field(
        default=None,
        metadata={
            "name": "VehPrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    driver_type: List["VehicleAvailRqcoreType.DriverType"] = field(
        default_factory=list,
        metadata={
            "name": "DriverType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_qualifier: List["VehicleAvailRqcoreType.RateQualifier"] = field(
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
    special_equip_prefs: Optional[
        ArrayOfVehicleAvailRqcoreTypeSpecialEquipPref
    ] = field(
        default=None,
        metadata={
            "name": "SpecialEquipPrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_query_type: Optional[RateQueryType] = field(
        default=None,
        metadata={
            "name": "RateQueryType",
            "type": "Attribute",
            "required": True,
        },
    )
    status: Optional[InventoryStatusType] = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    target_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "TargetSource",
            "type": "Attribute",
        },
    )

    @dataclass
    class VendorPrefs(object):
        vendor_pref: List["VehicleAvailRqcoreType.VendorPrefs.VendorPref"] = field(
            default_factory=list,
            metadata={
                "name": "VendorPref",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        participation_level_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ParticipationLevelCode",
                "type": "Attribute",
            },
        )
        location_category: Optional[str] = field(
            default=None,
            metadata={
                "name": "LocationCategory",
                "type": "Attribute",
            },
        )

        @dataclass
        class VendorPref(CompanyNamePrefType):
            corp_discount_nmbr: Optional[str] = field(
                default=None,
                metadata={
                    "name": "CorpDiscountNmbr",
                    "type": "Attribute",
                },
            )

    @dataclass
    class DriverType(object):
        age: Optional[int] = field(
            default=None,
            metadata={
                "name": "Age",
                "type": "Attribute",
            },
        )
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: Optional[str] = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )
        uri: Optional[str] = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateQualifier(object):
        travel_purpose: Optional[str] = field(
            default=None,
            metadata={
                "name": "TravelPurpose",
                "type": "Attribute",
            },
        )
        rate_category: Optional[str] = field(
            default=None,
            metadata={
                "name": "RateCategory",
                "type": "Attribute",
            },
        )
        corp_discount_nmbr: Optional[str] = field(
            default=None,
            metadata={
                "name": "CorpDiscountNmbr",
                "type": "Attribute",
            },
        )
        rate_qualifier: Optional[str] = field(
            default=None,
            metadata={
                "name": "RateQualifier",
                "type": "Attribute",
            },
        )
        rate_period: Optional[VehicleAvailRqcoreTypeRateQualifierRatePeriod] = field(
            default=None,
            metadata={
                "name": "RatePeriod",
                "type": "Attribute",
            },
        )
        guaranteed_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "GuaranteedInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateRange(object):
        min_rate: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "MinRate",
                "type": "Attribute",
            },
        )
        max_rate: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "MaxRate",
                "type": "Attribute",
            },
        )
        fixed_rate: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "FixedRate",
                "type": "Attribute",
            },
        )
        rate_time_unit: Optional[TimeUnitType] = field(
            default=None,
            metadata={
                "name": "RateTimeUnit",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleLocationAdditionalFeesType(object):
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Taxes(object):
        tax: List["VehicleLocationAdditionalFeesType.Taxes.Tax"] = field(
            default_factory=list,
            metadata={
                "name": "Tax",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        start: Optional[str] = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: Optional[str] = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: Optional[str] = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )

        @dataclass
        class Tax(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
            tax_code: Optional[str] = field(
                default=None,
                metadata={
                    "name": "TaxCode",
                    "type": "Attribute",
                },
            )
            percentage: Optional[Decimal] = field(
                default=None,
                metadata={
                    "name": "Percentage",
                    "type": "Attribute",
                },
            )

    @dataclass
    class Fees(object):
        fee: List["VehicleLocationAdditionalFeesType.Fees.Fee"] = field(
            default_factory=list,
            metadata={
                "name": "Fee",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class Fee(VehicleChargeType):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

    @dataclass
    class Surcharges(object):
        surcharge: List[
            "VehicleLocationAdditionalFeesType.Surcharges.Surcharge"
        ] = field(
            default_factory=list,
            metadata={
                "name": "Surcharge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        start: Optional[str] = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: Optional[str] = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: Optional[str] = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )

        @dataclass
        class Surcharge(VehicleChargeType):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

    @dataclass
    class MiscellaneousCharges(object):
        miscellaneous_charge: List[
            "VehicleLocationAdditionalFeesType.MiscellaneousCharges.MiscellaneousCharge"
        ] = field(
            default_factory=list,
            metadata={
                "name": "MiscellaneousCharge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        info: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "Info",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class MiscellaneousCharge(VehicleChargeType):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )


@dataclass
class VehicleLocationInformationType(FormattedTextType):
    type: Optional[str] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleRentalRateType(object):
    rate_distance: List["VehicleRentalRateType.RateDistance"] = field(
        default_factory=list,
        metadata={
            "name": "RateDistance",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle_charges: Optional[ArrayOfVehicleChargePurposeType] = field(
        default=None,
        metadata={
            "name": "VehicleCharges",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_qualifier: Optional[RateQualifierType] = field(
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
    pickup_return_rule: List["VehicleRentalRateType.PickupReturnRule"] = field(
        default_factory=list,
        metadata={
            "name": "PickupReturnRule",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class RateDistance(object):
        unlimited: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Unlimited",
                "type": "Attribute",
                "required": True,
            },
        )
        quantity: Optional[int] = field(
            default=None,
            metadata={
                "name": "Quantity",
                "type": "Attribute",
            },
        )
        dist_unit_name: Optional[DistanceUnitNameType] = field(
            default=None,
            metadata={
                "name": "DistUnitName",
                "type": "Attribute",
            },
        )
        vehicle_period_unit_name: Optional[VehiclePeriodUnitNameType] = field(
            default=None,
            metadata={
                "name": "VehiclePeriodUnitName",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateRestrictions(object):
        minimum_age: Optional[int] = field(
            default=None,
            metadata={
                "name": "MinimumAge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
                "required": True,
            },
        )
        maximum_age: Optional[int] = field(
            default=None,
            metadata={
                "name": "MaximumAge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
                "required": True,
            },
        )
        no_show_fee_ind: Optional[bool] = field(
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
        minimum_day_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "MinimumDayInd",
                "type": "Attribute",
            },
        )
        maximum_day_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "MaximumDayInd",
                "type": "Attribute",
            },
        )
        advanced_booking_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "AdvancedBookingInd",
                "type": "Attribute",
            },
        )
        restricted_mileage_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "RestrictedMileageInd",
                "type": "Attribute",
            },
        )
        corporate_rate_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "CorporateRateInd",
                "type": "Attribute",
            },
        )
        guarantee_req_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "GuaranteeReqInd",
                "type": "Attribute",
            },
        )
        maximum_vehicles_allowed: Optional[int] = field(
            default=None,
            metadata={
                "name": "MaximumVehiclesAllowed",
                "type": "Attribute",
            },
        )
        overnight_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "OvernightInd",
                "type": "Attribute",
            },
        )
        one_way_policy: Optional[RateRestrictionsOneWayPolicy] = field(
            default=None,
            metadata={
                "name": "OneWayPolicy",
                "type": "Attribute",
            },
        )
        cancellation_penalty_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "CancellationPenaltyInd",
                "type": "Attribute",
            },
        )
        modification_penalty_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "ModificationPenaltyInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateGuarantee(object):
        description: Optional[FormattedTextTextType] = field(
            default=None,
            metadata={
                "name": "Description",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        absolute_deadline: Optional[str] = field(
            default=None,
            metadata={
                "name": "AbsoluteDeadline",
                "type": "Attribute",
            },
        )
        offset_time_unit: Optional[TimeUnitType] = field(
            default=None,
            metadata={
                "name": "OffsetTimeUnit",
                "type": "Attribute",
            },
        )
        offset_unit_multiplier: Optional[int] = field(
            default=None,
            metadata={
                "name": "OffsetUnitMultiplier",
                "type": "Attribute",
            },
        )
        offset_drop_time: Optional[RateGuaranteeOffsetDropTime] = field(
            default=None,
            metadata={
                "name": "OffsetDropTime",
                "type": "Attribute",
            },
        )

    @dataclass
    class PickupReturnRule(object):
        day_of_week: Optional[DayOfWeekType] = field(
            default=None,
            metadata={
                "name": "DayOfWeek",
                "type": "Attribute",
            },
        )
        time: Optional[str] = field(
            default=None,
            metadata={
                "name": "Time",
                "type": "Attribute",
            },
        )
        rule_type: Optional[PickupReturnRuleRuleType] = field(
            default=None,
            metadata={
                "name": "RuleType",
                "type": "Attribute",
            },
        )


@dataclass
class VendorMessageType(FormattedTextType):
    info_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "InfoType",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfVehicleLocationInformationType(object):
    veh_rent_loc_info: List[VehicleLocationInformationType] = field(
        default_factory=list,
        metadata={
            "name": "VehRentLocInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfVehicleLocationLiabilitiesTypeCoverage(object):
    coverage: List["ArrayOfVehicleLocationLiabilitiesTypeCoverage.Coverage"] = field(
        default_factory=list,
        metadata={
            "name": "Coverage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Coverage(object):
        coverage_info: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "CoverageInfo",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        coverage_fees: Optional[
            ArrayOfVehicleLocationLiabilitiesTypeCoverageCoverageFee
        ] = field(
            default=None,
            metadata={
                "name": "CoverageFees",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        type: Optional[str] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )
        required_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "RequiredInd",
                "type": "Attribute",
            },
        )


@dataclass
class ArrayOfVendorMessageType(object):
    vendor_message: List[VendorMessageType] = field(
        default_factory=list,
        metadata={
            "name": "VendorMessage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class CancelInfoRstype(object):
    class Meta(object):
        name = "CancelInfoRSType"

    cancel_rules: Optional[ArrayOfCancelRuleType] = field(
        default=None,
        metadata={
            "name": "CancelRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    unique_id: Optional[UniqueIdType] = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class CustomerType(object):
    person_name: Optional[PersonNameType] = field(
        default=None,
        metadata={
            "name": "PersonName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: List["CustomerType.Telephone"] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    email: List[EmailType] = field(
        default_factory=list,
        metadata={
            "name": "Email",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    address: List["CustomerType.Address"] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    url: List[UrlType] = field(
        default_factory=list,
        metadata={
            "name": "URL",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    citizen_country_name: List["CustomerType.CitizenCountryName"] = field(
        default_factory=list,
        metadata={
            "name": "CitizenCountryName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    phys_chall_name: List[str] = field(
        default_factory=list,
        metadata={
            "name": "PhysChallName",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    pet_info: List[str] = field(
        default_factory=list,
        metadata={
            "name": "PetInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_form: List[PaymentFormType] = field(
        default_factory=list,
        metadata={
            "name": "PaymentForm",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    related_traveler: List[RelatedTravelerType] = field(
        default_factory=list,
        metadata={
            "name": "RelatedTraveler",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    contact_person: List[ContactPersonType] = field(
        default_factory=list,
        metadata={
            "name": "ContactPerson",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    document: List[DocumentType] = field(
        default_factory=list,
        metadata={
            "name": "Document",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    cust_loyalty: List["CustomerType.CustLoyalty"] = field(
        default_factory=list,
        metadata={
            "name": "CustLoyalty",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    employee_info: List[EmployeeInfoType] = field(
        default_factory=list,
        metadata={
            "name": "EmployeeInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    employer_info: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "EmployerInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    gender: Optional[CustomerTypeGender] = field(
        default=None,
        metadata={
            "name": "Gender",
            "type": "Attribute",
        },
    )
    deceased: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Deceased",
            "type": "Attribute",
        },
    )
    lockout_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "LockoutType",
            "type": "Attribute",
        },
    )
    birth_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "BirthDate",
            "type": "Attribute",
        },
    )
    currency_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "CurrencyCode",
            "type": "Attribute",
        },
    )
    decimal_places: Optional[int] = field(
        default=None,
        metadata={
            "name": "DecimalPlaces",
            "type": "Attribute",
        },
    )
    vip_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "VIP_Indicator",
            "type": "Attribute",
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )

    @dataclass
    class Telephone(object):
        phone_tech_type: Optional[str] = field(
            default=None,
            metadata={
                "name": "PhoneTechType",
                "type": "Attribute",
            },
        )
        phone_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "PhoneNumber",
                "type": "Attribute",
            },
        )
        effective_date: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "EffectiveDate",
                "type": "Attribute",
            },
        )
        expire_date: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "ExpireDate",
                "type": "Attribute",
            },
        )
        rph: Optional[str] = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )

    @dataclass
    class Address(AddressInfoType):
        company_name: Optional[CompanyNameType] = field(
            default=None,
            metadata={
                "name": "CompanyName",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        effective_date: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "EffectiveDate",
                "type": "Attribute",
            },
        )
        expire_date: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "ExpireDate",
                "type": "Attribute",
            },
        )

    @dataclass
    class CitizenCountryName(object):
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )

    @dataclass
    class CustLoyalty(object):
        program_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "ProgramID",
                "type": "Attribute",
            },
        )
        membership_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "MembershipID",
                "type": "Attribute",
            },
        )
        travel_sector: Optional[str] = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        rph: Optional[str] = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )
        vendor_code: List[str] = field(
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
    class PaymentAmount(object):
        amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "Amount",
                "type": "Attribute",
            },
        )
        approval_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ApprovalCode",
                "type": "Attribute",
            },
        )


@dataclass
class ServiceSoapGetVehCancelReservationInput(object):
    class Meta(object):
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
    class Body(object):
        veh_cancel_res_rq: Optional[VehCancelResRq] = field(
            default=None,
            metadata={
                "name": "VehCancelResRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehLocDetailInput(object):
    class Meta(object):
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
    class Body(object):
        veh_loc_detail_rq: Optional[VehLocDetailRq] = field(
            default=None,
            metadata={
                "name": "VehLocDetailRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehLocationSearchInput(object):
    class Meta(object):
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
    class Body(object):
        veh_location_search_rq: Optional[VehLocationSearchRq] = field(
            default=None,
            metadata={
                "name": "VehLocationSearchRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRateRuleInput(object):
    class Meta(object):
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
    class Body(object):
        veh_rate_rule_rq: Optional[VehRateRuleRq] = field(
            default=None,
            metadata={
                "name": "VehRateRuleRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRetReservationInput(object):
    class Meta(object):
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
    class Body(object):
        veh_ret_res_rq: Optional[VehRetResRq] = field(
            default=None,
            metadata={
                "name": "VehRetResRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleAvailCoreType(object):
    vehicle: Optional[VehicleType] = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_rate: List[VehicleRentalRateType] = field(
        default_factory=list,
        metadata={
            "name": "RentalRate",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    total_charge: List["VehicleAvailCoreType.TotalCharge"] = field(
        default_factory=list,
        metadata={
            "name": "TotalCharge",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_equips: Optional[ArrayOfVehicleEquipmentPricedType] = field(
        default=None,
        metadata={
            "name": "PricedEquips",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: Optional[ArrayOfVehicleChargePurposeType1] = field(
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    status: Optional[InventoryStatusType] = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
            "required": True,
        },
    )
    is_alternate_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "IsAlternateInd",
            "type": "Attribute",
        },
    )

    @dataclass
    class TotalCharge(object):
        currency_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        rate_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )
        rate_convert_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "RateConvertInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class Reference(UniqueIdType):
        date_time: Optional[XmlDateTime] = field(
            default=None,
            metadata={
                "name": "DateTime",
                "type": "Attribute",
            },
        )

    @dataclass
    class Vendor(CompanyNameType):
        participation_level_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ParticipationLevelCode",
                "type": "Attribute",
            },
        )

    @dataclass
    class VendorLocation(LocationType):
        extended_location_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: Optional[str] = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )
        name: Optional[str] = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )
        counter_loc_info: Optional[VendorLocationCounterLocInfo] = field(
            default=None,
            metadata={
                "name": "CounterLocInfo",
                "type": "Attribute",
            },
        )

    @dataclass
    class DropOffLocation(LocationType):
        extended_location_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "ExtendedLocationCode",
                "type": "Attribute",
            },
        )
        counter_location: Optional[str] = field(
            default=None,
            metadata={
                "name": "CounterLocation",
                "type": "Attribute",
            },
        )
        name: Optional[str] = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleLocationRequirementsType(object):
    age: Optional["VehicleLocationRequirementsType.Age"] = field(
        default=None,
        metadata={
            "name": "Age",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional_driver: Optional[
        "VehicleLocationRequirementsType.AdditionalDriver"
    ] = field(
        default=None,
        metadata={
            "name": "AdditionalDriver",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_options: Optional["VehicleLocationRequirementsType.PaymentOptions"] = field(
        default=None,
        metadata={
            "name": "PaymentOptions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    requirement_infos: Optional[
        ArrayOfVehicleLocationRequirementsTypeRequirementInfo
    ] = field(
        default=None,
        metadata={
            "name": "RequirementInfos",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Age(object):
        age_surcharge: List["VehicleLocationRequirementsType.Age.AgeSurcharge"] = field(
            default_factory=list,
            metadata={
                "name": "AgeSurcharge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        age_infos: Optional[ArrayOfVehicleLocationRequirementsTypeAgeAgeInfo] = field(
            default=None,
            metadata={
                "name": "AgeInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        minimum_age: Optional[int] = field(
            default=None,
            metadata={
                "name": "MinimumAge",
                "type": "Attribute",
            },
        )
        maximum_age: Optional[int] = field(
            default=None,
            metadata={
                "name": "MaximumAge",
                "type": "Attribute",
            },
        )

        @dataclass
        class AgeSurcharge(object):
            age: Optional[str] = field(
                default=None,
                metadata={
                    "name": "Age",
                    "type": "Attribute",
                },
            )
            amount: Optional[Decimal] = field(
                default=None,
                metadata={
                    "name": "Amount",
                    "type": "Attribute",
                },
            )

    @dataclass
    class AdditionalDriver(object):
        addl_driver_infos: Optional[
            ArrayOfVehicleLocationRequirementsTypeAdditionalDriverAddlDriverInfo
        ] = field(
            default=None,
            metadata={
                "name": "AddlDriverInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

    @dataclass
    class PaymentOptions(object):
        credit_card: Optional[AcceptablePaymentCardsInfoType] = field(
            default=None,
            metadata={
                "name": "CreditCard",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        debit_card: Optional[AcceptablePaymentCardsInfoType] = field(
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
        voucher: Optional[
            "VehicleLocationRequirementsType.PaymentOptions.Voucher"
        ] = field(
            default=None,
            metadata={
                "name": "Voucher",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
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
        deposit: Optional[AcceptablePaymentCardsInfoType] = field(
            default=None,
            metadata={
                "name": "Deposit",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        guarantee: Optional[AcceptablePaymentCardsInfoType] = field(
            default=None,
            metadata={
                "name": "Guarantee",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        pre_payment: Optional[AcceptablePaymentCardsInfoType] = field(
            default=None,
            metadata={
                "name": "PrePayment",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        payment_options_info: Optional[FormattedTextType] = field(
            default=None,
            metadata={
                "name": "PaymentOptionsInfo",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

        @dataclass
        class Cash(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class Voucher(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class BankAcct(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class DirectBill(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class LoyaltyRedemption(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )

        @dataclass
        class MiscChargeOrder(object):
            info: Optional[FormattedTextType] = field(
                default=None,
                metadata={
                    "name": "Info",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )


@dataclass
class VehicleLocationServicesOfferedType(object):
    on_location_services: Optional[
        ArrayOfVehicleLocationServicesOfferedTypeOnLocationService
    ] = field(
        default=None,
        metadata={
            "name": "OnLocationServices",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_location_services: Optional[
        ArrayOfVehicleLocationServicesOfferedTypeOffLocationService
    ] = field(
        default=None,
        metadata={
            "name": "OffLocationServices",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_equipments: Optional[
        ArrayOfVehicleLocationServicesOfferedTypeSpecialEquipment
    ] = field(
        default=None,
        metadata={
            "name": "SpecialEquipments",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleLocationVehiclesType(object):
    vehicle_infos: Optional[ArrayOfVehicleLocationVehiclesTypeVehicleInfo] = field(
        default=None,
        metadata={
            "name": "VehicleInfos",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle: List["VehicleLocationVehiclesType.Vehicle"] = field(
        default_factory=list,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Vehicle(VehicleType):
        text: List[FormattedTextType] = field(
            default_factory=list,
            metadata={
                "name": "Text",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        is_confirmable_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "IsConfirmableInd",
                "type": "Attribute",
            },
        )
        distance_unit: Optional[DistanceUnitNameType] = field(
            default=None,
            metadata={
                "name": "DistanceUnit",
                "type": "Attribute",
            },
        )
        distance_per_fuel_unit: Optional[int] = field(
            default=None,
            metadata={
                "name": "DistancePerFuelUnit",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleSegmentCoreType(object):
    conf_id: List[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "ConfID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_rental_core: Optional[VehicleRentalCoreType] = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle: Optional[VehicleType] = field(
        default=None,
        metadata={
            "name": "Vehicle",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_rate: Optional[VehicleRentalRateType] = field(
        default=None,
        metadata={
            "name": "RentalRate",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_equips: Optional[ArrayOfVehicleEquipmentPricedType] = field(
        default=None,
        metadata={
            "name": "PricedEquips",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: Optional[ArrayOfVehicleChargePurposeType1] = field(
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    index_number: Optional[int] = field(
        default=None,
        metadata={
            "name": "IndexNumber",
            "type": "Attribute",
        },
    )

    @dataclass
    class TotalCharge(object):
        rate_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        currency_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )


@dataclass
class CustomerPrimaryAdditionalType(object):
    primary: Optional["CustomerPrimaryAdditionalType.Primary"] = field(
        default=None,
        metadata={
            "name": "Primary",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional: List["CustomerPrimaryAdditionalType.Additional"] = field(
        default_factory=list,
        metadata={
            "name": "Additional",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Primary(CustomerType):
        customer_id: Optional[UniqueIdType] = field(
            default=None,
            metadata={
                "name": "CustomerID",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

    @dataclass
    class Additional(CustomerType):
        start: Optional[str] = field(
            default=None,
            metadata={
                "name": "Start",
                "type": "Attribute",
            },
        )
        duration: Optional[str] = field(
            default=None,
            metadata={
                "name": "Duration",
                "type": "Attribute",
            },
        )
        end: Optional[str] = field(
            default=None,
            metadata={
                "name": "End",
                "type": "Attribute",
            },
        )
        corp_discount_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "CorpDiscountName",
                "type": "Attribute",
            },
        )
        corp_discount_nmbr: Optional[str] = field(
            default=None,
            metadata={
                "name": "CorpDiscountNmbr",
                "type": "Attribute",
            },
        )
        qualification_method: Optional[AdditionalQualificationMethod] = field(
            default=None,
            metadata={
                "name": "QualificationMethod",
                "type": "Attribute",
            },
        )
        age: Optional[int] = field(
            default=None,
            metadata={
                "name": "Age",
                "type": "Attribute",
            },
        )
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: Optional[str] = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )
        uri: Optional[str] = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleLocationAdditionalDetailsType(object):
    veh_rent_loc_infos: Optional[ArrayOfVehicleLocationInformationType] = field(
        default=None,
        metadata={
            "name": "VehRentLocInfos",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    park_location: Optional[VehicleWhereAtFacilityType] = field(
        default=None,
        metadata={
            "name": "ParkLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    counter_location: Optional[VehicleWhereAtFacilityType] = field(
        default=None,
        metadata={
            "name": "CounterLocation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    operation_schedules: Optional[OperationSchedulesType] = field(
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
    one_way_drop_locations: Optional[
        ArrayOfVehicleLocationAdditionalDetailsTypeOneWayDropLocation
    ] = field(
        default=None,
        metadata={
            "name": "OneWayDropLocations",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class Shuttle(object):
        shuttle_infos: Optional[
            ArrayOfVehicleLocationAdditionalDetailsTypeShuttleShuttleInfo
        ] = field(
            default=None,
            metadata={
                "name": "ShuttleInfos",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        operation_schedules: Optional[OperationSchedulesType] = field(
            default=None,
            metadata={
                "name": "OperationSchedules",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleLocationLiabilitiesType(object):
    coverages: Optional[ArrayOfVehicleLocationLiabilitiesTypeCoverage] = field(
        default=None,
        metadata={
            "name": "Coverages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    info: Optional[FormattedTextType] = field(
        default=None,
        metadata={
            "name": "Info",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleReservationRqadditionalInfoType(object):
    class Meta(object):
        name = "VehicleReservationRQAdditionalInfoType"

    special_req_pref: List[VehicleSpecialReqPrefType] = field(
        default_factory=list,
        metadata={
            "name": "SpecialReqPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    coverage_prefs: Optional[
        ArrayOfVehicleReservationRqadditionalInfoTypeCoveragePref
    ] = field(
        default=None,
        metadata={
            "name": "CoveragePrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_loc_service: List[OffLocationServiceType] = field(
        default_factory=list,
        metadata={
            "name": "OffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    arrival_details: Optional[VehicleArrivalDetailsType] = field(
        default=None,
        metadata={
            "name": "ArrivalDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_payment_pref: List[
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
    tour_info: Optional[VehicleTourInfoType] = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    written_conf_inst: Optional[WrittenConfInstType] = field(
        default=None,
        metadata={
            "name": "WrittenConfInst",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    luggage_qty: Optional[int] = field(
        default=None,
        metadata={
            "name": "LuggageQty",
            "type": "Attribute",
        },
    )
    passenger_qty: Optional[int] = field(
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
        payment_type: Optional[str] = field(
            default=None,
            metadata={
                "name": "PaymentType",
                "type": "Attribute",
            },
        )
        type: Optional[RentalPaymentPrefType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            },
        )

    @dataclass
    class Reference(UniqueIdType):
        date_time: Optional[XmlDateTime] = field(
            default=None,
            metadata={
                "name": "DateTime",
                "type": "Attribute",
            },
        )
        amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "Amount",
                "type": "Attribute",
            },
        )
        currency_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        decimal_places: Optional[int] = field(
            default=None,
            metadata={
                "name": "DecimalPlaces",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleAvailRqadditionalInfoType(object):
    class Meta(object):
        name = "VehicleAvailRQAdditionalInfoType"

    customer: Optional[CustomerPrimaryAdditionalType] = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_req_pref: List[VehicleSpecialReqPrefType] = field(
        default_factory=list,
        metadata={
            "name": "SpecialReqPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    coverage_prefs: Optional[
        ArrayOfVehicleAvailRqadditionalInfoTypeCoveragePref
    ] = field(
        default=None,
        metadata={
            "name": "CoveragePrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_loc_service: List[OffLocationServiceType] = field(
        default_factory=list,
        metadata={
            "name": "OffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    arrival_details: Optional[VehicleArrivalDetailsType] = field(
        default=None,
        metadata={
            "name": "ArrivalDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: Optional[VehicleTourInfoType] = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    luggage_qty: Optional[int] = field(
        default=None,
        metadata={
            "name": "LuggageQty",
            "type": "Attribute",
        },
    )
    passenger_qty: Optional[int] = field(
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
    single_quote: Optional[bool] = field(
        default=None,
        metadata={
            "name": "SingleQuote",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailRsadditionalInfoType(object):
    class Meta(object):
        name = "VehicleAvailRSAdditionalInfoType"

    customer: Optional[CustomerPrimaryAdditionalType] = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleLocationDetailsType(object):
    address: List[AddressInfoType] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    telephone: List["VehicleLocationDetailsType.Telephone"] = field(
        default_factory=list,
        metadata={
            "name": "Telephone",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    additional_info: Optional[VehicleLocationAdditionalDetailsType] = field(
        default=None,
        metadata={
            "name": "AdditionalInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    at_airport: Optional[bool] = field(
        default=None,
        metadata={
            "name": "AtAirport",
            "type": "Attribute",
        },
    )
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )
    code_context: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodeContext",
            "type": "Attribute",
        },
    )
    extended_location_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "ExtendedLocationCode",
            "type": "Attribute",
        },
    )
    assoc_airport_loc_list: List[str] = field(
        default_factory=list,
        metadata={
            "name": "AssocAirportLocList",
            "type": "Attribute",
            "tokens": True,
        },
    )

    @dataclass
    class Telephone(object):
        phone_tech_type: Optional[str] = field(
            default=None,
            metadata={
                "name": "PhoneTechType",
                "type": "Attribute",
            },
        )
        phone_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "PhoneNumber",
                "type": "Attribute",
            },
        )
        rph: Optional[str] = field(
            default=None,
            metadata={
                "name": "RPH",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleReservationRqcoreType(object):
    class Meta(object):
        name = "VehicleReservationRQCoreType"

    unique_id: List[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_rental_core: Optional[VehicleRentalCoreType] = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    customer: Optional[CustomerPrimaryAdditionalType] = field(
        default=None,
        metadata={
            "name": "Customer",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor_pref: Optional[CompanyNamePrefType] = field(
        default=None,
        metadata={
            "name": "VendorPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_pref: Optional[VehiclePrefType] = field(
        default=None,
        metadata={
            "name": "VehPref",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    driver_type: List["VehicleReservationRqcoreType.DriverType"] = field(
        default_factory=list,
        metadata={
            "name": "DriverType",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_qualifier: Optional[RateQualifierType] = field(
        default=None,
        metadata={
            "name": "RateQualifier",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    fees: Optional[ArrayOfVehicleChargePurposeType1] = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vehicle_charges: Optional[ArrayOfVehicleChargePurposeType] = field(
        default=None,
        metadata={
            "name": "VehicleCharges",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    special_equip_prefs: Optional[
        "VehicleReservationRqcoreType.SpecialEquipPrefs"
    ] = field(
        default=None,
        metadata={
            "name": "SpecialEquipPrefs",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rate_distance: List["VehicleReservationRqcoreType.RateDistance"] = field(
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    status: Optional[str] = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )

    @dataclass
    class DriverType(object):
        age: Optional[int] = field(
            default=None,
            metadata={
                "name": "Age",
                "type": "Attribute",
            },
        )
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: Optional[str] = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )
        uri: Optional[str] = field(
            default=None,
            metadata={
                "name": "URI",
                "type": "Attribute",
            },
        )

    @dataclass
    class SpecialEquipPrefs(object):
        special_equip_pref: List[
            VehicleReservationRqcoreTypeSpecialEquipPrefsSpecialEquipPref
        ] = field(
            default_factory=list,
            metadata={
                "name": "SpecialEquipPref",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        charge: Optional[VehicleChargeType] = field(
            default=None,
            metadata={
                "name": "Charge",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )

    @dataclass
    class RateDistance(object):
        unlimited: Optional[bool] = field(
            default=None,
            metadata={
                "name": "Unlimited",
                "type": "Attribute",
                "required": True,
            },
        )
        quantity: Optional[int] = field(
            default=None,
            metadata={
                "name": "Quantity",
                "type": "Attribute",
            },
        )
        dist_unit_name: Optional[DistanceUnitNameType] = field(
            default=None,
            metadata={
                "name": "DistUnitName",
                "type": "Attribute",
            },
        )
        vehicle_period_unit_name: Optional[VehiclePeriodUnitNameType] = field(
            default=None,
            metadata={
                "name": "VehiclePeriodUnitName",
                "type": "Attribute",
            },
        )

    @dataclass
    class TotalCharge(object):
        rate_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )

    @dataclass
    class Queue(object):
        pseudo_city_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "PseudoCityCode",
                "type": "Attribute",
            },
        )
        queue_number: Optional[str] = field(
            default=None,
            metadata={
                "name": "QueueNumber",
                "type": "Attribute",
            },
        )
        queue_category: Optional[str] = field(
            default=None,
            metadata={
                "name": "QueueCategory",
                "type": "Attribute",
            },
        )
        system_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "SystemCode",
                "type": "Attribute",
            },
        )
        queue_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "QueueID",
                "type": "Attribute",
            },
        )


@dataclass
class VehAvailRateRq(object):
    class Meta(object):
        name = "VehAvailRateRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
        default=None,
        metadata={
            "name": "POS",
            "type": "Element",
        },
    )
    customer_id: List[UniqueIdType] = field(
        default_factory=list,
        metadata={
            "name": "CustomerID",
            "type": "Element",
        },
    )
    veh_avail_rqcore: Optional[VehicleAvailRqcoreType] = field(
        default=None,
        metadata={
            "name": "VehAvailRQCore",
            "type": "Element",
        },
    )
    veh_avail_rqinfo: Optional[VehicleAvailRqadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehAvailRQInfo",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehAvailRateRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )
    max_responses: Optional[int] = field(
        default=None,
        metadata={
            "name": "MaxResponses",
            "type": "Attribute",
        },
    )
    max_per_vendor_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "MaxPerVendorInd",
            "type": "Attribute",
        },
    )


@dataclass
class VehLocDetailRs(OtaResponse):
    class Meta(object):
        name = "VehLocDetailRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    vendor: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    location_detail: Optional[VehicleLocationDetailsType] = field(
        default=None,
        metadata={
            "name": "LocationDetail",
            "type": "Element",
        },
    )
    vehicles: Optional[VehicleLocationVehiclesType] = field(
        default=None,
        metadata={
            "name": "Vehicles",
            "type": "Element",
        },
    )
    requirements: Optional[VehicleLocationRequirementsType] = field(
        default=None,
        metadata={
            "name": "Requirements",
            "type": "Element",
        },
    )
    additional_fees: Optional[VehicleLocationAdditionalFeesType] = field(
        default=None,
        metadata={
            "name": "AdditionalFees",
            "type": "Element",
        },
    )
    liabilities: Optional[VehicleLocationLiabilitiesType] = field(
        default=None,
        metadata={
            "name": "Liabilities",
            "type": "Element",
        },
    )
    services_offered: Optional[VehicleLocationServicesOfferedType] = field(
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
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehLocDetailRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class Date(object):
        pick_up_date_time: Optional[str] = field(
            default=None,
            metadata={
                "name": "PickUpDateTime",
                "type": "Attribute",
            },
        )
        return_date_time: Optional[str] = field(
            default=None,
            metadata={
                "name": "ReturnDateTime",
                "type": "Attribute",
            },
        )


@dataclass
class VehRateRuleRs(OtaResponse):
    class Meta(object):
        name = "VehRateRuleRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
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
    rental_rate: List["VehRateRuleRs.RentalRate"] = field(
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
    priced_equips: Optional[ArrayOfVehicleEquipmentPricedType] = field(
        default=None,
        metadata={
            "name": "PricedEquips",
            "type": "Element",
        },
    )
    fees: Optional[ArrayOfVehicleChargePurposeType1] = field(
        default=None,
        metadata={
            "name": "Fees",
            "type": "Element",
        },
    )
    priced_coverages: Optional[ArrayOfCoveragePricedType] = field(
        default=None,
        metadata={
            "name": "PricedCoverages",
            "type": "Element",
        },
    )
    location_details: List["VehRateRuleRs.LocationDetails"] = field(
        default_factory=list,
        metadata={
            "name": "LocationDetails",
            "type": "Element",
        },
    )
    vendor_messages: Optional[ArrayOfVendorMessageType] = field(
        default=None,
        metadata={
            "name": "VendorMessages",
            "type": "Element",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehRateRuleRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehRentalCore(VehicleRentalCoreType):
        day_of_week: Optional[DayOfWeekType] = field(
            default=None,
            metadata={
                "name": "DayOfWeek",
                "type": "Attribute",
            },
        )
        currency_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        company_short_name: Optional[str] = field(
            default=None,
            metadata={
                "name": "CompanyShortName",
                "type": "Attribute",
            },
        )
        travel_sector: Optional[str] = field(
            default=None,
            metadata={
                "name": "TravelSector",
                "type": "Attribute",
            },
        )
        code: Optional[str] = field(
            default=None,
            metadata={
                "name": "Code",
                "type": "Attribute",
            },
        )
        code_context: Optional[str] = field(
            default=None,
            metadata={
                "name": "CodeContext",
                "type": "Attribute",
            },
        )

    @dataclass
    class Vehicle(VehicleType):
        description: Optional[FormattedTextTextType] = field(
            default=None,
            metadata={
                "name": "Description",
                "type": "Element",
            },
        )
        low_mileage: Optional[int] = field(
            default=None,
            metadata={
                "name": "LowMileage",
                "type": "Attribute",
            },
        )
        high_mileage: Optional[int] = field(
            default=None,
            metadata={
                "name": "HighMileage",
                "type": "Attribute",
            },
        )

    @dataclass
    class RentalRate(VehicleRentalRateType):
        written_conf_ind: Optional[bool] = field(
            default=None,
            metadata={
                "name": "WrittenConfInd",
                "type": "Attribute",
            },
        )

    @dataclass
    class TotalCharge(object):
        currency_code: Optional[str] = field(
            default=None,
            metadata={
                "name": "CurrencyCode",
                "type": "Attribute",
            },
        )
        rate_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "RateTotalAmount",
                "type": "Attribute",
            },
        )
        estimated_total_amount: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "EstimatedTotalAmount",
                "type": "Attribute",
            },
        )

    @dataclass
    class RateRules(object):
        advance_booking: Optional["VehRateRuleRs.RateRules.AdvanceBooking"] = field(
            default=None,
            metadata={
                "name": "AdvanceBooking",
                "type": "Element",
            },
        )
        pickup_return_rules: Optional[
            "VehRateRuleRs.RateRules.PickupReturnRules"
        ] = field(
            default=None,
            metadata={
                "name": "PickupReturnRules",
                "type": "Element",
            },
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
        cancel_penalty_info: List["VehRateRuleRs.RateRules.CancelPenaltyInfo"] = field(
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
        minimum_keep: Optional[XmlDuration] = field(
            default=None,
            metadata={
                "name": "MinimumKeep",
                "type": "Attribute",
            },
        )
        maximum_keep: Optional[XmlDuration] = field(
            default=None,
            metadata={
                "name": "MaximumKeep",
                "type": "Attribute",
            },
        )
        maximum_rental: Optional[XmlDuration] = field(
            default=None,
            metadata={
                "name": "MaximumRental",
                "type": "Attribute",
            },
        )

        @dataclass
        class AdvanceBooking(object):
            absolute_deadline: Optional[str] = field(
                default=None,
                metadata={
                    "name": "AbsoluteDeadline",
                    "type": "Attribute",
                },
            )
            offset_time_unit: Optional[TimeUnitType] = field(
                default=None,
                metadata={
                    "name": "OffsetTimeUnit",
                    "type": "Attribute",
                },
            )
            offset_unit_multiplier: Optional[int] = field(
                default=None,
                metadata={
                    "name": "OffsetUnitMultiplier",
                    "type": "Attribute",
                },
            )
            offset_drop_time: Optional[AdvanceBookingOffsetDropTime] = field(
                default=None,
                metadata={
                    "name": "OffsetDropTime",
                    "type": "Attribute",
                },
            )
            required_ind: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "RequiredInd",
                    "type": "Attribute",
                },
            )

        @dataclass
        class PickupReturnRules(object):
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
            class EarliestPickup(object):
                day_of_week: Optional[DayOfWeekType] = field(
                    default=None,
                    metadata={
                        "name": "DayOfWeek",
                        "type": "Attribute",
                    },
                )
                time: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "Time",
                        "type": "Attribute",
                    },
                )

            @dataclass
            class LatestPickup(object):
                day_of_week: Optional[DayOfWeekType] = field(
                    default=None,
                    metadata={
                        "name": "DayOfWeek",
                        "type": "Attribute",
                    },
                )
                time: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "Time",
                        "type": "Attribute",
                    },
                )

            @dataclass
            class LatestReturn(object):
                day_of_week: Optional[DayOfWeekType] = field(
                    default=None,
                    metadata={
                        "name": "DayOfWeek",
                        "type": "Attribute",
                    },
                )
                time: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "Time",
                        "type": "Attribute",
                    },
                )

        @dataclass
        class RateGuarantee(object):
            description: Optional[FormattedTextTextType] = field(
                default=None,
                metadata={
                    "name": "Description",
                    "type": "Element",
                },
            )
            absolute_deadline: Optional[str] = field(
                default=None,
                metadata={
                    "name": "AbsoluteDeadline",
                    "type": "Attribute",
                },
            )
            offset_time_unit: Optional[TimeUnitType] = field(
                default=None,
                metadata={
                    "name": "OffsetTimeUnit",
                    "type": "Attribute",
                },
            )
            offset_unit_multiplier: Optional[int] = field(
                default=None,
                metadata={
                    "name": "OffsetUnitMultiplier",
                    "type": "Attribute",
                },
            )
            offset_drop_time: Optional[RateGuaranteeOffsetDropTime] = field(
                default=None,
                metadata={
                    "name": "OffsetDropTime",
                    "type": "Attribute",
                },
            )

        @dataclass
        class PaymentRules(PaymentRulesType):
            acceptable_payments: List[
                "VehRateRuleRs.RateRules.PaymentRules.AcceptablePayments"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "AcceptablePayments",
                    "type": "Element",
                },
            )

            @dataclass
            class AcceptablePayments(object):
                acceptable_payment: List[
                    "VehRateRuleRs.RateRules.PaymentRules.AcceptablePayments.AcceptablePayment"
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "AcceptablePayment",
                        "type": "Element",
                    },
                )
                payment_type_code: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "PaymentTypeCode",
                        "type": "Attribute",
                    },
                )

                @dataclass
                class AcceptablePayment(object):
                    credit_card_code: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "CreditCardCode",
                            "type": "Attribute",
                        },
                    )

        @dataclass
        class CancelPenaltyInfo(object):
            deadline: List[
                "VehRateRuleRs.RateRules.CancelPenaltyInfo.Deadline"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "Deadline",
                    "type": "Element",
                },
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
            description: Optional[FormattedTextTextType] = field(
                default=None,
                metadata={
                    "name": "Description",
                    "type": "Element",
                },
            )
            guarantee_required_ind: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "GuaranteeRequiredInd",
                    "type": "Attribute",
                },
            )
            modify_penalty_ind: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "ModifyPenaltyInd",
                    "type": "Attribute",
                },
            )

            @dataclass
            class Deadline(object):
                absolute_deadline: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "AbsoluteDeadline",
                        "type": "Attribute",
                    },
                )
                offset_time_unit: Optional[TimeUnitType] = field(
                    default=None,
                    metadata={
                        "name": "OffsetTimeUnit",
                        "type": "Attribute",
                    },
                )
                offset_unit_multiplier: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "OffsetUnitMultiplier",
                        "type": "Attribute",
                    },
                )
                offset_drop_time: Optional[DeadlineOffsetDropTime] = field(
                    default=None,
                    metadata={
                        "name": "OffsetDropTime",
                        "type": "Attribute",
                    },
                )

            @dataclass
            class PenaltyFee(object):
                amount: Optional[Decimal] = field(
                    default=None,
                    metadata={
                        "name": "Amount",
                        "type": "Attribute",
                    },
                )

        @dataclass
        class RateDeposit(object):
            absolute_deadline: Optional[str] = field(
                default=None,
                metadata={
                    "name": "AbsoluteDeadline",
                    "type": "Attribute",
                },
            )
            offset_time_unit: Optional[TimeUnitType] = field(
                default=None,
                metadata={
                    "name": "OffsetTimeUnit",
                    "type": "Attribute",
                },
            )
            offset_unit_multiplier: Optional[int] = field(
                default=None,
                metadata={
                    "name": "OffsetUnitMultiplier",
                    "type": "Attribute",
                },
            )
            offset_drop_time: Optional[RateDepositOffsetDropTime] = field(
                default=None,
                metadata={
                    "name": "OffsetDropTime",
                    "type": "Attribute",
                },
            )
            deposit_required_ind: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "DepositRequiredInd",
                    "type": "Attribute",
                },
            )

    @dataclass
    class LocationDetails(VehicleLocationDetailsType):
        drop_off_indicator: Optional[bool] = field(
            default=None,
            metadata={
                "name": "DropOffIndicator",
                "type": "Attribute",
            },
        )


@dataclass
class VehResRq(object):
    class Meta(object):
        name = "VehResRQ"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    pos: Optional[ArrayOfSourceType] = field(
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
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehResRqTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )
    req_resp_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReqRespVersion",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehResRqcore(VehicleReservationRqcoreType):
        option_change_indicator: Optional[bool] = field(
            default=None,
            metadata={
                "name": "OptionChangeIndicator",
                "type": "Attribute",
            },
        )

    @dataclass
    class VehResRqinfo(VehicleReservationRqadditionalInfoType):
        res_status: Optional[TransactionActionType] = field(
            default=None,
            metadata={
                "name": "ResStatus",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleAvailVendorInfoType(object):
    vendor_messages: Optional[ArrayOfVendorMessageType] = field(
        default=None,
        metadata={
            "name": "VendorMessages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    off_loc_services: List[OffLocationServiceType] = field(
        default_factory=list,
        metadata={
            "name": "OffLocServices",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    payment_rules: Optional[ArrayOfMonetaryRuleType] = field(
        default=None,
        metadata={
            "name": "PaymentRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    location_details: List[VehicleLocationDetailsType] = field(
        default_factory=list,
        metadata={
            "name": "LocationDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: Optional[VehicleTourInfoType] = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleMatchedLocationType(object):
    location_detail: Optional[VehicleLocationDetailsType] = field(
        default=None,
        metadata={
            "name": "LocationDetail",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_loc_search_criterion: List[ItemSearchCriterionType] = field(
        default_factory=list,
        metadata={
            "name": "VehLocSearchCriterion",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    alternate_loc_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "AlternateLocInd",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleSegmentAdditionalInfoType(object):
    payment_rules: Optional[ArrayOfMonetaryRuleType] = field(
        default=None,
        metadata={
            "name": "PaymentRules",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    rental_payment_amount: List[PaymentDetailType] = field(
        default_factory=list,
        metadata={
            "name": "RentalPaymentAmount",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_coverages: Optional[ArrayOfCoveragePricedType] = field(
        default=None,
        metadata={
            "name": "PricedCoverages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    priced_off_loc_service: List[OffLocationServicePricedType] = field(
        default_factory=list,
        metadata={
            "name": "PricedOffLocService",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    vendor_messages: Optional[ArrayOfFormattedTextType] = field(
        default=None,
        metadata={
            "name": "VendorMessages",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    location_details: List[VehicleLocationDetailsType] = field(
        default_factory=list,
        metadata={
            "name": "LocationDetails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tour_info: Optional[VehicleTourInfoType] = field(
        default=None,
        metadata={
            "name": "TourInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    written_conf_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "WrittenConfInd",
            "type": "Attribute",
        },
    )


@dataclass
class ArrayOfVehicleMatchedLocationType(object):
    veh_matched_loc: List[VehicleMatchedLocationType] = field(
        default_factory=list,
        metadata={
            "name": "VehMatchedLoc",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ServiceSoapGetVehAvailRateInput(object):
    class Meta(object):
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
    class Body(object):
        veh_avail_rate_rq: Optional[VehAvailRateRq] = field(
            default=None,
            metadata={
                "name": "VehAvailRateRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehLocDetailOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_loc_detail_rs: Optional[VehLocDetailRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRateRuleOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_rate_rule_rs: Optional[VehRateRuleRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehReservationInput(object):
    class Meta(object):
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
    class Body(object):
        veh_res_rq: Optional[VehResRq] = field(
            default=None,
            metadata={
                "name": "VehResRQ",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehicleReservationType(object):
    customer: Optional[CustomerPrimaryAdditionalType] = field(
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
    veh_segment_info: Optional[VehicleSegmentAdditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehSegmentInfo",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    reservation_status: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReservationStatus",
            "type": "Attribute",
        },
    )
    create_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "CreateDateTime",
            "type": "Attribute",
        },
    )
    creator_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CreatorID",
            "type": "Attribute",
        },
    )
    last_modify_date_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "LastModifyDateTime",
            "type": "Attribute",
        },
    )
    last_modifier_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "LastModifierID",
            "type": "Attribute",
        },
    )
    purge_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "PurgeDate",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehSegmentCore(VehicleSegmentCoreType):
        option_change_allowed_indicator: Optional[bool] = field(
            default=None,
            metadata={
                "name": "OptionChangeAllowedIndicator",
                "type": "Attribute",
            },
        )


@dataclass
class VehicleVendorAvailabilityType(object):
    vendor: Optional[CompanyNameType] = field(
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
    info: Optional[VehicleAvailVendorInfoType] = field(
        default=None,
        metadata={
            "name": "Info",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )

    @dataclass
    class VehAvails(object):
        veh_avail: List["VehicleVendorAvailabilityType.VehAvails.VehAvail"] = field(
            default_factory=list,
            metadata={
                "name": "VehAvail",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        rate_category: Optional[str] = field(
            default=None,
            metadata={
                "name": "RateCategory",
                "type": "Attribute",
            },
        )

        @dataclass
        class VehAvail(object):
            veh_avail_core: Optional[VehicleAvailCoreType] = field(
                default=None,
                metadata={
                    "name": "VehAvailCore",
                    "type": "Element",
                    "namespace": "http://www.opentravel.org/OTA/2003/05",
                },
            )
            veh_avail_info: Optional[VehicleAvailAdditionalInfoType] = field(
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
            class AdvanceBooking(object):
                absolute_deadline: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "AbsoluteDeadline",
                        "type": "Attribute",
                    },
                )
                offset_time_unit: Optional[TimeUnitType] = field(
                    default=None,
                    metadata={
                        "name": "OffsetTimeUnit",
                        "type": "Attribute",
                    },
                )
                offset_unit_multiplier: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "OffsetUnitMultiplier",
                        "type": "Attribute",
                    },
                )
                offset_drop_time: Optional[AdvanceBookingOffsetDropTime] = field(
                    default=None,
                    metadata={
                        "name": "OffsetDropTime",
                        "type": "Attribute",
                    },
                )
                rules_apply_ind: Optional[bool] = field(
                    default=None,
                    metadata={
                        "name": "RulesApplyInd",
                        "type": "Attribute",
                    },
                )


@dataclass
class ArrayOfVehicleVendorAvailabilityType(object):
    veh_vendor_avail: List[VehicleVendorAvailabilityType] = field(
        default_factory=list,
        metadata={
            "name": "VehVendorAvail",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


class ServiceSoapGetVehLocDetail(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehLocDetail"
    input = ServiceSoapGetVehLocDetailInput
    output = ServiceSoapGetVehLocDetailOutput


class ServiceSoapGetVehRateRule(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehRateRule"
    input = ServiceSoapGetVehRateRuleInput
    output = ServiceSoapGetVehRateRuleOutput


@dataclass
class VehLocationSearchRs(OtaResponse):
    class Meta(object):
        name = "VehLocationSearchRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_matched_locs: Optional[ArrayOfVehicleMatchedLocationType] = field(
        default=None,
        metadata={
            "name": "VehMatchedLocs",
            "type": "Element",
        },
    )
    vendor: Optional[CompanyNameType] = field(
        default=None,
        metadata={
            "name": "Vendor",
            "type": "Element",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehLocationSearchRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleCancelRsadditionalInfoType(object):
    class Meta(object):
        name = "VehicleCancelRSAdditionalInfoType"

    veh_reservation: Optional[VehicleReservationType] = field(
        default=None,
        metadata={
            "name": "VehReservation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleResRscoreType(object):
    class Meta(object):
        name = "VehicleResRSCoreType"

    veh_reservation: Optional[VehicleReservationType] = field(
        default=None,
        metadata={
            "name": "VehReservation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    tpa_extensions: Optional[TpaExtensionsType] = field(
        default=None,
        metadata={
            "name": "TPA_Extensions",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleRetrieveResRscoreType(object):
    class Meta(object):
        name = "VehicleRetrieveResRSCoreType"

    veh_reservation: Optional[VehicleReservationType] = field(
        default=None,
        metadata={
            "name": "VehReservation",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_res_summaries: Optional[ArrayOfVehicleReservationSummaryType] = field(
        default=None,
        metadata={
            "name": "VehResSummaries",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ServiceSoapGetVehLocationSearchOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_location_search_rs: Optional[VehLocationSearchRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehCancelResRs(OtaResponse):
    class Meta(object):
        name = "VehCancelResRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
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
    veh_cancel_rsinfo: Optional[VehicleCancelRsadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehCancelRSInfo",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehCancelResRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehCancelRscore(CancelInfoRstype):
        cancel_status: Optional[TransactionStatusType] = field(
            default=None,
            metadata={
                "name": "CancelStatus",
                "type": "Attribute",
                "required": True,
            },
        )


@dataclass
class VehResRs(OtaResponse):
    class Meta(object):
        name = "VehResRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
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
    veh_res_rsinfo: Optional[VehicleResRsadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehResRSInfo",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehResRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )

    @dataclass
    class VehResRscore(VehicleResRscoreType):
        reservation_status: Optional[str] = field(
            default=None,
            metadata={
                "name": "ReservationStatus",
                "type": "Attribute",
            },
        )


@dataclass
class VehRetResRs(OtaResponse):
    class Meta(object):
        name = "VehRetResRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_ret_res_rscore: Optional[VehicleRetrieveResRscoreType] = field(
        default=None,
        metadata={
            "name": "VehRetResRSCore",
            "type": "Element",
        },
    )
    veh_ret_res_rsinfo: Optional[VehicleRetrieveResRsadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehRetResRSInfo",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehRetResRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAvailRscoreType(object):
    class Meta(object):
        name = "VehicleAvailRSCoreType"

    veh_rental_core: Optional[VehicleRentalCoreType] = field(
        default=None,
        metadata={
            "name": "VehRentalCore",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    veh_vendor_avails: Optional[ArrayOfVehicleVendorAvailabilityType] = field(
        default=None,
        metadata={
            "name": "VehVendorAvails",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ServiceSoapGetVehCancelReservationOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_cancel_res_rs: Optional[VehCancelResRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


class ServiceSoapGetVehLocationSearch(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehLocationSearch"
    input = ServiceSoapGetVehLocationSearchInput
    output = ServiceSoapGetVehLocationSearchOutput


@dataclass
class ServiceSoapGetVehReservationOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_res_rs: Optional[VehResRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class ServiceSoapGetVehRetReservationOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_ret_res_rs: Optional[VehRetResRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class VehAvailRateRs(OtaResponse):
    class Meta(object):
        name = "VehAvailRateRS"
        namespace = "http://www.opentravel.org/OTA/2003/05"

    success: Optional[SuccessType] = field(
        default=None,
        metadata={
            "name": "Success",
            "type": "Element",
        },
    )
    warnings: Optional[ArrayOfWarningType] = field(
        default=None,
        metadata={
            "name": "Warnings",
            "type": "Element",
        },
    )
    veh_avail_rscore: Optional[VehicleAvailRscoreType] = field(
        default=None,
        metadata={
            "name": "VehAvailRSCore",
            "type": "Element",
        },
    )
    veh_avail_rsinfo: Optional[VehicleAvailRsadditionalInfoType] = field(
        default=None,
        metadata={
            "name": "VehAvailRSInfo",
            "type": "Element",
        },
    )
    errors: Optional[ArrayOfErrorType] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
        },
    )
    echo_token: Optional[str] = field(
        default=None,
        metadata={
            "name": "EchoToken",
            "type": "Attribute",
        },
    )
    time_stamp: Optional[XmlDateTime] = field(
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
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    transaction_identifier: Optional[str] = field(
        default=None,
        metadata={
            "name": "TransactionIdentifier",
            "type": "Attribute",
        },
    )
    sequence_nmbr: Optional[int] = field(
        default=None,
        metadata={
            "name": "SequenceNmbr",
            "type": "Attribute",
        },
    )
    transaction_status_code: Optional[VehAvailRateRsTransactionStatusCode] = field(
        default=None,
        metadata={
            "name": "TransactionStatusCode",
            "type": "Attribute",
        },
    )
    retransmission_indicator: Optional[bool] = field(
        default=None,
        metadata={
            "name": "RetransmissionIndicator",
            "type": "Attribute",
        },
    )


@dataclass
class ServiceSoapGetVehAvailRateOutput(object):
    class Meta(object):
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
    class Body(object):
        veh_avail_rate_rs: Optional[VehAvailRateRs] = field(
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
        class Fault(object):
            faultcode: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultstring: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            faultactor: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )
            detail: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "",
                },
            )

    @dataclass
    class Header(object):
        information_header: Optional[InformationHeader] = field(
            default=None,
            metadata={
                "name": "informationHeader",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


class ServiceSoapGetVehCancelReservation(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehCancelReservation"
    input = ServiceSoapGetVehCancelReservationInput
    output = ServiceSoapGetVehCancelReservationOutput


class ServiceSoapGetVehReservation(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehReservation"
    input = ServiceSoapGetVehReservationInput
    output = ServiceSoapGetVehReservationOutput


class ServiceSoapGetVehRetReservation(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehRetReservation"
    input = ServiceSoapGetVehRetReservationInput
    output = ServiceSoapGetVehRetReservationOutput


class ServiceSoapGetVehAvailRate(object):
    style = "document"
    location = "https://ota2007a.carhire-solutions.com/service.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/getVehAvailRate"
    input = ServiceSoapGetVehAvailRateInput
    output = ServiceSoapGetVehAvailRateOutput
