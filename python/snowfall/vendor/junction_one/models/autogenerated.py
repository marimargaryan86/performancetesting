from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import (
    AwareDatetime,
    ConfigDict,
    Field,
    NaiveDatetime,
    RootModel,
    alias_generators,
)

from snowfall.stdlib.integration.pydantic import model

AwareOrNaiveDatetime = AwareDatetime | NaiveDatetime


class BaseModel(model.DefaultingBaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
    )


class AddCvvRequest(BaseModel):
    card_id: int | None = Field(None, alias="cardId")
    cvv: str | None = None


class Address(BaseModel):
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    street_number: str | None = Field(None, alias="streetNumber")
    zip_code: str | None = Field(None, alias="zipCode")


class AddressLocation(BaseModel):
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    id: int | None = None
    is_billing: bool | None = Field(None, alias="isBilling")
    owned_by_id: int | None = Field(None, alias="ownedById")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    street_number: str | None = Field(None, alias="streetNumber")
    zip_code: str | None = Field(None, alias="zipCode")


class Data(BaseModel):
    string: AddressLocation | None = Field(None, alias="String")


class Agency(BaseModel):
    code: str | None = None
    currency: str | None = None
    email: str | None = None
    flags: int | None = None
    name: str | None = None
    phone: str | None = None
    phone_after_hours: str | None = Field(None, alias="phoneAfterHours")
    phone_intl: str | None = Field(None, alias="phoneIntl")
    reservation_providers: dict[str, str] = Field(
        alias="reservationProviders",
        default_factory=dict,
    )
    website: str | None = None
    zone_id: str | None = Field(None, alias="zoneId", examples=["America/Toronto"])


class AgencyContactInfo(BaseModel):
    availability: str | None = None
    availability_after_hours: str | None = Field(None, alias="availabilityAfterHours")
    email: str | None = None
    phone: str | None = None
    phone_after_hours: str | None = Field(None, alias="phoneAfterHours")
    phone_intl: str | None = Field(None, alias="phoneIntl")
    price_after_hours: float | None = Field(None, alias="priceAfterHours")
    price_currency: str | None = Field(None, alias="priceCurrency")
    website: str | None = None


class AgencyFlags(Enum):
    has_flight_providers = "HAS_FLIGHT_PROVIDERS"
    has_hotel_providers = "HAS_HOTEL_PROVIDERS"
    has_car_providers = "HAS_CAR_PROVIDERS"
    has_train_providers = "HAS_TRAIN_PROVIDERS"
    is_public = "IS_PUBLIC"


class AgencySettings(BaseModel):
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    config: list[str] = Field(default_factory=list)
    id: int | None = None
    nms: int | None = None
    parent_agency_code: str | None = Field(None, alias="parentAgencyCode")


class AgentInquiry(BaseModel):
    active: bool | None = None
    company: str | None = None
    email: str | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")


class AgentPhone(BaseModel):
    country: str | None = None
    id: int | None = None
    phone: str | None = None


class AgentStatus(BaseModel):
    admin: bool | None = None
    agencies: list[Agency] = Field(default_factory=list)
    agent: bool | None = None


class AgodaBenefit(Enum):
    field_166 = "166"
    field_169 = "169"
    field_173 = "173"
    field_298 = "298"
    field_299 = "299"
    field_300 = "300"
    field_301 = "301"
    field_302 = "302"
    field_303 = "303"
    field_323 = "323"
    field_324 = "324"


class AgodaBoardCode(Enum):
    ro = "RO"
    bb = "BB"
    hb = "HB"
    fb = "FB"
    ai = "AI"


class AgodaBookingDetailRequest(BaseModel):
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")


class AgodaBookingStatus(Enum):
    booking_pending = "BookingPending"
    confirmed = "Confirmed"
    failed = "Failed"
    cancelled = "Cancelled"


class AgodaCancelRequest(BaseModel):
    reference_id: str | None = Field(None, alias="referenceId")


class AgodaCancellationInfo(BaseModel):
    pass


class AgodaCancellationPolicy(BaseModel):
    pass


class AgodaChannel(Enum):
    field_1 = "1"
    field_2 = "2"
    field_6 = "6"
    field_7 = "7"
    field_9 = "9"
    field_21 = "21"
    field_23 = "23"
    field_35 = "35"
    field_3958 = "3958"


class AgodaGuest(BaseModel):
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")


class AgodaGuestCount(BaseModel):
    adults: int | None = None
    children_ages: list[int] = Field(alias="childrenAges", default_factory=list)


class AgodaHotel(BaseModel):
    pass


class AgodaHotelSearchRequest(BaseModel):
    pass


class AgodaHourlyAvailableSlot(BaseModel):
    check_in_time: str | None = Field(None, alias="checkInTime")
    use_hour: int | None = Field(None, alias="useHour")


class AgodaPolicy(BaseModel):
    amount: float | None = None
    days_before_check_in: int | None = Field(None, alias="daysBeforeCheckIn")


class AgodaPrice(BaseModel):
    commission_percentage: float | None = Field(None, alias="commissionPercentage")
    currency: str | None = None
    payout_price: float | None = Field(None, alias="payoutPrice")


class AgodaRate(BaseModel):
    allotment: int | None = None
    benefits: list[AgodaBenefit] = Field(default_factory=list)
    board_code: AgodaBoardCode | None = Field(None, alias="boardCode")
    cancellation_policy: AgodaCancellationPolicy | None = Field(
        None,
        alias="cancellationPolicy",
    )
    channel: AgodaChannel | None = None
    commission_percentage: float | None = Field(None, alias="commissionPercentage")
    confirm_by_mins: int | None = Field(None, alias="confirmByMins")
    country_codes: list[str] = Field(alias="countryCodes", default_factory=list)
    hourly_available_slots: list[AgodaHourlyAvailableSlot] = Field(
        alias="hourlyAvailableSlots",
        default_factory=list,
    )
    instant_confirm: bool | None = Field(None, alias="instantConfirm")
    metadata: str | None = None
    price: float | None = None
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    sub_supplier_id: str | None = Field(None, alias="subSupplierId")


class AgodaResponseStatus(Enum):
    success = "SUCCESS"
    no_availability = "NO_AVAILABILITY"
    no_allotment = "NO_ALLOTMENT"
    booking_fail = "BOOKING_FAIL"
    booking_pending = "BOOKING_PENDING"
    booking_not_exists = "BOOKING_NOT_EXISTS"
    cancel_fail = "CANCEL_FAIL"
    malformed_request = "MALFORMED_REQUEST"
    unauthorized = "UNAUTHORIZED"
    booking_timeout = "BOOKING_TIMEOUT"
    rate_exceeded = "RATE_EXCEEDED"
    unexpected_error = "UNEXPECTED_ERROR"
    unsupported_country_code = "UNSUPPORTED_COUNTRY_CODE"
    supplier_server_error = "SUPPLIER_SERVER_ERROR"


class AgodaRoom(BaseModel):
    pass


class AircraftInfo(BaseModel):
    aircraft_type: str | None = Field(None, alias="aircraftType")
    tail_number: str | None = Field(None, alias="tailNumber")
    weight_class: str | None = Field(None, alias="weightClass")


class AircraftType(Enum):
    none = "None"
    bus = "Bus"
    helicopter = "Helicopter"
    jumbo = "Jumbo"
    larger_regional_jet = "LargerRegionalJet"
    narrowbody = "Narrowbody"
    smaller_regional_jet = "SmallerRegionalJet"
    train = "Train"
    turbo_prop = "TurboProp"
    widebody = "Widebody"


class Airline(BaseModel):
    active: bool | None = None
    alias: str | None = None
    callsign: str | None = None
    country: str | None = None
    iata: str | None = None
    icao: str | None = None
    id: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    name: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    short_name: str | None = Field(None, alias="shortName")
    ticketing_code: str | None = Field(None, alias="ticketingCode")


class AirlineLoyaltyProgram(BaseModel):
    airline_id: int | None = Field(None, alias="airlineId")
    id: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    main: bool | None = None


class AirlineSegmentPerks(Enum):
    wn_wanna_get_away = "WN_WANNA_GET_AWAY"
    wn_anytime = "WN_ANYTIME"
    wn_business = "WN_BUSINESS"


class AirlineTicketPerks(Enum):
    wn_wanna_get_away = "WN_WANNA_GET_AWAY"
    wn_anytime = "WN_ANYTIME"
    wn_business = "WN_BUSINESS"


class Airport(BaseModel):
    airline_count: int | None = Field(None, alias="airlineCount")
    altitude: int | None = None
    city: str | None = None
    code: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    dst: str | None = None
    group_iata: str | None = Field(None, alias="groupIata")
    iata: str | None = None
    icao: str | None = None
    id: int | None = None
    label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    timezone: str | None = None
    timezone_offset: float | None = Field(None, alias="timezoneOffset")


class AmadeusUserProfile(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_hash: str | None = Field(None, alias="profileHash")
    profile_id: str | None = Field(None, alias="profileId")
    user_id: int | None = Field(None, alias="userId")


class AmenityCategory(Enum):
    free_services = "freeServices"
    internet = "internet"
    parking = "parking"
    food = "food"


class AmenityCost(Enum):
    none = "None"
    free = "Free"
    paid = "Paid"
    free_or_paid = "FreeOrPaid"


class Amount(BaseModel):
    currency: str | None = None
    value: float | None = None


class AncillaryAssignment(BaseModel):
    boundary: str | None = None
    code: str | None = None
    consumer_index: int | None = Field(None, alias="consumerIndex")
    quantity: int | None = None
    ref: str | None = None


class AncillaryCategory(Enum):
    baggage = "BAGGAGE"
    meal = "MEAL"
    ssr = "SSR"
    other = "OTHER"


class AncillaryType(Enum):
    per_destination = "PerDestination"
    per_reservation = "PerReservation"
    per_user = "PerUser"


class Application(Enum):
    up_to = "up to"
    over = "over"


class AppliedDiscount(BaseModel):
    code: str | None = None
    conditions: list[str] = Field(default_factory=list)
    description: str | None = None
    id: str | None = None
    name: str | None = None


class ApprovalAction(Enum):
    approve = "APPROVE"
    reject = "REJECT"
    cancel = "CANCEL"


class ApprovalStatus(Enum):
    draft = "DRAFT"
    pending = "PENDING"
    approved = "APPROVED"
    rejected = "REJECTED"
    cancelled = "CANCELLED"


class ApprovalUiFlags(Enum):
    send_enabled = "SEND_ENABLED"
    approve_enabled = "APPROVE_ENABLED"
    reject_enabled = "REJECT_ENABLED"
    cancel_enabled = "CANCEL_ENABLED"


class ArrivalFlight(BaseModel):
    airline: str | None = None
    flight_number: str | None = Field(None, alias="flightNumber")


class Assessment(Enum):
    neutral = "Neutral"
    benefit = "Benefit"
    fee = "Fee"
    restriction = "Restriction"


class AssociatedAirline(BaseModel):
    airline_id: int | None = None
    associated_airline_id: int | None = Field(None, alias="associatedAirlineId")
    id: int | None = None


class BaggageAttributes(BaseModel):
    cxr: str | None = None
    seq_no: int | None = Field(None, alias="seqNo")
    service_type: str | None = Field(None, alias="serviceType")
    sub_code: str | None = Field(None, alias="subCode")


class BaseEntity(BaseModel):
    id: int | None = None
    nms: int | None = None


class BaseTrainStation(BaseModel):
    city: str | None = None
    code: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    flags: int | None = None
    id: int | None = None
    label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")


class BeverageType(Enum):
    none = "None"
    alcoholic = "Alcoholic"
    nonalcoholic = "Nonalcoholic"
    alcoholic_and_nonalcoholic = "AlcoholicAndNonalcoholic"
    premium_alcoholic = "PremiumAlcoholic"


class BookingAct(Enum):
    start = "START"
    reprice = "REPRICE"
    validate = "VALIDATE"
    pre_process = "PRE_PROCESS"
    sync_profiles = "SYNC_PROFILES"
    reserve = "RESERVE"
    commit_reservation = "COMMIT_RESERVATION"
    commit_seats = "COMMIT_SEATS"
    commit_ancillaries = "COMMIT_ANCILLARIES"
    cancel = "CANCEL"
    sync_pnrs = "SYNC_PNRS"
    post_reserve = "POST_RESERVE"
    post_commit = "POST_COMMIT"
    post_cancel = "POST_CANCEL"
    end = "END"


class Brand(BaseModel):
    brand_codes: list[str] = Field(alias="brandCodes", default_factory=list)
    brand_name: str | None = Field(None, alias="brandName")
    id: str | None = None


class Branding(BaseModel):
    hero_url: str | None = Field(None, alias="heroUrl")
    logo_url: str | None = Field(None, alias="logoUrl")
    primary_color: str | None = Field(None, alias="primaryColor")
    secondary_color: str | None = Field(None, alias="secondaryColor")


class CabinClass(Enum):
    economy = "Economy"
    premium_economy = "PremiumEconomy"
    business = "Business"
    premium_business = "PremiumBusiness"
    first = "First"
    premium_first = "PremiumFirst"


class CabinClassSpecs(Enum):
    ac_economy = "AC_ECONOMY"
    ac_premium_economy = "AC_PREMIUM_ECONOMY"
    ac_business = "AC_BUSINESS"
    ac_first_class = "AC_FIRST_CLASS"
    ba_economy = "BA_ECONOMY"
    ba_premium_economy = "BA_PREMIUM_ECONOMY"
    ba_business = "BA_BUSINESS"
    ba_first_class = "BA_FIRST_CLASS"
    wn_economy = "WN_ECONOMY"


class CabinPressureEnum(Enum):
    n_a = "n/a"
    normal = "normal"
    enhanced = "enhanced"
    unpressurized = "unpressurized"


class Campaign(BaseModel):
    accent_color: str | None = Field(None, alias="accentColor")
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    code: str | None = None
    email_template: str | None = Field(None, alias="emailTemplate")
    id: int | None = None
    logo_url: str | None = Field(None, alias="logoUrl")
    nms: int | None = None
    show_company_input: bool | None = Field(None, alias="showCompanyInput")


class CampaignUser(BaseModel):
    campaign_id: int | None = Field(None, alias="campaignId")
    id: int | None = None
    nms: int | None = None
    user_id: int | None = Field(None, alias="userId")


class Car(BaseModel):
    car_type: str | None = Field(None, alias="carType")
    class_code: str | None = Field(None, alias="classCode")
    class_name: str | None = Field(None, alias="className")
    doors: str | None = None
    features: int | None = None
    image_url: str | None = Field(None, alias="imageUrl")
    luggage: str | None = None
    make: str | None = None
    model: str | None = None
    mpg: str | None = None
    name: str | None = None
    seats: str | None = None
    transmission: str | None = None


class CarCategory(Enum):
    mini = "MINI"
    mini_elite = "MINI_ELITE"
    economy = "ECONOMY"
    economy_elite = "ECONOMY_ELITE"
    compact = "COMPACT"
    compact_elite = "COMPACT_ELITE"
    intermediate = "INTERMEDIATE"
    intermediate_elite = "INTERMEDIATE_ELITE"
    standard = "STANDARD"
    standard_elite = "STANDARD_ELITE"
    fullsize = "FULLSIZE"
    fullsize_elite = "FULLSIZE_ELITE"
    premium = "PREMIUM"
    premium_elite = "PREMIUM_ELITE"
    luxury = "LUXURY"
    luxury_elite = "LUXURY_ELITE"
    oversize = "OVERSIZE"
    special = "SPECIAL"


class CarExtra(BaseModel):
    code: str | None = None
    name: str | None = None
    price: float | None = None
    quantity: int | None = None
    total_price: float | None = Field(None, alias="totalPrice")


class CarFareType(Enum):
    economy = "Economy"
    standard = "Standard"
    premium = "Premium"


class CarFeatures(Enum):
    air_conditioner = "AIR_CONDITIONER"
    bluetooth = "BLUETOOTH"
    internet = "INTERNET"


class CarFlags(Enum):
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    has_rate_code = "HAS_RATE_CODE"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class CarInsurance(BaseModel):
    code: str | None = None
    name: str | None = None
    note: str | None = None
    price: float | None = None
    selected: bool | None = None
    total_price: float | None = Field(None, alias="totalPrice")


class CarLocation(BaseModel):
    address1: str | None = None
    address2: str | None = None
    airport: bool | None = None
    brand: str | None = None
    city: str | None = None
    code: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    distance: float | None = None
    flags: int | None = None
    hours: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    phone: str | None = None
    ref: str | None = None
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    vendor: str | None = None
    vendor_pref_level: int | None = Field(None, alias="vendorPrefLevel")
    zip_code: str | None = Field(None, alias="zipCode")


class CarLocationFlags(Enum):
    direct_connect = "DIRECT_CONNECT"
    preferred = "PREFERRED"
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    hidden = "HIDDEN"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class CarLocationMerged(BaseModel):
    airport: bool | None = None
    distance: float | None = None
    flags: int | None = None
    latitude: float | None = None
    locations: list[CarLocation] = Field(default_factory=list)
    longitude: float | None = None
    name: str | None = None
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    refs: list[str] = Field(default_factory=list)
    vendor_pref_level: int | None = Field(None, alias="vendorPrefLevel")


class CarOffer(BaseModel):
    approval_required: bool | None = Field(None, alias="approvalRequired")
    booking_blocked: bool | None = Field(None, alias="bookingBlocked")
    brand: str | None = None
    car: Car | None = None
    currency: str | None = None
    drop_off: str | None = Field(None, alias="dropOff")
    fare_type: CarFareType | None = Field(None, alias="fareType")
    flags: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    pick_up: str | None = Field(None, alias="pickUp")
    ref: str | None = None
    same_drop_off_location: bool | None = Field(None, alias="sameDropOffLocation")
    total_price: float | None = Field(None, alias="totalPrice")
    total_price_per_day: float | None = Field(None, alias="totalPricePerDay")
    total_vehicle: float | None = Field(None, alias="totalVehicle")
    vendor: str | None = None
    vendor_pref_level: int | None = Field(None, alias="vendorPrefLevel")


class CarType(Enum):
    two_door = "TWO_DOOR"
    four_door = "FOUR_DOOR"
    five_door = "FIVE_DOOR"
    wagon = "WAGON"
    passenger_van = "PASSENGER_VAN"
    limousine = "LIMOUSINE"
    sport = "SPORT"
    convertible = "CONVERTIBLE"
    suv = "SUV"
    open_air_all_terrain = "OPEN_AIR_ALL_TERRAIN"
    special = "SPECIAL"
    pick_up_2_door = "PICK_UP_2_DOOR"
    pick_up_4_door = "PICK_UP_4_DOOR"
    special_offer_car = "SPECIAL_OFFER_CAR"
    coupe = "COUPE"
    monospace = "MONOSPACE"
    recreational_vehicle = "RECREATIONAL_VEHICLE"
    motor_home = "MOTOR_HOME"
    two_wheel_vehicle = "TWO_WHEEL_VEHICLE"
    roadster = "ROADSTER"
    crossover = "CROSSOVER"
    commercial_van = "COMMERCIAL_VAN"


class CarVendor(BaseModel):
    code: str | None = None
    id: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    name: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")


class CardType(Enum):
    visa = "VISA"
    master = "MASTER"
    amex = "AMEX"
    diners = "DINERS"
    discover = "DISCOVER"
    uatp = "UATP"


class ChanceEnum(Enum):
    n_a = "n/a"
    some = "some"
    good = "good"
    very_good = "very good"
    full = "full"


class ComfortClass(BaseModel):
    code: str | None = None
    description: str | None = None
    id: str | None = None


class ConcurOrg(BaseModel):
    active: bool | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")


class ConcurOrgUser(BaseModel):
    active: bool | None = None
    employee_uid: str | None = Field(None, alias="employeeUid")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    org_user_id: int | None = Field(None, alias="orgUserId")


class Condition(BaseModel):
    description: str | None = None
    name: str | None = None


class ConnectivityTypeEnum(Enum):
    gsm_wi_fi = "GSM_WiFi"
    n_a = "n/a"
    wifi = "wifi"
    cellular_roaming = "cellular_roaming"
    trial = "Trial"


class ContentTypeEnum(Enum):
    avod = "avod"
    iptv = "iptv"
    livetv = "livetv"
    movies = "movies"
    n_a = "n/a"
    tvshows = "tvshows"


class Continent(Enum):
    af = "AF"
    an = "AN"
    as_ = "AS"
    eu = "EU"
    na = "NA"
    oc = "OC"
    sa = "SA"


class CorporateProfile(BaseModel):
    name: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_id: str | None = Field(None, alias="profileId")


class Cost(Enum):
    free = "free"
    free_or_paid = "free or paid"
    paid = "paid"
    n_a = "n/a"


class Country(BaseModel):
    authority_code: str | None = Field(None, alias="authorityCode")
    code: str | None = None
    code2: str | None = None
    code3: str | None = None
    continent: str | None = None
    currency_id: int | None = Field(None, alias="currencyId")
    id: int | None = None
    name: str | None = None


class CountryState(BaseModel):
    code: str | None = None
    country_id: int | None = Field(None, alias="countryId")
    id: int | None = None
    name: str | None = None


class CoverageEnum(Enum):
    full = "full"
    n_a = "n/a"
    none = "none"
    partial = "partial"


class CrashReport(BaseModel):
    created_on: int | None = Field(None, alias="createdOn")
    custom_data: str | None = Field(None, alias="customData")
    id: int | None = None
    nms: int | None = None
    os: str | None = None
    os_version: str | None = Field(None, alias="osVersion")
    phone_model: str | None = Field(None, alias="phoneModel")
    stack_trace: str | None = Field(None, alias="stackTrace")
    user_comment: str | None = Field(None, alias="userComment")
    version_code: str | None = Field(None, alias="versionCode")
    version_name: str | None = Field(None, alias="versionName")


class Credit(BaseModel):
    active: bool | None = None
    amount: float | None = None
    currency: str | None = None
    expiry: date | None = None
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    reference: str | None = None
    source: str | None = None
    user_id: int | None = Field(None, alias="userId")
    vendor: str | None = None


class CreditCard(BaseModel):
    address: Address | None = None
    card_number: str | None = Field(None, alias="cardNumber")
    cvv: str | None = None
    exp: str | None = Field(None, examples=["2022-03"])
    holder_name: str | None = Field(None, alias="holderName")
    id: int | None = None
    reservation_types: int | None = Field(None, alias="reservationTypes")
    stripe_id: str | None = Field(None, alias="stripeId")
    type: CardType | None = None


class Currency(BaseModel):
    code: str | None = None
    id: int | None = None
    issuing_country: str | None = Field(None, alias="issuingCountry")
    name: str | None = None
    numeric_code: str | None = Field(None, alias="numericCode")


class Cvv(BaseModel):
    card_id: int | None = Field(None, alias="cardId")
    cvv: str | None = None
    expiration: AwareOrNaiveDatetime | None = None
    id: int | None = None
    tripboard_id: int | None = Field(None, alias="tripboardId")


class DeliveryMediumEnum(Enum):
    in_seat = "in-seat"
    n_a = "n/a"
    none = "none"
    overhead = "overhead"
    pre_download = "pre-download"
    streaming = "streaming"
    tablet = "tablet"


class DeliveryOption(BaseModel):
    code: str | None = None
    name: str | None = None


class DemoRequest(BaseModel):
    decision_making_role: str | None = Field(None, alias="decisionMakingRole")
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    id: int | None = None
    last_name: str | None = Field(None, alias="lastName")
    phone_number: str | None = Field(None, alias="phoneNumber")


class DepartmentInfo(BaseModel):
    id: int | None = None
    member_count: int | None = Field(None, alias="memberCount")
    name: str | None = None


class DistanceUnit(Enum):
    mi = "MI"
    km = "KM"


class DistributionEnum(Enum):
    all = "all"
    n_a = "n/a"
    some = "some"


class Domain(BaseModel):
    active: bool | None = None
    branding: Branding | None = None
    code: str | None = None
    hosts: list[str] = Field(default_factory=list)
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    org_ids: list[int] = Field(alias="orgIds", default_factory=list)
    sso_service_codes: list[str] = Field(alias="ssoServiceCodes", default_factory=list)


class EmailStatus(Enum):
    confirmed = "Confirmed"
    unconfirmed = "Unconfirmed"


class EmergencyContact(BaseModel):
    full_name: str | None = Field(None, alias="fullName")
    phone_number: str | None = Field(None, alias="phoneNumber")


class EmptyData(BaseModel):
    pass


class EntertainementContentType(Enum):
    none = "NONE"
    avod = "AVOD"
    iptv = "IPTV"
    livetv = "LIVETV"
    movies = "MOVIES"
    tvshows = "TVSHOWS"


class ExceptionFlags(Enum):
    price_is_more_expensive = "PRICE_IS_MORE_EXPENSIVE"
    expired = "EXPIRED"
    no_longer_available = "NO_LONGER_AVAILABLE"
    credit_card_failure = "CREDIT_CARD_FAILURE"
    passport_required = "PASSPORT_REQUIRED"
    expired_offer = "EXPIRED_OFFER"
    min_age_violated = "MIN_AGE_VIOLATED"
    email_required = "EMAIL_REQUIRED"
    phone_required = "PHONE_REQUIRED"
    invalid_reward = "INVALID_REWARD"
    invalid_credit = "INVALID_CREDIT"
    dob_required = "DOB_REQUIRED"
    reserved_13 = "RESERVED_13"
    reserved_14 = "RESERVED_14"
    reserved_15 = "RESERVED_15"
    booking_failure = "BOOKING_FAILURE"
    user_is_locked = "USER_IS_LOCKED"
    kyc_failure = "KYC_FAILURE"
    cancel_failure = "CANCEL_FAILURE"
    vendor_change = "VENDOR_CHANGE"
    data_required = "DATA_REQUIRED"
    unconfirmed = "UNCONFIRMED"
    reserved_23 = "RESERVED_23"
    reserved_24 = "RESERVED_24"
    reserved_25 = "RESERVED_25"
    reserved_26 = "RESERVED_26"
    reserved_27 = "RESERVED_27"
    reserved_28 = "RESERVED_28"
    reserved_29 = "RESERVED_29"
    reserved_30 = "RESERVED_30"
    software = "SOFTWARE"


class ExceptionHandlingContext(BaseModel):
    pass


class ExchangeRate(BaseModel):
    base: str | None = None
    quote: str | None = None
    rate: float | None = None


class Exists(Enum):
    yes = "yes"
    no = "no"
    n_a = "n/a"


class Exists3(Enum):
    yes = "yes"
    no = "no"
    partial = "partial"


class ExpensifySettings(BaseModel):
    active: bool | None = None


class Ext(BaseModel):
    pass


class FareConditions(BaseModel):
    code: str | None = None
    conditions: list[Condition] = Field(default_factory=list)
    conditions_summary: str | None = Field(None, alias="conditionsSummary")
    description: str | None = None
    id: str | None = None


class FareRule(BaseModel):
    descriptions: dict[str, list[str]] = Field(default_factory=dict)
    fare_basis_code: str | None = Field(None, alias="fareBasisCode")
    segment_key: str | None = Field(None, alias="segmentKey")


class FareSegment(BaseModel):
    cabin: CabinClass | None = None
    class_of_service: str | None = Field(None, alias="classOfService")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    perks: int | None = None
    segment_id: str | None = Field(None, alias="segmentId")


class FareType(Enum):
    field_1 = "1"
    field_2 = "2"
    field_3 = "3"
    field_4 = "4"
    field_5 = "5"
    field_6 = "6"


class FareTypeSpecs(Enum):
    aa_sup_plus = "AA_SUP_PLUS"
    aa_luxury = "AA_LUXURY"
    ac_basic = "AC_BASIC"
    ac_std = "AC_STD"
    ac_std_plus = "AC_STD_PLUS"
    ac_std_plus_narrow = "AC_STD_PLUS_NARROW"
    ac_sup_narrow = "AC_SUP_NARROW"
    ac_sup_wide = "AC_SUP_WIDE"
    ac_sup_plus_wide = "AC_SUP_PLUS_WIDE"
    ac_luxury_wide = "AC_LUXURY_WIDE"
    wn = "WN"
    wn_y = "WN_Y"
    wn_k = "WN_K"


class Fee(BaseModel):
    amount: float | None = None
    currency: str | None = None


class FieldFlags(Enum):
    move_to_pnr = "MOVE_TO_PNR"
    move_to_reservation = "MOVE_TO_RESERVATION"
    required = "REQUIRED"
    out_of_policy = "OUT_OF_POLICY"


class FieldType(Enum):
    hidden = "HIDDEN"
    profile = "PROFILE"
    reservation = "RESERVATION"


class FieldValue(BaseModel):
    active: bool | None = None
    code: str | None = None
    field_id: int | None = Field(None, alias="fieldId")
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    remark_required: bool | None = Field(None, alias="remarkRequired")


class FieldValueType(Enum):
    lookup = "LOOKUP"
    text = "TEXT"


class FlatnessEnum(Enum):
    angle_flat = "angle flat"
    full_flat = "full flat"
    n_a = "n/a"
    not_flat = "not flat"


class FlightAttributeFee(BaseModel):
    amount_max: str | None = Field(None, alias="amountMax")
    amount_min: str | None = Field(None, alias="amountMin")
    currency_code: str | None = Field(None, alias="currencyCode")


class FlightClass(Enum):
    first = "First"
    business = "Business"
    economy = "Economy"


class FlightClassPref(BaseModel):
    premium: bool | None = None
    value: FlightClass | None = None


class FlightOptionPreferences(Enum):
    faster = "faster"
    cheaper = "cheaper"


class FlightOvernightPreferences(Enum):
    hotel = "hotel"
    red_eye = "red eye"


class FlightReservationSeatFlags(Enum):
    adult_only = "ADULT_ONLY"
    exit_row = "EXIT_ROW"


class FlightReservationSegment(BaseModel):
    aircraft: str | None = None
    airline: str | None = None
    arrival_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalOffsetDateTime",
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    arrival_time_offset: int | None = Field(None, alias="arrivalTimeOffset")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    departure_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureOffsetDateTime",
    )
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    departure_time_offset: int | None = Field(None, alias="departureTimeOffset")
    duration: int | None = None
    fare_basis_code: str | None = Field(None, alias="fareBasisCode")
    fare_brand: str | None = Field(None, alias="fareBrand")
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    flight_class: FlightClass | None = Field(None, alias="flightClass")
    flight_class_premium: bool | None = Field(None, alias="flightClassPremium")
    flight_number: str | None = Field(None, alias="flightNumber")
    operating_airline: str | None = Field(None, alias="operatingAirline")
    segment_key: str | None = Field(None, alias="segmentKey")
    service_class: str | None = Field(None, alias="serviceClass")


class FlightSearchFlight(BaseModel):
    arrival_airport: str | None = Field(None, alias="arrivalAirport")
    depart_date: date | None = Field(None, alias="departDate")
    departure_airport: str | None = Field(None, alias="departureAirport")


class FlightSeatMapRequest(BaseModel):
    refs: list[str] = Field(default_factory=list)
    reward_programs: dict[str, dict[str, int]] = Field(
        alias="rewardPrograms",
        default_factory=dict,
    )


class FlightSegmentRefData(BaseModel):
    aircraft_type: str | None = Field(None, alias="aircraftType")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    cabin_class: CabinClass | None = Field(None, alias="cabinClass")
    class_of_service: str | None = Field(None, alias="classOfService")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    fare_basis_code: str | None = Field(None, alias="fareBasisCode")
    fare_brand: str | None = Field(None, alias="fareBrand")
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    flight_class: FlightClass | None = Field(None, alias="flightClass")
    flight_class_premium: bool | None = Field(None, alias="flightClassPremium")
    flight_number: str | None = Field(None, alias="flightNumber")
    is_stop_segment: bool | None = Field(None, alias="isStopSegment")
    marketing_airline_code: str | None = Field(None, alias="marketingAirlineCode")
    marriage_group: str | None = Field(None, alias="marriageGroup")
    operating_airline_code: str | None = Field(None, alias="operatingAirlineCode")
    segment_key: str | None = Field(None, alias="segmentKey")


class FoodQuality(Enum):
    none = "None"
    better = "Better"
    standard = "Standard"


class FoodType(Enum):
    none = "None"
    meal = "Meal"
    premium_snack = "PremiumSnack"
    snack = "Snack"
    light_meal = "LightMeal"
    premium_meal = "PremiumMeal"


class FopFlags(Enum):
    on_account = "ON_ACCOUNT"
    on_account_selectable = "ON_ACCOUNT_SELECTABLE"
    credit = "CREDIT"
    cc_visa = "CC_VISA"
    cc_mastercard = "CC_MASTERCARD"
    cc_amex = "CC_AMEX"
    cc_dinners_club = "CC_DINNERS_CLUB"


class Fts(BaseModel):
    id: int | None = None
    resource_type: str | None = Field(None, alias="resourceType")


class FtsOperatorType(Enum):
    and_ = "AND"
    or_ = "OR"


class FtsResources(BaseModel):
    pass


class Gender(Enum):
    male = "male"
    female = "female"


class GeoLocation(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class GetCarRequest(BaseModel):
    ref: str | None = None
    user_owner_id: int | None = Field(None, alias="userOwnerId")


class GetCarResponse(BaseModel):
    brand: str | None = None
    car: Car | None = None
    currency: str | None = None
    days: int | None = None
    distance_overage: float | None = Field(None, alias="distanceOverage")
    distance_unit: DistanceUnit | None = Field(None, alias="distanceUnit")
    drop_off: CarLocation | None = Field(None, alias="dropOff")
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    extras: list[CarExtra] = Field(default_factory=list)
    flags: int | None = None
    free_distance_covered: float | None = Field(None, alias="freeDistanceCovered")
    hours: int | None = None
    insurance: list[CarInsurance] = Field(default_factory=list)
    invalid_reward_program: bool | None = Field(None, alias="invalidRewardProgram")
    org_id: int | None = Field(None, alias="orgId")
    pick_up: CarLocation | None = Field(None, alias="pickUp")
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    ref: str | None = None
    same_drop_off_location: bool | None = Field(None, alias="sameDropOffLocation")
    total_extras: float | None = Field(None, alias="totalExtras")
    total_fees: float | None = Field(None, alias="totalFees")
    total_insurance: float | None = Field(None, alias="totalInsurance")
    total_price: float | None = Field(None, alias="totalPrice")
    total_taxes: float | None = Field(None, alias="totalTaxes")
    total_vehicle: float | None = Field(None, alias="totalVehicle")
    unlimited_distance: bool | None = Field(None, alias="unlimitedDistance")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class GlobalUserReward(BaseModel):
    id: int | None = None
    idx: int | None = None
    member_id: str | None = Field(None, alias="memberId")
    reward_program_id: int | None = Field(None, alias="rewardProgramId")


class HotelAmenities(Enum):
    parking = "PARKING"
    restaurant = "RESTAURANT"
    internet_access_in_room = "INTERNET_ACCESS_IN_ROOM"
    free_breakfast = "FREE_BREAKFAST"
    bar = "BAR"
    pool = "POOL"
    fitness = "FITNESS"
    spa = "SPA"
    petfriendly = "PETFRIENDLY"


class HotelCancellation(BaseModel):
    cancellable: bool | None = None
    cancellation_fee_percent: float | None = Field(None, alias="cancellationFeePercent")
    deadline: AwareOrNaiveDatetime | None = None
    description: str | None = None
    fully_refundable: bool | None = Field(None, alias="fullyRefundable")
    non_refundable_rate: bool | None = Field(None, alias="nonRefundableRate")
    prepayment_percent: float | None = Field(None, alias="prepaymentPercent")


class HotelChain(BaseModel):
    active: bool | None = None
    code: str | None = None
    id: int | None = None
    marketer_code: str | None = Field(None, alias="marketerCode")
    marketer_name: str | None = Field(None, alias="marketerName")
    name: str | None = None


class HotelChainReward(BaseModel):
    chain_code: str | None = Field(None, alias="chainCode")
    chain_name: str | None = Field(None, alias="chainName")
    group_name: str | None = Field(None, alias="groupName")
    id: int | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")


class HotelInfoRequest(BaseModel):
    refs: list[str] = Field(default_factory=list)


class HotelMedia(BaseModel):
    media_height: int | None = Field(None, alias="mediaHeight")
    media_url: str | None = Field(None, alias="mediaURL")
    media_width: int | None = Field(None, alias="mediaWidth")
    thumbnail_height: int | None = Field(None, alias="thumbnailHeight")
    thumbnail_url: str | None = Field(None, alias="thumbnailURL")
    thumbnail_width: int | None = Field(None, alias="thumbnailWidth")


class HotelOfferFlags(Enum):
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    has_rate_code = "HAS_RATE_CODE"
    current_reservation = "CURRENT_RESERVATION"
    hotel_status_preferred = "HOTEL_STATUS_PREFERRED"
    hidden = "HIDDEN"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class HotelRateSource(Enum):
    sabre_gds = "SABRE_GDS"
    expedia = "EXPEDIA"
    bedsonline = "BEDSONLINE"
    booking_com = "BOOKING_COM"


class HotelRoomFlags(Enum):
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    has_rate_code = "HAS_RATE_CODE"
    reward_enabled = "REWARD_ENABLED"
    current_reservation = "CURRENT_RESERVATION"
    prepaid = "PREPAID"
    member_rate = "MEMBER_RATE"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"
    hidden = "HIDDEN"


class HotelRoomsRequest(BaseModel):
    refs: list[str] = Field(default_factory=list)
    reservation_id: int | None = Field(None, alias="reservationId")


class ImportProfileAct(Enum):
    inquire = "INQUIRE"
    dry_run = "DRY_RUN"
    proceed = "PROCEED"


class ImportProfileSource(Enum):
    corp_profile = "CORP_PROFILE"
    template = "TEMPLATE"


class InitUserAccountRequest(BaseModel):
    dob: date | None = None
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    flags: int | None = None
    gender: Gender | None = None
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    password: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    session_expires_in: int | None = Field(None, alias="sessionExpiresIn")
    suffix: str | None = None
    token: str | None = None


class IssueCreditCard(BaseModel):
    activation_date: date | None = Field(None, alias="activationDate")
    amount: int | None = None
    currency: str | None = None
    expiry_date: date | None = Field(None, alias="expiryDate")
    multi_use: bool | None = Field(None, alias="multiUse")


class KnownTravelerNumber(BaseModel):
    dob: AwareOrNaiveDatetime | None = None
    doc_number: str | None = Field(None, alias="docNumber")
    doc_type: str | None = Field(None, alias="docType")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    suffix: str | None = None


class KpiCountResponse(BaseModel):
    begin: AwareOrNaiveDatetime | None = None
    count: int | None = None
    end: AwareOrNaiveDatetime | None = None


class LayoutQualityType(Enum):
    better = "Better"
    standard = "Standard"
    none = "None"


class LayoutType(Enum):
    angled = "Angled"
    angled_pods = "AngledPods"
    forward_backward = "ForwardBackward"
    forward = "Forward"
    herringbone = "Herringbone"
    middle_seat_free = "MiddleSeatFree"
    layered = "Layered"
    none = "None"
    staggered_herringbone = "StaggeredHerringbone"
    reverse_herringbone = "ReverseHerringbone"
    staggered = "Staggered"
    v_shaped = "V_Shaped"
    yin_yang = "YinYang"


class LegroomEnum(Enum):
    less = "less"
    more = "more"
    n_a = "n/a"
    standard = "standard"


class ListFareRulesResponse(BaseModel):
    fare_rules: list[FareRule] = Field(alias="fareRules", default_factory=list)


class Localization(BaseModel):
    language: str | None = None
    text: str | None = None


class LocalizationList1(BaseModel):
    elements: list[Localization] = Field(default_factory=list)
    empty: bool | None = None
    first: Localization | None = None
    last: Localization | None = None
    localizations: list[Localization] = Field(default_factory=list)


class LocalizationList(RootModel[list[Localization] | LocalizationList1]):
    root: list[Localization] | LocalizationList1


class LocateCarRequest(BaseModel):
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    keyword: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    org_id: int | None = Field(None, alias="orgId")
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    refs: list[str] = Field(default_factory=list)
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class LookupTable(Enum):
    policycity = "policycity"


class MaskedUserRewardProgram(BaseModel):
    id: int | None = None
    idx: int | None = None
    number: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    user_id: int | None = Field(None, alias="userId")


class MediaSource(Enum):
    j1 = "J1"
    psngr1 = "PSNGR1"
    unsplash = "UNSPLASH"


class MediaType(Enum):
    image = "IMAGE"
    movie = "MOVIE"


class MessageHandlingContext(BaseModel):
    pass


class MissingFieldsFlags(Enum):
    cvc = "CVC"
    holder_name = "HOLDER_NAME"
    address = "ADDRESS"
    expiration = "EXPIRATION"


class MsgDatePair(BaseModel):
    end: date | None = None
    start: date | None = None
    text: str | None = None


class MsgLocation(BaseModel):
    address: str | None = None
    components: list[str] = Field(default_factory=list)
    geo: GeoLocation | None = None
    place_id: str | None = Field(None, alias="placeId")
    text: str | None = None


class MsgMention(BaseModel):
    text: str | None = None
    user_id: int | None = Field(None, alias="userId")


class NotificationType(Enum):
    msg_comment = "MSG_COMMENT"
    msg_mention = "MSG_MENTION"
    msg_reaction = "MSG_REACTION"
    msg_reply = "MSG_REPLY"
    trip_board_processing = "TRIP_BOARD_PROCESSING"
    trip_post = "TRIP_POST"
    trip_update = "TRIP_UPDATE"
    user_weak_password = "USER_WEAK_PASSWORD"


class OccurrenceStatus(Enum):
    unknown = "UNKNOWN"
    past = "PAST"
    occurring = "OCCURRING"
    future = "FUTURE"


class OperationStatus(Enum):
    ongoing = "ONGOING"
    pending = "PENDING"
    pending_exception = "PENDING_EXCEPTION"
    pending_waypoint = "PENDING_WAYPOINT"
    processed = "PROCESSED"
    approved = "APPROVED"
    rejected = "REJECTED"
    canceled = "CANCELED"
    sent_for_approval_to_travelers = "SENT_FOR_APPROVAL_TO_TRAVELERS"
    sent_for_approval_to_approvers = "SENT_FOR_APPROVAL_TO_APPROVERS"


class OperatorEnum(Enum):
    and_ = "and"
    or_ = "or"


class OptSvcApplication(Enum):
    not_offered = "not offered"
    displayed = "displayed"
    free = "free"
    for_a_charge = "for a charge"


class OptionalServiceIdentifier(BaseModel):
    group_code: str | None = Field(None, alias="groupCode")
    sub_code: str | None = Field(None, alias="subCode")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class OrgAgency(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    contact_info: AgencyContactInfo | None = Field(None, alias="contactInfo")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")


class OrgAirlinePref(BaseModel):
    airline_code: str | None = Field(None, alias="airlineCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")


class OrgBudgetType(Enum):
    company_wide = "companyWide"


class OrgCarVendorPref(BaseModel):
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")
    vendor_code: str | None = Field(None, alias="vendorCode")


class OrgDomain(BaseModel):
    active: bool | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")


class OrgEmail(BaseModel):
    active: bool | None = None
    email: str | None = None
    id: int | None = None
    nms: int | None = None


class OrgEntryData(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    description: str | None = None
    flags: int | None = None
    name: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    timezone: str | None = None
    website: str | None = None


class OrgEntryDataImpl(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    description: str | None = None
    flags: int | None = None
    name: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    timezone: str | None = None
    website: str | None = None


class OrgFlags(Enum):
    user_can_post = "USER_CAN_POST"
    feed_disabled = "FEED_DISABLED"
    trip_chat_disabled = "TRIP_CHAT_DISABLED"
    trip_invite_user = "TRIP_INVITE_USER"


class OrgHotelChainPref(BaseModel):
    chain_code: str | None = Field(None, alias="chainCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")


class OrgHotelChainRoomPref(BaseModel):
    chain_code: str | None = Field(None, alias="chainCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")
    rate_code: str | None = Field(None, alias="rateCode")


class OrgIntegrationType(Enum):
    expensify = "EXPENSIFY"


class OrgLoyaltyProgram(BaseModel):
    id: int | None = None
    idx: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    number: str | None = None
    org_id: int | None = Field(None, alias="orgId")


class OrgProject(BaseModel):
    hidden: bool | None = None
    id: int | None = None
    name: str | None = None


class OrgRateCode(BaseModel):
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    rate_code_id: int | None = Field(None, alias="rateCodeId")


class OrgRateCodeText(BaseModel):
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    text: str | None = None


class OrgSettings(BaseModel):
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    config: list[str] = Field(default_factory=list)
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")


class OrgType(Enum):
    agency = "AGENCY"
    community = "COMMUNITY"
    corporate = "CORPORATE"
    supplier = "SUPPLIER"


class OrgUserField(BaseModel):
    field_id: int | None = Field(None, alias="fieldId")
    field_value_id: int | None = Field(None, alias="fieldValueId")
    id: int | None = None
    nms: int | None = None
    org_user_id: int | None = Field(None, alias="orgUserId")
    remark: str | None = None
    value: str | None = None


class OrgUserRole(Enum):
    guest = "Guest"
    user = "User"
    booker = "Booker"
    manager = "Manager"


class OrgUserStatus(Enum):
    accepted = "Accepted"
    suspended = "Suspended"


class OrgUserUpdateEntryData(BaseModel):
    business_address: AddressLocation | None = Field(None, alias="businessAddress")
    business_phone_number: str | None = Field(None, alias="businessPhoneNumber")
    position: str | None = None
    role: OrgUserRole | None = None


class OriginDestination(BaseModel):
    airline: str | None = None
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    segments: list[str] = Field(default_factory=list)
    stops: list[str] = Field(default_factory=list)


class OriginDestinationRequest(BaseModel):
    arrival_airport: str | None = Field(None, alias="arrivalAirport")
    departure_airport: str | None = Field(None, alias="departureAirport")
    departure_date: date | None = Field(None, alias="departureDate")


class OtaRatePlanType(Enum):
    association = "ASSOCIATION"
    club_concierge = "CLUB_CONCIERGE"
    convention = "CONVENTION"
    corporate = "CORPORATE"
    day_rate = "DAY_RATE"
    distressed_inventory = "DISTRESSED_INVENTORY"
    family_plan = "FAMILY_PLAN"
    government = "GOVERNMENT"
    military = "MILITARY"
    negotiated = "NEGOTIATED"
    package = "PACKAGE"
    promotional = "PROMOTIONAL"
    regular_rack = "REGULAR_RACK"
    senior_citizen = "SENIOR_CITIZEN"
    tour_wholesale = "TOUR_WHOLESALE"
    travel_industry = "TRAVEL_INDUSTRY"
    weekend = "WEEKEND"
    last_room_available = "LAST_ROOM_AVAILABLE"
    non_last_room_available = "NON_LAST_ROOM_AVAILABLE"
    consortia = "CONSORTIA"
    group = "GROUP"
    contract = "CONTRACT"
    promotional_package_tour = "PROMOTIONAL_PACKAGE_TOUR"
    published = "PUBLISHED"
    net = "NET"
    multi_day_package = "MULTI_DAY_PACKAGE"
    weekly = "WEEKLY"
    monthly = "MONTHLY"
    standard_redemption_rate = "STANDARD_REDEMPTION_RATE"
    discount_redemption_rate = "DISCOUNT_REDEMPTION_RATE"


class OutOfPolicy(BaseModel):
    id: int | None = None
    message: str | None = None


class PassengerEntry(BaseModel):
    offer_item_id: str | None = Field(None, alias="offerItemId")
    ptc: str | None = None
    ref: str | None = None


class PassportData(BaseModel):
    dob: AwareOrNaiveDatetime | None = None
    doc_number: str | None = Field(None, alias="docNumber")
    doc_type: str | None = Field(None, alias="docType")
    expiration_date: AwareOrNaiveDatetime | None = Field(None, alias="expirationDate")
    first_name: str | None = Field(None, alias="firstName")
    issue_country: str | None = Field(None, alias="issueCountry")
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    nationality: str | None = None
    suffix: str | None = None


class PciCard(BaseModel):
    id: int | None = None
    missing_fields_flags: int | None = Field(None, alias="missingFieldsFlags")
    name: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    owner_id: int | None = Field(None, alias="ownerId")
    reservation_types: int | None = Field(None, alias="reservationTypes")
    user_id: int | None = Field(None, alias="userId")


class PenaltyType(Enum):
    exchange_before = "exchangeBefore"
    exchange_after = "exchangeAfter"
    refund_before = "refundBefore"
    refund_after = "refundAfter"


class PendingEmailStatus(Enum):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"


class PerformanceEnum(Enum):
    basic = "basic"
    better = "better"
    best = "best"
    n_a = "n/a"


class PlaneType(Enum):
    unknown = "UNKNOWN"
    narrowbody = "NARROWBODY"
    widebody = "WIDEBODY"


class PlatformType(Enum):
    android = "ANDROID"
    desktop = "DESKTOP"
    ios = "IOS"
    none = "NONE"
    web = "WEB"


class PolicyAction(Enum):
    out_of_policy = "OUT_OF_POLICY"
    approve = "APPROVE"
    block = "BLOCK"
    hide = "HIDE"


class PolicyCity(BaseModel):
    code: str | None = None
    country: str | None = None
    id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    radius: float | None = None


class PolicyLookupTable(BaseModel):
    code: str | None = None
    name: str | None = None


class PolicyOptionLeg(BaseModel):
    duration: int | None = None
    flight_class: FlightClassPref | None = Field(None, alias="flightClass")
    pair: str | None = None


class PolicyResult(Enum):
    not_specified = "NOT_SPECIFIED"
    in_policy = "IN_POLICY"
    out_of_policy = "OUT_OF_POLICY"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"
    hidden = "HIDDEN"


class PolicyRuleAction(Enum):
    in_policy = "IN_POLICY"
    out_of_policy = "OUT_OF_POLICY"
    approve = "APPROVE"
    block = "BLOCK"
    hide = "HIDE"


class PolicyRuleResult(BaseModel):
    policy_id: int | None = Field(None, alias="policyId")
    result: PolicyResult | None = None
    rule_id: int | None = Field(None, alias="ruleId")


class PolicyRuleSpecs(Enum):
    car_non_preferred = "car_non_preferred"
    car_has_preference = "car_has_preference"
    car_max_price_per_day = "car_max_price_per_day"
    car_max_fare_type = "car_max_fare_type"
    train_max_od_price = "train_max_od_price"
    train_advanced_purchase = "train_advanced_purchase"
    hotel_non_preferred = "hotel_non_preferred"
    hotel_has_preference = "hotel_has_preference"
    hotel_max_rating = "hotel_max_rating"
    hotel_min_rating = "hotel_min_rating"
    hotel_has_rating = "hotel_has_rating"
    hotel_price_max = "hotel_price_max"
    disable_prepaid = "disable_prepaid"
    hotel_maincitycode_and_price_max = "hotel_maincitycode_and_price_max"
    hotel_budget_cap_cities = "hotel_budget_cap_cities"
    hotel_budget_cap_country = "hotel_budget_cap_country"
    paid_seat = "paid_seat"
    flight_non_preferred = "flight_non_preferred"
    flight_has_preference = "flight_has_preference"
    flight_long_od_price = "flight_long_od_price"
    flight_short_od_price = "flight_short_od_price"
    advanced_purchase = "advanced_purchase"
    flight_class_max = "flight_class_max"
    flight_class_time = "flight_class_time"
    long_flight_class_exception = "long_flight_class_exception"
    flight_fare_type_max = "flight_fare_type_max"
    long_flight_fare_type_exception = "long_flight_fare_type_exception"
    flight_lowest_logical = "flight_lowest_logical"
    flight_refundable_fares = "flight_refundable_fares"
    flight_restricted_fares = "flight_restricted_fares"


class PolicyStatistics(BaseModel):
    cheapest_price: float | None = Field(None, alias="cheapestPrice")
    lowest_logical: float | None = Field(None, alias="lowestLogical")


class PolicyType(Enum):
    org = "ORG"
    travel = "TRAVEL"
    guest = "GUEST"


class PowerDistribution(Enum):
    none = "None"
    all = "All"
    some = "Some"


class PowerType(Enum):
    none = "None"
    usb = "Usb"
    power = "Power"
    usb_power = "UsbPower"
    usb_a = "UsbA"
    usb_power_a = "UsbPowerA"


class PrepareTrainReservationResponse(BaseModel):
    raw_data: dict[str, Any] = Field(alias="rawData", default_factory=dict)
    total_price: float | None = Field(None, alias="totalPrice")


class PriceSummary(BaseModel):
    credit_amount: float | None = Field(None, alias="creditAmount")
    currency: str | None = None
    due_amount: float | None = Field(None, alias="dueAmount")
    fop_flags: int | None = Field(None, alias="fopFlags")
    penalty_amount: float | None = Field(None, alias="penaltyAmount")
    refund_amount: float | None = Field(None, alias="refundAmount")
    taxes_and_fees_amount: float | None = Field(None, alias="taxesAndFeesAmount")
    total_amount: float | None = Field(None, alias="totalAmount")


class PricedFare(BaseModel):
    currency: str | None = None
    flags: int | None = None
    has_limited_options: bool | None = Field(None, alias="hasLimitedOptions")
    has_mixed_cabin: bool | None = Field(None, alias="hasMixedCabin")
    has_multi_tickets: bool | None = Field(None, alias="hasMultiTickets")
    has_special_rate: bool | None = Field(None, alias="hasSpecialRate")
    is_current_fare: bool | None = Field(None, alias="isCurrentFare")
    is_seat_selection_available: bool | None = Field(
        None,
        alias="isSeatSelectionAvailable",
    )
    is_transborder: bool | None = Field(None, alias="isTransborder")
    name: str | None = None
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    penalties: int | None = None
    penalty_id: str | None = Field(None, alias="penaltyId")
    perks: int | None = None
    price: float | None = None
    refs: list[str] = Field(default_factory=list)
    segments: list[FareSegment] = Field(default_factory=list)


class PrimaryFlightStatus(Enum):
    scheduled = "Scheduled"
    proposed = "Proposed"
    in_air = "InAir"
    landed = "Landed"
    cancelled = "Cancelled"
    no_takeoff_info = "NoTakeoffInfo"
    delayed = "Delayed"
    unknown = "Unknown"
    out_gate = "OutGate"
    in_gate = "InGate"
    expected = "Expected"
    past_flight = "PastFlight"


class ProfileUpdateTypes(Enum):
    general = "GENERAL"
    role = "ROLE"
    status = "STATUS"
    address = "ADDRESS"
    email = "EMAIL"
    new_org_user = "NEW_ORG_USER"
    new_user_account = "NEW_USER_ACCOUNT"


class Provider(BaseModel):
    active: bool | None = None
    code: str | None = None
    id: int | None = None
    name: str | None = None
    provider_type: str | None = Field(None, alias="providerType")


class ProviderPnr(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    local_created_on: AwareOrNaiveDatetime | None = Field(None, alias="localCreatedOn")
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    pnr: str | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    time_zone: str | None = Field(None, alias="timeZone")
    trip_board_id: int | None = Field(None, alias="tripBoardId")


class ProviderPnrReport(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    local_created_on: AwareOrNaiveDatetime | None = Field(None, alias="localCreatedOn")
    nms: int | None = None
    org_name: str | None = Field(None, alias="orgName")
    pnr: str | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    time_zone: str | None = Field(None, alias="timeZone")
    trip_board_id: int | None = Field(None, alias="tripBoardId")


class Quality(Enum):
    n_a = "n/a"
    better = "better"
    standard = "standard"


class Localizations(BaseModel):
    elements: list[Localization] = Field(default_factory=list)
    empty: bool | None = None
    first: Localization | None = None
    last: Localization | None = None
    localizations: list[Localization] = Field(default_factory=list)


class Railcard(BaseModel):
    active: bool | None = None
    code: str | None = None
    id: int | None = None
    localizations: list[Localization] | Localizations | None = None
    name: str | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    vendor: str | None = None


class RateCode(BaseModel):
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    code: str | None = None
    description: str | None = None
    id: int | None = None
    is_default: bool | None = Field(None, alias="isDefault")
    org_default: bool | None = Field(None, alias="orgDefault")
    provider_code: str | None = Field(None, alias="providerCode")


class RateCodeInfo(BaseModel):
    code: str | None = None
    description: str | None = None


class ReasonType(Enum):
    policy = "policy"
    preferred = "preferred"


class RefPolicyInfo(BaseModel):
    org_id: int | None = Field(None, alias="orgId")
    policy_rule_results: list[PolicyRuleResult] = Field(
        alias="policyRuleResults",
        default_factory=list,
    )
    ref: str | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class ReportAirlinesByOrg(BaseModel):
    airline_code: str | None = Field(None, alias="airlineCode")
    airline_name: str | None = Field(None, alias="airlineName")
    amount: list[Amount] = Field(default_factory=list)
    segments: int | None = None


class ReportCityPairs(BaseModel):
    arrival_code: str | None = Field(None, alias="arrivalCode")
    current_basic_segments: int | None = Field(None, alias="currentBasicSegments")
    current_economy_segments: int | None = Field(None, alias="currentEconomySegments")
    current_premium_segments: int | None = Field(None, alias="currentPremiumSegments")
    current_segments: int | None = Field(None, alias="currentSegments")
    current_spend: list[Amount] = Field(alias="currentSpend", default_factory=list)
    departure_code: str | None = Field(None, alias="departureCode")
    market_share: float | None = Field(None, alias="marketShare")
    qsi: float | None = None
    total_basic_segments: int | None = Field(None, alias="totalBasicSegments")
    total_economy_segments: int | None = Field(None, alias="totalEconomySegments")
    total_premium_segments: int | None = Field(None, alias="totalPremiumSegments")
    total_segments: int | None = Field(None, alias="totalSegments")
    total_spend: list[Amount] = Field(alias="totalSpend", default_factory=list)


class ReportFlightByCityPair(BaseModel):
    arrival_code: str | None = Field(None, alias="arrivalCode")
    departure_code: str | None = Field(None, alias="departureCode")
    total_segments: int | None = Field(None, alias="totalSegments")
    total_spend: float | None = Field(None, alias="totalSpend")


class ReportFlightByEmployee(BaseModel):
    amount: float | None = None
    segments: int | None = None
    user_id: int | None = Field(None, alias="userId")
    user_name: str | None = Field(None, alias="userName")


class ReportFlightsHotelsInfo(BaseModel):
    budget: float | None = None
    flights_tickets: float | None = Field(None, alias="flightsTickets")
    flights_total_spend: float | None = Field(None, alias="flightsTotalSpend")
    hotels_average_days: float | None = Field(None, alias="hotelsAverageDays")
    hotels_average_rate: float | None = Field(None, alias="hotelsAverageRate")
    hotels_days: int | None = Field(None, alias="hotelsDays")
    hotels_total_spend: float | None = Field(None, alias="hotelsTotalSpend")


class ReportGraphInfo(BaseModel):
    amount_spend: float | None = Field(None, alias="amountSpend")
    budget: float | None = None
    day: date | None = None


class ReportOrganizationSpendInfo(BaseModel):
    total_spend: float | None = Field(None, alias="totalSpend")


class ReportProspectiveCustomer(BaseModel):
    company_name: str | None = Field(None, alias="companyName")
    current_basic_segments: int | None = Field(None, alias="currentBasicSegments")
    current_economy_segments: int | None = Field(None, alias="currentEconomySegments")
    current_premium_segments: int | None = Field(None, alias="currentPremiumSegments")
    current_segments: int | None = Field(None, alias="currentSegments")
    current_spend: float | None = Field(None, alias="currentSpend")
    org_id: int | None = Field(None, alias="orgId")
    total_basic_segments: int | None = Field(None, alias="totalBasicSegments")
    total_economy_segments: int | None = Field(None, alias="totalEconomySegments")
    total_premium_segments: int | None = Field(None, alias="totalPremiumSegments")
    total_segments: int | None = Field(None, alias="totalSegments")
    total_spend: float | None = Field(None, alias="totalSpend")


class ReqItinerarySegment(BaseModel):
    arr: str | None = None
    cabin: int | None = None
    cxr: str | None = None
    date: str | None = None
    dep: str | None = None
    fbc: str | None = None
    fltno: int | None = None
    rbd: str | None = None
    rule_no: str | None = Field(None, alias="ruleNo")


class RequestId(BaseModel):
    pass


class ReservationConsumer(BaseModel):
    dob: date | None = None
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    on_lap_index: int | None = Field(None, alias="onLapIndex")
    user_id: int | None = Field(None, alias="userId")


class ReservationField(BaseModel):
    field_id: int | None = Field(None, alias="fieldId")
    field_value_id: int | None = Field(None, alias="fieldValueId")
    id: int | None = None
    nms: int | None = None
    remark: str | None = None
    reservation_id: int | None = Field(None, alias="reservationId")
    user_id: int | None = Field(None, alias="userId")
    value: str | None = None


class ReservationFlags(Enum):
    can_hold = "CAN_HOLD"
    held = "HELD"
    reprice_required = "REPRICE_REQUIRED"
    passive = "PASSIVE"
    confirmation_is_optional = "CONFIRMATION_IS_OPTIONAL"
    passport_required = "PASSPORT_REQUIRED"
    use_station_names = "USE_STATION_NAMES"
    display_seat_preferences = "DISPLAY_SEAT_PREFERENCES"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"
    pre_process_required = "PRE_PROCESS_REQUIRED"
    partial_cancellation = "PARTIAL_CANCELLATION"
    pay_on_site = "PAY_ON_SITE"


class ReservationMedia(BaseModel):
    media_height: int | None = Field(None, alias="mediaHeight")
    media_url: str | None = Field(None, alias="mediaUrl")
    media_width: int | None = Field(None, alias="mediaWidth")
    thumbnail_height: int | None = Field(None, alias="thumbnailHeight")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    thumbnail_width: int | None = Field(None, alias="thumbnailWidth")


class ReservationStatus(Enum):
    pending = "PENDING"
    booked = "BOOKED"
    pending_changes = "PENDING_CHANGES"
    pending_cancel = "PENDING_CANCEL"
    canceled = "CANCELED"
    unavailable = "UNAVAILABLE"


class ReservationType(Enum):
    car = "Car"
    flight = "Flight"
    hotel = "Hotel"
    misc = "Misc"
    train = "Train"


class ResourceNotificationResponse(BaseModel):
    id: int | None = None
    name: str | None = None
    nms: int | None = None


class ResourceType(Enum):
    agency_settings = "AGENCY_SETTINGS"
    notification = "NOTIFICATION"
    notification_center = "NOTIFICATION_CENTER"
    msg = "MSG"
    org = "ORG"
    post = "POST"
    trip = "TRIP"
    trip_board = "TRIP_BOARD"
    trip_board_ref = "TRIP_BOARD_REF"
    user = "USER"
    user_account = "USER_ACCOUNT"
    wall = "WALL"


class RespItineraryAmenityRef(BaseModel):
    aircraft: str | None = None
    beverage: str | None = None
    entertainment: str | None = None
    fresh_food: str | None = Field(None, alias="freshFood")
    layout: str | None = None
    power: str | None = None
    seat: str | None = None
    wifi: str | None = None


class RespItineraryErrors(BaseModel):
    messages: list[str] = Field(default_factory=list)
    unmatched_fares: list[str] = Field(alias="unmatchedFares", default_factory=list)
    unmatched_segments: list[str] = Field(
        alias="unmatchedSegments",
        default_factory=list,
    )


class RespItinerarySegment(BaseModel):
    amenity: RespItineraryAmenityRef | None = None
    boarding_priority: list[list[str]] = Field(
        alias="boardingPriority",
        default_factory=list,
    )
    carry_on_bag: list[list[str]] = Field(alias="carryOnBag", default_factory=list)
    check_in_priority: list[list[str]] = Field(
        alias="checkInPriority",
        default_factory=list,
    )
    checked_bag: list[list[str]] = Field(alias="checkedBag", default_factory=list)
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    id: str | None = None
    lounge_access: list[list[str]] = Field(alias="loungeAccess", default_factory=list)
    overnight: Exists | None = None
    same_day_change: list[list[str]] = Field(
        alias="sameDayChange",
        default_factory=list,
    )
    seat_selection: list[list[str]] = Field(alias="seatSelection", default_factory=list)
    upas: list[str] = Field(default_factory=list)
    upgrade_eligibility: list[list[str]] = Field(
        alias="upgradeEligibility",
        default_factory=list,
    )


class ResponseStatus(Enum):
    ok = "OK"
    failed = "Failed"


class RestoreSession(BaseModel):
    restored: list[str] = Field(default_factory=list)


class ReviewFlightsRequest(BaseModel):
    refs: list[str] = Field(default_factory=list)


class RewardProgram(BaseModel):
    active: bool | None = None
    code: str | None = None
    ext_type: ReservationType | None = Field(None, alias="extType")
    id: int | None = None
    name: str | None = None
    type: ReservationType | None = None


class RewardProgramInfo(BaseModel):
    number: str | None = None
    vendor: str | None = None


class RewardProgramListResponse(BaseModel):
    code: int | None = None
    data: list[RewardProgram] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class RewardProgramResponse(BaseModel):
    code: int | None = None
    data: RewardProgram | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Role(BaseModel):
    code: str | None = None
    id: int | None = None
    name: str | None = None


class RoomOccupancy(BaseModel):
    adults: int | None = None
    children_ages: list[int] = Field(alias="childrenAges", default_factory=list)
    rooms: int | None = None


class RoomPerks(Enum):
    early_checkin = "EARLY_CHECKIN"
    late_checkout = "LATE_CHECKOUT"
    upgradable = "UPGRADABLE"
    resort_credit_available = "RESORT_CREDIT_AVAILABLE"
    breakfast_included = "BREAKFAST_INCLUDED"
    third_night_free = "THIRD_NIGHT_FREE"
    complimentary_airport_transfer = "COMPLIMENTARY_AIRPORT_TRANSFER"
    welcome_drink_included = "WELCOME_DRINK_INCLUDED"
    spa_credits_included = "SPA_CREDITS_INCLUDED"
    parking = "PARKING"


class RoomRateCode(BaseModel):
    code: str | None = None
    description: str | None = None


class SabreCabinClass(BaseModel):
    airline: str | None = None
    cabin_class: CabinClass | None = Field(None, alias="cabinClass")
    cabin_class_override: CabinClass | None = Field(None, alias="cabinClassOverride")
    description: str | None = None
    id: int | None = None
    service_class: str | None = Field(None, alias="serviceClass")


class SabreCommand(BaseModel):
    command: str | None = None
    conversation_id: str | None = Field(None, alias="conversationId")
    token: str | None = None


class SabreProfileType(Enum):
    tvl = "TVL"
    crp = "CRP"


class SabreRecordLocator(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_profile_id: str | None = Field(None, alias="agencyProfileId")
    command_remarks: bool | None = Field(None, alias="commandRemarks")
    corporate_profile_id: str | None = Field(None, alias="corporateProfileId")
    creation_timestamp: AwareOrNaiveDatetime | None = Field(
        None,
        alias="creationTimestamp",
    )
    dk_numbers: list[str] = Field(alias="dkNumbers", default_factory=list)
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    hash: str | None = None
    id: int | None = None
    last_updated_timestamp: AwareOrNaiveDatetime | None = Field(
        None,
        alias="lastUpdatedTimestamp",
    )
    pnr: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    total_price: float | None = Field(None, alias="totalPrice")
    traveler_profile_ids: list[str] = Field(
        alias="travelerProfileIds",
        default_factory=list,
    )
    trip_id: int | None = Field(None, alias="tripId")
    update_requested: AwareOrNaiveDatetime | None = Field(None, alias="updateRequested")


class SabreRecordLocatorTime(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    update_time: AwareOrNaiveDatetime | None = Field(None, alias="updateTime")


class SabreUserProfile(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_hash: str | None = Field(None, alias="profileHash")
    profile_id: str | None = Field(None, alias="profileId")
    user_id: int | None = Field(None, alias="userId")


class SameDayChange(BaseModel):
    application: OptSvcApplication | None = None
    assessment: Assessment | None = None
    code: str | None = None
    commercial_name: str | None = Field(None, alias="commercialName")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fee: Fee | None = None
    group_code: str | None = Field(None, alias="groupCode")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class ScheduleStatus(Enum):
    on_time = "OnTime"
    early = "Early"
    delayed = "Delayed"


class SearchCarRequest(BaseModel):
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    location_refs: list[str] = Field(alias="locationRefs", default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    reservation_id: int | None = Field(None, alias="reservationId")
    trip_id: int | None = Field(None, alias="tripId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SearchCarResponse(BaseModel):
    cars: list[CarOffer] = Field(default_factory=list)
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    locations: dict[str, CarLocation] = Field(default_factory=dict)
    org_id: int | None = Field(None, alias="orgId")
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SearchCarResponseResponse(BaseModel):
    code: int | None = None
    data: SearchCarResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SearchCategory(Enum):
    flight = "FLIGHT"
    hotel = "HOTEL"
    car = "CAR"
    train = "TRAIN"
    seat = "SEAT"


class SearchFlightsRequest(BaseModel):
    inf: int | None = None
    ods: list[OriginDestinationRequest] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    refs: list[str] = Field(default_factory=list)
    reservation_ids: list[int] = Field(alias="reservationIds", default_factory=list)
    trip_id: int | None = Field(None, alias="tripId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SearchFlightsRequestType(Enum):
    one_way = "ONE_WAY"
    itinerary = "ITINERARY"
    itinerary_resume = "ITINERARY_RESUME"
    outer = "OUTER"


class SearchHotelsRequest(BaseModel):
    checkin_date: date | None = Field(None, alias="checkinDate")
    checkout_date: date | None = Field(None, alias="checkoutDate")
    currency: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    org_id: int | None = Field(None, alias="orgId")
    radius: float | None = None
    reservation_id: int | None = Field(None, alias="reservationId")
    trip_id: int | None = Field(None, alias="tripId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SeatFlags(Enum):
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class SeatFlatness(Enum):
    none = "None"
    angle_flat = "AngleFlat"
    full_flat = "FullFlat"
    not_flat = "NotFlat"


class SeatLegRoom(Enum):
    none = "None"
    less = "Less"
    more = "More"
    standard = "Standard"


class SeatMapColumnInfo(BaseModel):
    aisle: bool | None = None
    center: bool | None = None
    column: str | None = None
    window: bool | None = None


class SeatMapDeck(Enum):
    lower = "LOWER"
    upper = "UPPER"
    main = "MAIN"


class SeatMapSegmentSpecs(Enum):
    southwest = "SOUTHWEST"
    copa = "COPA"


class SeatMapSegmentStatus(Enum):
    available = "AVAILABLE"
    disabled = "DISABLED"
    disallowed = "DISALLOWED"
    open_seating = "OPEN_SEATING"
    unavailable = "UNAVAILABLE"


class SeatPreference(Enum):
    window = "window"
    aisle = "aisle"


class SeatSelection(BaseModel):
    application: OptSvcApplication | None = None
    assessment: Assessment | None = None
    code: str | None = None
    commercial_name: str | None = Field(None, alias="commercialName")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fee: Fee | None = None
    group_code: str | None = Field(None, alias="groupCode")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class SeatStatus(Enum):
    available = "AVAILABLE"
    added_fee = "ADDED_FEE"
    unavailable = "UNAVAILABLE"
    no_seat = "NO_SEAT"


class SeatType(Enum):
    none = "None"
    above_average_legroom = "AboveAverageLegroom"
    angle_flat_seat = "AngleFlatSeat"
    below_average_legroom = "BelowAverageLegroom"
    cradle_recliner = "CradleRecliner"
    full_flat_pod = "FullFlatPod"
    full_flat_seat = "FullFlatSeat"
    middle_seat_free = "MiddleSeatFree"
    private_suite = "PrivateSuite"
    recliner_seat = "ReclinerSeat"
    skycouch = "Skycouch"
    standard_legroom = "StandardLegroom"
    unknown = "Unknown"


class SeatTypeSpecs(Enum):
    default_free = "DEFAULT_FREE"
    default_paid = "DEFAULT_PAID"
    aa_default_free_seat = "AA_DEFAULT_FREE_SEAT"
    aa_preferred = "AA_PREFERRED"
    aa_main_cabin_extra = "AA_MAIN_CABIN_EXTRA"
    ua_default_free_seat = "UA_DEFAULT_FREE_SEAT"
    uad_default_free_seat = "UAD_DEFAULT_FREE_SEAT"
    ua_economy = "UA_ECONOMY"
    uad_economy = "UAD_ECONOMY"
    ua_economy_plus = "UA_ECONOMY_PLUS"
    ua_economy_plus_limited_recline = "UA_ECONOMY_PLUS_LIMITED_RECLINE"
    ua_business = "UA_BUSINESS"
    uad_business = "UAD_BUSINESS"
    ua_first = "UA_FIRST"
    uad_first = "UAD_FIRST"


class SecondaryFlightStatus(Enum):
    original = "Original"
    diverted = "Diverted"
    recovery = "Recovery"


class Segment(BaseModel):
    airline: str | None = None
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    depart_time: AwareOrNaiveDatetime | None = Field(None, alias="departTime")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    flight_number: str | None = Field(None, alias="flightNumber")
    operating_airline: str | None = Field(None, alias="operatingAirline")
    segment_key: str | None = Field(None, alias="segmentKey")


class SegmentPerks(Enum):
    free_seat_selection = "FREE_SEAT_SELECTION"
    preferred_seat = "PREFERRED_SEAT"
    fully_lie_flat_seat = "FULLY_LIE_FLAT_SEAT"
    complimentary_premium_beverage = "COMPLIMENTARY_PREMIUM_BEVERAGE"
    free_premium_beverages = "FREE_PREMIUM_BEVERAGES"
    complimentary_meal = "COMPLIMENTARY_MEAL"
    premium_meal_snack = "PREMIUM_MEAL_SNACK"
    wifi_available = "WIFI_AVAILABLE"
    free_wifi = "FREE_WIFI"
    leather_seat = "LEATHER_SEAT"


class SegmentPerksSpecs(Enum):
    free_seat_selection = "FREE_SEAT_SELECTION"
    preferred_seat = "PREFERRED_SEAT"
    fully_lie_flat_seat = "FULLY_LIE_FLAT_SEAT"
    complimentary_premium_beverage = "COMPLIMENTARY_PREMIUM_BEVERAGE"
    free_premium_beverages = "FREE_PREMIUM_BEVERAGES"
    complimentary_meal = "COMPLIMENTARY_MEAL"
    premium_meal_snack = "PREMIUM_MEAL_SNACK"
    wifi_available = "WIFI_AVAILABLE"
    free_wifi = "FREE_WIFI"
    leather_seat = "LEATHER_SEAT"


class SelectionTypeEnum(Enum):
    n_a = "n/a"
    on_demand = "on-demand"
    live = "live"
    loop = "loop"


class ServiceFee(BaseModel):
    currency: str | None = None
    fop_label: str | None = Field(None, alias="fopLabel")
    fop_record: str | None = Field(None, alias="fopRecord")
    total: float | None = None


class SettlementType(Enum):
    credit = "Credit"
    debit = "Debit"
    reservation = "Reservation"


class ShopFlightsRequest(BaseModel):
    ods: list[OriginDestinationRequest] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)


class SignUpCampaign(BaseModel):
    cid: str | None = None
    created_at: AwareOrNaiveDatetime | None = Field(None, alias="createdAt")
    email: str | None = None
    id: int | None = None


class SignUpUserRequest(BaseModel):
    campaign_code: str | None = Field(None, alias="campaignCode")
    cid: str | None = None
    email: str | None = None
    recaptcha: str | None = None


class Size(BaseModel):
    application: Application | None = None
    cm: str | None = None
    in_: str | None = Field(None, alias="in")


class StatBudget(BaseModel):
    accrual_term: int | None = Field(None, alias="accrualTerm")
    amount: float | None = None
    end_date: date | None = Field(None, alias="endDate")
    start_date: date | None = Field(None, alias="startDate")


class StorageType(Enum):
    ro = "RO"
    rw = "RW"


class StringListResponse(BaseModel):
    code: int | None = None
    data: list[str] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class StringResponse(BaseModel):
    code: int | None = None
    data: str | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SupplierInquiry(BaseModel):
    active: bool | None = None
    company: str | None = None
    email: str | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")


class SupplierType(Enum):
    airline = "airline"


class Task(BaseModel):
    active: bool | None = None
    executed_by: str | None = Field(None, alias="executedBy")
    executed_in: int | None = Field(None, alias="executedIn")
    executed_on: int | None = Field(None, alias="executedOn")
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    period_ms: int | None = Field(None, alias="periodMs")
    running: bool | None = None


class TermsAndConditions(BaseModel):
    label: str | None = None
    url: str | None = None


class TfsAirline(BaseModel):
    active: bool | None = None
    iata: str | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    synced_on: int | None = Field(None, alias="syncedOn")
    tf_code: str | None = Field(None, alias="tfCode")


class TfsAirport(BaseModel):
    active: bool | None = None
    city: str | None = None
    city_code: str | None = Field(None, alias="cityCode")
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    iata: str | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    synced_on: int | None = Field(None, alias="syncedOn")


class TfsCity(BaseModel):
    active: bool | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    iata: str | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    synced_on: int | None = Field(None, alias="syncedOn")


class TfsSupplierRoute(BaseModel):
    active: bool | None = None
    destination: str | None = None
    id: int | None = None
    nms: int | None = None
    origin: str | None = None
    supplier: str | None = None
    synced_on: int | None = Field(None, alias="syncedOn")


class TicketFlags(Enum):
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    has_special_rate = "HAS_SPECIAL_RATE"
    mixed_cabin = "MIXED_CABIN"
    limited_options = "LIMITED_OPTIONS"
    multi_tickets = "MULTI_TICKETS"
    transborder = "TRANSBORDER"
    display_airline_status = "DISPLAY_AIRLINE_STATUS"
    airline_status_preferred = "AIRLINE_STATUS_PREFERRED"
    seat_selection_available = "SEAT_SELECTION_AVAILABLE"
    current_fare = "CURRENT_FARE"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class TicketMedia(BaseModel):
    bucket: str | None = None
    code: str | None = None
    id: int | None = None
    key: str | None = None
    nms: int | None = None
    url: str | None = None


class TicketPenalties(Enum):
    no_seat_selection = "NO_SEAT_SELECTION"
    no_changes = "NO_CHANGES"
    no_refunds = "NO_REFUNDS"
    no_upgrades = "NO_UPGRADES"
    no_lounge_access = "NO_LOUNGE_ACCESS"
    no_ffp = "NO_FFP"
    no_checked_bags = "NO_CHECKED_BAGS"
    board_last = "BOARD_LAST"
    no_overhead_bin = "NO_OVERHEAD_BIN"


class TicketPenaltiesSpecs(Enum):
    aa_basic = "AA_BASIC"
    ac_basic = "AC_BASIC"
    ua_basic = "UA_BASIC"
    uad_basic = "UAD_BASIC"


class TicketPerks(Enum):
    checked_bag_for_a_fee = "CHECKED_BAG_FOR_A_FEE"
    one_free_checked_bag = "ONE_FREE_CHECKED_BAG"
    two_free_checked_bag = "TWO_FREE_CHECKED_BAG"
    changes_for_a_fee = "CHANGES_FOR_A_FEE"
    free_changes = "FREE_CHANGES"
    changes_for_a_discounted_fee = "CHANGES_FOR_A_DISCOUNTED_FEE"
    free_same_day_standby = "FREE_SAME_DAY_STANDBY"
    priority_boarding = "PRIORITY_BOARDING"
    priority_checkin = "PRIORITY_CHECKIN"
    lounge_access = "LOUNGE_ACCESS"
    priority_security = "PRIORITY_SECURITY"
    same_day_changes = "SAME_DAY_CHANGES"
    refundable = "REFUNDABLE"
    reusable_funds = "REUSABLE_FUNDS"
    carbon_offsetting = "CARBON_OFFSETTING"
    carbon_neutral = "CARBON_NEUTRAL"


class TicketPerksSpecs(Enum):
    checked_bag_for_a_fee = "CHECKED_BAG_FOR_A_FEE"
    one_free_checked_bag = "ONE_FREE_CHECKED_BAG"
    two_free_checked_bag = "TWO_FREE_CHECKED_BAG"
    changes_for_a_fee = "CHANGES_FOR_A_FEE"
    free_changes = "FREE_CHANGES"
    changes_for_a_discounted_fee = "CHANGES_FOR_A_DISCOUNTED_FEE"
    free_same_day_standby = "FREE_SAME_DAY_STANDBY"
    priority_boarding = "PRIORITY_BOARDING"
    priority_checkin = "PRIORITY_CHECKIN"
    lounge_access = "LOUNGE_ACCESS"
    priority_security = "PRIORITY_SECURITY"


class Unit(BaseModel):
    date_based: bool | None = Field(None, alias="dateBased")
    duration_estimated: bool | None = Field(None, alias="durationEstimated")
    time_based: bool | None = Field(None, alias="timeBased")


class UtcOffset(BaseModel):
    nano: int | None = None
    negative: bool | None = None
    positive: bool | None = None
    seconds: int | None = None
    units: list[Unit] = Field(default_factory=list)
    zero: bool | None = None


class TimeZone(BaseModel):
    abbrev: str | None = None
    id: int | None = None
    is_dst: bool | None = Field(None, alias="isDst")
    name: str | None = None
    utc_offset: UtcOffset | None = Field(None, alias="utcOffset")


class TimeZoneListResponse(BaseModel):
    code: int | None = None
    data: list[TimeZone] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class TopicType(Enum):
    profile = "PROFILE"


class TotalMaxWeight(BaseModel):
    application: Application | None = None
    kg: str | None = None
    lb: str | None = None


class TrString(BaseModel):
    name: str | None = None
    value: str | None = None


class TrStrings(BaseModel):
    strings: list[TrString] = Field(default_factory=list)


class TrainCarrier(BaseModel):
    code: str | None = None
    codes: dict[str, str] = Field(default_factory=dict)
    id: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    name: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")


class TrainFareSegment(BaseModel):
    applied_discount_id: str | None = Field(None, alias="appliedDiscountId")
    comfort_class_id: str | None = Field(None, alias="comfortClassId")
    fare_condition_id: str | None = Field(None, alias="fareConditionId")
    fare_condition_ids: list[str] = Field(
        alias="fareConditionIds",
        default_factory=list,
    )
    fare_name: str | None = Field(None, alias="fareName")
    perks: int | None = None
    quantity: int | None = None
    segment_id: str | None = Field(None, alias="segmentId")


class TrainOriginDestination(BaseModel):
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_station_name: str | None = Field(None, alias="arrivalStationName")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    carrier_code: str | None = Field(None, alias="carrierCode")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_station_name: str | None = Field(None, alias="departureStationName")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    segments: list[str] = Field(default_factory=list)
    stops: list[str] = Field(default_factory=list)


class TrainOriginDestinationRequest(BaseModel):
    arrival_date: date | None = Field(None, alias="arrivalDate")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: str | None = Field(None, alias="arrivalTime")
    departure_date: date | None = Field(None, alias="departureDate")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: str | None = Field(None, alias="departureTime")


class TrainPricedFare(BaseModel):
    allowed_arrival_stations: list[str] = Field(
        alias="allowedArrivalStations",
        default_factory=list,
    )
    allowed_departure_stations: list[str] = Field(
        alias="allowedDepartureStations",
        default_factory=list,
    )
    currency: str | None = None
    discount_amount: float | None = Field(None, alias="discountAmount")
    fare_restriction: str | None = Field(None, alias="fareRestriction")
    flags: int | None = None
    has_mixed_cabin: bool | None = Field(None, alias="hasMixedCabin")
    has_rate_code: bool | None = Field(None, alias="hasRateCode")
    has_travelcard: bool | None = Field(None, alias="hasTravelcard")
    is_current_fare: bool | None = Field(None, alias="isCurrentFare")
    is_transborder: bool | None = Field(None, alias="isTransborder")
    name: str | None = None
    open_return: bool | None = Field(None, alias="openReturn")
    open_return_until: date | None = Field(None, alias="openReturnUntil")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    perks: int | None = None
    price: float | None = None
    railcard_ids: list[int] = Field(alias="railcardIds", default_factory=list)
    refs: list[str] = Field(default_factory=list)
    route_restriction: str | None = Field(None, alias="routeRestriction")
    segments: list[TrainFareSegment] = Field(default_factory=list)


class TrainReservationTicket(BaseModel):
    ticket_number: str | None = Field(None, alias="ticketNumber")
    ticket_url: str | None = Field(None, alias="ticketUrl")


class TrainSeat(BaseModel):
    car: str | None = None
    consumer_index: int | None = Field(None, alias="consumerIndex")
    seat: str | None = None


class TrainSeatPreferenceFlags(Enum):
    backward_facing_direction = "BACKWARD_FACING_DIRECTION"
    forward_facing_direction = "FORWARD_FACING_DIRECTION"
    airline_style_direction = "AIRLINE_STYLE_DIRECTION"
    window_position = "WINDOW_POSITION"
    aisle_position = "AISLE_POSITION"
    individual_position = "INDIVIDUAL_POSITION"
    quiet_coach_type = "QUIET_COACH_TYPE"
    standard_coach_type = "STANDARD_COACH_TYPE"
    phone_zone_coach_type = "PHONE_ZONE_COACH_TYPE"
    near_luggage_rack = "NEAR_LUGGAGE_RACK"
    table_seat = "TABLE_SEAT"
    near_toilet = "NEAR_TOILET"
    power_socket = "POWER_SOCKET"
    outward = "OUTWARD"
    inward = "INWARD"
    six_seats_compartment = "SIX_SEATS_COMPARTMENT"
    side_by_side_seats = "SIDE_BY_SIDE_SEATS"
    four_seater_booth = "FOUR_SEATER_BOOTH"
    family = "FAMILY"
    upstairs = "UPSTAIRS"
    downstairs = "DOWNSTAIRS"
    close_to = "CLOSE_TO"
    opposite = "OPPOSITE"
    solo_seat = "SOLO_SEAT"
    facing_direction = "FACING_DIRECTION"


class TrainSeatReservabilityType(Enum):
    disabled = "DISABLED"
    optional = "OPTIONAL"
    mandatory = "MANDATORY"


class TrainSegmentInfo(BaseModel):
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    available_quantity: int | None = Field(None, alias="availableQuantity")
    carrier_code: str | None = Field(None, alias="carrierCode")
    class_code: str | None = Field(None, alias="classCode")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    equipment: str | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_rules: str | None = Field(None, alias="fareRules")
    fare_type: FareType | None = Field(None, alias="fareType")
    logo: str | None = None
    perks: int | None = None
    train_name: str | None = Field(None, alias="trainName")
    train_number: str | None = Field(None, alias="trainNumber")


class TrainSegmentPerks(Enum):
    wifi = "WIFI"
    quiet_car = "QUIET_CAR"
    checked_baggage = "CHECKED_BAGGAGE"
    lounge = "LOUNGE"
    snack_car = "SNACK_CAR"
    traditional_dining = "TRADITIONAL_DINING"
    cafe = "CAFE"
    tray_meal = "TRAY_MEAL"
    seat_assignment = "SEAT_ASSIGNMENT"
    wheelchair_ramp = "WHEELCHAIR_RAMP"


class TrainStation(BaseModel):
    active: bool | None = None
    city: str | None = None
    code: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    flags: int | None = None
    group_code: str | None = Field(None, alias="groupCode")
    id: int | None = None
    label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    searchable: bool | None = None
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    vendor_codes: list[str] = Field(alias="vendorCodes", default_factory=list)


class TrainStationFlags(Enum):
    multi_city = "MULTI_CITY"
    open_return = "OPEN_RETURN"
    time_required = "TIME_REQUIRED"
    has_railcards = "HAS_RAILCARDS"
    use_station_names = "USE_STATION_NAMES"


class TrainStationGroup(BaseModel):
    city: str | None = None
    code: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    flags: int | None = None
    id: int | None = None
    label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")


class TrainStationGroupListResponse(BaseModel):
    code: int | None = None
    data: list[TrainStationGroup] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class TrainTicketFlags(Enum):
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    has_rate_code = "HAS_RATE_CODE"
    mixed_cabin = "MIXED_CABIN"
    transborder = "TRANSBORDER"
    current_fare = "CURRENT_FARE"
    has_travelcard = "HAS_TRAVELCARD"
    open_return = "OPEN_RETURN"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class TrainTransportMode(Enum):
    train = "TRAIN"
    bus = "BUS"
    ferry = "FERRY"
    walk = "WALK"
    metro = "METRO"
    tram = "TRAM"
    other = "OTHER"


class TrainlineRewardProgram(BaseModel):
    id: int | None = None
    internal_id: str | None = Field(None, alias="internalId")
    reward_program_id: int | None = Field(None, alias="rewardProgramId")


class TravelPolicyParameterType(Enum):
    int = "INT"
    decimal = "DECIMAL"
    enum = "ENUM"
    bool = "BOOL"
    string = "STRING"
    list = "LIST"
    lookup = "LOOKUP"


class TravelerProfile(BaseModel):
    name: str | None = None
    profile_id: str | None = Field(None, alias="profileId")
    user_id: int | None = Field(None, alias="userId")


class TripBoardActionTrail(BaseModel):
    action: str | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    request_headers: dict[str, str] = Field(
        alias="requestHeaders",
        default_factory=dict,
    )
    request_method: str | None = Field(None, alias="requestMethod")
    request_uri: str | None = Field(None, alias="requestUri")
    resource_id: int | None = Field(None, alias="resourceId")
    resource_type: ResourceType | None = Field(None, alias="resourceType")
    time: int | None = None
    user_id: int | None = Field(None, alias="userId")


class TripBoardFee(BaseModel):
    booker_id: int | None = Field(None, alias="bookerId")
    currency: str | None = None
    fop_card_id: int | None = Field(None, alias="fopCardId")
    fop_label: str | None = Field(None, alias="fopLabel")
    fop_record: str | None = Field(None, alias="fopRecord")
    id: int | None = None
    locator: str | None = None
    messages: list[str] = Field(default_factory=list)
    nms: int | None = None
    total: float | None = None
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    trip_id: int | None = Field(None, alias="tripId")
    ui_flags: int | None = Field(None, alias="uiFlags")


class TripBoardFlags(Enum):
    require_approval = "REQUIRE_APPROVAL"
    allow_user_invites = "ALLOW_USER_INVITES"
    allow_user_bookings = "ALLOW_USER_BOOKINGS"
    cvv_required = "CVV_REQUIRED"
    approved = "APPROVED"


class TripBoardFop(BaseModel):
    amount: float | None = None
    card_id: int | None = Field(None, alias="cardId")
    credit_id: int | None = Field(None, alias="creditId")
    description: str | None = None
    id: int | None = None
    label: str | None = None
    nms: int | None = None
    on_account: bool | None = Field(None, alias="onAccount")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    trip_board_ref_id: int | None = Field(None, alias="tripBoardRefId")
    trip_id: int | None = Field(None, alias="tripId")


class TripBoardProcessingFlags(Enum):
    reprice = "REPRICE"
    hold = "HOLD"
    commit = "COMMIT"
    sync = "SYNC"
    cancel = "CANCEL"


class TripBoardRefMessageType(Enum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"


class TripBoardStatus(Enum):
    discarded = "DISCARDED"
    draft = "DRAFT"
    pending = "PENDING"
    processing = "PROCESSING"
    confirmed = "CONFIRMED"


class TripSummaryLine(BaseModel):
    date: AwareOrNaiveDatetime | None = None
    id: int | None = None
    status: ReservationStatus | None = None
    type: ReservationType | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class TspmOrgProfile(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_hash: str | None = Field(None, alias="profileHash")
    profile_id: str | None = Field(None, alias="profileId")
    storage_type: StorageType | None = Field(None, alias="storageType")


class TspmOrgProfileListResponse(BaseModel):
    code: int | None = None
    data: list[TspmOrgProfile] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class TspmOrgProfileResponse(BaseModel):
    code: int | None = None
    data: TspmOrgProfile | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class TspmUserProfile(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_hash: str | None = Field(None, alias="profileHash")
    profile_id: str | None = Field(None, alias="profileId")
    user_id: int | None = Field(None, alias="userId")


class TypeEnum(Enum):
    chance = "chance"
    n_a = "n/a"
    none = "none"
    smartphone_data_roam = "smartphone_data_roam"
    wifi = "wifi"


class UPAPhoto(BaseModel):
    caption: str | None = None
    id: str | None = None
    large_url: str | None = Field(None, alias="largeUrl")
    medium_url: str | None = Field(None, alias="mediumUrl")
    thumb_url: str | None = Field(None, alias="thumbUrl")


class UTA(BaseModel):
    assessment: str | None = None
    categories: list[str] = Field(default_factory=list)
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fees: list[FlightAttributeFee] = Field(default_factory=list)
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")


class UiFlags(Enum):
    add_enabled = "ADD_ENABLED"
    delete_enabled = "DELETE_ENABLED"
    edit_enabled = "EDIT_ENABLED"
    action_1_enabled = "ACTION_1_ENABLED"
    action_2_enabled = "ACTION_2_ENABLED"
    action_3_enabled = "ACTION_3_ENABLED"
    action_4_enabled = "ACTION_4_ENABLED"
    action_5_enabled = "ACTION_5_ENABLED"
    action_6_enabled = "ACTION_6_ENABLED"
    action_7_enabled = "ACTION_7_ENABLED"
    action_8_enabled = "ACTION_8_ENABLED"
    view_admin = "VIEW_ADMIN"
    view_agent = "VIEW_AGENT"


class UpaCommon(BaseModel):
    caption: str | None = None
    embed_url: str | None = Field(None, alias="embedUrl")
    large_url: str | None = Field(None, alias="largeUrl")
    medium_square_url: str | None = Field(None, alias="mediumSquareUrl")
    thumb_url: str | None = Field(None, alias="thumbUrl")
    url: str | None = None


class UpgradeEligibility(BaseModel):
    application: OptSvcApplication | None = None
    assessment: Assessment | None = None
    code: str | None = None
    commercial_name: str | None = Field(None, alias="commercialName")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fee: Fee | None = None
    group_code: str | None = Field(None, alias="groupCode")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class UserAccountEmail(BaseModel):
    email: str | None = None
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    status: EmailStatus | None = None
    user_id: int | None = Field(None, alias="userId")


class UserAccountEmailListResponse(BaseModel):
    code: int | None = None
    data: list[UserAccountEmail] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class UserAccountEmailResponse(BaseModel):
    code: int | None = None
    data: UserAccountEmail | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class UserAccountFlags(Enum):
    marketing_opt_in = "MARKETING_OPT_IN"


class UserAccountKycStatus(Enum):
    passed = "PASSED"
    suspicious = "SUSPICIOUS"
    failed = "FAILED"


class UserAccountPreferences(BaseModel):
    airport_code: str | None = Field(None, alias="airportCode")
    currency: str | None = None
    locale: str | None = None
    restrict_ip: bool | None = Field(None, alias="restrictIp")
    seat: SeatPreference | None = None
    ssr: list[str] = Field(default_factory=list)


class UserAccountStatus(Enum):
    active = "Active"
    pending = "Pending"
    locked = "Locked"


class UserAddress(BaseModel):
    address: AddressLocation | None = None
    id: int | None = None
    label: str | None = None


class UserAddressResponse(BaseModel):
    code: int | None = None
    data: UserAddress | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class UserCreationValidationStatusEnum(Enum):
    ok = "OK"
    user_pending = "UserPending"
    user_already_exists = "UserAlreadyExists"


class UserCreditCardType(Enum):
    visa = "VISA"
    americanexpress = "AMERICANEXPRESS"
    mastercard = "MASTERCARD"
    discover = "DISCOVER"
    jcb = "JCB"
    dinersclub = "DINERSCLUB"
    uatp = "UATP"
    unknown = "UNKNOWN"


class UserDocumentPassport(BaseModel):
    country: str | None = None
    expiry: date | None = None
    nationality: str | None = None
    number: str | None = None


class UserDocuments(BaseModel):
    goes: str | None = None
    passport: UserDocumentPassport | None = None
    redress_number: str | None = Field(None, alias="redressNumber")
    tsa: str | None = None


class UserFlags(Enum):
    tsa_precheck = "TSA_PRECHECK"
    driver = "DRIVER"
    adult = "ADULT"


class UserOrgInfo(BaseModel):
    description: str | None = None
    name: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    status: OrgUserStatus | None = None


class UserRewardProgram(BaseModel):
    id: int | None = None
    idx: int | None = None
    number: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    user_id: int | None = Field(None, alias="userId")


class UserRewardProgramListResponse(BaseModel):
    code: int | None = None
    data: list[UserRewardProgram] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class UserRewardProgramResponse(BaseModel):
    code: int | None = None
    data: UserRewardProgram | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class UserRole(Enum):
    admin = "Admin"
    agency_admin = "AgencyAdmin"
    agent = "Agent"
    user = "User"


class UserSession(BaseModel):
    expiry: AwareOrNaiveDatetime | None = None
    ip: str | None = None
    token: str | None = None
    user_id: int | None = Field(None, alias="userId")


class UserSessionResponse(BaseModel):
    code: int | None = None
    data: UserSession | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class UserTieType(Enum):
    ro = "RO"
    rw = "RW"


class UserValidationResponse(BaseModel):
    code: str | None = None
    email: str | None = None
    id: int | None = None
    token: str | None = None


class UserValidationResponseResponse(BaseModel):
    code: int | None = None
    data: UserValidationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class VendorStatusType(Enum):
    nonpreferred = "nonpreferred"
    preferred = "preferred"


class Views(BaseModel):
    pass


class VisibilityType(Enum):
    private = "PRIVATE"
    public = "PUBLIC"


class Wall(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    visibility: VisibilityType | None = None


class WallResponse(BaseModel):
    code: int | None = None
    data: Wall | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class WaypointFlags(Enum):
    reprice_required = "REPRICE_REQUIRED"
    credit_card_verification = "CREDIT_CARD_VERIFICATION"
    reserved_3 = "RESERVED_3"
    reserved_4 = "RESERVED_4"
    reserved_5 = "RESERVED_5"
    reserved_6 = "RESERVED_6"
    reserved_7 = "RESERVED_7"
    reserved_8 = "RESERVED_8"
    reserved_9 = "RESERVED_9"
    reserved_10 = "RESERVED_10"
    reserved_11 = "RESERVED_11"
    reserved_12 = "RESERVED_12"
    reserved_13 = "RESERVED_13"
    reserved_14 = "RESERVED_14"
    reserved_15 = "RESERVED_15"
    ticketing = "TICKETING"
    reserved_17 = "RESERVED_17"
    reserved_18 = "RESERVED_18"
    reserved_19 = "RESERVED_19"
    reserved_20 = "RESERVED_20"
    reserved_21 = "RESERVED_21"
    reserved_22 = "RESERVED_22"
    reserved_23 = "RESERVED_23"
    reserved_24 = "RESERVED_24"
    reserved_25 = "RESERVED_25"
    reserved_26 = "RESERVED_26"
    reserved_27 = "RESERVED_27"
    reserved_28 = "RESERVED_28"
    reserved_29 = "RESERVED_29"
    reserved_30 = "RESERVED_30"
    reserved_31 = "RESERVED_31"


class Weight(BaseModel):
    application: Application | None = None
    kg: str | None = None
    lb: str | None = None


class WidthEnum(Enum):
    n_a = "n/a"
    standard = "standard"
    wider = "wider"


class WifiChance(Enum):
    none = "None"
    some = "Some"
    good = "Good"
    very_good = "VeryGood"
    full = "Full"


class WindowSizeEnum(Enum):
    n_a = "n/a"
    standard = "standard"
    larger = "larger"
    smaller = "smaller"


class ActionTrail(BaseModel):
    action: str | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    request_headers: dict[str, str] = Field(
        alias="requestHeaders",
        default_factory=dict,
    )
    request_method: str | None = Field(None, alias="requestMethod")
    request_uri: str | None = Field(None, alias="requestUri")
    resource_id: int | None = Field(None, alias="resourceId")
    resource_type: ResourceType | None = Field(None, alias="resourceType")
    time: int | None = None
    user_id: int | None = Field(None, alias="userId")


class AddCardRequest(BaseModel):
    billing_address: Address | None = Field(None, alias="billingAddress")
    cvc: str | None = None
    expiration: str | None = Field(None, examples=["2022-03"])
    holder_name: str | None = Field(None, alias="holderName")
    is_default: bool | None = Field(None, alias="isDefault")
    name: str | None = None
    number: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    reservation_types: int | None = Field(None, alias="reservationTypes")
    user_id: int | None = Field(None, alias="userId")


class AddressLocationMap(BaseModel):
    code: int | None = None
    data: Data | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AdvanceChangeInner(BaseModel):
    assessment: Assessment | None = None
    description: str | None = None
    fee: Fee | None = None
    headline: str | None = None


class AgencyListResponse(BaseModel):
    code: int | None = None
    data: list[Agency] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class AgencyResponse(BaseModel):
    code: int | None = None
    data: Agency | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgencySettingsListResponse(BaseModel):
    code: int | None = None
    data: list[AgencySettings] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class AgencySettingsResponse(BaseModel):
    code: int | None = None
    data: AgencySettings | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgentPhoneListResponse(BaseModel):
    code: int | None = None
    data: list[AgentPhone] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class AgentStatusResponse(BaseModel):
    code: int | None = None
    data: AgentStatus | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgodaBookingDetailResponse(BaseModel):
    benefits: list[AgodaBenefit] = Field(default_factory=list)
    board_code: AgodaBoardCode | None = Field(None, alias="boardCode")
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")
    booking_status: AgodaBookingStatus | None = Field(None, alias="bookingStatus")
    channel: AgodaChannel | None = None
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    guest_count: AgodaGuestCount | None = Field(None, alias="guestCount")
    hotel: str | None = None
    hotel_confirmation_reference: str | None = Field(
        None,
        alias="hotelConfirmationReference",
    )
    hourly_slot: AgodaHourlyAvailableSlot | None = Field(None, alias="hourlySlot")
    instant_confirm: bool | None = Field(None, alias="instantConfirm")
    price: AgodaPrice | None = None
    quantity: int | None = None
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    remark: str | None = None
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    room_code: str | None = Field(None, alias="roomCode")
    special_requests: str | None = Field(None, alias="specialRequests")
    supplier_booking_id: str | None = Field(None, alias="supplierBookingId")
    version: str | None = None


class AgodaBookingDetailResponseResponse(BaseModel):
    code: int | None = None
    data: AgodaBookingDetailResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgodaBookingRequest(BaseModel):
    benefits: list[AgodaBenefit] = Field(default_factory=list)
    board_code: AgodaBoardCode | None = Field(None, alias="boardCode")
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")
    channel: AgodaChannel | None = None
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    currency: str | None = None
    guest: AgodaGuest | None = None
    guest_count: AgodaGuestCount | None = Field(None, alias="guestCount")
    hotel: str | None = None
    metadata: str | None = None
    quantity: int | None = None
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    room_code: str | None = Field(None, alias="roomCode")
    selected_hourly_slot: AgodaHourlyAvailableSlot | None = Field(
        None,
        alias="selectedHourlySlot",
    )
    special_requests: str | None = Field(None, alias="specialRequests")
    total_price: float | None = Field(None, alias="totalPrice")


class AgodaBookingResponse(BaseModel):
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")
    remark: str | None = None
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None


class AgodaBookingResponseResponse(BaseModel):
    code: int | None = None
    data: AgodaBookingResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgodaCancelResponse(BaseModel):
    cancellation_fees: float | None = Field(None, alias="cancellationFees")
    reference_id: str | None = Field(None, alias="referenceId")
    remark: str | None = None
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None


class AgodaCancelResponseResponse(BaseModel):
    code: int | None = None
    data: AgodaCancelResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgodaHotelSearchResponse(BaseModel):
    remark: str | None = None
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None


class AgodaHotelSearchResponseResponse(BaseModel):
    code: int | None = None
    data: AgodaHotelSearchResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgodaPrecheckRequest(BaseModel):
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    currency: str | None = None
    hotel: str | None = None
    metadata: str | None = None
    occupancy: RoomOccupancy | None = None
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    selected_hourly_slot: AgodaHourlyAvailableSlot | None = Field(
        None,
        alias="selectedHourlySlot",
    )
    total_price: float | None = Field(None, alias="totalPrice")


class AgodaPrecheckResponse(BaseModel):
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    currency: str | None = None
    hotel: AgodaHotel | None = None
    remark: str | None = None
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None


class AgodaPrecheckResponseResponse(BaseModel):
    code: int | None = None
    data: AgodaPrecheckResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AgodaResponse(BaseModel):
    remark: str | None = None
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None


class Aircraft(BaseModel):
    display_text: str | None = Field(None, alias="displayText")
    type: AircraftType | None = None


class AirlineListResponse(BaseModel):
    code: int | None = None
    data: list[Airline] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class AirportListResponse(BaseModel):
    code: int | None = None
    data: list[Airport] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class AirportResponse(BaseModel):
    code: int | None = None
    data: Airport | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class AmadeusOrgProfile(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_hash: str | None = Field(None, alias="profileHash")
    profile_id: str | None = Field(None, alias="profileId")
    storage_type: StorageType | None = Field(None, alias="storageType")


class AncillaryOffer(BaseModel):
    available_quantity: int | None = Field(None, alias="availableQuantity")
    boundary: str | None = None
    code: str | None = None
    description: str | None = None
    local_currency: str | None = Field(None, alias="localCurrency")
    local_price: float | None = Field(None, alias="localPrice")
    local_taxes: float | None = Field(None, alias="localTaxes")
    max_quantity: int | None = Field(None, alias="maxQuantity")
    min_quantity: int | None = Field(None, alias="minQuantity")
    name: str | None = None
    passenger_refs: list[str] = Field(alias="passengerRefs", default_factory=list)
    price: float | None = None
    ref: str | None = None
    taxes: float | None = None
    type: AncillaryType | None = None
    vendor: str | None = None


class AncillaryOffers(BaseModel):
    ancillaries: list[AncillaryOffer] = Field(default_factory=list)
    ref: str | None = None


class ApiKey(BaseModel):
    active: bool | None = None
    description: str | None = None
    id: int | None = None
    key: str | None = None
    platform: PlatformType | None = None


class ApprovalItem(BaseModel):
    comment: str | None = None
    created_at: AwareOrNaiveDatetime | None = Field(None, alias="createdAt")
    policy_ids: list[int] = Field(alias="policyIds", default_factory=list)
    status: ApprovalStatus | None = None
    user_id: int | None = Field(None, alias="userId")


class BaseTrainStationResponse(BaseModel):
    code: int | None = None
    data: BaseTrainStation | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Beverage(BaseModel):
    alcoholic_free: bool | None = Field(None, alias="alcoholicFree")
    display_text: str | None = Field(None, alias="displayText")
    nonalcoholic_free: bool | None = Field(None, alias="nonalcoholicFree")
    quality: FoodQuality | None = None
    type: BeverageType | None = None


class BoardingPriority(BaseModel):
    application: OptSvcApplication | None = None
    assessment: Assessment | None = None
    code: str | None = None
    commercial_name: str | None = Field(None, alias="commercialName")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fee: Fee | None = None
    group_code: str | None = Field(None, alias="groupCode")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class BooleanResponse(BaseModel):
    code: int | None = None
    data: bool | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class CampaignListResponse(BaseModel):
    code: int | None = None
    data: list[Campaign] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class CampaignResponse(BaseModel):
    code: int | None = None
    data: Campaign | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class CancellationInner(BaseModel):
    assessment: Assessment | None = None
    description: str | None = None
    fee: Fee | None = None
    headline: str | None = None


class CarReservationExt(BaseModel):
    arrival_flight: ArrivalFlight | None = Field(None, alias="arrivalFlight")
    brand: str | None = None
    car: Car | None = None
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    confirmation_number: str | None = Field(None, alias="confirmationNumber")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    days: int | None = None
    distance_overage: float | None = Field(None, alias="distanceOverage")
    distance_unit: DistanceUnit | None = Field(None, alias="distanceUnit")
    drop_off: CarLocation | None = Field(None, alias="dropOff")
    extras: list[CarExtra] = Field(default_factory=list)
    free_distance_covered: float | None = Field(None, alias="freeDistanceCovered")
    hours: int | None = None
    insurances: list[CarInsurance] = Field(default_factory=list)
    pick_up: CarLocation | None = Field(None, alias="pickUp")
    same_drop_off_location: bool | None = Field(None, alias="sameDropOffLocation")
    total_extras: float | None = Field(None, alias="totalExtras")
    total_fees: float | None = Field(None, alias="totalFees")
    total_insurance: float | None = Field(None, alias="totalInsurance")
    total_taxes: float | None = Field(None, alias="totalTaxes")
    total_vehicle: float | None = Field(None, alias="totalVehicle")
    unlimited_distance: bool | None = Field(None, alias="unlimitedDistance")


class CarVendorListResponse(BaseModel):
    code: int | None = None
    data: list[CarVendor] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class CheckInPriority(BaseModel):
    application: OptSvcApplication | None = None
    assessment: Assessment | None = None
    code: str | None = None
    commercial_name: str | None = Field(None, alias="commercialName")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fee: Fee | None = None
    group_code: str | None = Field(None, alias="groupCode")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class ConcurOrgListResponse(BaseModel):
    code: int | None = None
    data: list[ConcurOrg] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ConcurOrgResponse(BaseModel):
    code: int | None = None
    data: ConcurOrg | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class CountryListResponse(BaseModel):
    code: int | None = None
    data: list[Country] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class CountryStateListResponse(BaseModel):
    code: int | None = None
    data: list[CountryState] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class CreateOrgRequest(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    customer_number: str | None = Field(None, alias="customerNumber")
    description: str | None = None
    email: str | None = None
    flags: int | None = None
    name: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    sabre_profile_id: str | None = Field(None, alias="sabreProfileId")
    sabre_template_id: str | None = Field(None, alias="sabreTemplateId")
    timezone: str | None = None
    type: OrgType | None = None
    visibility: VisibilityType | None = None
    website: str | None = None


class CreateOrgUserRequest(BaseModel):
    dob: date | None = None
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    flags: int | None = None
    gender: Gender | None = None
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    org_data: OrgUserUpdateEntryData | None = Field(None, alias="orgData")
    phone_number: str | None = Field(None, alias="phoneNumber")
    suffix: str | None = None


class CreateUserAccountRequest(BaseModel):
    dob: date | None = None
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    flags: int | None = None
    gender: Gender | None = None
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    phone_number: str | None = Field(None, alias="phoneNumber")
    suffix: str | None = None


class CreditListResponse(BaseModel):
    code: int | None = None
    data: list[Credit] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class CreditResponse(BaseModel):
    code: int | None = None
    data: Credit | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class CurrencyListResponse(BaseModel):
    code: int | None = None
    data: list[Currency] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class DisplayTextSummary(BaseModel):
    display_text: str | None = Field(None, alias="displayText")
    exists: Exists3 | None = None


class DomainListResponse(BaseModel):
    code: int | None = None
    data: list[Domain] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class DomainResponse(BaseModel):
    code: int | None = None
    data: Domain | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class EmptyDataResponse(BaseModel):
    code: int | None = None
    data: EmptyData | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class EmptyResponse(BaseModel):
    code: int | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Entertainement(BaseModel):
    content_type: list[EntertainementContentType] = Field(
        alias="contentType",
        default_factory=list,
    )
    cost: AmenityCost | None = None
    display_text: str | None = Field(None, alias="displayText")


class EntertainmentOfferings(BaseModel):
    content_type: ContentTypeEnum | None = Field(None, alias="contentType")
    delivery_medium: DeliveryMediumEnum | None = Field(None, alias="deliveryMedium")
    selection_type: SelectionTypeEnum | None = Field(None, alias="selectionType")


class EntertainmentOfferingsGroup(BaseModel):
    offerings: list[EntertainmentOfferings] = Field(default_factory=list)
    operator: OperatorEnum | None = None


class EnumsHolder(BaseModel):
    approval_action: ApprovalAction | None = Field(None, alias="approvalAction")
    exception_flags: ExceptionFlags | None = Field(None, alias="exceptionFlags")
    fare_type: FareType | None = Field(None, alias="fareType")
    field_flag: FieldFlags | None = Field(None, alias="fieldFlag")
    platform_type: PlatformType | None = Field(None, alias="platformType")
    train_seat_preference_flags: TrainSeatPreferenceFlags | None = Field(
        None,
        alias="trainSeatPreferenceFlags",
    )
    trip_board_processing_flags: TripBoardProcessingFlags | None = Field(
        None,
        alias="tripBoardProcessingFlags",
    )


class ExchangeRateListResponse(BaseModel):
    code: int | None = None
    data: list[ExchangeRate] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ExpensifySettingsResponse(BaseModel):
    code: int | None = None
    data: ExpensifySettings | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class FieldModel(BaseModel):
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    code: str | None = None
    flags: int | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    remark_code: str | None = Field(None, alias="remarkCode")
    reservation_type: ReservationType | None = Field(None, alias="reservationType")
    type: FieldType | None = None
    value_type: FieldValueType | None = Field(None, alias="valueType")


class FieldResponse(BaseModel):
    code: int | None = None
    data: FieldModel | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class FieldValueListResponse(BaseModel):
    code: int | None = None
    data: list[FieldValue] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class FieldValueResponse(BaseModel):
    code: int | None = None
    data: FieldValue | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class FlightAttribute(BaseModel):
    categories: list[str] = Field(default_factory=list)
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fees: list[FlightAttributeFee] = Field(default_factory=list)
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")


class FlightRefData(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    flight_details: list[str] = Field(alias="flightDetails", default_factory=list)
    flight_key: str | None = Field(None, alias="flightKey")
    offer_id: str | None = Field(None, alias="offerId")
    owner: str | None = None
    passengers: list[PassengerEntry] = Field(default_factory=list)
    segment_perks: int | None = Field(None, alias="segmentPerks")
    segments: list[FlightSegmentRefData] = Field(default_factory=list)
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")


class FlightReservationAncillary(BaseModel):
    boundary: str | None = None
    code: str | None = None
    description: str | None = None
    local_currency: str | None = Field(None, alias="localCurrency")
    local_price: float | None = Field(None, alias="localPrice")
    local_taxes: float | None = Field(None, alias="localTaxes")
    name: str | None = None
    price: float | None = None
    quantity: int | None = None
    status: ReservationStatus | None = None
    taxes: float | None = None
    type: AncillaryType | None = None
    vendor: str | None = None


class FlightReservationOd(BaseModel):
    arrival_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalOffsetDateTime",
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    arrival_time_offset: int | None = Field(None, alias="arrivalTimeOffset")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    departure_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureOffsetDateTime",
    )
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    departure_time_offset: int | None = Field(None, alias="departureTimeOffset")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    segments: list[FlightReservationSegment] = Field(default_factory=list)
    stops: list[str] = Field(default_factory=list)


class FlightReservationSeat(BaseModel):
    consumer_index: int | None = Field(None, alias="consumerIndex")
    preference: SeatPreference | None = None
    price: float | None = None
    seat_column: str | None = Field(None, alias="seatColumn")
    seat_flags: int | None = Field(None, alias="seatFlags")
    seat_key: str | None = Field(None, alias="seatKey")
    seat_row: str | None = Field(None, alias="seatRow")
    segment_key: str | None = Field(None, alias="segmentKey")
    status: ReservationStatus | None = None
    taxes: float | None = None


class FlightReservationSsr(BaseModel):
    code: str | None = None
    comment: str | None = None
    consumer_index: int | None = Field(None, alias="consumerIndex")
    status: ReservationStatus | None = None


class Food(BaseModel):
    display_text: str | None = Field(None, alias="displayText")
    free: bool | None = None
    quality: FoodQuality | None = None
    type: FoodType | None = None


class FreeBaggageData(BaseModel):
    attributes: BaggageAttributes | None = None
    display_text: str | None = Field(None, alias="displayText")
    optional_service_id: str | None = Field(None, alias="optionalServiceId")
    pieces: str | None = None
    size: Size | None = None
    total_weight: TotalMaxWeight | None = Field(None, alias="totalWeight")
    weight: Weight | None = None


class FreshFood(BaseModel):
    cost: Cost | None = None
    display_text: str | None = Field(None, alias="displayText")
    exists: Exists | None = None
    id: str | None = None
    quality: Quality | None = None
    type: TypeEnum | None = None
    updated_at: str | None = Field(None, alias="updatedAt")


class GetCarResponseResponse(BaseModel):
    code: int | None = None
    data: GetCarResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Hotel(BaseModel):
    address1: str | None = None
    address2: str | None = None
    amenities: int | None = None
    brand_code: str | None = Field(None, alias="brandCode")
    brand_name: str | None = Field(None, alias="brandName")
    chain_code: str | None = Field(None, alias="chainCode")
    chain_name: str | None = Field(None, alias="chainName")
    city: str | None = None
    city_code: str | None = Field(None, alias="cityCode")
    code_context: str | None = Field(None, alias="codeContext")
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    fax: str | None = None
    hotel_code: str | None = Field(None, alias="hotelCode")
    hotel_name: str | None = Field(None, alias="hotelName")
    latitude: float | None = None
    longitude: float | None = None
    main_city_code: str | None = Field(None, alias="mainCityCode")
    medias: list[HotelMedia] = Field(default_factory=list)
    phone: str | None = None
    rating: float | None = None
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    street_number: str | None = Field(None, alias="streetNumber")
    zip_code: str | None = Field(None, alias="zipCode")


class HotelChainListResponse(BaseModel):
    code: int | None = None
    data: list[HotelChain] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class HotelOffer(BaseModel):
    checkin_date: date | None = Field(None, alias="checkinDate")
    checkout_date: date | None = Field(None, alias="checkoutDate")
    commission_percent: float | None = Field(None, alias="commissionPercent")
    currency: str | None = None
    distance: float | None = None
    flags: int | None = None
    hotel: Hotel | None = None
    hotel_pref_level: int | None = Field(None, alias="hotelPrefLevel")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    price_per_night: float | None = Field(None, alias="pricePerNight")
    rate_codes: list[str] = Field(alias="rateCodes", default_factory=list)
    refs: list[str] = Field(default_factory=list)
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    taxes_and_fees_per_night: float | None = Field(None, alias="taxesAndFeesPerNight")
    total_price: float | None = Field(None, alias="totalPrice")


class HotelReservationExt(BaseModel):
    address1: str | None = None
    address2: str | None = None
    amenities: int | None = None
    atmosphere_description: str | None = Field(None, alias="atmosphereDescription")
    brand_code: str | None = Field(None, alias="brandCode")
    cancellation: HotelCancellation | None = None
    chain_code: str | None = Field(None, alias="chainCode")
    checkin_date: date | None = Field(None, alias="checkinDate")
    checkin_time: str | None = Field(None, alias="checkinTime")
    checkout_date: date | None = Field(None, alias="checkoutDate")
    checkout_time: str | None = Field(None, alias="checkoutTime")
    city: str | None = None
    city_code: str | None = Field(None, alias="cityCode")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    confirmation_number: str | None = Field(None, alias="confirmationNumber")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    external_segment_id: str | None = Field(None, alias="externalSegmentId")
    fax: str | None = None
    guests: int | None = None
    hotel_chain_name: str | None = Field(None, alias="hotelChainName")
    hotel_group_name: str | None = Field(None, alias="hotelGroupName")
    hotel_name: str | None = Field(None, alias="hotelName")
    hotel_refs: list[str] = Field(alias="hotelRefs", default_factory=list)
    important: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    main_city_code: str | None = Field(None, alias="mainCityCode")
    media: list[ReservationMedia] = Field(default_factory=list)
    perks: int | None = None
    phone: str | None = None
    price_per_night: float | None = Field(None, alias="pricePerNight")
    rating: float | None = None
    room_description: str | None = Field(None, alias="roomDescription")
    room_flags: int | None = Field(None, alias="roomFlags")
    room_type: str | None = Field(None, alias="roomType")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    street_number: str | None = Field(None, alias="streetNumber")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    taxes_and_fees_per_night: float | None = Field(None, alias="taxesAndFeesPerNight")
    zip_code: str | None = Field(None, alias="zipCode")


class HotelRoom(BaseModel):
    approval_required: bool | None = Field(None, alias="approvalRequired")
    bed_type: str | None = Field(None, alias="bedType")
    booking_blocked: bool | None = Field(None, alias="bookingBlocked")
    cancellation: HotelCancellation | None = None
    checkin_time: str | None = Field(None, alias="checkinTime")
    checkout_time: str | None = Field(None, alias="checkoutTime")
    commission: float | None = None
    currency: str | None = None
    description: str | None = None
    flags: int | None = None
    hidden: bool | None = None
    hotel_pref_level: int | None = Field(None, alias="hotelPrefLevel")
    important: str | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    perks: int | None = None
    price_per_night: float | None = Field(None, alias="pricePerNight")
    rate_code: RoomRateCode | None = Field(None, alias="rateCode")
    rate_plan_type: OtaRatePlanType | None = Field(None, alias="ratePlanType")
    ref: str | None = None
    room_id: str | None = Field(None, alias="roomId")
    room_type: str | None = Field(None, alias="roomType")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    taxes_and_fees_per_night: float | None = Field(None, alias="taxesAndFeesPerNight")
    total_price: float | None = Field(None, alias="totalPrice")


class HotelRoomResponse(BaseModel):
    room: HotelRoom | None = None


class HotelRoomResponseResponse(BaseModel):
    code: int | None = None
    data: HotelRoomResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class HotelRoomsResponse(BaseModel):
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    rooms: list[HotelRoom] = Field(default_factory=list)


class HotelRoomsResponseResponse(BaseModel):
    code: int | None = None
    data: HotelRoomsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ImportSabreOrgProfileResponse(BaseModel):
    act: ImportProfileAct | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    link_traveler_profile: bool | None = Field(None, alias="linkTravelerProfile")
    org_id: int | None = Field(None, alias="orgId")
    org_name: str | None = Field(None, alias="orgName")
    sabre_profile_id: str | None = Field(None, alias="sabreProfileId")
    sabre_template_id: str | None = Field(None, alias="sabreTemplateId")
    suppress_user_emails: bool | None = Field(None, alias="suppressUserEmails")
    user_profile_source: ImportProfileSource | None = Field(
        None,
        alias="userProfileSource",
    )
    users: list[TravelerProfile] = Field(default_factory=list)


class ImportSabreOrgProfileResponseResponse(BaseModel):
    code: int | None = None
    data: ImportSabreOrgProfileResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class IsReservationExt(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)


class Items1(BaseModel):
    empty: bool | None = None
    first: TripSummaryLine | None = None
    last: TripSummaryLine | None = None


class Items(RootModel[list[TripSummaryLine] | Items1]):
    root: list[TripSummaryLine] | Items1


class KpiCountResponseResponse(BaseModel):
    code: int | None = None
    data: KpiCountResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Layout(BaseModel):
    direct_aisle_access: bool | None = Field(None, alias="directAisleAccess")
    display_text: str | None = Field(None, alias="displayText")
    quality: LayoutQualityType | None = None
    row_layout: str | None = Field(None, alias="rowLayout")
    type: LayoutType | None = None


class ListAncillariesResponse(BaseModel):
    ancillary_offers: list[AncillaryOffers] = Field(
        alias="ancillaryOffers",
        default_factory=list,
    )


class ListAncillariesResponseResponse(BaseModel):
    code: int | None = None
    data: ListAncillariesResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListFareRulesResponseResponse(BaseModel):
    code: int | None = None
    data: ListFareRulesResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListFieldsResponse(BaseModel):
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)
    fields: list[FieldModel] = Field(default_factory=list)


class ListFieldsResponseResponse(BaseModel):
    code: int | None = None
    data: ListFieldsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListReservationFieldResponse(BaseModel):
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)
    fields: list[FieldModel] = Field(default_factory=list)
    reservation_fields: list[ReservationField] = Field(
        alias="reservationFields",
        default_factory=list,
    )


class ListReservationFieldResponseResponse(BaseModel):
    code: int | None = None
    data: ListReservationFieldResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class LocateCarResponse(BaseModel):
    locations: list[CarLocationMerged] = Field(default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )


class LocateCarResponseResponse(BaseModel):
    code: int | None = None
    data: LocateCarResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class LoungeAccess(BaseModel):
    application: OptSvcApplication | None = None
    assessment: Assessment | None = None
    code: str | None = None
    commercial_name: str | None = Field(None, alias="commercialName")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fee: Fee | None = None
    group_code: str | None = Field(None, alias="groupCode")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    sub_group_code: str | None = Field(None, alias="subGroupCode")


class LoyaltyProgram(BaseModel):
    active: bool | None = None
    code: str | None = None
    id: int | None = None
    logo_url: str | None = Field(None, alias="logoUrl")
    name: str | None = None
    prefix: str | None = None
    type: ReservationType | None = None
    website_url: str | None = Field(None, alias="websiteUrl")


class LoyaltyProgramListResponse(BaseModel):
    code: int | None = None
    data: list[LoyaltyProgram] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class MaskedCreditCard(BaseModel):
    address: Address | None = None
    brand: str | None = None
    exp_date: str | None = Field(None, alias="expDate")
    holder_name: str | None = Field(None, alias="holderName")
    id: int | None = None
    is_default: bool | None = Field(None, alias="isDefault")
    last_digits: str | None = Field(None, alias="lastDigits")
    missing_fields_flags: int | None = Field(None, alias="missingFieldsFlags")
    name: str | None = None
    reservation_types: int | None = Field(None, alias="reservationTypes")
    type: UserCreditCardType | None = None


class MaskedCreditCardListResponse(BaseModel):
    code: int | None = None
    data: list[MaskedCreditCard] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class MaskedCreditCardResponse(BaseModel):
    code: int | None = None
    data: MaskedCreditCard | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Media(BaseModel):
    active: bool | None = None
    attribution_name: str | None = Field(None, alias="attributionName")
    attribution_url: str | None = Field(None, alias="attributionUrl")
    external_id: str | None = Field(None, alias="externalId")
    height: int | None = None
    id: int | None = None
    nms: int | None = None
    query: str | None = None
    source: MediaSource | None = None
    type: MediaType | None = None
    url: str | None = None
    width: int | None = None


class MediaRepository(BaseModel):
    count_cached: int | None = Field(None, alias="countCached")
    count_total: int | None = Field(None, alias="countTotal")
    id: int | None = None
    last_queried_on: AwareOrNaiveDatetime | None = Field(None, alias="lastQueriedOn")
    nms: int | None = None
    query: str | None = None
    source: MediaSource | None = None


class MiscReservationExt(BaseModel):
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    place_id: str | None = Field(None, alias="placeId")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    venue_name: str | None = Field(None, alias="venueName")
    zip_code: str | None = Field(None, alias="zipCode")


class Msg(BaseModel):
    active: bool | None = None
    dates: list[MsgDatePair] = Field(default_factory=list)
    ext: Ext | None = None
    hashtags: list[str] = Field(default_factory=list)
    id: int | None = None
    likes: list[int] = Field(default_factory=list)
    locations: list[MsgLocation] = Field(default_factory=list)
    media: list[Media] = Field(default_factory=list)
    mentions: list[MsgMention] = Field(default_factory=list)
    msgs: list[Msg] = Field(default_factory=list)
    nms: int | None = None
    parent_id: int | None = Field(None, alias="parentId")
    post_id: int | None = Field(None, alias="postId")
    processed_on: int | None = Field(None, alias="processedOn")
    text: str | None = None
    time: int | None = None
    user_id: int | None = Field(None, alias="userId")


class NotificationCenter(BaseModel):
    ext: Ext | None = None
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    unseen: int | None = None
    unseen_agent_posts: int | None = Field(None, alias="unseenAgentPosts")
    unseen_user_posts: int | None = Field(None, alias="unseenUserPosts")


class NotificationCenterResponse(BaseModel):
    code: int | None = None
    data: NotificationCenter | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Offer(BaseModel):
    fares: dict[str, list[PricedFare]] = Field(default_factory=dict)
    od_id: str | None = Field(None, alias="odId")


class Org(BaseModel):
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    billing_address_location_id: int | None = Field(
        None,
        alias="billingAddressLocationId",
    )
    branding: Branding | None = None
    customer_number: str | None = Field(None, alias="customerNumber")
    description: str | None = None
    flags: int | None = None
    id: int | None = None
    name: str | None = None
    nms: int | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    timezone: str | None = None
    type: OrgType | None = None
    visibility: VisibilityType | None = None
    website: str | None = None


class OrgAgencyResponse(BaseModel):
    code: int | None = None
    data: OrgAgency | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgAirlinePrefListResponse(BaseModel):
    code: int | None = None
    data: list[OrgAirlinePref] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgAirlinePrefResponse(BaseModel):
    code: int | None = None
    data: OrgAirlinePref | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgBudgetEntry(BaseModel):
    accrual_term: int | None = Field(None, alias="accrualTerm")
    amount: float | None = None
    name: str | None = None
    start_date: date | None = Field(None, alias="startDate")
    type: OrgBudgetType | None = None


class OrgCarVendorPrefListResponse(BaseModel):
    code: int | None = None
    data: list[OrgCarVendorPref] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgCarVendorPrefResponse(BaseModel):
    code: int | None = None
    data: OrgCarVendorPref | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgDomainListResponse(BaseModel):
    code: int | None = None
    data: list[OrgDomain] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgDomainResponse(BaseModel):
    code: int | None = None
    data: OrgDomain | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgEmailListResponse(BaseModel):
    code: int | None = None
    data: list[OrgEmail] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgEmailResponse(BaseModel):
    code: int | None = None
    data: OrgEmail | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgHotelChainPrefListResponse(BaseModel):
    code: int | None = None
    data: list[OrgHotelChainPref] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgHotelChainPrefResponse(BaseModel):
    code: int | None = None
    data: OrgHotelChainPref | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgHotelChainRoomPrefListResponse(BaseModel):
    code: int | None = None
    data: list[OrgHotelChainRoomPref] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgIntegration(BaseModel):
    id: int | None = None
    latest_sync_id: int | None = Field(None, alias="latestSyncId")
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    owned_by: str | None = Field(None, alias="ownedBy")
    settings: dict[str, Any] = Field(default_factory=dict)
    type: OrgIntegrationType | None = None


class OrgIntegrationExpensify(BaseModel):
    id: int | None = None
    latest_sync_id: int | None = Field(None, alias="latestSyncId")
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    owned_by: str | None = Field(None, alias="ownedBy")
    settings: ExpensifySettings | None = None
    type: OrgIntegrationType | None = None


class OrgListResponse(BaseModel):
    code: int | None = None
    data: list[Org] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgLoyaltyProgramListResponse(BaseModel):
    code: int | None = None
    data: list[OrgLoyaltyProgram] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgLoyaltyProgramResponse(BaseModel):
    code: int | None = None
    data: OrgLoyaltyProgram | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgProjectListResponse(BaseModel):
    code: int | None = None
    data: list[OrgProject] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgProjectResponse(BaseModel):
    code: int | None = None
    data: OrgProject | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgRateCodeListResponse(BaseModel):
    code: int | None = None
    data: list[OrgRateCode] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgRateCodeResponse(BaseModel):
    code: int | None = None
    data: OrgRateCode | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgRateCodeTextResponse(BaseModel):
    code: int | None = None
    data: OrgRateCodeText | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgResponse(BaseModel):
    code: int | None = None
    data: Org | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgSettingsListResponse(BaseModel):
    code: int | None = None
    data: list[OrgSettings] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgSettingsResponse(BaseModel):
    code: int | None = None
    data: OrgSettings | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgUser(BaseModel):
    approver_policy_ids: list[int] = Field(
        alias="approverPolicyIds",
        default_factory=list,
    )
    business_address_id: int | None = Field(None, alias="businessAddressId")
    business_phone_number: str | None = Field(None, alias="businessPhoneNumber")
    guest_policy_count: int | None = Field(None, alias="guestPolicyCount")
    guest_policy_ids: list[int] = Field(alias="guestPolicyIds", default_factory=list)
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    position: str | None = None
    role: OrgUserRole | None = None
    status: OrgUserStatus | None = None
    travel_policy_ids: list[int] = Field(alias="travelPolicyIds", default_factory=list)
    user_id: int | None = Field(None, alias="userId")


class OrgUserEntryData(BaseModel):
    business_address: AddressLocation | None = Field(None, alias="businessAddress")
    business_phone_number: str | None = Field(None, alias="businessPhoneNumber")
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    position: str | None = None
    role: OrgUserRole | None = None


class OrgUserFieldListResponse(BaseModel):
    code: int | None = None
    data: list[OrgUserField] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgUserFieldResponse(BaseModel):
    code: int | None = None
    data: OrgUserField | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgUserIdEntryDataList(BaseModel):
    org_users: list[int] = Field(alias="orgUsers", default_factory=list)
    update: OrgUserUpdateEntryData | None = None


class OrgUserListResponse(BaseModel):
    code: int | None = None
    data: list[OrgUser] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class OrgUserResponse(BaseModel):
    code: int | None = None
    data: OrgUser | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgUsersResponse(BaseModel):
    errors: dict[str, str] = Field(default_factory=dict)
    organization_users: list[OrgUser] = Field(
        alias="organizationUsers",
        default_factory=list,
    )


class OrgUsersResponseResponse(BaseModel):
    code: int | None = None
    data: OrgUsersResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrganizationReportCityPairs(BaseModel):
    market_share: float | None = Field(None, alias="marketShare")
    org_id: int | None = Field(None, alias="orgId")
    org_logo_url: str | None = Field(None, alias="orgLogoUrl")
    org_name: str | None = Field(None, alias="orgName")
    report_city_pairs: list[ReportCityPairs] = Field(
        alias="reportCityPairs",
        default_factory=list,
    )


class OrganizationReportCityPairsResponse(BaseModel):
    code: int | None = None
    data: OrganizationReportCityPairs | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class PaidBaggageData(BaseModel):
    attributes: BaggageAttributes | None = None
    display_text: str | None = Field(None, alias="displayText")
    excess_first: str | None = Field(None, alias="excessFirst")
    excess_last: str | None = Field(None, alias="excessLast")
    fee: Fee | None = None
    free: str | None = None
    optional_service_id: str | None = Field(None, alias="optionalServiceId")
    os_sequence: str | None = Field(None, alias="osSequence")
    size: Size | None = None
    weight: Weight | None = None


class ParentResource(BaseModel):
    id: int | None = None
    type: ResourceType | None = None


class Penalty(BaseModel):
    currency_code: str | None = Field(None, alias="currencyCode")
    enabled: bool | None = None
    penalty_amount: float | None = Field(None, alias="penaltyAmount")
    type: PenaltyType | None = None


class PenaltyData(BaseModel):
    penalties: list[Penalty] = Field(default_factory=list)


class PendingEmail(BaseModel):
    active: bool | None = None
    bcc_emails: list[str] = Field(alias="bccEmails", default_factory=list)
    email: str | None = None
    id: int | None = None
    is_html: bool | None = Field(None, alias="isHtml")
    message: str | None = None
    name: str | None = None
    nms: int | None = None
    status: PendingEmailStatus | None = None
    subject: str | None = None


class PendingEmailListResponse(BaseModel):
    code: int | None = None
    data: list[PendingEmail] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class PendingEmailResponse(BaseModel):
    code: int | None = None
    data: PendingEmail | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class PolicyLookupTableResponse(BaseModel):
    code: int | None = None
    data: PolicyLookupTable | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class PolicyOptionFligthClassByDuration(BaseModel):
    by_legs: list[PolicyOptionLeg] = Field(alias="byLegs", default_factory=list)
    max: FlightClassPref | None = None


class PolicyOptions(BaseModel):
    flight_classes: list[FlightClassPref] = Field(
        alias="flightClasses",
        default_factory=list,
    )
    flight_classes_by_duration: PolicyOptionFligthClassByDuration | None = Field(
        None,
        alias="flightClassesByDuration",
    )


class PolicyRuleException(BaseModel):
    active: bool | None = None
    code: PolicyRuleSpecs | None = None
    id: int | None = None
    nms: int | None = None
    policy_rule_id: int | None = Field(None, alias="policyRuleId")
    vars: dict[str, dict[str, Any]] = Field(default_factory=dict)


class PolicyRuleExceptionResponse(BaseModel):
    code: int | None = None
    data: PolicyRuleException | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class PostPin(BaseModel):
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    post_id: int | None = Field(None, alias="postId")


class Power(BaseModel):
    distribution: PowerDistribution | None = None
    type: PowerType | None = None


class ProviderPnrReportListResponse(BaseModel):
    code: int | None = None
    data: list[ProviderPnrReport] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class RailcardListResponse(BaseModel):
    code: int | None = None
    data: list[Railcard] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class RateCodeListResponse(BaseModel):
    code: int | None = None
    data: list[RateCode] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class RateCodeResponse(BaseModel):
    code: int | None = None
    data: RateCode | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class RealTimeFlightInfo(BaseModel):
    aircraft: str | None = None
    arrival_gate: str | None = Field(None, alias="arrivalGate")
    arrival_local_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalLocalDateTime",
    )
    arrival_status: ScheduleStatus | None = Field(None, alias="arrivalStatus")
    arrival_terminal: str | None = Field(None, alias="arrivalTerminal")
    arrival_utc_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalUtcDateTime",
    )
    departure_gate: str | None = Field(None, alias="departureGate")
    departure_local_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureLocalDateTime",
    )
    departure_status: ScheduleStatus | None = Field(None, alias="departureStatus")
    departure_terminal: str | None = Field(None, alias="departureTerminal")
    departure_utc_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureUtcDateTime",
    )
    link_map: str | None = Field(None, alias="linkMap")
    primary_status: PrimaryFlightStatus | None = Field(None, alias="primaryStatus")
    secondary_status: SecondaryFlightStatus | None = Field(
        None,
        alias="secondaryStatus",
    )


class Reason(BaseModel):
    active: bool | None = None
    id: int | None = None
    position: int | None = None
    reason: str | None = None
    reason_type: ReasonType | None = Field(None, alias="reasonType")
    reservation_type: ReservationType | None = Field(None, alias="reservationType")


class ReasonListResponse(BaseModel):
    code: int | None = None
    data: list[Reason] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ReportAirlinesByOrgListResponse(BaseModel):
    code: int | None = None
    data: list[ReportAirlinesByOrg] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ReportCar(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    brand: str | None = None
    car_class_name: str | None = Field(None, alias="carClassName")
    car_name: str | None = Field(None, alias="carName")
    car_type: str | None = Field(None, alias="carType")
    consumer_count: int | None = Field(None, alias="consumerCount")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    days: int | None = None
    dropoff: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: Ext | None = None
    flags: int | None = None
    hours: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    pickup: str | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class ReportCityPairsListResponse(BaseModel):
    code: int | None = None
    data: list[ReportCityPairs] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ReportFlightByCityPairListResponse(BaseModel):
    code: int | None = None
    data: list[ReportFlightByCityPair] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ReportFlightByEmployeeListResponse(BaseModel):
    code: int | None = None
    data: list[ReportFlightByEmployee] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ReportFlightSegment(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    departure_station: str | None = Field(None, alias="departureStation")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: Ext | None = None
    fare_type: FareType | None = Field(None, alias="fareType")
    flags: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    segments: int | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class ReportHotel(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    brand_code: str | None = Field(None, alias="brandCode")
    chain_code: str | None = Field(None, alias="chainCode")
    chain_name: str | None = Field(None, alias="chainName")
    city: str | None = None
    country: str | None = None
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: Ext | None = None
    flags: int | None = None
    guests: int | None = None
    hotel_code: str | None = Field(None, alias="hotelCode")
    hotel_name: str | None = Field(None, alias="hotelName")
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class ReportOrganizationSpendInfoResponse(BaseModel):
    code: int | None = None
    data: ReportOrganizationSpendInfo | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ReportProspectiveCustomerListResponse(BaseModel):
    code: int | None = None
    data: list[ReportProspectiveCustomer] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class ReportTrain(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    booker_id: int | None = Field(None, alias="bookerId")
    consumer_count: int | None = Field(None, alias="consumerCount")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    departure_station: str | None = Field(None, alias="departureStation")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: Ext | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    flags: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    segment_count: int | None = Field(None, alias="segmentCount")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class ReqItinerary(BaseModel):
    acct_code: str | None = Field(None, alias="acctCode")
    currency: str | None = None
    office_id: str | None = Field(None, alias="officeId")
    pcc: str | None = None
    pos: str | None = None
    psgrs: list[str] = Field(default_factory=list)
    segments: list[ReqItinerarySegment] = Field(default_factory=list)
    src: str | None = None
    travel_agency_id: str | None = Field(None, alias="travelAgencyId")


class Reservation(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: IsReservationExt | None = None
    flags: int | None = None
    id: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    type: ReservationType | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class ReservationFieldResponse(BaseModel):
    code: int | None = None
    data: ReservationField | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ReservationReport(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: Ext | None = None
    flags: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class ReservationResponse(BaseModel):
    code: int | None = None
    data: Reservation | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ResourceNotificationResponseResponse(BaseModel):
    code: int | None = None
    data: ResourceNotificationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class RespItineraryFare(BaseModel):
    advance_change: list[str] = Field(alias="advanceChange", default_factory=list)
    brand: str | None = None
    cancellation: list[str] = Field(default_factory=list)
    segments: list[RespItinerarySegment] = Field(default_factory=list)


class RespItineraryLeg(BaseModel):
    amenity_summary: str | None = Field(None, alias="amenitySummary")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    fares: list[RespItineraryFare] = Field(default_factory=list)
    total_travel_time: str | None = Field(None, alias="totalTravelTime")


class SabreOrgProfile(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    profile_hash: str | None = Field(None, alias="profileHash")
    profile_id: str | None = Field(None, alias="profileId")
    storage_type: StorageType | None = Field(None, alias="storageType")
    template_id: str | None = Field(None, alias="templateId")


class SabreOrgProfileResponse(BaseModel):
    code: int | None = None
    data: SabreOrgProfile | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SearchFlightRefData(BaseModel):
    account_code: str | None = Field(None, alias="accountCode")
    agency_code: str | None = Field(None, alias="agencyCode")
    airline: str | None = None
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    created_on_utc: AwareOrNaiveDatetime | None = Field(None, alias="createdOnUtc")
    currency: str | None = None
    flights: list[FlightRefData] = Field(default_factory=list)
    fop_flags: int | None = Field(None, alias="fopFlags")
    in_policy: bool | None = Field(None, alias="inPolicy")
    inf: int | None = None
    inner_one_way: bool | None = Field(None, alias="innerOneWay")
    itinerary_ref: str | None = Field(None, alias="itineraryRef")
    itinerary_ref_size: int | None = Field(None, alias="itineraryRefSize")
    loyalty_program_number: str | None = Field(None, alias="loyaltyProgramNumber")
    org_id: int | None = Field(None, alias="orgId")
    policy_rule_results: list[PolicyRuleResult] = Field(
        alias="policyRuleResults",
        default_factory=list,
    )
    provider_code: str | None = Field(None, alias="providerCode")
    request_type: SearchFlightsRequestType | None = Field(None, alias="requestType")
    reservation_flags: int | None = Field(None, alias="reservationFlags")
    reshop_reservation_ids: list[int] = Field(
        alias="reshopReservationIds",
        default_factory=list,
    )
    response_id: str | None = Field(None, alias="responseId")
    seat_selection_available: bool | None = Field(None, alias="seatSelectionAvailable")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")
    transaction_identifier: str | None = Field(None, alias="transactionIdentifier")
    transborder: bool | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SearchFlightsResponse(BaseModel):
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    od_count: int | None = Field(None, alias="odCount")
    ods: dict[str, OriginDestination] = Field(default_factory=dict)
    offers: list[Offer] = Field(default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    penalties: dict[str, PenaltyData] = Field(default_factory=dict)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    segments: dict[str, Segment] = Field(default_factory=dict)


class SearchFlightsResponseResponse(BaseModel):
    code: int | None = None
    data: SearchFlightsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SearchHotelsResponse(BaseModel):
    hotels: list[HotelOffer] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SearchHotelsResponseResponse(BaseModel):
    code: int | None = None
    data: SearchHotelsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SearchTrainRequest(BaseModel):
    ods: list[TrainOriginDestinationRequest] = Field(default_factory=list)
    open_return: bool | None = Field(None, alias="openReturn")
    org_id: int | None = Field(None, alias="orgId")
    railcards: list[int] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    reservation_ids: list[int] = Field(alias="reservationIds", default_factory=list)
    trip_id: int | None = Field(None, alias="tripId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class Seat(BaseModel):
    display_text: str | None = Field(None, alias="displayText")
    flatness: str | None = None
    leg_room: SeatLegRoom | None = Field(None, alias="legRoom")
    pitch: str | None = None
    wider_seat: bool | None = Field(None, alias="widerSeat")


class SeatAssignment(BaseModel):
    consumer_index: int | None = Field(None, alias="consumerIndex")
    preference: SeatPreference | None = None
    seat_key: str | None = Field(None, alias="seatKey")
    segment_key: str | None = Field(None, alias="segmentKey")


class SeatMapSeat(BaseModel):
    approval_required: bool | None = Field(None, alias="approvalRequired")
    booking_blocked: bool | None = Field(None, alias="bookingBlocked")
    chargeable: bool | None = None
    column: str | None = None
    exit_row: bool | None = Field(None, alias="exitRow")
    flags: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    leg_space: bool | None = Field(None, alias="legSpace")
    no_infant: bool | None = Field(None, alias="noInfant")
    no_seat: bool | None = Field(None, alias="noSeat")
    occupied: bool | None = None
    preferred: bool | None = None
    premium: bool | None = None
    price: float | None = None
    restricted_recline: bool | None = Field(None, alias="restrictedRecline")
    row: str | None = None
    seat_key: str | None = Field(None, alias="seatKey")
    seat_type: str | None = Field(None, alias="seatType")
    status: SeatStatus | None = None
    taxes: float | None = None
    to_be_left_vacant: bool | None = Field(None, alias="toBeLeftVacant")


class SecureCreditCard(BaseModel):
    address: Address | None = None
    cvc: str | None = None
    exp: str | None = Field(None, examples=["2022-03"])
    holder_name: str | None = Field(None, alias="holderName")
    number: str | None = None
    type: UserCreditCardType | None = None


class Settlement(BaseModel):
    amount: float | None = None
    currency: str | None = None
    date: AwareOrNaiveDatetime | None = None
    description: str | None = None
    id: int | None = None
    label: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    reservation_id: int | None = Field(None, alias="reservationId")
    reservation_type: ReservationType | None = Field(None, alias="reservationType")
    type: SettlementType | None = None
    user_id: int | None = Field(None, alias="userId")


class Summary(BaseModel):
    aircraft: DisplayTextSummary | None = None
    beverage: DisplayTextSummary | None = None
    entertainment: DisplayTextSummary | None = None
    fresh_food: DisplayTextSummary | None = Field(None, alias="freshFood")
    id: str | None = None
    layout: DisplayTextSummary | None = None
    power: DisplayTextSummary | None = None
    seat: DisplayTextSummary | None = None
    wifi: DisplayTextSummary | None = None


class Supplier(BaseModel):
    id: int | None = None
    supplier_code: str | None = Field(None, alias="supplierCode")
    supplier_type: SupplierType | None = Field(None, alias="supplierType")
    user_id: int | None = Field(None, alias="userId")


class SupplierListResponse(BaseModel):
    code: int | None = None
    data: list[Supplier] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class SupplierResponse(BaseModel):
    code: int | None = None
    data: Supplier | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class TrainOffer(BaseModel):
    fares: dict[str, list[TrainPricedFare]] = Field(default_factory=dict)
    od_id: str | None = Field(None, alias="odId")


class TrainOriginDestinationInfo(BaseModel):
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    carrier: str | None = None
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    segments: list[TrainSegmentInfo] = Field(default_factory=list)


class TrainReservationSegment(BaseModel):
    applied_discount_id: str | None = Field(None, alias="appliedDiscountId")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_station_name: str | None = Field(None, alias="arrivalStationName")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    carrier_name: str | None = Field(None, alias="carrierName")
    class_code: str | None = Field(None, alias="classCode")
    comfort_class_id: str | None = Field(None, alias="comfortClassId")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_station_name: str | None = Field(None, alias="departureStationName")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    fare_condition_id: str | None = Field(None, alias="fareConditionId")
    fare_condition_ids: list[str] = Field(
        alias="fareConditionIds",
        default_factory=list,
    )
    fare_name: str | None = Field(None, alias="fareName")
    fare_rules: str | None = Field(None, alias="fareRules")
    logo: str | None = None
    ref: str | None = None
    seats: list[TrainSeat] = Field(default_factory=list)
    tickets: list[str] = Field(default_factory=list)
    train_name: str | None = Field(None, alias="trainName")
    train_number: str | None = Field(None, alias="trainNumber")
    transport_mode: TrainTransportMode | None = Field(None, alias="transportMode")


class TrainSegment(BaseModel):
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    carrier_name: str | None = Field(None, alias="carrierName")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    equipment: str | None = None
    logo: str | None = None
    train_name: str | None = Field(None, alias="trainName")
    train_number: str | None = Field(None, alias="trainNumber")
    transport_mode: TrainTransportMode | None = Field(None, alias="transportMode")


class TravelPolicyParameter(BaseModel):
    description: str | None = None
    max_value: float | None = Field(None, alias="maxValue")
    min_value: float | None = Field(None, alias="minValue")
    name: str | None = None
    required: bool | None = None
    table: LookupTable | None = None
    type: TravelPolicyParameterType | None = None
    values: list[str] = Field(default_factory=list)


class Summary1(BaseModel):
    empty: bool | None = None
    first: TripSummaryLine | None = None
    last: TripSummaryLine | None = None


class Trip(BaseModel):
    agency_billed_on: AwareOrNaiveDatetime | None = Field(None, alias="agencyBilledOn")
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_flags: int | None = Field(None, alias="agencyFlags")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    arranger_ids: list[int] = Field(alias="arrangerIds", default_factory=list)
    booker_ids: list[int] = Field(alias="bookerIds", default_factory=list)
    confirmed_boards: int | None = Field(None, alias="confirmedBoards")
    description: str | None = None
    draft_boards: int | None = Field(None, alias="draftBoards")
    end_date: date | None = Field(None, alias="endDate")
    granted_ids: list[int] = Field(alias="grantedIds", default_factory=list)
    id: int | None = None
    invitee_ids: list[int] = Field(alias="inviteeIds", default_factory=list)
    name: str | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    pending_boards: int | None = Field(None, alias="pendingBoards")
    post_processed_on: int | None = Field(None, alias="postProcessedOn")
    processing_boards: int | None = Field(None, alias="processingBoards")
    send_itinerary_at: int | None = Field(None, alias="sendItineraryAt")
    start_date: date | None = Field(None, alias="startDate")
    summary: list[TripSummaryLine] | Summary1 | None = None
    total: float | None = None
    trip_board_flags: int | None = Field(None, alias="tripBoardFlags")
    ui_flags: int | None = Field(None, alias="uiFlags")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    visibility: VisibilityType | None = None


class TripBoardRef(BaseModel):
    active: bool | None = None
    amend_id: int | None = Field(None, alias="amendId")
    amend_reservation_ids: list[int] = Field(
        alias="amendReservationIds",
        default_factory=list,
    )
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    credit: float | None = None
    currency: str | None = None
    due: float | None = None
    earlier_due: float | None = Field(None, alias="earlierDue")
    end_date: date | None = Field(None, alias="endDate")
    exception_flags: int | None = Field(None, alias="exceptionFlags")
    exception_on_id: int | None = Field(None, alias="exceptionOnId")
    fop_flags: int | None = Field(None, alias="fopFlags")
    fops: list[TripBoardFop] = Field(default_factory=list)
    id: int | None = None
    messages: list[str] = Field(default_factory=list)
    nms: int | None = None
    penalty: float | None = None
    priced_on: AwareOrNaiveDatetime | None = Field(None, alias="pricedOn")
    provider_code: str | None = Field(None, alias="providerCode")
    ref: str | None = None
    refund: float | None = None
    reservation_ids: list[int] = Field(alias="reservationIds", default_factory=list)
    reservation_type: ReservationType | None = Field(None, alias="reservationType")
    start_date: date | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    summary: list[TripSummaryLine] | Summary1 | None = None
    total: float | None = None
    trip_board_flags: int | None = Field(None, alias="tripBoardFlags")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    trip_id: int | None = Field(None, alias="tripId")
    ui_flags: int | None = Field(None, alias="uiFlags")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    user_reward_program_id: dict[str, int] = Field(
        alias="userRewardProgramId",
        default_factory=dict,
    )
    vendor: str | None = None
    waypoint_attrs: dict[str, str] = Field(alias="waypointAttrs", default_factory=dict)
    waypoint_flags: int | None = Field(None, alias="waypointFlags")


class TripMedia(BaseModel):
    id: int | None = None
    index: int | None = None
    media: Media | None = None
    media_id: int | None = Field(None, alias="mediaId")
    nms: int | None = None
    trip_id: int | None = Field(None, alias="tripId")


class UPA(BaseModel):
    categories: list[str] = Field(default_factory=list)
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fees: list[FlightAttributeFee] = Field(default_factory=list)
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    photos: list[UPAPhoto] = Field(default_factory=list)
    small_icon_url: str | None = Field(None, alias="smallIconUrl")


class Upa(BaseModel):
    att_descr: str | None = Field(None, alias="attDescr")
    categories: list[str] = Field(default_factory=list)
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    fees: list[Fee] = Field(default_factory=list)
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    optional_service_identifiers: list[OptionalServiceIdentifier] = Field(
        alias="optionalServiceIdentifiers",
        default_factory=list,
    )
    photos: list[UpaCommon] = Field(default_factory=list)
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    tours: list[UpaCommon] = Field(default_factory=list)
    videos: list[UpaCommon] = Field(default_factory=list)


class User(BaseModel):
    active: bool | None = None
    color: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    flags: int | None = None
    full_name: str | None = Field(None, alias="fullName")
    gender: Gender | None = None
    id: int | None = None
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    nms: int | None = None
    picture_url: str | None = Field(None, alias="pictureUrl")
    short_name: str | None = Field(None, alias="shortName")
    status: UserAccountStatus | None = None
    suffix: str | None = None


class UserAccount(BaseModel):
    active: bool | None = None
    agency_codes: list[str] = Field(alias="agencyCodes", default_factory=list)
    agent_sines: list[str] = Field(alias="agentSines", default_factory=list)
    color: str | None = None
    dob: date | None = None
    documents: UserDocuments | None = None
    emergency_contact: EmergencyContact | None = Field(None, alias="emergencyContact")
    first_name: str | None = Field(None, alias="firstName")
    flags: int | None = None
    full_name: str | None = Field(None, alias="fullName")
    gender: Gender | None = None
    id: int | None = None
    kyc: UserAccountKycStatus | None = None
    last_name: str | None = Field(None, alias="lastName")
    middle_name: str | None = Field(None, alias="middleName")
    nms: int | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    picture_url: str | None = Field(None, alias="pictureUrl")
    preferences: UserAccountPreferences | None = None
    primary_email: str | None = Field(None, alias="primaryEmail")
    role: UserRole | None = None
    short_name: str | None = Field(None, alias="shortName")
    status: UserAccountStatus | None = None
    suffix: str | None = None


class UserAccountListResponse(BaseModel):
    code: int | None = None
    data: list[UserAccount] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class UserAccountResponse(BaseModel):
    code: int | None = None
    data: UserAccount | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class UserCreationValidationStatus(BaseModel):
    status: UserCreationValidationStatusEnum | None = None
    user_account: UserAccount | None = Field(None, alias="userAccount")
    user_account_email: UserAccountEmail | None = Field(None, alias="userAccountEmail")


class UserListResponse(BaseModel):
    code: int | None = None
    data: list[User] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class UserProfileInfo(BaseModel):
    business_address: AddressLocation | None = Field(None, alias="businessAddress")
    corporate_loyalty_programs: list[OrgLoyaltyProgram] = Field(
        alias="corporateLoyaltyPrograms",
        default_factory=list,
    )
    home_address: AddressLocation | None = Field(None, alias="homeAddress")
    loyalty_programs: dict[str, LoyaltyProgram] = Field(
        alias="loyaltyPrograms",
        default_factory=dict,
    )
    org: Org | None = None
    org_arranger_emails: list[str] = Field(
        alias="orgArrangerEmails",
        default_factory=list,
    )
    org_credit_cards: list[CreditCard] = Field(
        alias="orgCreditCards",
        default_factory=list,
    )
    org_email: str | None = Field(None, alias="orgEmail")
    org_user: OrgUser | None = Field(None, alias="orgUser")
    primary_email: str | None = Field(None, alias="primaryEmail")
    rewards: dict[str, list[RewardProgramInfo]] = Field(default_factory=dict)
    sabre_org_profile: SabreOrgProfile | None = Field(None, alias="sabreOrgProfile")
    sabre_user_profile: SabreUserProfile | None = Field(None, alias="sabreUserProfile")
    user_account: UserAccount | None = Field(None, alias="userAccount")
    user_credit_cards: list[CreditCard] = Field(
        alias="userCreditCards",
        default_factory=list,
    )


class UserResponse(BaseModel):
    code: int | None = None
    data: User | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class UserTie(BaseModel):
    dst_user_id: int | None = Field(None, alias="dstUserId")
    id: int | None = None
    src_user_id: int | None = Field(None, alias="srcUserId")
    tie_type: UserTieType | None = Field(None, alias="tieType")


class UserTieResponse(BaseModel):
    code: int | None = None
    data: UserTie | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Wifi(BaseModel):
    chance: WifiChance | None = None
    cost: AmenityCost | None = None


class AdvanceChange(BaseModel):
    after_departure: AdvanceChangeInner | None = Field(None, alias="afterDeparture")
    anytime: AdvanceChangeInner | None = None
    before_departure: AdvanceChangeInner | None = Field(None, alias="beforeDeparture")
    id: str | None = None


class Approval(BaseModel):
    approvals: list[ApprovalItem] = Field(default_factory=list)
    booker_comment: str | None = Field(None, alias="bookerComment")
    booker_id: int | None = Field(None, alias="bookerId")
    canceled_by: int | None = Field(None, alias="canceledBy")
    cancelled_by: int | None = Field(None, alias="cancelledBy")
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    policy_ids: list[int] = Field(alias="policyIds", default_factory=list)
    status: ApprovalStatus | None = None
    submitted_at: AwareOrNaiveDatetime | None = Field(None, alias="submittedAt")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    trip_id: int | None = Field(None, alias="tripId")
    trip_name: str | None = Field(None, alias="tripName")


class ApprovalList(BaseModel):
    approval: list[Approval] = Field(default_factory=list)
    approvals: list[Approval] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)


class ApprovalListResponse(BaseModel):
    code: int | None = None
    data: ApprovalList | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ApprovalResponse(BaseModel):
    code: int | None = None
    data: Approval | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Cancellation(BaseModel):
    after_departure: CancellationInner | None = Field(None, alias="afterDeparture")
    anytime: CancellationInner | None = None
    before_departure: CancellationInner | None = Field(None, alias="beforeDeparture")
    id: str | None = None


class CarReservation(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: CarReservationExt | None = None
    flags: int | None = None
    id: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    type: ReservationType | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class CarReservationResponse(BaseModel):
    code: int | None = None
    data: CarReservation | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class CarryOnBaggage(BaseModel):
    assessment: Assessment | None = None
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    free_bags: FreeBaggageData | None = Field(None, alias="freeBags")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    paid_bags: list[PaidBaggageData] = Field(alias="paidBags", default_factory=list)
    small_icon_url: str | None = Field(None, alias="smallIconUrl")


class CheckedBaggage(BaseModel):
    assessment: Assessment | None = None
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    description: str | None = None
    free_bags: FreeBaggageData | None = Field(None, alias="freeBags")
    headline: str | None = None
    id: str | None = None
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    paid_bags: list[PaidBaggageData] = Field(alias="paidBags", default_factory=list)
    small_icon_url: str | None = Field(None, alias="smallIconUrl")


class Entertainment(BaseModel):
    cost: Cost | None = None
    display_text: str | None = Field(None, alias="displayText")
    exists: Exists | None = None
    id: str | None = None
    offerings: EntertainmentOfferingsGroup | None = None
    quality: Quality | None = None
    type: TypeEnum | None = None
    updated_at: str | None = Field(None, alias="updatedAt")


class FareOffer(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    free_luggage_allowance: int | None = Field(None, alias="freeLuggageAllowance")
    origin_destination: OriginDestination | None = Field(
        None,
        alias="originDestination",
    )
    penalties: list[Penalty] = Field(default_factory=list)
    private_fare_type: str | None = Field(None, alias="privateFareType")
    rate_code: str | None = Field(None, alias="rateCode")
    ref_data: SearchFlightRefData | None = Field(None, alias="refData")
    segments: dict[str, Segment] = Field(default_factory=dict)
    ticket_penalties: int | None = Field(None, alias="ticketPenalties")
    ticket_perks: int | None = Field(None, alias="ticketPerks")


class FlightReservationExt(BaseModel):
    air_price: float | None = Field(None, alias="airPrice")
    ancillaries: list[FlightReservationAncillary] = Field(default_factory=list)
    ancillary_price: float | None = Field(None, alias="ancillaryPrice")
    ancillary_taxes: float | None = Field(None, alias="ancillaryTaxes")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    od: FlightReservationOd | None = None
    seat_price: float | None = Field(None, alias="seatPrice")
    seat_taxes: float | None = Field(None, alias="seatTaxes")
    seats: list[FlightReservationSeat] = Field(default_factory=list)
    ssr: list[FlightReservationSsr] = Field(default_factory=list)
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    ticket_numbers: list[str] = Field(alias="ticketNumbers", default_factory=list)


class FtsResponse(BaseModel):
    orgs: list[Org] = Field(default_factory=list)
    user_accounts: list[UserAccount] = Field(alias="userAccounts", default_factory=list)


class FtsResponseResponse(BaseModel):
    code: int | None = None
    data: FtsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class FtsUsersByOrgResponse(BaseModel):
    user_emails: dict[str, str] = Field(alias="userEmails", default_factory=dict)
    users: list[User] = Field(default_factory=list)


class FtsUsersByOrgResponseResponse(BaseModel):
    code: int | None = None
    data: FtsUsersByOrgResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class GetTrainResponse(BaseModel):
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    org_id: int | None = Field(None, alias="orgId")
    org_projects: list[OrgProject] = Field(alias="orgProjects", default_factory=list)
    origin_destinations: list[TrainOriginDestinationInfo] = Field(
        alias="originDestinations",
        default_factory=list,
    )
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    stations: dict[str, TrainStation] = Field(default_factory=dict)
    total_price: float | None = Field(None, alias="totalPrice")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class GetTrainResponseResponse(BaseModel):
    code: int | None = None
    data: GetTrainResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class GetTripResponse(BaseModel):
    trip: Trip | None = None
    users: dict[str, User] = Field(default_factory=dict)


class GetTripResponseResponse(BaseModel):
    code: int | None = None
    data: GetTripResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class HotelInfoResponse(BaseModel):
    checkin_time: str | None = Field(None, alias="checkinTime")
    checkout_time: str | None = Field(None, alias="checkoutTime")
    description: str | None = None
    medias: list[HotelMedia] = Field(default_factory=list)
    offer: HotelOffer | None = None
    org_id: int | None = Field(None, alias="orgId")
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class HotelInfoResponseResponse(BaseModel):
    code: int | None = None
    data: HotelInfoResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class HotelReservation(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: HotelReservationExt | None = None
    flags: int | None = None
    id: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    type: ReservationType | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class HotelReservationListResponse(BaseModel):
    code: int | None = None
    data: list[HotelReservation] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class HotelReservationResponse(BaseModel):
    code: int | None = None
    data: HotelReservation | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListCarReservationResponse(BaseModel):
    car_reservations: list[CarReservation] = Field(
        alias="carReservations",
        default_factory=list,
    )


class ListCarReservationResponseResponse(BaseModel):
    code: int | None = None
    data: ListCarReservationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListOrgUserByOrgResponse(BaseModel):
    addresses: list[AddressLocation] = Field(default_factory=list)
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)
    fields: list[FieldModel] = Field(default_factory=list)
    org_user_fields: list[OrgUserField] = Field(
        alias="orgUserFields",
        default_factory=list,
    )
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)
    user_emails: dict[str, str] = Field(alias="userEmails", default_factory=dict)
    users: list[User] = Field(default_factory=list)


class ListOrgUserByOrgResponseResponse(BaseModel):
    code: int | None = None
    data: ListOrgUserByOrgResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListOrgUserByPolicyResponse(BaseModel):
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)
    users: list[User] = Field(default_factory=list)


class ListOrgUserByPolicyResponseResponse(BaseModel):
    code: int | None = None
    data: ListOrgUserByPolicyResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListOrgUserByUserResponse(BaseModel):
    addresses: list[AddressLocation] = Field(default_factory=list)
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)
    orgs: list[Org] = Field(default_factory=list)


class ListOrgUserByUserResponseResponse(BaseModel):
    code: int | None = None
    data: ListOrgUserByUserResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListPolicyApprover(BaseModel):
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)
    users: list[User] = Field(default_factory=list)


class ListPolicyApproverResponse(BaseModel):
    code: int | None = None
    data: ListPolicyApprover | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListReservationResponse(BaseModel):
    reservations: list[Reservation] = Field(default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)


class ListReservationResponseResponse(BaseModel):
    code: int | None = None
    data: ListReservationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListTripsResponse(BaseModel):
    trips: list[Trip] = Field(default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)


class ListTripsResponseResponse(BaseModel):
    code: int | None = None
    data: ListTripsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListUserAccountsResponse(BaseModel):
    user_account_emails: list[UserAccountEmail] = Field(
        alias="userAccountEmails",
        default_factory=list,
    )
    user_accounts: list[UserAccount] = Field(alias="userAccounts", default_factory=list)


class ListUserAccountsResponseResponse(BaseModel):
    code: int | None = None
    data: ListUserAccountsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListUserTieResponse(BaseModel):
    ties: list[UserTie] = Field(default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)


class ListUserTieResponseResponse(BaseModel):
    code: int | None = None
    data: ListUserTieResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class MiscReservation(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: MiscReservationExt | None = None
    flags: int | None = None
    id: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    type: ReservationType | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class Notification(BaseModel):
    count: int | None = None
    ext: Ext | None = None
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    parents: list[ParentResource] = Field(default_factory=list)
    read: bool | None = None
    sample_msg_text: str | None = Field(None, alias="sampleMsgText")
    sample_user_ids: list[int] = Field(alias="sampleUserIds", default_factory=list)
    seen: bool | None = None
    status: OperationStatus | None = None
    target_id: int | None = Field(None, alias="targetId")
    target_type: ResourceType | None = Field(None, alias="targetType")
    time: int | None = None
    trip_name: str | None = Field(None, alias="tripName")
    type: NotificationType | None = None


class NotificationResponse(BaseModel):
    code: int | None = None
    data: Notification | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class PolicyRule(BaseModel):
    action: PolicyRuleAction | None = None
    active: bool | None = None
    code: PolicyRuleSpecs | None = None
    exceptions: list[PolicyRuleException] = Field(default_factory=list)
    id: int | None = None
    nms: int | None = None
    policy_id: int | None = Field(None, alias="policyId")
    vars: dict[str, dict[str, Any]] = Field(default_factory=dict)


class PolicyRuleResponse(BaseModel):
    code: int | None = None
    data: PolicyRule | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class PolicyRuleSpec(BaseModel):
    category: SearchCategory | None = None
    code: str | None = None
    description: str | None = None
    params: list[TravelPolicyParameter] = Field(default_factory=list)
    post: bool | None = None


class PolicyRuleSpecListResponse(BaseModel):
    code: int | None = None
    data: list[PolicyRuleSpec] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class Post(BaseModel):
    active: bool | None = None
    archive_on: int | None = Field(None, alias="archiveOn")
    followers: list[int] = Field(default_factory=list)
    id: int | None = None
    msg: Msg | None = None
    nms: int | None = None
    ui_flags: int | None = Field(None, alias="uiFlags")
    users: dict[str, User] = Field(default_factory=dict)
    wall_id: int | None = Field(None, alias="wallId")


class PostResponse(BaseModel):
    code: int | None = None
    data: Post | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ReportByOrgResponse(BaseModel):
    org_users: list[OrgUser] = Field(alias="orgUsers", default_factory=list)
    reports: list[dict[str, Any]] = Field(default_factory=list)
    user_emails: dict[str, str] = Field(alias="userEmails", default_factory=dict)
    users: list[User] = Field(default_factory=list)


class ReportByOrgResponseResponse(BaseModel):
    code: int | None = None
    data: ReportByOrgResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class RespItineraryData(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    legs: list[RespItineraryLeg] = Field(default_factory=list)


class ReviewTripBoardRefsResponse(BaseModel):
    not_in_policy_reasons: list[Reason] = Field(
        alias="notInPolicyReasons",
        default_factory=list,
    )
    not_preferred_reasons: list[Reason] = Field(
        alias="notPreferredReasons",
        default_factory=list,
    )
    org_projects: list[OrgProject] = Field(alias="orgProjects", default_factory=list)
    trip_board_ref_ids: list[int] = Field(alias="tripBoardRefIds", default_factory=list)
    user_to_reward_program_ids: dict[str, list[int]] = Field(
        alias="userToRewardProgramIds",
        default_factory=dict,
    )
    users: dict[str, User] = Field(default_factory=dict)
    vendor_to_reward_programs: dict[str, dict[str, RewardProgram]] = Field(
        alias="vendorToRewardPrograms",
        default_factory=dict,
    )


class ReviewTripBoardRefsResponseResponse(BaseModel):
    code: int | None = None
    data: ReviewTripBoardRefsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SearchTrainResponse(BaseModel):
    applied_discounts: dict[str, AppliedDiscount] = Field(
        alias="appliedDiscounts",
        default_factory=dict,
    )
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    comfort_classes: dict[str, ComfortClass] = Field(
        alias="comfortClasses",
        default_factory=dict,
    )
    fare_conditions: dict[str, FareConditions] = Field(
        alias="fareConditions",
        default_factory=dict,
    )
    next_page_ref: str | None = Field(None, alias="nextPageRef")
    od_count: int | None = Field(None, alias="odCount")
    od_index: int | None = Field(None, alias="odIndex")
    ods: dict[str, TrainOriginDestination] = Field(default_factory=dict)
    offers: list[TrainOffer] = Field(default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    page_replaces_previous_results: bool | None = Field(
        None,
        alias="pageReplacesPreviousResults",
    )
    prev_page_ref: str | None = Field(None, alias="prevPageRef")
    railcards: dict[str, Railcard] = Field(default_factory=dict)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    segments: dict[str, TrainSegment] = Field(default_factory=dict)
    stations: dict[str, TrainStation] = Field(default_factory=dict)


class SearchTrainResponseResponse(BaseModel):
    code: int | None = None
    data: SearchTrainResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SeatMapRow(BaseModel):
    exit_row: bool | None = Field(None, alias="exitRow")
    row: int | None = None
    seats: list[SeatMapSeat] = Field(default_factory=list)


class SegmentAmenityData(BaseModel):
    aircraft: Aircraft | None = None
    beverage: Beverage | None = None
    entertainement: Entertainement | None = None
    food: Food | None = None
    layout: Layout | None = None
    power: Power | None = None
    seat: Seat | None = None
    wifi: Wifi | None = None


class SegmentInfo(BaseModel):
    airline: str | None = None
    amenities: SegmentAmenityData | None = None
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    depart_time: AwareOrNaiveDatetime | None = Field(None, alias="departTime")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    flight_class: FlightClass | None = Field(None, alias="flightClass")
    flight_class_premium: bool | None = Field(None, alias="flightClassPremium")
    flight_number: str | None = Field(None, alias="flightNumber")
    operating_airline: str | None = Field(None, alias="operatingAirline")
    real_time_info: RealTimeFlightInfo | None = Field(None, alias="realTimeInfo")
    upa_list: list[UPA] = Field(alias="upaList", default_factory=list)
    uta_list: list[UTA] = Field(alias="utaList", default_factory=list)


class TrainReservationOd(BaseModel):
    allowed_arrival_stations: list[str] = Field(
        alias="allowedArrivalStations",
        default_factory=list,
    )
    allowed_departure_stations: list[str] = Field(
        alias="allowedDepartureStations",
        default_factory=list,
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_station_name: str | None = Field(None, alias="arrivalStationName")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_station_name: str | None = Field(None, alias="departureStationName")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_restriction: str | None = Field(None, alias="fareRestriction")
    fare_type: FareType | None = Field(None, alias="fareType")
    railcard_ids: list[int] = Field(alias="railcardIds", default_factory=list)
    requested_arrival_station: str | None = Field(None, alias="requestedArrivalStation")
    requested_departure_station: str | None = Field(
        None,
        alias="requestedDepartureStation",
    )
    route_restriction: str | None = Field(None, alias="routeRestriction")
    seat_reservability: TrainSeatReservabilityType | None = Field(
        None,
        alias="seatReservability",
    )
    segments: list[TrainReservationSegment] = Field(default_factory=list)
    tickets: list[TrainReservationTicket] = Field(default_factory=list)


class TripBoard(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_flags: int | None = Field(None, alias="agencyFlags")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    end_date: date | None = Field(None, alias="endDate")
    exception_flags: int | None = Field(None, alias="exceptionFlags")
    fees: list[TripBoardFee] = Field(default_factory=list)
    id: int | None = None
    nms: int | None = None
    notes: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    owned_by: str | None = Field(None, alias="ownedBy")
    processing_flags: int | None = Field(None, alias="processingFlags")
    record_locators: list[str] = Field(alias="recordLocators", default_factory=list)
    refs: list[TripBoardRef] = Field(default_factory=list)
    start_date: date | None = Field(None, alias="startDate")
    status: TripBoardStatus | None = None
    status_changed_on: AwareOrNaiveDatetime | None = Field(
        None,
        alias="statusChangedOn",
    )
    summary: list[TripSummaryLine] | Summary1 | None = None
    sync_interval: int | None = Field(None, alias="syncInterval")
    sync_on: AwareOrNaiveDatetime | None = Field(None, alias="syncOn")
    trip_board_flags: int | None = Field(None, alias="tripBoardFlags")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    ui_flags: int | None = Field(None, alias="uiFlags")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    waypoint_flags: int | None = Field(None, alias="waypointFlags")


class Amenity(BaseModel):
    aircrafts: list[Aircraft] = Field(default_factory=list)
    beverages: list[Beverage] = Field(default_factory=list)
    entertainments: list[Entertainment] = Field(default_factory=list)
    fresh_foods: list[FreshFood] = Field(alias="freshFoods", default_factory=list)
    layouts: list[Layout] = Field(default_factory=list)
    powers: list[Power] = Field(default_factory=list)
    seats: list[Seat] = Field(default_factory=list)
    wifis: list[Wifi] = Field(default_factory=list)


class FeedResponse(BaseModel):
    down_to: int | None = Field(None, alias="downTo")
    orgs: list[Org] = Field(default_factory=list)
    posts: list[Post] = Field(default_factory=list)
    up_from: int | None = Field(None, alias="upFrom")
    users: list[User] = Field(default_factory=list)
    walls: list[Wall] = Field(default_factory=list)


class FeedResponseResponse(BaseModel):
    code: int | None = None
    data: FeedResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class FlightInfo(BaseModel):
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    depart_time: AwareOrNaiveDatetime | None = Field(None, alias="departTime")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    restricted_fare: bool | None = Field(None, alias="restrictedFare")
    segments: list[SegmentInfo] = Field(default_factory=list)


class FlightItem(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    airline: str | None = None
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    airline_status: VendorStatusType | None = Field(None, alias="airlineStatus")
    change_price: PriceSummary | None = Field(None, alias="changePrice")
    flights: list[FlightInfo] = Field(default_factory=list)
    in_policy: bool | None = Field(None, alias="inPolicy")
    org_id: int | None = Field(None, alias="orgId")
    rate_code: str | None = Field(None, alias="rateCode")
    reshop_reservation_ids: list[int] = Field(
        alias="reshopReservationIds",
        default_factory=list,
    )
    seat_selection_available: bool | None = Field(None, alias="seatSelectionAvailable")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")
    transborder: bool | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class FlightReservation(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: FlightReservationExt | None = None
    flags: int | None = None
    id: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    type: ReservationType | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class FlightReservationResponse(BaseModel):
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    flight: FlightReservation | None = None


class FlightReservationResponseResponse(BaseModel):
    code: int | None = None
    data: FlightReservationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListFlightReservationsResponse(BaseModel):
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    reservations: list[FlightReservation] = Field(default_factory=list)


class ListFlightReservationsResponseResponse(BaseModel):
    code: int | None = None
    data: ListFlightReservationsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListNotificationsResponse(BaseModel):
    down_to: int | None = Field(None, alias="downTo")
    notifications: list[Notification] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)


class ListNotificationsResponseResponse(BaseModel):
    code: int | None = None
    data: ListNotificationsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class Policy(BaseModel):
    action: PolicyAction | None = None
    active: bool | None = None
    approver_count: int | None = Field(None, alias="approverCount")
    enforce_approval: bool | None = Field(None, alias="enforceApproval")
    guest_count: int | None = Field(None, alias="guestCount")
    id: int | None = None
    label: str | None = None
    message_for_reservation: dict[str, str] = Field(
        alias="messageForReservation",
        default_factory=dict,
    )
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    policy_rules: list[PolicyRule] = Field(alias="policyRules", default_factory=list)
    type: PolicyType | None = None
    user_count: int | None = Field(None, alias="userCount")


class PolicyListResponse(BaseModel):
    code: int | None = None
    data: list[Policy] = Field(default_factory=list)
    error: str | None = None
    status: ResponseStatus | None = None


class PolicyResponse(BaseModel):
    code: int | None = None
    data: Policy | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class RespData(BaseModel):
    advance_change: list[AdvanceChange] = Field(
        alias="advanceChange",
        default_factory=list,
    )
    amenity: Amenity | None = None
    amenity_summary: list[Summary] = Field(alias="amenitySummary", default_factory=list)
    boarding_priority: list[BoardingPriority] = Field(
        alias="boardingPriority",
        default_factory=list,
    )
    brand: list[Brand] = Field(default_factory=list)
    cancellation: list[Cancellation] = Field(default_factory=list)
    carry_on_bag: list[CarryOnBaggage] = Field(alias="carryOnBag", default_factory=list)
    check_in_priority: list[CheckInPriority] = Field(
        alias="checkInPriority",
        default_factory=list,
    )
    checked_bag: list[CheckedBaggage] = Field(alias="checkedBag", default_factory=list)
    lounge_access: list[LoungeAccess] = Field(
        alias="loungeAccess",
        default_factory=list,
    )
    same_day_change: list[SameDayChange] = Field(
        alias="sameDayChange",
        default_factory=list,
    )
    seat_selection: list[SeatSelection] = Field(
        alias="seatSelection",
        default_factory=list,
    )
    upa: list[Upa] = Field(default_factory=list)
    upgrade_eligibility: list[UpgradeEligibility] = Field(
        alias="upgradeEligibility",
        default_factory=list,
    )


class RespItinerary(BaseModel):
    data: RespItineraryData | None = None
    errors: RespItineraryErrors | None = None
    is_lcc: bool | None = Field(None, alias="isLcc")
    rq: ReqItinerary | None = None
    valid: bool | None = None


class ReviewFlightsResponse(BaseModel):
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    currency: str | None = None
    items: dict[str, FlightItem] = Field(default_factory=dict)
    refs: list[str] = Field(default_factory=list)
    reservations: dict[str, FlightReservation] = Field(default_factory=dict)
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")
    user_to_reward_program_ids: dict[str, list[int]] = Field(
        alias="userToRewardProgramIds",
        default_factory=dict,
    )
    users: dict[str, User] = Field(default_factory=dict)
    vendor_to_reward_programs: dict[str, dict[str, RewardProgram]] = Field(
        alias="vendorToRewardPrograms",
        default_factory=dict,
    )


class ReviewFlightsResponseResponse(BaseModel):
    code: int | None = None
    data: ReviewFlightsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class SeatMapCabin(BaseModel):
    column_layout: str | None = Field(None, alias="columnLayout")
    columns: list[SeatMapColumnInfo] = Field(default_factory=list)
    deck: SeatMapDeck | None = None
    first_row: int | None = Field(None, alias="firstRow")
    last_row: int | None = Field(None, alias="lastRow")
    rows: list[SeatMapRow] = Field(default_factory=list)


class SeatMapSegment(BaseModel):
    cabins: list[SeatMapCabin] = Field(default_factory=list)
    currency: str | None = None
    reservation_id: int | None = Field(None, alias="reservationId")
    seat_types: dict[str, SeatType] = Field(alias="seatTypes", default_factory=dict)
    segment_key: str | None = Field(None, alias="segmentKey")
    status: SeatMapSegmentStatus | None = None
    transaction_identifier: str | None = Field(None, alias="transactionIdentifier")


class TrainReservationExt(BaseModel):
    applied_discounts: list[AppliedDiscount] = Field(
        alias="appliedDiscounts",
        default_factory=list,
    )
    carrier_code: str | None = Field(None, alias="carrierCode")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    comfort_classes: list[ComfortClass] = Field(
        alias="comfortClasses",
        default_factory=list,
    )
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    delivery_option: str | None = Field(None, alias="deliveryOption")
    discount_amount: float | None = Field(None, alias="discountAmount")
    enabled_seat_preferences_flags: int | None = Field(
        None,
        alias="enabledSeatPreferencesFlags",
    )
    external_id: str | None = Field(None, alias="externalId")
    fare_conditions: list[FareConditions] = Field(
        alias="fareConditions",
        default_factory=list,
    )
    has_travelcard: bool | None = Field(None, alias="hasTravelcard")
    od: TrainReservationOd | None = None
    open_return_until: date | None = Field(None, alias="openReturnUntil")
    railcards: list[Railcard] = Field(default_factory=list)
    requested_railcard_ids: list[int] = Field(
        alias="requestedRailcardIds",
        default_factory=list,
    )
    supported_delivery_options: list[DeliveryOption] = Field(
        alias="supportedDeliveryOptions",
        default_factory=list,
    )
    terms_and_conditions: str | None = Field(None, alias="termsAndConditions")
    terms_and_conditions_acceptance: bool | None = Field(
        None,
        alias="termsAndConditionsAcceptance",
    )
    terms_and_conditions_label: str | None = Field(
        None,
        alias="termsAndConditionsLabel",
    )
    terms_and_conditions_list: list[TermsAndConditions] = Field(
        alias="termsAndConditionsList",
        default_factory=list,
    )
    ticket_collection_codes: str | None = Field(None, alias="ticketCollectionCodes")
    train_seat_preference_flags: int | None = Field(
        None,
        alias="trainSeatPreferenceFlags",
    )
    transaction_id: str | None = Field(None, alias="transactionId")


class ApprovalInfo(BaseModel):
    draft_approval: Approval | None = Field(None, alias="draftApproval")
    org_users: list[OrgUser] = Field(alias="orgUsers", default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    sent_approval: Approval | None = Field(None, alias="sentApproval")
    ui_flags: int | None = Field(None, alias="uiFlags")
    users: list[User] = Field(default_factory=list)


class ApprovalInfoResponse(BaseModel):
    code: int | None = None
    data: ApprovalInfo | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class FlightDetailInformation(BaseModel):
    airline: str | None = None
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    airline_status: VendorStatusType | None = Field(None, alias="airlineStatus")
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    flights: list[FlightInfo] = Field(default_factory=list)
    in_policy: bool | None = Field(None, alias="inPolicy")
    org_id: int | None = Field(None, alias="orgId")
    org_projects: list[OrgProject] = Field(alias="orgProjects", default_factory=list)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    rate_codes: list[str] = Field(alias="rateCodes", default_factory=list)
    seat_selection_available: bool | None = Field(None, alias="seatSelectionAvailable")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class FlightSeatMapResponse(BaseModel):
    segments: list[SeatMapSegment] = Field(default_factory=list)


class FlightSeatMapResponseResponse(BaseModel):
    code: int | None = None
    data: FlightSeatMapResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OfferPolicyInfo(BaseModel):
    orgs: list[Org] = Field(default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    refs: list[RefPolicyInfo] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)


class OfferPolicyInfoResponse(BaseModel):
    code: int | None = None
    data: OfferPolicyInfo | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class OrgUserPolicyData(BaseModel):
    guest_policies: list[Policy] = Field(alias="guestPolicies", default_factory=list)
    org_policies: list[Policy] = Field(alias="orgPolicies", default_factory=list)
    org_user: OrgUser | None = Field(None, alias="orgUser")
    travel_policies: list[Policy] = Field(alias="travelPolicies", default_factory=list)


class OrgUserPolicyDataResponse(BaseModel):
    code: int | None = None
    data: OrgUserPolicyData | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class RespImpl(BaseModel):
    aircrafts: dict[str, Aircraft] = Field(default_factory=dict)
    beverages: dict[str, Beverage] = Field(default_factory=dict)
    data: RespData | None = None
    entertainments: dict[str, Entertainment] = Field(default_factory=dict)
    foods: dict[str, FreshFood] = Field(default_factory=dict)
    itineraries: list[RespItinerary] = Field(default_factory=list)
    layouts: dict[str, Layout] = Field(default_factory=dict)
    powers: dict[str, Power] = Field(default_factory=dict)
    seats: dict[str, Seat] = Field(default_factory=dict)
    wifis: dict[str, Wifi] = Field(default_factory=dict)


class TrainReservation(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    currency: str | None = None
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    ext: TrainReservationExt | None = None
    flags: int | None = None
    id: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    label: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    provider_code: str | None = Field(None, alias="providerCode")
    rlk: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    status: ReservationStatus | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    trip_id: int | None = Field(None, alias="tripId")
    ttl: AwareOrNaiveDatetime | None = None
    type: ReservationType | None = None
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    vendor: str | None = None
    vendor_pnr: str | None = Field(None, alias="vendorPnr")


class TrainReservationResponse(BaseModel):
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    stations: dict[str, TrainStation] = Field(default_factory=dict)
    train_reservation: TrainReservation | None = Field(None, alias="trainReservation")


class TrainReservationResponseResponse(BaseModel):
    code: int | None = None
    data: TrainReservationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class GetTripBoardsResponse(BaseModel):
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    boards: list[TripBoard] = Field(default_factory=list)
    car_reservations: dict[str, CarReservation] = Field(
        alias="carReservations",
        default_factory=dict,
    )
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)
    fields: list[FieldModel] = Field(default_factory=list)
    flight_reservations: dict[str, FlightReservation] = Field(
        alias="flightReservations",
        default_factory=dict,
    )
    hotel_reservations: dict[str, HotelReservation] = Field(
        alias="hotelReservations",
        default_factory=dict,
    )
    medias: list[TripMedia] = Field(default_factory=list)
    misc_reservations: dict[str, MiscReservation] = Field(
        alias="miscReservations",
        default_factory=dict,
    )
    org: Org | None = None
    reservation_fields: list[ReservationField] = Field(
        alias="reservationFields",
        default_factory=list,
    )
    reward_programs: dict[str, RewardProgram] = Field(
        alias="rewardPrograms",
        default_factory=dict,
    )
    target_resource_id: int | None = Field(None, alias="targetResourceId")
    train_carriers: dict[str, TrainCarrier] = Field(
        alias="trainCarriers",
        default_factory=dict,
    )
    train_reservations: dict[str, TrainReservation] = Field(
        alias="trainReservations",
        default_factory=dict,
    )
    train_stations: dict[str, TrainStation] = Field(
        alias="trainStations",
        default_factory=dict,
    )
    trip: Trip | None = None
    user_reward_programs: dict[str, MaskedUserRewardProgram] = Field(
        alias="userRewardPrograms",
        default_factory=dict,
    )
    users: dict[str, User] = Field(default_factory=dict)


class GetTripBoardsResponseResponse(BaseModel):
    code: int | None = None
    data: GetTripBoardsResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class ListTrainReservationResponse(BaseModel):
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    stations: dict[str, TrainStation] = Field(default_factory=dict)
    train_reservations: list[TrainReservation] = Field(
        alias="trainReservations",
        default_factory=list,
    )


class ListTrainReservationResponseResponse(BaseModel):
    code: int | None = None
    data: ListTrainReservationResponse | None = None
    error: str | None = None
    status: ResponseStatus | None = None


class RecordLocator(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    arranger_ids: list[int] = Field(alias="arrangerIds", default_factory=list)
    car_reservations: list[CarReservation] = Field(
        alias="carReservations",
        default_factory=list,
    )
    fees: list[ServiceFee] = Field(default_factory=list)
    flight_reservations: list[FlightReservation] = Field(
        alias="flightReservations",
        default_factory=list,
    )
    hotel_reservations: list[HotelReservation] = Field(
        alias="hotelReservations",
        default_factory=list,
    )
    key: str | None = None
    misc_reservations: list[MiscReservation] = Field(
        alias="miscReservations",
        default_factory=list,
    )
    pnr: str | None = None
    train_reservations: list[TrainReservation] = Field(
        alias="trainReservations",
        default_factory=list,
    )
    trip_id: int | None = Field(None, alias="tripId")


class RecordLocatorResponse(BaseModel):
    code: int | None = None
    data: RecordLocator | None = None
    error: str | None = None
    status: ResponseStatus | None = None


Msg.model_rebuild()
