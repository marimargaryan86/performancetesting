from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlDateTime, XmlTime

__NAMESPACE__ = "http://railgds.net/ws/publishing"


@dataclass(frozen=True)
class AcceptableFopValidCardLengthType:
    class Meta:
        name = "acceptableFopValidCardLengthType"

    value: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AmenityType:
    class Meta:
        name = "amenityType"

    code: str | None = field(
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
            "required": True,
        },
    )


@dataclass(frozen=True)
class CarrierType:
    class Meta:
        name = "carrierType"

    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    supply_channel: str | None = field(
        default=None,
        metadata={
            "name": "supplyChannel",
            "type": "Attribute",
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    supply_channel_code: str | None = field(
        default=None,
        metadata={
            "name": "supplyChannelCode",
            "type": "Attribute",
            "required": True,
        },
    )
    image: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class CountryType:
    class Meta:
        name = "countryType"

    country_code: str | None = field(
        default=None,
        metadata={
            "name": "countryCode",
            "type": "Attribute",
            "required": True,
        },
    )
    continent_code: str | None = field(
        default=None,
        metadata={
            "name": "continentCode",
            "type": "Attribute",
            "required": True,
        },
    )
    country_calling_code: str | None = field(
        default=None,
        metadata={
            "name": "countryCallingCode",
            "type": "Attribute",
        },
    )
    country_name: str | None = field(
        default=None,
        metadata={
            "name": "countryName",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class EquipmentTypeType:
    class Meta:
        name = "equipmentTypeType"

    code: str | None = field(
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
            "required": True,
        },
    )


@dataclass(frozen=True)
class FareCodeApplicabilityRestriction:
    class Meta:
        name = "fareCodeApplicabilityRestriction"

    value: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class GroupStationType:
    class Meta:
        name = "groupStationType"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


class HoursType(Enum):
    OPEN_PERIOD = "open-period"
    ALL_DAY = "all-day"
    UNSPECIFIED = "unspecified"


class IsInputType(Enum):
    YES = "YES"
    NO = "NO"


@dataclass(frozen=True)
class Label:
    class Meta:
        name = "label"

    sub_code: str | None = field(
        default=None,
        metadata={
            "name": "subCode",
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class LoyaltyCardType:
    class Meta:
        name = "loyaltyCardType"

    marketing_carrier: str | None = field(
        default=None,
        metadata={
            "name": "marketingCarrier",
            "type": "Attribute",
        },
    )
    program: str | None = field(
        default=None,
        metadata={
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
class MarketingInformationType:
    class Meta:
        name = "marketingInformationType"

    service_code: str | None = field(
        default=None,
        metadata={
            "name": "serviceCode",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class MemberStationType:
    class Meta:
        name = "memberStationType"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class RangersAndRoversType:
    class Meta:
        name = "rangersAndRoversType"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class RegionCountryType:
    class Meta:
        name = "regionCountryType"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class Reservable:
    class Meta:
        name = "reservable"

    value: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


class ScheduleType(Enum):
    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    EVERYDAY = "EVERYDAY"
    WEEKDAYS = "WEEKDAYS"
    WEEKENDS = "WEEKENDS"
    HOLIDAY = "HOLIDAY"


@dataclass(frozen=True)
class SeatAttribute:
    class Meta:
        name = "seatAttribute"

    code: str | None = field(
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
class SeatPreference:
    class Meta:
        name = "seatPreference"

    code: str | None = field(
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


class Sources(Enum):
    AMT = "AMT"
    ATOC = "ATOC"
    BENE = "BENE"
    CWT = "CWT"
    DBB = "DBB"
    DBN = "DBN"
    EFNR = "EFNR"
    LINKON = "Linkon"
    REN = "REN"
    TRI = "TRI"
    VIA = "VIA"
    SNCF = "SNCF"


class SrtDataType(Enum):
    ACCEPTABLE_FOP = "acceptableFop"
    AMENITY = "amenity"
    CARRIER = "carrier"
    COUNTRY = "country"
    EQUIPMENT_TYPE = "equipmentType"
    FARE_QUALIFIER = "fareQualifier"
    REGION = "region"
    STATION = "station"
    MARKETING_INFORMATION = "marketingInformation"
    RANGERS_AND_ROVERS = "rangersAndRovers"
    LOYALTY_CARD = "loyaltyCard"
    STRUCTURE = "structure"
    STATION_RICH_CONTENT = "stationRichContent"
    SUPPLY_CHANNEL_FARE_CODE = "supplyChannelFareCode"
    RESERVABLE = "reservable"
    FARE_CODE_APPLICABILITY_RESTRICTION = "fareCodeApplicabilityRestriction"
    SEAT_ATTRIBUTE = "seatAttribute"
    SEAT_PREFERENCE = "seatPreference"
    STATION_CORE_SUPPLY_CHANNEL_DATA = "stationCoreSupplyChannelData"


class StationApitype(Enum):
    YES = "YES"
    NO = "NO"
    OUTPUT_ONLY = "OUTPUT_ONLY"


class StationCoreSupplyChannelDataAmenityDetailDayOfWeek(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class StationCoreSupplyChannelDataAmenityType(Enum):
    TICKET_OFFICE = "TICKET_OFFICE"
    TICKET_VENDING_MACHINE = "TICKET_VENDING_MACHINE"


@dataclass(frozen=True)
class StationCoreSupplyChannelDataInternalGroup:
    class Meta:
        name = "stationCoreSupplyChannelData_internalGroup"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationRichContentList:
    class Meta:
        name = "stationRichContent_list"

    sub_code: str | None = field(
        default=None,
        metadata={
            "name": "subCode",
            "type": "Attribute",
        },
    )
    flag: bool | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StationRichContentTextValue:
    class Meta:
        name = "stationRichContent_textValue"

    locale: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
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


class StructureAttributeType(Enum):
    LIST = "list"
    TEXT = "text"
    SCHEDULE = "schedule"


class SupplierTypeType(Enum):
    CODE = "CODE"
    ALIAS = "ALIAS"
    SMARTCARD = "SMARTCARD"
    LOCAL = "LOCAL"


@dataclass(frozen=True)
class SupplyChannelFareCode:
    class Meta:
        name = "supplyChannelFareCode"

    supply_channel_code: str | None = field(
        default=None,
        metadata={
            "name": "supplyChannelCode",
            "type": "Attribute",
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    active: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    effective_start_date: XmlDate | None = field(
        default=None,
        metadata={
            "name": "effectiveStartDate",
            "type": "Attribute",
            "required": True,
        },
    )
    cabin_class: str | None = field(
        default=None,
        metadata={
            "name": "cabinClass",
            "type": "Attribute",
            "required": True,
        },
    )
    service_class: str | None = field(
        default=None,
        metadata={
            "name": "serviceClass",
            "type": "Attribute",
            "required": True,
        },
    )
    fare_class: str | None = field(
        default=None,
        metadata={
            "name": "fareClass",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class AcceptableFopType:
    class Meta:
        name = "acceptableFopType"

    valid_card_length: list[AcceptableFopValidCardLengthType] = field(
        default_factory=list,
        metadata={
            "name": "validCardLength",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    payment_method: str | None = field(
        default=None,
        metadata={
            "name": "paymentMethod",
            "type": "Attribute",
            "required": True,
        },
    )
    security_code_length: int | None = field(
        default=None,
        metadata={
            "name": "securityCodeLength",
            "type": "Attribute",
            "required": True,
        },
    )
    expiry_date_required: bool | None = field(
        default=None,
        metadata={
            "name": "expiryDateRequired",
            "type": "Attribute",
            "required": True,
        },
    )
    issue_series_required: bool | None = field(
        default=None,
        metadata={
            "name": "issueSeriesRequired",
            "type": "Attribute",
            "required": True,
        },
    )
    start_date_required: bool | None = field(
        default=None,
        metadata={
            "name": "startDateRequired",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class CitySupplyChannelCity:
    class Meta:
        name = "city_supplyChannelCity"

    source: Sources | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class FareQualifierType:
    class Meta:
        name = "fareQualifierType"

    program: str | None = field(
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
            "required": True,
        },
    )
    description: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    is_input: IsInputType | None = field(
        default=None,
        metadata={
            "name": "isInput",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class RegionType:
    class Meta:
        name = "regionType"

    country: list[RegionCountryType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationCoreSupplyChannelDataAmenityDetail:
    class Meta:
        name = "stationCoreSupplyChannelData_amenityDetail"

    day_of_week: StationCoreSupplyChannelDataAmenityDetailDayOfWeek | None = field(
        default=None,
        metadata={
            "name": "dayOfWeek",
            "type": "Attribute",
            "required": True,
        },
    )
    start_time: XmlTime | None = field(
        default=None,
        metadata={
            "name": "startTime",
            "type": "Attribute",
            "required": True,
        },
    )
    end_time: XmlTime | None = field(
        default=None,
        metadata={
            "name": "endTime",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationRichContentSchedule:
    class Meta:
        name = "stationRichContent_schedule"

    schedule_type: ScheduleType | None = field(
        default=None,
        metadata={
            "name": "scheduleType",
            "type": "Attribute",
            "required": True,
        },
    )
    hours_type: HoursType | None = field(
        default=None,
        metadata={
            "name": "hoursType",
            "type": "Attribute",
            "required": True,
        },
    )
    start_time: str | None = field(
        default=None,
        metadata={
            "name": "startTime",
            "type": "Attribute",
        },
    )
    end_time: str | None = field(
        default=None,
        metadata={
            "name": "endTime",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StationRichContentText:
    class Meta:
        name = "stationRichContent_text"

    value: list[StationRichContentTextValue] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    sub_code: str | None = field(
        default=None,
        metadata={
            "name": "subCode",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StructureAttribute:
    class Meta:
        name = "structureAttribute"

    label: list[Label] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    type_value: StructureAttributeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class SupplierType:
    class Meta:
        name = "supplierType"

    member_station: list[MemberStationType] = field(
        default_factory=list,
        metadata={
            "name": "memberStation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    group_station: list[GroupStationType] = field(
        default_factory=list,
        metadata={
            "name": "groupStation",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    source: Sources | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: SupplierTypeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    code_type: str | None = field(
        default=None,
        metadata={
            "name": "codeType",
            "type": "Attribute",
        },
    )
    type_name: str | None = field(
        default=None,
        metadata={
            "name": "typeName",
            "type": "Attribute",
        },
    )
    alias: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class City:
    class Meta:
        name = "city"

    supply_channel_city: list[CitySupplyChannelCity] = field(
        default_factory=list,
        metadata={
            "name": "supplyChannelCity",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    country: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    state_province: str | None = field(
        default=None,
        metadata={
            "name": "stateProvince",
            "type": "Attribute",
        },
    )
    latitude: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    longitude: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StationCoreSupplyChannelDataAmenity:
    class Meta:
        name = "stationCoreSupplyChannelData_amenity"

    amenity_detail: list[StationCoreSupplyChannelDataAmenityDetail] = field(
        default_factory=list,
        metadata={
            "name": "amenityDetail",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    type_value: StationCoreSupplyChannelDataAmenityType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationRichContentStructureData:
    class Meta:
        name = "stationRichContent_StructureData"

    text: list[StationRichContentText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    schedule: list[StationRichContentSchedule] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    list_value: list[StationRichContentList] = field(
        default_factory=list,
        metadata={
            "name": "list",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    attribute_code: str | None = field(
        default=None,
        metadata={
            "name": "attributeCode",
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: StructureAttributeType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationType:
    class Meta:
        name = "stationType"

    supplier: list[SupplierType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )
    code: str | None = field(
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
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    main_station: str | None = field(
        default=None,
        metadata={
            "name": "mainStation",
            "type": "Attribute",
            "required": True,
        },
    )
    iata_code: str | None = field(
        default=None,
        metadata={
            "name": "iataCode",
            "type": "Attribute",
        },
    )
    country_code: str | None = field(
        default=None,
        metadata={
            "name": "countryCode",
            "type": "Attribute",
        },
    )
    time_zone: str | None = field(
        default=None,
        metadata={
            "name": "timeZone",
            "type": "Attribute",
            "required": True,
        },
    )
    latitude: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    longitude: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    city: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    state_province_code: str | None = field(
        default=None,
        metadata={
            "name": "stateProvinceCode",
            "type": "Attribute",
        },
    )
    itinerary_station: StationApitype | None = field(
        default=None,
        metadata={
            "name": "itineraryStation",
            "type": "Attribute",
        },
    )
    fare_station: StationApitype | None = field(
        default=None,
        metadata={
            "name": "fareStation",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StructureGenericAttribute:
    class Meta:
        name = "structure_GenericAttribute"

    structure_attribute: list[StructureAttribute] = field(
        default_factory=list,
        metadata={
            "name": "structureAttribute",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    gcx_code: str | None = field(
        default=None,
        metadata={
            "name": "gcxCode",
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationCoreSupplyChannelDataSupplyChannel:
    class Meta:
        name = "stationCoreSupplyChannelData_supplyChannel"

    amenity: list[StationCoreSupplyChannelDataAmenity] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    internal_group: list[StationCoreSupplyChannelDataInternalGroup] = field(
        default_factory=list,
        metadata={
            "name": "internalGroup",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    sequence: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    sc_code: str | None = field(
        default=None,
        metadata={
            "name": "scCode",
            "type": "Attribute",
        },
    )
    sc_alt_code: str | None = field(
        default=None,
        metadata={
            "name": "scAltCode",
            "type": "Attribute",
        },
    )
    sc_station_group_code: str | None = field(
        default=None,
        metadata={
            "name": "scStationGroupCode",
            "type": "Attribute",
        },
    )
    itinerary_station: StationApitype | None = field(
        default=None,
        metadata={
            "name": "itineraryStation",
            "type": "Attribute",
        },
    )
    fare_station: StationApitype | None = field(
        default=None,
        metadata={
            "name": "fareStation",
            "type": "Attribute",
        },
    )
    cd_updated: str | None = field(
        default=None,
        metadata={
            "name": "cdUpdated",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StationRichContentGenericAttribute:
    class Meta:
        name = "stationRichContent_GenericAttribute"

    structure_data: list[StationRichContentStructureData] = field(
        default_factory=list,
        metadata={
            "name": "structureData",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )
    gcx_code: str | None = field(
        default=None,
        metadata={
            "name": "gcxCode",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class Structure:
    class Meta:
        name = "structure"

    generic_attribute: list[StructureGenericAttribute] = field(
        default_factory=list,
        metadata={
            "name": "genericAttribute",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    locale: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    last_changed: str | None = field(
        default=None,
        metadata={
            "name": "lastChanged",
            "type": "Attribute",
            "required": True,
        },
    )
    country_code: str | None = field(
        default=None,
        metadata={
            "name": "countryCode",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class StationCoreSupplyChannelDataStation:
    class Meta:
        name = "stationCoreSupplyChannelData_Station"

    supply_channel: list[StationCoreSupplyChannelDataSupplyChannel] = field(
        default_factory=list,
        metadata={
            "name": "supplyChannel",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )
    is_internal: bool | None = field(
        default=None,
        metadata={
            "name": "isInternal",
            "type": "Attribute",
            "required": True,
        },
    )
    srtcode: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StationRichContentStation:
    class Meta:
        name = "stationRichContent_Station"

    code: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    ticket_printed_name: str | None = field(
        default=None,
        metadata={
            "name": "ticketPrintedName",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    alias_station_code: str | None = field(
        default=None,
        metadata={
            "name": "aliasStationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    phone: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    address_line1: str | None = field(
        default=None,
        metadata={
            "name": "addressLine1",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    address_line2: str | None = field(
        default=None,
        metadata={
            "name": "addressLine2",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    address_line3: str | None = field(
        default=None,
        metadata={
            "name": "addressLine3",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    address_city: str | None = field(
        default=None,
        metadata={
            "name": "addressCity",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    address_province: str | None = field(
        default=None,
        metadata={
            "name": "addressProvince",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    address_postal_code: str | None = field(
        default=None,
        metadata={
            "name": "addressPostalCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    iata_station_code: str | None = field(
        default=None,
        metadata={
            "name": "iataStationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    national_location_code: str | None = field(
        default=None,
        metadata={
            "name": "nationalLocationCode",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    train_operating_company: str | None = field(
        default=None,
        metadata={
            "name": "trainOperatingCompany",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    phone_internal: str | None = field(
        default=None,
        metadata={
            "name": "phoneInternal",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )
    ticket_issuing_system: str | None = field(
        default=None,
        metadata={
            "name": "ticketIssuingSystem",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    ticket_office: str | None = field(
        default=None,
        metadata={
            "name": "ticketOffice",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    ticket_vending_machine: str | None = field(
        default=None,
        metadata={
            "name": "ticketVendingMachine",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    generic_attribute: list[StationRichContentGenericAttribute] = field(
        default_factory=list,
        metadata={
            "name": "genericAttribute",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )


@dataclass(frozen=True)
class StationRichContent:
    class Meta:
        name = "stationRichContent"

    station: list[StationRichContentStation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 1,
        },
    )
    last_changed: str | None = field(
        default=None,
        metadata={
            "name": "lastChanged",
            "type": "Attribute",
            "required": True,
        },
    )
    country_code: str | None = field(
        default=None,
        metadata={
            "name": "countryCode",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class SrtData:
    class Meta:
        name = "srtData"
        namespace = "http://railgds.net/ws/publishing"

    acceptable_fop: list[AcceptableFopType] = field(
        default_factory=list,
        metadata={
            "name": "acceptableFop",
            "type": "Element",
        },
    )
    amenity: list[AmenityType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    carrier: list[CarrierType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    country: list[CountryType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    equipment_type: list[EquipmentTypeType] = field(
        default_factory=list,
        metadata={
            "name": "equipmentType",
            "type": "Element",
        },
    )
    fare_qualifier: list[FareQualifierType] = field(
        default_factory=list,
        metadata={
            "name": "fareQualifier",
            "type": "Element",
        },
    )
    region: list[RegionType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    station: list[StationType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    marketing_information: list[MarketingInformationType] = field(
        default_factory=list,
        metadata={
            "name": "marketingInformation",
            "type": "Element",
        },
    )
    rangers_and_rovers: list[RangersAndRoversType] = field(
        default_factory=list,
        metadata={
            "name": "rangersAndRovers",
            "type": "Element",
        },
    )
    loyalty_card: list[LoyaltyCardType] = field(
        default_factory=list,
        metadata={
            "name": "loyaltyCard",
            "type": "Element",
        },
    )
    structure: list[Structure] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    station_rich_content: list[StationRichContent] = field(
        default_factory=list,
        metadata={
            "name": "stationRichContent",
            "type": "Element",
        },
    )
    fare_code_applicability_restriction: list[FareCodeApplicabilityRestriction] = field(
        default_factory=list,
        metadata={
            "name": "fareCodeApplicabilityRestriction",
            "type": "Element",
        },
    )
    reservable: list[Reservable] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    supply_channel_fare_code: list[SupplyChannelFareCode] = field(
        default_factory=list,
        metadata={
            "name": "supplyChannelFareCode",
            "type": "Element",
        },
    )
    seat_attribute: list[SeatAttribute] = field(
        default_factory=list,
        metadata={
            "name": "seatAttribute",
            "type": "Element",
        },
    )
    seat_preference: list[SeatPreference] = field(
        default_factory=list,
        metadata={
            "name": "seatPreference",
            "type": "Element",
        },
    )
    core_station: list[StationCoreSupplyChannelDataStation] = field(
        default_factory=list,
        metadata={
            "name": "coreStation",
            "type": "Element",
        },
    )
    last_changed: object | None = field(
        default=None,
        metadata={
            "name": "lastChanged",
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: SrtDataType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    silver_core_version: str | None = field(
        default=None,
        metadata={
            "name": "silverCoreVersion",
            "type": "Attribute",
        },
    )
    data_packaged: XmlDateTime | None = field(
        default=None,
        metadata={
            "name": "dataPackaged",
            "type": "Attribute",
        },
    )


@dataclass(frozen=True)
class StatusMessages:
    class Meta:
        target_namespace = "http://railgds.net/ws/publishing"


@dataclass(frozen=True)
class StatusMessageType:
    class Meta:
        target_namespace = "http://railgds.net/ws/publishing"

    message: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    code: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )
    internal: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
        },
    )


@dataclass(frozen=True)
class RequestStatusType:
    class Meta:
        target_namespace = "http://railgds.net/ws/publishing"

    success: bool | None = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
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
                "namespace": "http://railgds.net/ws/publishing",
                "min_occurs": 1,
            },
        )


@dataclass(frozen=True)
class DataStationsResponseType:
    class Meta:
        target_namespace = "http://railgds.net/ws/publishing"

    request_status: RequestStatusType | None = field(
        default=None,
        metadata={
            "name": "requestStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )

    stations: list[StationType] = field(
        default_factory=list,
        metadata={
            "name": "station",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 0,
        },
    )


@dataclass(frozen=True)
class DataAcceptableFOPResponseType:
    class Meta:
        target_namespace = "http://railgds.net/ws/publishing"

    request_status: RequestStatusType | None = field(
        default=None,
        metadata={
            "name": "requestStatus",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "required": True,
        },
    )

    acceptable_fop: list[AcceptableFopType] = field(
        default_factory=list,
        metadata={
            "name": "acceptableFop",
            "type": "Element",
            "namespace": "http://railgds.net/ws/publishing",
            "min_occurs": 0,
        },
    )


@dataclass(frozen=True)
class PublishingAPIOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/publishing"

    body: Optional["PublishingAPIOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["PublishingAPIOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Header:
        """Empty header."""

    @dataclass(frozen=True)
    class Body:
        data_response: DataStationsResponseType | None = field(
            default=None,
            metadata={
                "name": "dataResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/publishing",
            },
        )


@dataclass(frozen=True)
class PublishingAPIAcceptableFOPOutput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/publishing"

    body: Optional["PublishingAPIAcceptableFOPOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["PublishingAPIAcceptableFOPOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Header:
        """Empty header."""

    @dataclass(frozen=True)
    class Body:
        data_response: DataAcceptableFOPResponseType | None = field(
            default=None,
            metadata={
                "name": "dataResponse",
                "type": "Element",
                "namespace": "http://railgds.net/ws/publishing",
            },
        )


@dataclass(frozen=True)
class DataRequestType:
    class Meta:
        target_namespace = "http://railgds.net/ws/publishing"

    type_value: SrtDataType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass(frozen=True)
class PublishingAPIInput:
    class Meta:
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"
        target_namespace = "http://railgds.net/ws/publishing"

    body: Optional["PublishingAPIInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["PublishingAPIInput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass(frozen=True)
    class Header:
        """Empty header."""

    @dataclass(frozen=True)
    class Body:
        request: DataRequestType | None = field(
            default=None,
            metadata={
                "name": "dataRequest",
                "type": "Element",
                "namespace": "http://railgds.net/ws/publishing",
            },
        )
