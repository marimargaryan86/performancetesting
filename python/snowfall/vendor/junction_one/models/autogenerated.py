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
    )


class AddCvvRequest(BaseModel):
    card_id: int | None = Field(None, alias="cardId")
    cvv: str | None = None


class Address(BaseModel):
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    city: str | None = None
    address1: str | None = None
    address2: str | None = None
    zip_code: str | None = Field(None, alias="zipCode")
    street_number: str | None = Field(None, alias="streetNumber")


class AddressLocation(BaseModel):
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    city: str | None = None
    address1: str | None = None
    address2: str | None = None
    zip_code: str | None = Field(None, alias="zipCode")
    street_number: str | None = Field(None, alias="streetNumber")
    id: int | None = None
    is_billing: bool | None = Field(None, alias="isBilling")
    owned_by_id: int | None = Field(None, alias="ownedById")


class Data(BaseModel):
    string: AddressLocation | None = Field(None, alias="String")


class Agency(BaseModel):
    code: str | None = None
    currency: str | None = None
    name: str | None = None
    email: str | None = None
    website: str | None = None
    phone: str | None = None
    phone_after_hours: str | None = Field(None, alias="phoneAfterHours")
    phone_intl: str | None = Field(None, alias="phoneIntl")
    reservation_providers: dict[str, str] = Field(
        alias="reservationProviders",
        default_factory=dict,
    )
    flags: int | None = None
    zone_id: str | None = Field(None, alias="zoneId", examples=["America/Toronto"])


class AgencyContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None
    phone_after_hours: str | None = Field(None, alias="phoneAfterHours")
    phone_intl: str | None = Field(None, alias="phoneIntl")
    price_after_hours: float | None = Field(None, alias="priceAfterHours")
    price_currency: str | None = Field(None, alias="priceCurrency")
    availability: str | None = None
    availability_after_hours: str | None = Field(None, alias="availabilityAfterHours")
    website: str | None = None


class AgencyFlags(Enum):
    has_flight_providers = "HAS_FLIGHT_PROVIDERS"
    has_hotel_providers = "HAS_HOTEL_PROVIDERS"
    has_car_providers = "HAS_CAR_PROVIDERS"
    has_train_providers = "HAS_TRAIN_PROVIDERS"
    is_public = "IS_PUBLIC"


class AgencySettings(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    parent_agency_code: str | None = Field(None, alias="parentAgencyCode")
    config: list[str] = Field(default_factory=list)


class AgentInquiry(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    name: str | None = None
    email: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    company: str | None = None


class AgentPhone(BaseModel):
    id: int | None = None
    country: str | None = None
    phone: str | None = None


class AgentStatus(BaseModel):
    admin: bool | None = None
    agent: bool | None = None
    agencies: list[Agency] = Field(default_factory=list)


class AgodaPolicy(BaseModel):
    amount: float | None = None
    days_before_check_in: int | None = Field(None, alias="daysBeforeCheckIn")


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


class AircraftInfo(BaseModel):
    aircraft_type: str | None = Field(None, alias="aircraftType")
    weight_class: str | None = Field(None, alias="weightClass")
    tail_number: str | None = Field(None, alias="tailNumber")


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
    id: int | None = None
    name: str | None = None
    alias: str | None = None
    short_name: str | None = Field(None, alias="shortName")
    iata: str | None = None
    icao: str | None = None
    callsign: str | None = None
    country: str | None = None
    active: bool | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    ticketing_code: str | None = Field(None, alias="ticketingCode")


class AirlineLoyaltyProgram(BaseModel):
    id: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    airline_id: int | None = Field(None, alias="airlineId")
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
    id: int | None = None
    name: str | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    iata: str | None = None
    icao: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude: int | None = None
    timezone_offset: float | None = Field(None, alias="timezoneOffset")
    timezone: str | None = None
    dst: str | None = None
    airline_count: int | None = Field(None, alias="airlineCount")
    group_iata: str | None = Field(None, alias="groupIata")
    label: str | None = None
    code: str | None = None


class AmadeusUserProfile(BaseModel):
    id: int | None = None
    nms: int | None = None
    user_id: int | None = Field(None, alias="userId")
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    profile_id: str | None = Field(None, alias="profileId")
    profile_hash: str | None = Field(None, alias="profileHash")


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
    value: float | None = None
    currency: str | None = None


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


class ApiKeyMapper(BaseModel):
    pass


class Application(Enum):
    up_to = "up to"
    over = "over"


class AppliedDiscount(BaseModel):
    id: str | None = None
    code: str | None = None
    name: str | None = None
    description: str | None = None
    conditions: list[str] = Field(default_factory=list)


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
    id: int | None = None
    airline_id: int | None = None
    associated_airline_id: int | None = Field(None, alias="associatedAirlineId")


class BaggageAttributes(BaseModel):
    cxr: str | None = None
    seq_no: int | None = Field(None, alias="seqNo")
    service_type: str | None = Field(None, alias="serviceType")
    sub_code: str | None = Field(None, alias="subCode")


class BaseEntity(BaseModel):
    id: int | None = None
    nms: int | None = None


class BaseTrainStation(BaseModel):
    id: int | None = None
    code: str | None = None
    name: str | None = None
    city: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    state: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    flags: int | None = None
    label: str | None = None


class Benefit(Enum):
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


class BeverageType(Enum):
    none = "None"
    alcoholic = "Alcoholic"
    nonalcoholic = "Nonalcoholic"
    alcoholic_and_nonalcoholic = "AlcoholicAndNonalcoholic"
    premium_alcoholic = "PremiumAlcoholic"


class BoardCode(Enum):
    ro = "RO"
    bb = "BB"
    hb = "HB"
    fb = "FB"
    ai = "AI"


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


class BookingDetailRequest(BaseModel):
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")


class BookingResponse(BaseModel):
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None
    remark: str | None = None
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")


class BookingStatus(Enum):
    booking_pending = "BookingPending"
    confirmed = "Confirmed"
    failed = "Failed"
    cancelled = "Cancelled"


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
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    code: str | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    show_company_input: bool | None = Field(None, alias="showCompanyInput")
    accent_color: str | None = Field(None, alias="accentColor")
    logo_url: str | None = Field(None, alias="logoUrl")
    email_template: str | None = Field(None, alias="emailTemplate")


class CampaignUser(BaseModel):
    id: int | None = None
    nms: int | None = None
    campaign_id: int | None = Field(None, alias="campaignId")
    user_id: int | None = Field(None, alias="userId")


class CancelRequest(BaseModel):
    reference_id: str | None = Field(None, alias="referenceId")


class CancelResponse(BaseModel):
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None
    remark: str | None = None
    reference_id: str | None = Field(None, alias="referenceId")
    cancellation_fees: float | None = Field(None, alias="cancellationFees")


class CancellationInfo(BaseModel):
    pass


class CancellationPolicy(BaseModel):
    pass


class Car(BaseModel):
    make: str | None = None
    image_url: str | None = Field(None, alias="imageUrl")
    model: str | None = None
    name: str | None = None
    class_code: str | None = Field(None, alias="classCode")
    class_name: str | None = Field(None, alias="className")
    car_type: str | None = Field(None, alias="carType")
    transmission: str | None = None
    mpg: str | None = None
    features: int | None = None
    doors: str | None = None
    luggage: str | None = None
    seats: str | None = None


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
    quantity: int | None = None
    price: float | None = None
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
    selected: bool | None = None
    note: str | None = None
    price: float | None = None
    total_price: float | None = Field(None, alias="totalPrice")


class CarLocation(BaseModel):
    code: str | None = None
    vendor: str | None = None
    brand: str | None = None
    name: str | None = None
    phone: str | None = None
    hours: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance: float | None = None
    airport: bool | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    city: str | None = None
    address1: str | None = None
    address2: str | None = None
    zip_code: str | None = Field(None, alias="zipCode")
    flags: int | None = None
    ref: str | None = None
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    vendor_pref_level: int | None = Field(None, alias="vendorPrefLevel")


class CarLocationFlags(Enum):
    direct_connect = "DIRECT_CONNECT"
    preferred = "PREFERRED"
    display_policy = "DISPLAY_POLICY"
    in_policy = "IN_POLICY"
    hidden = "HIDDEN"
    approval_required = "APPROVAL_REQUIRED"
    booking_blocked = "BOOKING_BLOCKED"


class CarLocationMerged(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance: float | None = None
    airport: bool | None = None
    flags: int | None = None
    refs: list[str] = Field(default_factory=list)
    locations: list[CarLocation] = Field(default_factory=list)
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    vendor_pref_level: int | None = Field(None, alias="vendorPrefLevel")


class CarOffer(BaseModel):
    car: Car | None = None
    fare_type: CarFareType | None = Field(None, alias="fareType")
    vendor: str | None = None
    brand: str | None = None
    pick_up: str | None = Field(None, alias="pickUp")
    same_drop_off_location: bool | None = Field(None, alias="sameDropOffLocation")
    drop_off: str | None = Field(None, alias="dropOff")
    flags: int | None = None
    currency: str | None = None
    total_vehicle: float | None = Field(None, alias="totalVehicle")
    total_price: float | None = Field(None, alias="totalPrice")
    ref: str | None = None
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    vendor_pref_level: int | None = Field(None, alias="vendorPrefLevel")
    total_price_per_day: float | None = Field(None, alias="totalPricePerDay")
    in_policy: bool | None = Field(None, alias="inPolicy")
    approval_required: bool | None = Field(None, alias="approvalRequired")
    booking_blocked: bool | None = Field(None, alias="bookingBlocked")


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
    id: int | None = None
    code: str | None = None
    name: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")


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


class Channel(Enum):
    field_1 = "1"
    field_2 = "2"
    field_6 = "6"
    field_7 = "7"
    field_9 = "9"
    field_21 = "21"
    field_23 = "23"
    field_35 = "35"
    field_3958 = "3958"


class ComfortClass(BaseModel):
    id: str | None = None
    code: str | None = None
    description: str | None = None


class ConcurOrg(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    org_id: int | None = Field(None, alias="orgId")
    name: str | None = None


class ConcurOrgUser(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    org_user_id: int | None = Field(None, alias="orgUserId")
    org_id: int | None = Field(None, alias="orgId")
    employee_uid: str | None = Field(None, alias="employeeUid")


class ConcurOrgUserMapper(BaseModel):
    pass


class Condition(BaseModel):
    name: str | None = None
    description: str | None = None


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
    org_id: int | None = Field(None, alias="orgId")
    profile_id: str | None = Field(None, alias="profileId")
    name: str | None = None


class Cost(Enum):
    free = "free"
    free_or_paid = "free or paid"
    paid = "paid"
    n_a = "n/a"


class Country(BaseModel):
    id: int | None = None
    name: str | None = None
    code: str | None = None
    code2: str | None = None
    code3: str | None = None
    authority_code: str | None = Field(None, alias="authorityCode")
    continent: str | None = None
    currency_id: int | None = Field(None, alias="currencyId")


class CountryState(BaseModel):
    id: int | None = None
    name: str | None = None
    code: str | None = None
    country_id: int | None = Field(None, alias="countryId")


class CoverageEnum(Enum):
    full = "full"
    n_a = "n/a"
    none = "none"
    partial = "partial"


class CrashReport(BaseModel):
    id: int | None = None
    os: str | None = None
    os_version: str | None = Field(None, alias="osVersion")
    version_code: str | None = Field(None, alias="versionCode")
    version_name: str | None = Field(None, alias="versionName")
    phone_model: str | None = Field(None, alias="phoneModel")
    custom_data: str | None = Field(None, alias="customData")
    stack_trace: str | None = Field(None, alias="stackTrace")
    user_comment: str | None = Field(None, alias="userComment")
    nms: int | None = None
    created_on: int | None = Field(None, alias="createdOn")


class CrashReportMapper(BaseModel):
    pass


class Credit(BaseModel):
    id: int | None = None
    active: bool | None = None
    user_id: int | None = Field(None, alias="userId")
    org_id: int | None = Field(None, alias="orgId")
    vendor: str | None = None
    reference: str | None = None
    currency: str | None = None
    amount: float | None = None
    expiry: date | None = None
    source: str | None = None


class CreditCard(BaseModel):
    id: int | None = None
    stripe_id: str | None = Field(None, alias="stripeId")
    holder_name: str | None = Field(None, alias="holderName")
    card_number: str | None = Field(None, alias="cardNumber")
    type: CardType | None = None
    exp: str | None = Field(None, examples=["2022-03"])
    cvv: str | None = None
    address: Address | None = None
    reservation_types: int | None = Field(None, alias="reservationTypes")


class Currency(BaseModel):
    id: int | None = None
    name: str | None = None
    numeric_code: str | None = Field(None, alias="numericCode")
    code: str | None = None
    issuing_country: str | None = Field(None, alias="issuingCountry")


class Cvv(BaseModel):
    id: int | None = None
    card_id: int | None = Field(None, alias="cardId")
    cvv: str | None = None
    tripboard_id: int | None = Field(None, alias="tripboardId")
    expiration: AwareOrNaiveDatetime | None = None


class CvvMapper(BaseModel):
    pass


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
    id: int | None = None
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    email: str | None = None
    decision_making_role: str | None = Field(None, alias="decisionMakingRole")
    phone_number: str | None = Field(None, alias="phoneNumber")


class DemoRequestMapper(BaseModel):
    pass


class DepartmentInfo(BaseModel):
    id: int | None = None
    name: str | None = None
    member_count: int | None = Field(None, alias="memberCount")


class DistanceUnit(Enum):
    mi = "MI"
    km = "KM"


class DistributionEnum(Enum):
    all = "all"
    n_a = "n/a"
    some = "some"


class Domain(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    code: str | None = None
    name: str | None = None
    hosts: list[str] = Field(default_factory=list)
    sso_service_codes: list[str] = Field(alias="ssoServiceCodes", default_factory=list)
    org_ids: list[int] = Field(alias="orgIds", default_factory=list)
    branding: Branding | None = None


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
    id: str | None = None
    code: str | None = None
    description: str | None = None
    conditions_summary: str | None = Field(None, alias="conditionsSummary")
    conditions: list[Condition] = Field(default_factory=list)


class FareRule(BaseModel):
    fare_basis_code: str | None = Field(None, alias="fareBasisCode")
    segment_key: str | None = Field(None, alias="segmentKey")
    descriptions: dict[str, list[str]] = Field(default_factory=dict)


class FareSegment(BaseModel):
    segment_id: str | None = Field(None, alias="segmentId")
    cabin: CabinClass | None = None
    class_of_service: str | None = Field(None, alias="classOfService")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    perks: int | None = None


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
    id: int | None = None
    nms: int | None = None
    field_id: int | None = Field(None, alias="fieldId")
    code: str | None = None
    name: str | None = None
    active: bool | None = None
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
    currency_code: str | None = Field(None, alias="currencyCode")
    amount_min: str | None = Field(None, alias="amountMin")
    amount_max: str | None = Field(None, alias="amountMax")


class FlightClass(Enum):
    first = "First"
    business = "Business"
    economy = "Economy"


class FlightClassPref(BaseModel):
    value: FlightClass | None = None
    premium: bool | None = None


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
    segment_key: str | None = Field(None, alias="segmentKey")
    airline: str | None = None
    operating_airline: str | None = Field(None, alias="operatingAirline")
    duration: int | None = None
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    arrival_time_offset: int | None = Field(None, alias="arrivalTimeOffset")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    departure_time_offset: int | None = Field(None, alias="departureTimeOffset")
    flight_number: str | None = Field(None, alias="flightNumber")
    flight_class: FlightClass | None = Field(None, alias="flightClass")
    flight_class_premium: bool | None = Field(None, alias="flightClassPremium")
    service_class: str | None = Field(None, alias="serviceClass")
    fare_basis_code: str | None = Field(None, alias="fareBasisCode")
    fare_brand: str | None = Field(None, alias="fareBrand")
    aircraft: str | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    departure_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureOffsetDateTime",
    )
    arrival_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalOffsetDateTime",
    )


class FlightSearchFlight(BaseModel):
    arrival_airport: str | None = Field(None, alias="arrivalAirport")
    departure_airport: str | None = Field(None, alias="departureAirport")
    depart_date: date | None = Field(None, alias="departDate")


class FlightSeatMapRequest(BaseModel):
    refs: list[str] = Field(default_factory=list)
    reward_programs: dict[str, dict[str, int]] = Field(
        alias="rewardPrograms",
        default_factory=dict,
    )


class FlightSegmentRefData(BaseModel):
    segment_key: str | None = Field(None, alias="segmentKey")
    flight_number: str | None = Field(None, alias="flightNumber")
    marketing_airline_code: str | None = Field(None, alias="marketingAirlineCode")
    operating_airline_code: str | None = Field(None, alias="operatingAirlineCode")
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    duration: int | None = None
    class_of_service: str | None = Field(None, alias="classOfService")
    fare_basis_code: str | None = Field(None, alias="fareBasisCode")
    fare_brand: str | None = Field(None, alias="fareBrand")
    flight_class: FlightClass | None = Field(None, alias="flightClass")
    flight_class_premium: bool | None = Field(None, alias="flightClassPremium")
    fare_type: FareType | None = Field(None, alias="fareType")
    fare_name: str | None = Field(None, alias="fareName")
    aircraft_type: str | None = Field(None, alias="aircraftType")
    is_stop_segment: bool | None = Field(None, alias="isStopSegment")
    marriage_group: str | None = Field(None, alias="marriageGroup")
    cabin_class: CabinClass | None = Field(None, alias="cabinClass")
    co2_emissions: float | None = Field(None, alias="co2Emissions")


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
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    pick_up: CarLocation | None = Field(None, alias="pickUp")
    same_drop_off_location: bool | None = Field(None, alias="sameDropOffLocation")
    drop_off: CarLocation | None = Field(None, alias="dropOff")
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    extras: list[CarExtra] = Field(default_factory=list)
    insurance: list[CarInsurance] = Field(default_factory=list)
    days: int | None = None
    hours: int | None = None
    total_extras: float | None = Field(None, alias="totalExtras")
    total_insurance: float | None = Field(None, alias="totalInsurance")
    total_taxes: float | None = Field(None, alias="totalTaxes")
    total_fees: float | None = Field(None, alias="totalFees")
    total_vehicle: float | None = Field(None, alias="totalVehicle")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    flags: int | None = None
    unlimited_distance: bool | None = Field(None, alias="unlimitedDistance")
    free_distance_covered: float | None = Field(None, alias="freeDistanceCovered")
    distance_overage: float | None = Field(None, alias="distanceOverage")
    distance_unit: DistanceUnit | None = Field(None, alias="distanceUnit")
    ref: str | None = None
    invalid_reward_program: bool | None = Field(None, alias="invalidRewardProgram")
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")


class GlobalUserReward(BaseModel):
    id: int | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    idx: int | None = None
    member_id: str | None = Field(None, alias="memberId")


class Guest(BaseModel):
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    email: str | None = None


class GuestCount(BaseModel):
    adults: int | None = None
    children_ages: list[int] = Field(alias="childrenAges", default_factory=list)


class Hotel(BaseModel):
    pass


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
    non_refundable_rate: bool | None = Field(None, alias="nonRefundableRate")
    cancellable: bool | None = None
    deadline: AwareOrNaiveDatetime | None = None
    cancellation_fee_percent: float | None = Field(None, alias="cancellationFeePercent")
    prepayment_percent: float | None = Field(None, alias="prepaymentPercent")
    fully_refundable: bool | None = Field(None, alias="fullyRefundable")
    description: str | None = None


class HotelChain(BaseModel):
    id: int | None = None
    code: str | None = None
    name: str | None = None
    marketer_code: str | None = Field(None, alias="marketerCode")
    marketer_name: str | None = Field(None, alias="marketerName")
    active: bool | None = None


class HotelChainReward(BaseModel):
    id: int | None = None
    chain_name: str | None = Field(None, alias="chainName")
    group_name: str | None = Field(None, alias="groupName")
    chain_code: str | None = Field(None, alias="chainCode")
    reward_program_id: int | None = Field(None, alias="rewardProgramId")


class HotelInfoRequest(BaseModel):
    refs: list[str] = Field(default_factory=list)


class HotelMedia(BaseModel):
    thumbnail_height: int | None = Field(None, alias="thumbnailHeight")
    thumbnail_width: int | None = Field(None, alias="thumbnailWidth")
    thumbnail_url: str | None = Field(None, alias="thumbnailURL")
    media_height: int | None = Field(None, alias="mediaHeight")
    media_width: int | None = Field(None, alias="mediaWidth")
    media_url: str | None = Field(None, alias="mediaURL")


class HotelOffer(BaseModel):
    hotel: Hotel | None = None
    checkin_date: date | None = Field(None, alias="checkinDate")
    checkout_date: date | None = Field(None, alias="checkoutDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    taxes_and_fees_per_night: float | None = Field(None, alias="taxesAndFeesPerNight")
    price_per_night: float | None = Field(None, alias="pricePerNight")
    flags: int | None = None
    distance: float | None = None
    rate_codes: list[str] = Field(alias="rateCodes", default_factory=list)
    refs: list[str] = Field(default_factory=list)
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    commission_percent: float | None = Field(None, alias="commissionPercent")
    hotel_pref_level: int | None = Field(None, alias="hotelPrefLevel")


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


class HotelSearchRequest(BaseModel):
    pass


class HotelSearchResponse(BaseModel):
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None
    remark: str | None = None


class HourlyAvailableSlot(BaseModel):
    use_hour: int | None = Field(None, alias="useHour")
    check_in_time: str | None = Field(None, alias="checkInTime")


class ImportProfileAct(Enum):
    inquire = "INQUIRE"
    dry_run = "DRY_RUN"
    proceed = "PROCEED"


class ImportProfileSource(Enum):
    corp_profile = "CORP_PROFILE"
    template = "TEMPLATE"


class InitUserAccountRequest(BaseModel):
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    dob: date | None = None
    gender: Gender | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    flags: int | None = None
    token: str | None = None
    password: str | None = None
    session_expires_in: int | None = Field(None, alias="sessionExpiresIn")


class IssueCreditCard(BaseModel):
    amount: int | None = None
    expiry_date: date | None = Field(None, alias="expiryDate")
    activation_date: date | None = Field(None, alias="activationDate")
    currency: str | None = None
    multi_use: bool | None = Field(None, alias="multiUse")


class KnownTravelerNumber(BaseModel):
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    dob: AwareOrNaiveDatetime | None = None
    doc_type: str | None = Field(None, alias="docType")
    doc_number: str | None = Field(None, alias="docNumber")


class KpiCountResponse(BaseModel):
    begin: AwareOrNaiveDatetime | None = None
    end: AwareOrNaiveDatetime | None = None
    count: int | None = None


class KpiMapper(BaseModel):
    pass


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
    localizations: list[Localization] = Field(default_factory=list)
    empty: bool | None = None
    elements: list[Localization] = Field(default_factory=list)
    first: Localization | None = None
    last: Localization | None = None


class LocalizationList(RootModel[list[Localization] | LocalizationList1]):
    root: list[Localization] | LocalizationList1


class LocateCarRequest(BaseModel):
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    keyword: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    refs: list[str] = Field(default_factory=list)


class LookupTable(Enum):
    policycity = "policycity"


class MaskedUserRewardProgram(BaseModel):
    id: int | None = None
    number: str | None = None
    user_id: int | None = Field(None, alias="userId")
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    idx: int | None = None


class MediaSource(Enum):
    j1 = "J1"
    psngr1 = "PSNGR1"
    unsplash = "UNSPLASH"


class MediaType(Enum):
    image = "IMAGE"
    movie = "MOVIE"


class MessageHandlingContext(BaseModel):
    pass


class MsgDatePair(BaseModel):
    text: str | None = None
    start: date | None = None
    end: date | None = None


class MsgLocation(BaseModel):
    text: str | None = None
    place_id: str | None = Field(None, alias="placeId")
    geo: GeoLocation | None = None
    address: str | None = None
    components: list[str] = Field(default_factory=list)


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
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    org_id: int | None = Field(None, alias="orgId")
    contact_info: AgencyContactInfo | None = Field(None, alias="contactInfo")


class OrgAirlinePref(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    airline_code: str | None = Field(None, alias="airlineCode")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")


class OrgBudgetType(Enum):
    company_wide = "companyWide"


class OrgCarVendorPref(BaseModel):
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    vendor_code: str | None = Field(None, alias="vendorCode")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")


class OrgDomain(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    org_id: int | None = Field(None, alias="orgId")
    name: str | None = None


class OrgEmail(BaseModel):
    id: int | None = None
    nms: int | None = None
    email: str | None = None
    active: bool | None = None


class OrgEmailMapper(BaseModel):
    pass


class OrgEntryData(BaseModel):
    name: str | None = None
    flags: int | None = None
    description: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    agency_code: str | None = Field(None, alias="agencyCode")
    timezone: str | None = None
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    website: str | None = None


class OrgEntryDataImpl(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    name: str | None = None
    description: str | None = None
    flags: int | None = None
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    website: str | None = None
    timezone: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")


class OrgFlags(Enum):
    user_can_post = "USER_CAN_POST"
    feed_disabled = "FEED_DISABLED"
    trip_chat_disabled = "TRIP_CHAT_DISABLED"
    trip_invite_user = "TRIP_INVITE_USER"


class OrgHotelChainPref(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    chain_code: str | None = Field(None, alias="chainCode")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")


class OrgHotelChainRoomPref(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    chain_code: str | None = Field(None, alias="chainCode")
    rate_code: str | None = Field(None, alias="rateCode")
    policy_id: int | None = Field(None, alias="policyId")
    preference_level: int | None = Field(None, alias="preferenceLevel")


class OrgIntegrationType(Enum):
    expensify = "EXPENSIFY"


class OrgLoyaltyProgram(BaseModel):
    id: int | None = None
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    org_id: int | None = Field(None, alias="orgId")
    number: str | None = None
    idx: int | None = None


class OrgProject(BaseModel):
    id: int | None = None
    name: str | None = None
    hidden: bool | None = None


class OrgProjectMapper(BaseModel):
    pass


class OrgRateCode(BaseModel):
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    rate_code_id: int | None = Field(None, alias="rateCodeId")


class OrgRateCodeMapper(BaseModel):
    pass


class OrgRateCodeText(BaseModel):
    id: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    text: str | None = None


class OrgRateCodeTextMapper(BaseModel):
    pass


class OrgSettings(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    config: list[str] = Field(default_factory=list)


class OrgType(Enum):
    agency = "AGENCY"
    community = "COMMUNITY"
    corporate = "CORPORATE"
    supplier = "SUPPLIER"


class OrgUserField(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_user_id: int | None = Field(None, alias="orgUserId")
    field_id: int | None = Field(None, alias="fieldId")
    field_value_id: int | None = Field(None, alias="fieldValueId")
    value: str | None = None
    remark: str | None = None


class OrgUserRole(Enum):
    guest = "Guest"
    user = "User"
    booker = "Booker"
    manager = "Manager"


class OrgUserStatus(Enum):
    accepted = "Accepted"
    suspended = "Suspended"


class OrgUserUpdateEntryData(BaseModel):
    position: str | None = None
    business_phone_number: str | None = Field(None, alias="businessPhoneNumber")
    business_address: AddressLocation | None = Field(None, alias="businessAddress")
    role: OrgUserRole | None = None


class OriginDestination(BaseModel):
    airline: str | None = None
    departure_station: str | None = Field(None, alias="departureStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    duration: int | None = None
    segments: list[str] = Field(default_factory=list)
    stops: list[str] = Field(default_factory=list)
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")


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
    ref: str | None = None
    ptc: str | None = None
    offer_item_id: str | None = Field(None, alias="offerItemId")


class PassportData(BaseModel):
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    dob: AwareOrNaiveDatetime | None = None
    doc_type: str | None = Field(None, alias="docType")
    doc_number: str | None = Field(None, alias="docNumber")
    issue_country: str | None = Field(None, alias="issueCountry")
    nationality: str | None = None
    expiration_date: AwareOrNaiveDatetime | None = Field(None, alias="expirationDate")


class PciCard(BaseModel):
    id: int | None = None
    user_id: int | None = Field(None, alias="userId")
    org_id: int | None = Field(None, alias="orgId")
    name: str | None = None
    reservation_types: int | None = Field(None, alias="reservationTypes")
    complete: bool | None = None
    owner_id: int | None = Field(None, alias="ownerId")


class PciCardMapper(BaseModel):
    pass


class PenaltyType(Enum):
    exchange_before = "exchangeBefore"
    exchange_after = "exchangeAfter"
    refund_before = "refundBefore"
    refund_after = "refundAfter"


class PendingEmailMapper(BaseModel):
    pass


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
    id: int | None = None
    code: str | None = None
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius: float | None = None
    country: str | None = None


class PolicyCityMapper(BaseModel):
    pass


class PolicyLookupTable(BaseModel):
    name: str | None = None
    code: str | None = None


class PolicyMapper(BaseModel):
    pass


class PolicyOptionLeg(BaseModel):
    pair: str | None = None
    duration: int | None = None
    flight_class: FlightClassPref | None = Field(None, alias="flightClass")


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


class PolicyRuleExceptionMapper(BaseModel):
    pass


class PolicyRuleMapper(BaseModel):
    pass


class PolicyRuleResult(BaseModel):
    policy_id: int | None = Field(None, alias="policyId")
    rule_id: int | None = Field(None, alias="ruleId")
    result: PolicyResult | None = None


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


class PrecheckResponse(BaseModel):
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None
    remark: str | None = None
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    currency: str | None = None
    hotel: Hotel | None = None


class PrepareTrainReservationResponse(BaseModel):
    total_price: float | None = Field(None, alias="totalPrice")
    raw_data: dict[str, Any] = Field(alias="rawData", default_factory=dict)


class Price(BaseModel):
    payout_price: float | None = Field(None, alias="payoutPrice")
    currency: str | None = None
    commission_percentage: float | None = Field(None, alias="commissionPercentage")


class PriceSummary(BaseModel):
    currency: str | None = None
    due_amount: float | None = Field(None, alias="dueAmount")
    refund_amount: float | None = Field(None, alias="refundAmount")
    credit_amount: float | None = Field(None, alias="creditAmount")
    penalty_amount: float | None = Field(None, alias="penaltyAmount")
    taxes_and_fees_amount: float | None = Field(None, alias="taxesAndFeesAmount")
    total_amount: float | None = Field(None, alias="totalAmount")
    fop_flags: int | None = Field(None, alias="fopFlags")


class PricedFare(BaseModel):
    currency: str | None = None
    price: float | None = None
    name: str | None = None
    penalty_id: str | None = Field(None, alias="penaltyId")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    flags: int | None = None
    penalties: int | None = None
    perks: int | None = None
    segments: list[FareSegment] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    is_transborder: bool | None = Field(None, alias="isTransborder")
    has_mixed_cabin: bool | None = Field(None, alias="hasMixedCabin")
    is_current_fare: bool | None = Field(None, alias="isCurrentFare")
    is_seat_selection_available: bool | None = Field(
        None,
        alias="isSeatSelectionAvailable",
    )
    has_limited_options: bool | None = Field(None, alias="hasLimitedOptions")
    has_multi_tickets: bool | None = Field(None, alias="hasMultiTickets")
    has_special_rate: bool | None = Field(None, alias="hasSpecialRate")


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
    id: int | None = None
    code: str | None = None
    name: str | None = None
    provider_type: str | None = Field(None, alias="providerType")
    active: bool | None = None


class ProviderPnr(BaseModel):
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    time_zone: str | None = Field(None, alias="timeZone")
    local_created_on: AwareOrNaiveDatetime | None = Field(None, alias="localCreatedOn")
    org_id: int | None = Field(None, alias="orgId")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    provider_code: str | None = Field(None, alias="providerCode")
    pnr: str | None = None


class ProviderPnrReport(BaseModel):
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    time_zone: str | None = Field(None, alias="timeZone")
    local_created_on: AwareOrNaiveDatetime | None = Field(None, alias="localCreatedOn")
    org_name: str | None = Field(None, alias="orgName")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    provider_code: str | None = Field(None, alias="providerCode")
    pnr: str | None = None


class Quality(Enum):
    n_a = "n/a"
    better = "better"
    standard = "standard"


class Localizations(BaseModel):
    localizations: list[Localization] = Field(default_factory=list)
    empty: bool | None = None
    elements: list[Localization] = Field(default_factory=list)
    first: Localization | None = None
    last: Localization | None = None


class Railcard(BaseModel):
    id: int | None = None
    code: str | None = None
    name: str | None = None
    vendor: str | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    active: bool | None = None
    localizations: list[Localization] | Localizations | None = None


class Rate(BaseModel):
    sub_supplier_id: str | None = Field(None, alias="subSupplierId")
    board_code: BoardCode | None = Field(None, alias="boardCode")
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    channel: Channel | None = None
    country_codes: list[str] = Field(alias="countryCodes", default_factory=list)
    allotment: int | None = None
    price: float | None = None
    cancellation_policy: CancellationPolicy | None = Field(
        None,
        alias="cancellationPolicy",
    )
    confirm_by_mins: int | None = Field(None, alias="confirmByMins")
    benefits: list[Benefit] = Field(default_factory=list)
    commission_percentage: float | None = Field(None, alias="commissionPercentage")
    hourly_available_slots: list[HourlyAvailableSlot] = Field(
        alias="hourlyAvailableSlots",
        default_factory=list,
    )
    metadata: str | None = None
    instant_confirm: bool | None = Field(None, alias="instantConfirm")


class RateCode(BaseModel):
    id: int | None = None
    code: str | None = None
    description: str | None = None
    active: bool | None = None
    is_default: bool | None = Field(None, alias="isDefault")
    agency_code: str | None = Field(None, alias="agencyCode")
    org_default: bool | None = Field(None, alias="orgDefault")
    provider_code: str | None = Field(None, alias="providerCode")


class RateCodeInfo(BaseModel):
    description: str | None = None
    code: str | None = None


class RateCodeMapper(BaseModel):
    pass


class ReasonType(Enum):
    policy = "policy"
    preferred = "preferred"


class RefPolicyInfo(BaseModel):
    ref: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    policy_rule_results: list[PolicyRuleResult] = Field(
        alias="policyRuleResults",
        default_factory=list,
    )


class ReportAirlinesByOrg(BaseModel):
    airline_code: str | None = Field(None, alias="airlineCode")
    airline_name: str | None = Field(None, alias="airlineName")
    segments: int | None = None
    amount: list[Amount] = Field(default_factory=list)


class ReportCityPairs(BaseModel):
    departure_code: str | None = Field(None, alias="departureCode")
    arrival_code: str | None = Field(None, alias="arrivalCode")
    total_spend: list[Amount] = Field(alias="totalSpend", default_factory=list)
    current_spend: list[Amount] = Field(alias="currentSpend", default_factory=list)
    total_segments: int | None = Field(None, alias="totalSegments")
    current_segments: int | None = Field(None, alias="currentSegments")
    total_basic_segments: int | None = Field(None, alias="totalBasicSegments")
    total_economy_segments: int | None = Field(None, alias="totalEconomySegments")
    total_premium_segments: int | None = Field(None, alias="totalPremiumSegments")
    current_basic_segments: int | None = Field(None, alias="currentBasicSegments")
    current_economy_segments: int | None = Field(None, alias="currentEconomySegments")
    current_premium_segments: int | None = Field(None, alias="currentPremiumSegments")
    qsi: float | None = None
    market_share: float | None = Field(None, alias="marketShare")


class ReportFlightByCityPair(BaseModel):
    departure_code: str | None = Field(None, alias="departureCode")
    arrival_code: str | None = Field(None, alias="arrivalCode")
    total_spend: float | None = Field(None, alias="totalSpend")
    total_segments: int | None = Field(None, alias="totalSegments")


class ReportFlightByEmployee(BaseModel):
    user_id: int | None = Field(None, alias="userId")
    user_name: str | None = Field(None, alias="userName")
    amount: float | None = None
    segments: int | None = None


class ReportFlightsHotelsInfo(BaseModel):
    flights_total_spend: float | None = Field(None, alias="flightsTotalSpend")
    flights_tickets: float | None = Field(None, alias="flightsTickets")
    hotels_total_spend: float | None = Field(None, alias="hotelsTotalSpend")
    hotels_average_rate: float | None = Field(None, alias="hotelsAverageRate")
    hotels_average_days: float | None = Field(None, alias="hotelsAverageDays")
    hotels_days: int | None = Field(None, alias="hotelsDays")
    budget: float | None = None


class ReportGraphInfo(BaseModel):
    day: date | None = None
    amount_spend: float | None = Field(None, alias="amountSpend")
    budget: float | None = None


class ReportOrganizationSpendInfo(BaseModel):
    total_spend: float | None = Field(None, alias="totalSpend")


class ReportProspectiveCustomer(BaseModel):
    org_id: int | None = Field(None, alias="orgId")
    company_name: str | None = Field(None, alias="companyName")
    current_spend: float | None = Field(None, alias="currentSpend")
    current_segments: int | None = Field(None, alias="currentSegments")
    total_spend: float | None = Field(None, alias="totalSpend")
    total_segments: int | None = Field(None, alias="totalSegments")
    total_basic_segments: int | None = Field(None, alias="totalBasicSegments")
    total_economy_segments: int | None = Field(None, alias="totalEconomySegments")
    total_premium_segments: int | None = Field(None, alias="totalPremiumSegments")
    current_basic_segments: int | None = Field(None, alias="currentBasicSegments")
    current_economy_segments: int | None = Field(None, alias="currentEconomySegments")
    current_premium_segments: int | None = Field(None, alias="currentPremiumSegments")


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
    user_id: int | None = Field(None, alias="userId")
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    dob: date | None = None
    on_lap_index: int | None = Field(None, alias="onLapIndex")


class ReservationField(BaseModel):
    id: int | None = None
    nms: int | None = None
    reservation_id: int | None = Field(None, alias="reservationId")
    user_id: int | None = Field(None, alias="userId")
    field_id: int | None = Field(None, alias="fieldId")
    field_value_id: int | None = Field(None, alias="fieldValueId")
    value: str | None = None
    remark: str | None = None


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
    thumbnail_height: int | None = Field(None, alias="thumbnailHeight")
    thumbnail_width: int | None = Field(None, alias="thumbnailWidth")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    media_height: int | None = Field(None, alias="mediaHeight")
    media_width: int | None = Field(None, alias="mediaWidth")
    media_url: str | None = Field(None, alias="mediaUrl")


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
    id: int | None = None
    active: bool | None = None
    name: str | None = None
    code: str | None = None
    type: ReservationType | None = None
    ext_type: ReservationType | None = Field(None, alias="extType")


class RewardProgramInfo(BaseModel):
    number: str | None = None
    vendor: str | None = None


class RewardProgramListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[RewardProgram] = Field(default_factory=list)


class RewardProgramResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: RewardProgram | None = None


class Role(BaseModel):
    id: int | None = None
    code: str | None = None
    name: str | None = None


class Room(BaseModel):
    pass


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
    id: int | None = None
    service_class: str | None = Field(None, alias="serviceClass")
    airline: str | None = None
    description: str | None = None
    cabin_class: CabinClass | None = Field(None, alias="cabinClass")
    cabin_class_override: CabinClass | None = Field(None, alias="cabinClassOverride")


class SabreCommand(BaseModel):
    token: str | None = None
    conversation_id: str | None = Field(None, alias="conversationId")
    command: str | None = None


class SabreProfileType(Enum):
    tvl = "TVL"
    crp = "CRP"


class SabreRecordLocator(BaseModel):
    id: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    pnr: str | None = None
    trip_id: int | None = Field(None, alias="tripId")
    traveler_profile_ids: list[str] = Field(
        alias="travelerProfileIds",
        default_factory=list,
    )
    dk_numbers: list[str] = Field(alias="dkNumbers", default_factory=list)
    corporate_profile_id: str | None = Field(None, alias="corporateProfileId")
    agency_profile_id: str | None = Field(None, alias="agencyProfileId")
    creation_timestamp: AwareOrNaiveDatetime | None = Field(
        None,
        alias="creationTimestamp",
    )
    last_updated_timestamp: AwareOrNaiveDatetime | None = Field(
        None,
        alias="lastUpdatedTimestamp",
    )
    total_price: float | None = Field(None, alias="totalPrice")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    hash: str | None = None
    command_remarks: bool | None = Field(None, alias="commandRemarks")
    update_requested: AwareOrNaiveDatetime | None = Field(None, alias="updateRequested")


class SabreRecordLocatorTime(BaseModel):
    id: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    update_time: AwareOrNaiveDatetime | None = Field(None, alias="updateTime")


class SabreUserProfile(BaseModel):
    id: int | None = None
    nms: int | None = None
    user_id: int | None = Field(None, alias="userId")
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    profile_id: str | None = Field(None, alias="profileId")
    profile_hash: str | None = Field(None, alias="profileHash")


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
    location_refs: list[str] = Field(alias="locationRefs", default_factory=list)
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    reservation_id: int | None = Field(None, alias="reservationId")
    trip_id: int | None = Field(None, alias="tripId")


class SearchCarResponse(BaseModel):
    cars: list[CarOffer] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    pick_up_date: AwareOrNaiveDatetime | None = Field(None, alias="pickUpDate")
    drop_off_date: AwareOrNaiveDatetime | None = Field(None, alias="dropOffDate")
    locations: dict[str, CarLocation] = Field(default_factory=dict)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )


class SearchCarResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: SearchCarResponse | None = None


class SearchCategory(Enum):
    flight = "FLIGHT"
    hotel = "HOTEL"
    car = "CAR"
    train = "TRAIN"
    seat = "SEAT"


class SearchFlightsRequest(BaseModel):
    ods: list[OriginDestinationRequest] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    reservation_ids: list[int] = Field(alias="reservationIds", default_factory=list)
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    inf: int | None = None


class SearchFlightsRequestType(Enum):
    one_way = "ONE_WAY"
    itinerary = "ITINERARY"
    itinerary_resume = "ITINERARY_RESUME"
    outer = "OUTER"


class SearchHotelsRequest(BaseModel):
    checkin_date: date | None = Field(None, alias="checkinDate")
    checkout_date: date | None = Field(None, alias="checkoutDate")
    latitude: float | None = None
    longitude: float | None = None
    radius: float | None = None
    currency: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    reservation_id: int | None = Field(None, alias="reservationId")
    trip_id: int | None = Field(None, alias="tripId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class SearchHotelsResponse(BaseModel):
    hotels: list[HotelOffer] = Field(default_factory=list)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )


class SearchHotelsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: SearchHotelsResponse | None = None


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
    column: str | None = None
    window: bool | None = None
    aisle: bool | None = None
    center: bool | None = None


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
    flight_number: str | None = Field(None, alias="flightNumber")
    airline: str | None = None
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    depart_time: AwareOrNaiveDatetime | None = Field(None, alias="departTime")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    duration: int | None = None
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
    total: float | None = None
    fop_label: str | None = Field(None, alias="fopLabel")
    fop_record: str | None = Field(None, alias="fopRecord")


class SettlementType(Enum):
    credit = "Credit"
    debit = "Debit"
    reservation = "Reservation"


class ShopFlightsRequest(BaseModel):
    ods: list[OriginDestinationRequest] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)


class SignUpCampaign(BaseModel):
    id: int | None = None
    email: str | None = None
    cid: str | None = None
    created_at: AwareOrNaiveDatetime | None = Field(None, alias="createdAt")


class SignUpCampaignMapper(BaseModel):
    pass


class SignUpUserRequest(BaseModel):
    email: str | None = None
    recaptcha: str | None = None
    cid: str | None = None
    campaign_code: str | None = Field(None, alias="campaignCode")


class Size(BaseModel):
    application: Application | None = None
    cm: str | None = None
    in_: str | None = Field(None, alias="in")


class StatBudget(BaseModel):
    start_date: date | None = Field(None, alias="startDate")
    end_date: date | None = Field(None, alias="endDate")
    amount: float | None = None
    accrual_term: int | None = Field(None, alias="accrualTerm")


class StorageType(Enum):
    ro = "RO"
    rw = "RW"


class StringListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[str] = Field(default_factory=list)


class StringResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: str | None = None


class SupplierInquiry(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    name: str | None = None
    email: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    company: str | None = None


class SupplierMapper(BaseModel):
    pass


class SupplierType(Enum):
    airline = "airline"


class Task(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    running: bool | None = None
    name: str | None = None
    executed_by: str | None = Field(None, alias="executedBy")
    executed_on: int | None = Field(None, alias="executedOn")
    executed_in: int | None = Field(None, alias="executedIn")
    period_ms: int | None = Field(None, alias="periodMs")


class TermsAndConditions(BaseModel):
    label: str | None = None
    url: str | None = None


class TfsAirline(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    synced_on: int | None = Field(None, alias="syncedOn")
    tf_code: str | None = Field(None, alias="tfCode")
    iata: str | None = None
    name: str | None = None


class TfsAirport(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    synced_on: int | None = Field(None, alias="syncedOn")
    iata: str | None = None
    name: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    city: str | None = None
    city_code: str | None = Field(None, alias="cityCode")


class TfsCity(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    synced_on: int | None = Field(None, alias="syncedOn")
    iata: str | None = None
    name: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")


class TfsSupplierRoute(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    synced_on: int | None = Field(None, alias="syncedOn")
    supplier: str | None = None
    origin: str | None = None
    destination: str | None = None


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
    id: int | None = None
    nms: int | None = None
    bucket: str | None = None
    code: str | None = None
    key: str | None = None
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
    duration_estimated: bool | None = Field(None, alias="durationEstimated")
    time_based: bool | None = Field(None, alias="timeBased")
    date_based: bool | None = Field(None, alias="dateBased")


class UtcOffset(BaseModel):
    seconds: int | None = None
    zero: bool | None = None
    nano: int | None = None
    negative: bool | None = None
    positive: bool | None = None
    units: list[Unit] = Field(default_factory=list)


class TimeZone(BaseModel):
    id: int | None = None
    name: str | None = None
    abbrev: str | None = None
    utc_offset: UtcOffset | None = Field(None, alias="utcOffset")
    is_dst: bool | None = Field(None, alias="isDst")


class TimeZoneListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[TimeZone] = Field(default_factory=list)


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
    id: int | None = None
    code: str | None = None
    name: str | None = None
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    loyalty_program_id: int | None = Field(None, alias="loyaltyProgramId")
    codes: dict[str, str] = Field(default_factory=dict)


class TrainFareSegment(BaseModel):
    segment_id: str | None = Field(None, alias="segmentId")
    fare_name: str | None = Field(None, alias="fareName")
    quantity: int | None = None
    perks: int | None = None
    applied_discount_id: str | None = Field(None, alias="appliedDiscountId")
    fare_condition_id: str | None = Field(None, alias="fareConditionId")
    comfort_class_id: str | None = Field(None, alias="comfortClassId")
    fare_condition_ids: list[str] = Field(
        alias="fareConditionIds",
        default_factory=list,
    )


class TrainOriginDestination(BaseModel):
    carrier_code: str | None = Field(None, alias="carrierCode")
    duration: int | None = None
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_station_name: str | None = Field(None, alias="departureStationName")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_station_name: str | None = Field(None, alias="arrivalStationName")
    stops: list[str] = Field(default_factory=list)
    segments: list[str] = Field(default_factory=list)


class TrainOriginDestinationRequest(BaseModel):
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_date: date | None = Field(None, alias="departureDate")
    departure_time: str | None = Field(None, alias="departureTime")
    arrival_date: date | None = Field(None, alias="arrivalDate")
    arrival_time: str | None = Field(None, alias="arrivalTime")


class TrainPricedFare(BaseModel):
    currency: str | None = None
    price: float | None = None
    discount_amount: float | None = Field(None, alias="discountAmount")
    name: str | None = None
    flags: int | None = None
    perks: int | None = None
    segments: list[TrainFareSegment] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    railcard_ids: list[int] = Field(alias="railcardIds", default_factory=list)
    route_restriction: str | None = Field(None, alias="routeRestriction")
    fare_restriction: str | None = Field(None, alias="fareRestriction")
    open_return_until: date | None = Field(None, alias="openReturnUntil")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    allowed_departure_stations: list[str] = Field(
        alias="allowedDepartureStations",
        default_factory=list,
    )
    allowed_arrival_stations: list[str] = Field(
        alias="allowedArrivalStations",
        default_factory=list,
    )
    has_travelcard: bool | None = Field(None, alias="hasTravelcard")
    is_transborder: bool | None = Field(None, alias="isTransborder")
    has_mixed_cabin: bool | None = Field(None, alias="hasMixedCabin")
    has_rate_code: bool | None = Field(None, alias="hasRateCode")
    open_return: bool | None = Field(None, alias="openReturn")
    is_current_fare: bool | None = Field(None, alias="isCurrentFare")


class TrainReservationTicket(BaseModel):
    ticket_number: str | None = Field(None, alias="ticketNumber")
    ticket_url: str | None = Field(None, alias="ticketUrl")


class TrainSeat(BaseModel):
    car: str | None = None
    seat: str | None = None
    consumer_index: int | None = Field(None, alias="consumerIndex")


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
    train_number: str | None = Field(None, alias="trainNumber")
    train_name: str | None = Field(None, alias="trainName")
    equipment: str | None = None
    logo: str | None = None
    carrier_code: str | None = Field(None, alias="carrierCode")
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    duration: int | None = None
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    class_code: str | None = Field(None, alias="classCode")
    available_quantity: int | None = Field(None, alias="availableQuantity")
    perks: int | None = None
    fare_rules: str | None = Field(None, alias="fareRules")


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
    id: int | None = None
    code: str | None = None
    name: str | None = None
    city: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    state: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    flags: int | None = None
    label: str | None = None
    vendor_codes: list[str] = Field(alias="vendorCodes", default_factory=list)
    active: bool | None = None
    provider_code: str | None = Field(None, alias="providerCode")
    searchable: bool | None = None
    group_code: str | None = Field(None, alias="groupCode")


class TrainStationFlags(Enum):
    multi_city = "MULTI_CITY"
    open_return = "OPEN_RETURN"
    time_required = "TIME_REQUIRED"
    has_railcards = "HAS_RAILCARDS"
    use_station_names = "USE_STATION_NAMES"


class TrainStationGroup(BaseModel):
    id: int | None = None
    code: str | None = None
    name: str | None = None
    city: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    state: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    flags: int | None = None
    label: str | None = None


class TrainStationGroupListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[TrainStationGroup] = Field(default_factory=list)


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
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    internal_id: str | None = Field(None, alias="internalId")


class TravelPolicyParameterType(Enum):
    int = "INT"
    decimal = "DECIMAL"
    enum = "ENUM"
    bool = "BOOL"
    string = "STRING"
    list = "LIST"
    lookup = "LOOKUP"


class TravelerProfile(BaseModel):
    user_id: int | None = Field(None, alias="userId")
    profile_id: str | None = Field(None, alias="profileId")
    name: str | None = None


class TripBoardActionTrail(BaseModel):
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    org_id: int | None = Field(None, alias="orgId")
    user_id: int | None = Field(None, alias="userId")
    action: str | None = None
    resource_id: int | None = Field(None, alias="resourceId")
    resource_type: ResourceType | None = Field(None, alias="resourceType")
    request_headers: dict[str, str] = Field(
        alias="requestHeaders",
        default_factory=dict,
    )
    request_method: str | None = Field(None, alias="requestMethod")
    request_uri: str | None = Field(None, alias="requestUri")
    time: int | None = None


class TripBoardFee(BaseModel):
    id: int | None = None
    nms: int | None = None
    trip_id: int | None = Field(None, alias="tripId")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    booker_id: int | None = Field(None, alias="bookerId")
    currency: str | None = None
    total: float | None = None
    fop_card_id: int | None = Field(None, alias="fopCardId")
    fop_label: str | None = Field(None, alias="fopLabel")
    fop_record: str | None = Field(None, alias="fopRecord")
    locator: str | None = None
    messages: list[str] = Field(default_factory=list)
    ui_flags: int | None = Field(None, alias="uiFlags")


class TripBoardFlags(Enum):
    require_approval = "REQUIRE_APPROVAL"
    allow_user_invites = "ALLOW_USER_INVITES"
    allow_user_bookings = "ALLOW_USER_BOOKINGS"
    cvv_required = "CVV_REQUIRED"


class TripBoardFop(BaseModel):
    id: int | None = None
    nms: int | None = None
    trip_id: int | None = Field(None, alias="tripId")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    trip_board_ref_id: int | None = Field(None, alias="tripBoardRefId")
    card_id: int | None = Field(None, alias="cardId")
    credit_id: int | None = Field(None, alias="creditId")
    label: str | None = None
    description: str | None = None
    amount: float | None = None
    on_account: bool | None = Field(None, alias="onAccount")


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
    id: int | None = None
    type: ReservationType | None = None
    date: AwareOrNaiveDatetime | None = None
    status: ReservationStatus | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)


class TspmOrgProfile(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    profile_id: str | None = Field(None, alias="profileId")
    profile_hash: str | None = Field(None, alias="profileHash")
    storage_type: StorageType | None = Field(None, alias="storageType")


class TspmOrgProfileListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[TspmOrgProfile] = Field(default_factory=list)


class TspmOrgProfileResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: TspmOrgProfile | None = None


class TspmUserProfile(BaseModel):
    id: int | None = None
    nms: int | None = None
    user_id: int | None = Field(None, alias="userId")
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    profile_id: str | None = Field(None, alias="profileId")
    profile_hash: str | None = Field(None, alias="profileHash")


class TypeEnum(Enum):
    chance = "chance"
    n_a = "n/a"
    none = "none"
    smartphone_data_roam = "smartphone_data_roam"
    wifi = "wifi"


class UPAPhoto(BaseModel):
    caption: str | None = None
    id: str | None = None
    thumb_url: str | None = Field(None, alias="thumbUrl")
    medium_url: str | None = Field(None, alias="mediumUrl")
    large_url: str | None = Field(None, alias="largeUrl")


class UTA(BaseModel):
    id: str | None = None
    headline: str | None = None
    description: str | None = None
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    categories: list[str] = Field(default_factory=list)
    fees: list[FlightAttributeFee] = Field(default_factory=list)
    assessment: str | None = None


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
    id: int | None = None
    nms: int | None = None
    user_id: int | None = Field(None, alias="userId")
    email: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    status: EmailStatus | None = None


class UserAccountEmailListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[UserAccountEmail] = Field(default_factory=list)


class UserAccountEmailResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserAccountEmail | None = None


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
    id: int | None = None
    address: AddressLocation | None = None
    label: str | None = None


class UserAddressResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserAddress | None = None


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
    number: str | None = None
    country: str | None = None
    expiry: date | None = None
    nationality: str | None = None


class UserDocuments(BaseModel):
    passport: UserDocumentPassport | None = None
    tsa: str | None = None
    goes: str | None = None
    redress_number: str | None = Field(None, alias="redressNumber")


class UserFlags(Enum):
    tsa_precheck = "TSA_PRECHECK"
    driver = "DRIVER"
    adult = "ADULT"


class UserOrgInfo(BaseModel):
    org_id: int | None = Field(None, alias="orgId")
    name: str | None = None
    description: str | None = None
    status: OrgUserStatus | None = None


class UserRewardProgram(BaseModel):
    id: int | None = None
    user_id: int | None = Field(None, alias="userId")
    reward_program_id: int | None = Field(None, alias="rewardProgramId")
    number: str | None = None
    idx: int | None = None


class UserRewardProgramListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[UserRewardProgram] = Field(default_factory=list)


class UserRewardProgramResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserRewardProgram | None = None


class UserRole(Enum):
    admin = "Admin"
    agency_admin = "AgencyAdmin"
    agent = "Agent"
    user = "User"


class UserSession(BaseModel):
    user_id: int | None = Field(None, alias="userId")
    token: str | None = None
    expiry: AwareOrNaiveDatetime | None = None
    ip: str | None = None


class UserSessionResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserSession | None = None


class UserTieType(Enum):
    ro = "RO"
    rw = "RW"


class UserValidationResponse(BaseModel):
    id: int | None = None
    code: str | None = None
    email: str | None = None
    token: str | None = None


class UserValidationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserValidationResponse | None = None


class VendorStatusType(Enum):
    nonpreferred = "nonpreferred"
    preferred = "preferred"


class Views(BaseModel):
    pass


class VisibilityType(Enum):
    private = "PRIVATE"
    public = "PUBLIC"


class Wall(BaseModel):
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    visibility: VisibilityType | None = None


class WallResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Wall | None = None


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
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    org_id: int | None = Field(None, alias="orgId")
    user_id: int | None = Field(None, alias="userId")
    action: str | None = None
    resource_id: int | None = Field(None, alias="resourceId")
    resource_type: ResourceType | None = Field(None, alias="resourceType")
    request_headers: dict[str, str] = Field(
        alias="requestHeaders",
        default_factory=dict,
    )
    request_method: str | None = Field(None, alias="requestMethod")
    request_uri: str | None = Field(None, alias="requestUri")
    time: int | None = None


class AddCardRequest(BaseModel):
    user_id: int | None = Field(None, alias="userId")
    org_id: int | None = Field(None, alias="orgId")
    name: str | None = None
    number: str | None = None
    cvc: str | None = None
    expiration: str | None = Field(None, examples=["2022-03"])
    holder_name: str | None = Field(None, alias="holderName")
    billing_address: Address | None = Field(None, alias="billingAddress")
    is_default: bool | None = Field(None, alias="isDefault")
    reservation_types: int | None = Field(None, alias="reservationTypes")


class AddressLocationMap(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Data | None = None


class AdvanceChangeInner(BaseModel):
    assessment: Assessment | None = None
    description: str | None = None
    fee: Fee | None = None
    headline: str | None = None


class AgencyListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Agency] = Field(default_factory=list)


class AgencyResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Agency | None = None


class AgencySettingsListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[AgencySettings] = Field(default_factory=list)


class AgencySettingsResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: AgencySettings | None = None


class AgentPhoneListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[AgentPhone] = Field(default_factory=list)


class AgentStatusResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: AgentStatus | None = None


class AgodaResponse(BaseModel):
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None
    remark: str | None = None


class Aircraft(BaseModel):
    type: AircraftType | None = None
    display_text: str | None = Field(None, alias="displayText")


class AirlineListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Airline] = Field(default_factory=list)


class AirportListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Airport] = Field(default_factory=list)


class AirportResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Airport | None = None


class AmadeusOrgProfile(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    profile_id: str | None = Field(None, alias="profileId")
    profile_hash: str | None = Field(None, alias="profileHash")
    storage_type: StorageType | None = Field(None, alias="storageType")


class AncillaryOffer(BaseModel):
    ref: str | None = None
    vendor: str | None = None
    code: str | None = None
    name: str | None = None
    description: str | None = None
    boundary: str | None = None
    type: AncillaryType | None = None
    price: float | None = None
    taxes: float | None = None
    local_price: float | None = Field(None, alias="localPrice")
    local_taxes: float | None = Field(None, alias="localTaxes")
    local_currency: str | None = Field(None, alias="localCurrency")
    max_quantity: int | None = Field(None, alias="maxQuantity")
    min_quantity: int | None = Field(None, alias="minQuantity")
    available_quantity: int | None = Field(None, alias="availableQuantity")
    passenger_refs: list[str] = Field(alias="passengerRefs", default_factory=list)


class AncillaryOffers(BaseModel):
    ref: str | None = None
    ancillaries: list[AncillaryOffer] = Field(default_factory=list)


class ApiKey(BaseModel):
    id: int | None = None
    active: bool | None = None
    key: str | None = None
    description: str | None = None
    platform: PlatformType | None = None


class ApprovalItem(BaseModel):
    user_id: int | None = Field(None, alias="userId")
    created_at: AwareOrNaiveDatetime | None = Field(None, alias="createdAt")
    policy_ids: list[int] = Field(alias="policyIds", default_factory=list)
    status: ApprovalStatus | None = None
    comment: str | None = None


class BaseTrainStationResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: BaseTrainStation | None = None


class Beverage(BaseModel):
    quality: FoodQuality | None = None
    type: BeverageType | None = None
    alcoholic_free: bool | None = Field(None, alias="alcoholicFree")
    nonalcoholic_free: bool | None = Field(None, alias="nonalcoholicFree")
    display_text: str | None = Field(None, alias="displayText")


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


class BookingDetailResponse(BaseModel):
    response_status: AgodaResponseStatus | None = Field(None, alias="responseStatus")
    version: str | None = None
    remark: str | None = None
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")
    supplier_booking_id: str | None = Field(None, alias="supplierBookingId")
    booking_status: BookingStatus | None = Field(None, alias="bookingStatus")
    hotel: str | None = None
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    room_code: str | None = Field(None, alias="roomCode")
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    board_code: BoardCode | None = Field(None, alias="boardCode")
    channel: Channel | None = None
    quantity: int | None = None
    special_requests: str | None = Field(None, alias="specialRequests")
    guest_count: GuestCount | None = Field(None, alias="guestCount")
    price: Price | None = None
    benefits: list[Benefit] = Field(default_factory=list)
    hourly_slot: HourlyAvailableSlot | None = Field(None, alias="hourlySlot")
    hotel_confirmation_reference: str | None = Field(
        None,
        alias="hotelConfirmationReference",
    )
    instant_confirm: bool | None = Field(None, alias="instantConfirm")


class BookingDetailResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: BookingDetailResponse | None = None


class BookingRequest(BaseModel):
    hotel: str | None = None
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    booking_reference_id: str | None = Field(None, alias="bookingReferenceId")
    room_code: str | None = Field(None, alias="roomCode")
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    board_code: BoardCode | None = Field(None, alias="boardCode")
    channel: Channel | None = None
    currency: str | None = None
    quantity: int | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    guest: Guest | None = None
    special_requests: str | None = Field(None, alias="specialRequests")
    guest_count: GuestCount | None = Field(None, alias="guestCount")
    benefits: list[Benefit] = Field(default_factory=list)
    selected_hourly_slot: HourlyAvailableSlot | None = Field(
        None,
        alias="selectedHourlySlot",
    )
    metadata: str | None = None


class BookingResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: BookingResponse | None = None


class BooleanResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: bool | None = None


class CampaignListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Campaign] = Field(default_factory=list)


class CampaignResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Campaign | None = None


class CancelResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: CancelResponse | None = None


class CancellationInner(BaseModel):
    assessment: Assessment | None = None
    description: str | None = None
    fee: Fee | None = None
    headline: str | None = None


class CarReservationExt(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    car: Car | None = None
    confirmation_number: str | None = Field(None, alias="confirmationNumber")
    brand: str | None = None
    pick_up: CarLocation | None = Field(None, alias="pickUp")
    drop_off: CarLocation | None = Field(None, alias="dropOff")
    same_drop_off_location: bool | None = Field(None, alias="sameDropOffLocation")
    arrival_flight: ArrivalFlight | None = Field(None, alias="arrivalFlight")
    extras: list[CarExtra] = Field(default_factory=list)
    insurances: list[CarInsurance] = Field(default_factory=list)
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    total_taxes: float | None = Field(None, alias="totalTaxes")
    total_extras: float | None = Field(None, alias="totalExtras")
    total_insurance: float | None = Field(None, alias="totalInsurance")
    total_fees: float | None = Field(None, alias="totalFees")
    total_vehicle: float | None = Field(None, alias="totalVehicle")
    unlimited_distance: bool | None = Field(None, alias="unlimitedDistance")
    free_distance_covered: float | None = Field(None, alias="freeDistanceCovered")
    distance_overage: float | None = Field(None, alias="distanceOverage")
    distance_unit: DistanceUnit | None = Field(None, alias="distanceUnit")
    days: int | None = None
    hours: int | None = None


class CarVendorListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[CarVendor] = Field(default_factory=list)


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
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ConcurOrg] = Field(default_factory=list)


class ConcurOrgResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ConcurOrg | None = None


class CountryListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Country] = Field(default_factory=list)


class CountryStateListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[CountryState] = Field(default_factory=list)


class CreateOrgRequest(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    name: str | None = None
    description: str | None = None
    flags: int | None = None
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    website: str | None = None
    timezone: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    sabre_profile_id: str | None = Field(None, alias="sabreProfileId")
    sabre_template_id: str | None = Field(None, alias="sabreTemplateId")
    type: OrgType | None = None
    visibility: VisibilityType | None = None
    customer_number: str | None = Field(None, alias="customerNumber")
    email: str | None = None


class CreateOrgUserRequest(BaseModel):
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    dob: date | None = None
    gender: Gender | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    flags: int | None = None
    org_data: OrgUserUpdateEntryData | None = Field(None, alias="orgData")


class CreateUserAccountRequest(BaseModel):
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    dob: date | None = None
    gender: Gender | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    flags: int | None = None


class CreditListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Credit] = Field(default_factory=list)


class CreditResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Credit | None = None


class CurrencyListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Currency] = Field(default_factory=list)


class DisplayTextSummary(BaseModel):
    display_text: str | None = Field(None, alias="displayText")
    exists: Exists3 | None = None


class DomainListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Domain] = Field(default_factory=list)


class DomainResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Domain | None = None


class EmptyDataResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: EmptyData | None = None


class EmptyResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None


class Entertainement(BaseModel):
    cost: AmenityCost | None = None
    content_type: list[EntertainementContentType] = Field(
        alias="contentType",
        default_factory=list,
    )
    display_text: str | None = Field(None, alias="displayText")


class EntertainmentOfferings(BaseModel):
    content_type: ContentTypeEnum | None = Field(None, alias="contentType")
    delivery_medium: DeliveryMediumEnum | None = Field(None, alias="deliveryMedium")
    selection_type: SelectionTypeEnum | None = Field(None, alias="selectionType")


class EntertainmentOfferingsGroup(BaseModel):
    offerings: list[EntertainmentOfferings] = Field(default_factory=list)
    operator: OperatorEnum | None = None


class EnumsHolder(BaseModel):
    platform_type: PlatformType | None = Field(None, alias="platformType")
    field_flag: FieldFlags | None = Field(None, alias="fieldFlag")
    fare_type: FareType | None = Field(None, alias="fareType")
    exception_flags: ExceptionFlags | None = Field(None, alias="exceptionFlags")
    trip_board_processing_flags: TripBoardProcessingFlags | None = Field(
        None,
        alias="tripBoardProcessingFlags",
    )
    train_seat_preference_flags: TrainSeatPreferenceFlags | None = Field(
        None,
        alias="trainSeatPreferenceFlags",
    )
    approval_action: ApprovalAction | None = Field(None, alias="approvalAction")


class ExchangeRateListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ExchangeRate] = Field(default_factory=list)


class ExpensifySettingsResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ExpensifySettings | None = None


class FieldModel(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    code: str | None = None
    remark_code: str | None = Field(None, alias="remarkCode")
    name: str | None = None
    type: FieldType | None = None
    value_type: FieldValueType | None = Field(None, alias="valueType")
    active: bool | None = None
    flags: int | None = None
    reservation_type: ReservationType | None = Field(None, alias="reservationType")


class FieldResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FieldModel | None = None


class FieldValueListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[FieldValue] = Field(default_factory=list)


class FieldValueResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FieldValue | None = None


class FlightAttribute(BaseModel):
    id: str | None = None
    headline: str | None = None
    description: str | None = None
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    categories: list[str] = Field(default_factory=list)
    fees: list[FlightAttributeFee] = Field(default_factory=list)


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
    segments: list[FlightSegmentRefData] = Field(default_factory=list)
    segment_perks: int | None = Field(None, alias="segmentPerks")
    total_price: float | None = Field(None, alias="totalPrice")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")


class FlightReservationAncillary(BaseModel):
    vendor: str | None = None
    code: str | None = None
    name: str | None = None
    description: str | None = None
    boundary: str | None = None
    type: AncillaryType | None = None
    price: float | None = None
    taxes: float | None = None
    local_price: float | None = Field(None, alias="localPrice")
    local_taxes: float | None = Field(None, alias="localTaxes")
    local_currency: str | None = Field(None, alias="localCurrency")
    quantity: int | None = None
    status: ReservationStatus | None = None


class FlightReservationOd(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    duration: int | None = None
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    arrival_time_offset: int | None = Field(None, alias="arrivalTimeOffset")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    departure_time_offset: int | None = Field(None, alias="departureTimeOffset")
    segments: list[FlightReservationSegment] = Field(default_factory=list)
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    stops: list[str] = Field(default_factory=list)
    departure_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureOffsetDateTime",
    )
    arrival_offset_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalOffsetDateTime",
    )


class FlightReservationSeat(BaseModel):
    consumer_index: int | None = Field(None, alias="consumerIndex")
    status: ReservationStatus | None = None
    segment_key: str | None = Field(None, alias="segmentKey")
    seat_key: str | None = Field(None, alias="seatKey")
    seat_column: str | None = Field(None, alias="seatColumn")
    seat_row: str | None = Field(None, alias="seatRow")
    price: float | None = None
    taxes: float | None = None
    preference: SeatPreference | None = None
    seat_flags: int | None = Field(None, alias="seatFlags")


class FlightReservationSsr(BaseModel):
    consumer_index: int | None = Field(None, alias="consumerIndex")
    code: str | None = None
    comment: str | None = None
    status: ReservationStatus | None = None


class Food(BaseModel):
    quality: FoodQuality | None = None
    type: FoodType | None = None
    free: bool | None = None
    display_text: str | None = Field(None, alias="displayText")


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
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: GetCarResponse | None = None


class HotelChainListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[HotelChain] = Field(default_factory=list)


class HotelInfoResponse(BaseModel):
    offer: HotelOffer | None = None
    medias: list[HotelMedia] = Field(default_factory=list)
    checkin_time: str | None = Field(None, alias="checkinTime")
    checkout_time: str | None = Field(None, alias="checkoutTime")
    description: str | None = None
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")


class HotelInfoResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: HotelInfoResponse | None = None


class HotelReservationExt(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    hotel_refs: list[str] = Field(alias="hotelRefs", default_factory=list)
    cancellation: HotelCancellation | None = None
    checkin_date: date | None = Field(None, alias="checkinDate")
    checkout_date: date | None = Field(None, alias="checkoutDate")
    checkin_time: str | None = Field(None, alias="checkinTime")
    checkout_time: str | None = Field(None, alias="checkoutTime")
    fax: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    guests: int | None = None
    hotel_name: str | None = Field(None, alias="hotelName")
    hotel_chain_name: str | None = Field(None, alias="hotelChainName")
    hotel_group_name: str | None = Field(None, alias="hotelGroupName")
    price_per_night: float | None = Field(None, alias="pricePerNight")
    room_type: str | None = Field(None, alias="roomType")
    rating: float | None = None
    room_description: str | None = Field(None, alias="roomDescription")
    atmosphere_description: str | None = Field(None, alias="atmosphereDescription")
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    city: str | None = None
    address1: str | None = None
    address2: str | None = None
    zip_code: str | None = Field(None, alias="zipCode")
    street_number: str | None = Field(None, alias="streetNumber")
    media: list[ReservationMedia] = Field(default_factory=list)
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    taxes_and_fees_per_night: float | None = Field(None, alias="taxesAndFeesPerNight")
    city_code: str | None = Field(None, alias="cityCode")
    main_city_code: str | None = Field(None, alias="mainCityCode")
    perks: int | None = None
    chain_code: str | None = Field(None, alias="chainCode")
    brand_code: str | None = Field(None, alias="brandCode")
    amenities: int | None = None
    external_segment_id: str | None = Field(None, alias="externalSegmentId")
    confirmation_number: str | None = Field(None, alias="confirmationNumber")
    room_flags: int | None = Field(None, alias="roomFlags")
    important: str | None = None


class HotelRoom(BaseModel):
    room_type: str | None = Field(None, alias="roomType")
    description: str | None = None
    bed_type: str | None = Field(None, alias="bedType")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    price_per_night: float | None = Field(None, alias="pricePerNight")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    taxes_and_fees_per_night: float | None = Field(None, alias="taxesAndFeesPerNight")
    checkin_time: str | None = Field(None, alias="checkinTime")
    checkout_time: str | None = Field(None, alias="checkoutTime")
    cancellation: HotelCancellation | None = None
    rate_code: RoomRateCode | None = Field(None, alias="rateCode")
    rate_plan_type: OtaRatePlanType | None = Field(None, alias="ratePlanType")
    perks: int | None = None
    flags: int | None = None
    ref: str | None = None
    room_id: str | None = Field(None, alias="roomId")
    out_of_policy_id: int | None = Field(None, alias="outOfPolicyId")
    out_of_policy_rule_ids: list[int] = Field(
        alias="outOfPolicyRuleIds",
        default_factory=list,
    )
    commission: float | None = None
    important: str | None = None
    hotel_pref_level: int | None = Field(None, alias="hotelPrefLevel")
    hidden: bool | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    approval_required: bool | None = Field(None, alias="approvalRequired")
    booking_blocked: bool | None = Field(None, alias="bookingBlocked")


class HotelRoomResponse(BaseModel):
    room: HotelRoom | None = None


class HotelRoomResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: HotelRoomResponse | None = None


class HotelRoomsResponse(BaseModel):
    rooms: list[HotelRoom] = Field(default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )


class HotelRoomsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: HotelRoomsResponse | None = None


class HotelSearchResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: HotelSearchResponse | None = None


class ImportSabreOrgProfileResponse(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    org_name: str | None = Field(None, alias="orgName")
    sabre_profile_id: str | None = Field(None, alias="sabreProfileId")
    sabre_template_id: str | None = Field(None, alias="sabreTemplateId")
    suppress_user_emails: bool | None = Field(None, alias="suppressUserEmails")
    link_traveler_profile: bool | None = Field(None, alias="linkTravelerProfile")
    user_profile_source: ImportProfileSource | None = Field(
        None,
        alias="userProfileSource",
    )
    act: ImportProfileAct | None = None
    users: list[TravelerProfile] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")


class ImportSabreOrgProfileResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ImportSabreOrgProfileResponse | None = None


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
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: KpiCountResponse | None = None


class Layout(BaseModel):
    type: LayoutType | None = None
    quality: LayoutQualityType | None = None
    display_text: str | None = Field(None, alias="displayText")
    row_layout: str | None = Field(None, alias="rowLayout")
    direct_aisle_access: bool | None = Field(None, alias="directAisleAccess")


class ListAncillariesResponse(BaseModel):
    ancillary_offers: list[AncillaryOffers] = Field(
        alias="ancillaryOffers",
        default_factory=list,
    )


class ListAncillariesResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListAncillariesResponse | None = None


class ListFareRulesResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListFareRulesResponse | None = None


class ListFieldsResponse(BaseModel):
    fields: list[FieldModel] = Field(default_factory=list)
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)


class ListFieldsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListFieldsResponse | None = None


class ListReservationFieldResponse(BaseModel):
    reservation_fields: list[ReservationField] = Field(
        alias="reservationFields",
        default_factory=list,
    )
    fields: list[FieldModel] = Field(default_factory=list)
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)


class ListReservationFieldResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListReservationFieldResponse | None = None


class LocateCarResponse(BaseModel):
    locations: list[CarLocationMerged] = Field(default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )


class LocateCarResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: LocateCarResponse | None = None


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
    id: int | None = None
    active: bool | None = None
    code: str | None = None
    name: str | None = None
    type: ReservationType | None = None
    website_url: str | None = Field(None, alias="websiteUrl")
    logo_url: str | None = Field(None, alias="logoUrl")
    prefix: str | None = None


class LoyaltyProgramListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[LoyaltyProgram] = Field(default_factory=list)


class MaskedCreditCard(BaseModel):
    id: int | None = None
    name: str | None = None
    address: Address | None = None
    is_default: bool | None = Field(None, alias="isDefault")
    brand: str | None = None
    exp_date: str | None = Field(None, alias="expDate")
    last_digits: str | None = Field(None, alias="lastDigits")
    type: UserCreditCardType | None = None
    complete: bool | None = None
    holder_name: str | None = Field(None, alias="holderName")
    reservation_types: int | None = Field(None, alias="reservationTypes")


class MaskedCreditCardListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[MaskedCreditCard] = Field(default_factory=list)


class MaskedCreditCardResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: MaskedCreditCard | None = None


class Media(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    external_id: str | None = Field(None, alias="externalId")
    query: str | None = None
    height: int | None = None
    width: int | None = None
    source: MediaSource | None = None
    type: MediaType | None = None
    attribution_name: str | None = Field(None, alias="attributionName")
    attribution_url: str | None = Field(None, alias="attributionUrl")
    url: str | None = None


class MediaRepository(BaseModel):
    id: int | None = None
    nms: int | None = None
    source: MediaSource | None = None
    query: str | None = None
    last_queried_on: AwareOrNaiveDatetime | None = Field(None, alias="lastQueriedOn")
    count_cached: int | None = Field(None, alias="countCached")
    count_total: int | None = Field(None, alias="countTotal")


class MiscReservationExt(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    country: str | None = None
    country_code: str | None = Field(None, alias="countryCode")
    state: str | None = None
    state_code: str | None = Field(None, alias="stateCode")
    city: str | None = None
    address1: str | None = None
    address2: str | None = None
    zip_code: str | None = Field(None, alias="zipCode")
    latitude: float | None = None
    longitude: float | None = None
    venue_name: str | None = Field(None, alias="venueName")
    description: str | None = None
    phone: str | None = None
    place_id: str | None = Field(None, alias="placeId")


class Msg(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    post_id: int | None = Field(None, alias="postId")
    parent_id: int | None = Field(None, alias="parentId")
    user_id: int | None = Field(None, alias="userId")
    text: str | None = None
    likes: list[int] = Field(default_factory=list)
    processed_on: int | None = Field(None, alias="processedOn")
    ext: Ext | None = None
    msgs: list[Msg] = Field(default_factory=list)
    time: int | None = None
    media: list[Media] = Field(default_factory=list)
    dates: list[MsgDatePair] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    locations: list[MsgLocation] = Field(default_factory=list)
    mentions: list[MsgMention] = Field(default_factory=list)


class NotificationCenter(BaseModel):
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    ext: Ext | None = None
    unseen: int | None = None
    unseen_agent_posts: int | None = Field(None, alias="unseenAgentPosts")
    unseen_user_posts: int | None = Field(None, alias="unseenUserPosts")


class NotificationCenterResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: NotificationCenter | None = None


class Offer(BaseModel):
    od_id: str | None = Field(None, alias="odId")
    fares: dict[str, list[PricedFare]] = Field(default_factory=dict)


class Org(BaseModel):
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    name: str | None = None
    description: str | None = None
    flags: int | None = None
    billing_address_location_id: int | None = Field(
        None,
        alias="billingAddressLocationId",
    )
    billing_address: AddressLocation | None = Field(None, alias="billingAddress")
    website: str | None = None
    timezone: str | None = None
    phone_number: str | None = Field(None, alias="phoneNumber")
    active: bool | None = None
    type: OrgType | None = None
    visibility: VisibilityType | None = None
    branding: Branding | None = None
    customer_number: str | None = Field(None, alias="customerNumber")


class OrgAgencyResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgAgency | None = None


class OrgAirlinePrefListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgAirlinePref] = Field(default_factory=list)


class OrgAirlinePrefResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgAirlinePref | None = None


class OrgBudgetEntry(BaseModel):
    name: str | None = None
    start_date: date | None = Field(None, alias="startDate")
    accrual_term: int | None = Field(None, alias="accrualTerm")
    amount: float | None = None
    type: OrgBudgetType | None = None


class OrgCarVendorPrefListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgCarVendorPref] = Field(default_factory=list)


class OrgCarVendorPrefResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgCarVendorPref | None = None


class OrgDomainListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgDomain] = Field(default_factory=list)


class OrgDomainResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgDomain | None = None


class OrgEmailListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgEmail] = Field(default_factory=list)


class OrgEmailResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgEmail | None = None


class OrgHotelChainPrefListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgHotelChainPref] = Field(default_factory=list)


class OrgHotelChainPrefResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgHotelChainPref | None = None


class OrgHotelChainRoomPrefListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgHotelChainRoomPref] = Field(default_factory=list)


class OrgIntegration(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    type: OrgIntegrationType | None = None
    latest_sync_id: int | None = Field(None, alias="latestSyncId")
    owned_by: str | None = Field(None, alias="ownedBy")
    settings: dict[str, Any] = Field(default_factory=dict)


class OrgIntegrationExpensify(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    type: OrgIntegrationType | None = None
    latest_sync_id: int | None = Field(None, alias="latestSyncId")
    owned_by: str | None = Field(None, alias="ownedBy")
    settings: ExpensifySettings | None = None


class OrgListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Org] = Field(default_factory=list)


class OrgLoyaltyProgramListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgLoyaltyProgram] = Field(default_factory=list)


class OrgLoyaltyProgramResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgLoyaltyProgram | None = None


class OrgProjectListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgProject] = Field(default_factory=list)


class OrgProjectResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgProject | None = None


class OrgRateCodeListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgRateCode] = Field(default_factory=list)


class OrgRateCodeResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgRateCode | None = None


class OrgRateCodeTextResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgRateCodeText | None = None


class OrgResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Org | None = None


class OrgSettingsListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgSettings] = Field(default_factory=list)


class OrgSettingsResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgSettings | None = None


class OrgUser(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    user_id: int | None = Field(None, alias="userId")
    status: OrgUserStatus | None = None
    role: OrgUserRole | None = None
    position: str | None = None
    business_phone_number: str | None = Field(None, alias="businessPhoneNumber")
    business_address_id: int | None = Field(None, alias="businessAddressId")
    travel_policy_ids: list[int] = Field(alias="travelPolicyIds", default_factory=list)
    guest_policy_ids: list[int] = Field(alias="guestPolicyIds", default_factory=list)
    guest_policy_count: int | None = Field(None, alias="guestPolicyCount")
    approver_policy_ids: list[int] = Field(
        alias="approverPolicyIds",
        default_factory=list,
    )


class OrgUserEntryData(BaseModel):
    position: str | None = None
    business_phone_number: str | None = Field(None, alias="businessPhoneNumber")
    business_address: AddressLocation | None = Field(None, alias="businessAddress")
    role: OrgUserRole | None = None
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")


class OrgUserFieldListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgUserField] = Field(default_factory=list)


class OrgUserFieldResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgUserField | None = None


class OrgUserIdEntryDataList(BaseModel):
    org_users: list[int] = Field(alias="orgUsers", default_factory=list)
    update: OrgUserUpdateEntryData | None = None


class OrgUserListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[OrgUser] = Field(default_factory=list)


class OrgUserResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgUser | None = None


class OrgUsersResponse(BaseModel):
    errors: dict[str, str] = Field(default_factory=dict)
    organization_users: list[OrgUser] = Field(
        alias="organizationUsers",
        default_factory=list,
    )


class OrgUsersResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgUsersResponse | None = None


class OrganizationReportCityPairs(BaseModel):
    org_id: int | None = Field(None, alias="orgId")
    org_name: str | None = Field(None, alias="orgName")
    org_logo_url: str | None = Field(None, alias="orgLogoUrl")
    market_share: float | None = Field(None, alias="marketShare")
    report_city_pairs: list[ReportCityPairs] = Field(
        alias="reportCityPairs",
        default_factory=list,
    )


class OrganizationReportCityPairsResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrganizationReportCityPairs | None = None


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
    type: PenaltyType | None = None
    enabled: bool | None = None
    penalty_amount: float | None = Field(None, alias="penaltyAmount")
    currency_code: str | None = Field(None, alias="currencyCode")


class PenaltyData(BaseModel):
    penalties: list[Penalty] = Field(default_factory=list)


class PendingEmail(BaseModel):
    id: int | None = None
    nms: int | None = None
    status: PendingEmailStatus | None = None
    email: str | None = None
    name: str | None = None
    subject: str | None = None
    is_html: bool | None = Field(None, alias="isHtml")
    message: str | None = None
    bcc_emails: list[str] = Field(alias="bccEmails", default_factory=list)
    active: bool | None = None


class PendingEmailListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[PendingEmail] = Field(default_factory=list)


class PendingEmailResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: PendingEmail | None = None


class PolicyLookupTableResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: PolicyLookupTable | None = None


class PolicyOptionFligthClassByDuration(BaseModel):
    max: FlightClassPref | None = None
    by_legs: list[PolicyOptionLeg] = Field(alias="byLegs", default_factory=list)


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
    id: int | None = None
    nms: int | None = None
    code: PolicyRuleSpecs | None = None
    active: bool | None = None
    policy_rule_id: int | None = Field(None, alias="policyRuleId")
    vars: dict[str, dict[str, Any]] = Field(default_factory=dict)


class PolicyRuleExceptionResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: PolicyRuleException | None = None


class PostPin(BaseModel):
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    post_id: int | None = Field(None, alias="postId")


class Power(BaseModel):
    type: PowerType | None = None
    distribution: PowerDistribution | None = None


class PrecheckRequest(BaseModel):
    hotel: str | None = None
    check_in: date | None = Field(None, alias="checkIn")
    check_out: date | None = Field(None, alias="checkOut")
    occupancy: RoomOccupancy | None = None
    rate_plan_code: str | None = Field(None, alias="ratePlanCode")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    selected_hourly_slot: HourlyAvailableSlot | None = Field(
        None,
        alias="selectedHourlySlot",
    )
    metadata: str | None = None


class PrecheckResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: PrecheckResponse | None = None


class ProviderPnrReportListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ProviderPnrReport] = Field(default_factory=list)


class RailcardListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Railcard] = Field(default_factory=list)


class RateCodeListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[RateCode] = Field(default_factory=list)


class RateCodeResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: RateCode | None = None


class RealTimeFlightInfo(BaseModel):
    aircraft: str | None = None
    primary_status: PrimaryFlightStatus | None = Field(None, alias="primaryStatus")
    secondary_status: SecondaryFlightStatus | None = Field(
        None,
        alias="secondaryStatus",
    )
    departure_terminal: str | None = Field(None, alias="departureTerminal")
    departure_gate: str | None = Field(None, alias="departureGate")
    departure_local_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureLocalDateTime",
    )
    departure_utc_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="departureUtcDateTime",
    )
    departure_status: ScheduleStatus | None = Field(None, alias="departureStatus")
    arrival_terminal: str | None = Field(None, alias="arrivalTerminal")
    arrival_gate: str | None = Field(None, alias="arrivalGate")
    arrival_local_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalLocalDateTime",
    )
    arrival_utc_date_time: AwareOrNaiveDatetime | None = Field(
        None,
        alias="arrivalUtcDateTime",
    )
    arrival_status: ScheduleStatus | None = Field(None, alias="arrivalStatus")
    link_map: str | None = Field(None, alias="linkMap")


class Reason(BaseModel):
    id: int | None = None
    active: bool | None = None
    reason_type: ReasonType | None = Field(None, alias="reasonType")
    reservation_type: ReservationType | None = Field(None, alias="reservationType")
    reason: str | None = None
    position: int | None = None


class ReasonListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Reason] = Field(default_factory=list)


class ReportAirlinesByOrgListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ReportAirlinesByOrg] = Field(default_factory=list)


class ReportCar(BaseModel):
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    flags: int | None = None
    booker_id: int | None = Field(None, alias="bookerId")
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    label: str | None = None
    vendor: str | None = None
    rlk: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    in_policy: bool | None = Field(None, alias="inPolicy")
    status: ReservationStatus | None = None
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    ttl: AwareOrNaiveDatetime | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    ext: Ext | None = None
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    brand: str | None = None
    car_name: str | None = Field(None, alias="carName")
    car_type: str | None = Field(None, alias="carType")
    car_class_name: str | None = Field(None, alias="carClassName")
    pickup: str | None = None
    dropoff: str | None = None
    days: int | None = None
    hours: int | None = None
    consumer_count: int | None = Field(None, alias="consumerCount")


class ReportCityPairsListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ReportCityPairs] = Field(default_factory=list)


class ReportFlightByCityPairListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ReportFlightByCityPair] = Field(default_factory=list)


class ReportFlightByEmployeeListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ReportFlightByEmployee] = Field(default_factory=list)


class ReportFlightSegment(BaseModel):
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    flags: int | None = None
    booker_id: int | None = Field(None, alias="bookerId")
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    label: str | None = None
    vendor: str | None = None
    rlk: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    in_policy: bool | None = Field(None, alias="inPolicy")
    status: ReservationStatus | None = None
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    ttl: AwareOrNaiveDatetime | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    ext: Ext | None = None
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_station: str | None = Field(None, alias="departureStation")
    fare_type: FareType | None = Field(None, alias="fareType")
    segments: int | None = None


class ReportHotel(BaseModel):
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    flags: int | None = None
    booker_id: int | None = Field(None, alias="bookerId")
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    label: str | None = None
    vendor: str | None = None
    rlk: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    in_policy: bool | None = Field(None, alias="inPolicy")
    status: ReservationStatus | None = None
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    ttl: AwareOrNaiveDatetime | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    ext: Ext | None = None
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    hotel_name: str | None = Field(None, alias="hotelName")
    hotel_code: str | None = Field(None, alias="hotelCode")
    brand_code: str | None = Field(None, alias="brandCode")
    chain_name: str | None = Field(None, alias="chainName")
    chain_code: str | None = Field(None, alias="chainCode")
    country: str | None = None
    city: str | None = None
    guests: int | None = None


class ReportOrganizationSpendInfoResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ReportOrganizationSpendInfo | None = None


class ReportProspectiveCustomerListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[ReportProspectiveCustomer] = Field(default_factory=list)


class ReportTrain(BaseModel):
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    flags: int | None = None
    booker_id: int | None = Field(None, alias="bookerId")
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    label: str | None = None
    vendor: str | None = None
    rlk: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    in_policy: bool | None = Field(None, alias="inPolicy")
    status: ReservationStatus | None = None
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    ttl: AwareOrNaiveDatetime | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    ext: Ext | None = None
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_station: str | None = Field(None, alias="departureStation")
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    segment_count: int | None = Field(None, alias="segmentCount")
    consumer_count: int | None = Field(None, alias="consumerCount")


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
    id: int | None = None
    ext: IsReservationExt | None = None
    trip_id: int | None = Field(None, alias="tripId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    rlk: str | None = None
    vendor: str | None = None
    label: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    in_policy: bool | None = Field(None, alias="inPolicy")
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    status: ReservationStatus | None = None
    ttl: AwareOrNaiveDatetime | None = None
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    flags: int | None = None
    type: ReservationType | None = None


class ReservationFieldResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ReservationField | None = None


class ReservationReport(BaseModel):
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    flags: int | None = None
    booker_id: int | None = Field(None, alias="bookerId")
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    label: str | None = None
    vendor: str | None = None
    rlk: str | None = None
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    in_policy: bool | None = Field(None, alias="inPolicy")
    status: ReservationStatus | None = None
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    ttl: AwareOrNaiveDatetime | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    ext: Ext | None = None
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )


class ReservationResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Reservation | None = None


class ResourceNotificationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ResourceNotificationResponse | None = None


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
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    agency_code: str | None = Field(None, alias="agencyCode")
    profile_id: str | None = Field(None, alias="profileId")
    template_id: str | None = Field(None, alias="templateId")
    profile_hash: str | None = Field(None, alias="profileHash")
    storage_type: StorageType | None = Field(None, alias="storageType")


class SabreOrgProfileResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: SabreOrgProfile | None = None


class SearchFlightRefData(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    created_on_utc: AwareOrNaiveDatetime | None = Field(None, alias="createdOnUtc")
    org_id: int | None = Field(None, alias="orgId")
    provider_code: str | None = Field(None, alias="providerCode")
    fop_flags: int | None = Field(None, alias="fopFlags")
    response_id: str | None = Field(None, alias="responseId")
    flights: list[FlightRefData] = Field(default_factory=list)
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    inf: int | None = None
    in_policy: bool | None = Field(None, alias="inPolicy")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    policy_rule_results: list[PolicyRuleResult] = Field(
        alias="policyRuleResults",
        default_factory=list,
    )
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    account_code: str | None = Field(None, alias="accountCode")
    request_type: SearchFlightsRequestType | None = Field(None, alias="requestType")
    itinerary_ref: str | None = Field(None, alias="itineraryRef")
    itinerary_ref_size: int | None = Field(None, alias="itineraryRefSize")
    airline: str | None = None
    transborder: bool | None = None
    seat_selection_available: bool | None = Field(None, alias="seatSelectionAvailable")
    reshop_reservation_ids: list[int] = Field(
        alias="reshopReservationIds",
        default_factory=list,
    )
    loyalty_program_number: str | None = Field(None, alias="loyaltyProgramNumber")
    reservation_flags: int | None = Field(None, alias="reservationFlags")
    transaction_identifier: str | None = Field(None, alias="transactionIdentifier")
    inner_one_way: bool | None = Field(None, alias="innerOneWay")


class SearchFlightsResponse(BaseModel):
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    ods: dict[str, OriginDestination] = Field(default_factory=dict)
    penalties: dict[str, PenaltyData] = Field(default_factory=dict)
    segments: dict[str, Segment] = Field(default_factory=dict)
    offers: list[Offer] = Field(default_factory=list)
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    od_count: int | None = Field(None, alias="odCount")


class SearchFlightsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: SearchFlightsResponse | None = None


class SearchTrainRequest(BaseModel):
    ods: list[TrainOriginDestinationRequest] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    railcards: list[int] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    reservation_ids: list[int] = Field(alias="reservationIds", default_factory=list)
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    open_return: bool | None = Field(None, alias="openReturn")


class Seat(BaseModel):
    wider_seat: bool | None = Field(None, alias="widerSeat")
    pitch: str | None = None
    leg_room: SeatLegRoom | None = Field(None, alias="legRoom")
    flatness: str | None = None
    display_text: str | None = Field(None, alias="displayText")


class SeatAssignment(BaseModel):
    consumer_index: int | None = Field(None, alias="consumerIndex")
    segment_key: str | None = Field(None, alias="segmentKey")
    seat_key: str | None = Field(None, alias="seatKey")
    preference: SeatPreference | None = None


class SeatMapSeat(BaseModel):
    column: str | None = None
    row: str | None = None
    flags: int | None = None
    status: SeatStatus | None = None
    seat_key: str | None = Field(None, alias="seatKey")
    occupied: bool | None = None
    chargeable: bool | None = None
    no_seat: bool | None = Field(None, alias="noSeat")
    premium: bool | None = None
    restricted_recline: bool | None = Field(None, alias="restrictedRecline")
    no_infant: bool | None = Field(None, alias="noInfant")
    leg_space: bool | None = Field(None, alias="legSpace")
    preferred: bool | None = None
    exit_row: bool | None = Field(None, alias="exitRow")
    to_be_left_vacant: bool | None = Field(None, alias="toBeLeftVacant")
    price: float | None = None
    taxes: float | None = None
    seat_type: str | None = Field(None, alias="seatType")
    in_policy: bool | None = Field(None, alias="inPolicy")
    approval_required: bool | None = Field(None, alias="approvalRequired")
    booking_blocked: bool | None = Field(None, alias="bookingBlocked")


class SecureCreditCard(BaseModel):
    number: str | None = None
    exp: str | None = Field(None, examples=["2022-03"])
    cvc: str | None = None
    type: UserCreditCardType | None = None
    holder_name: str | None = Field(None, alias="holderName")
    address: Address | None = None


class Settlement(BaseModel):
    id: int | None = None
    type: SettlementType | None = None
    reservation_id: int | None = Field(None, alias="reservationId")
    reservation_type: ReservationType | None = Field(None, alias="reservationType")
    org_id: int | None = Field(None, alias="orgId")
    user_id: int | None = Field(None, alias="userId")
    date: AwareOrNaiveDatetime | None = None
    label: str | None = None
    description: str | None = None
    currency: str | None = None
    amount: float | None = None


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
    user_id: int | None = Field(None, alias="userId")
    supplier_code: str | None = Field(None, alias="supplierCode")
    supplier_type: SupplierType | None = Field(None, alias="supplierType")


class SupplierListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Supplier] = Field(default_factory=list)


class SupplierResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Supplier | None = None


class TrainOffer(BaseModel):
    od_id: str | None = Field(None, alias="odId")
    fares: dict[str, list[TrainPricedFare]] = Field(default_factory=dict)


class TrainOriginDestinationInfo(BaseModel):
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    carrier: str | None = None
    duration: int | None = None
    segments: list[TrainSegmentInfo] = Field(default_factory=list)
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")


class TrainReservationSegment(BaseModel):
    ref: str | None = None
    duration: int | None = None
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_station_name: str | None = Field(None, alias="arrivalStationName")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_station_name: str | None = Field(None, alias="departureStationName")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    train_number: str | None = Field(None, alias="trainNumber")
    train_name: str | None = Field(None, alias="trainName")
    class_code: str | None = Field(None, alias="classCode")
    fare_name: str | None = Field(None, alias="fareName")
    fare_rules: str | None = Field(None, alias="fareRules")
    logo: str | None = None
    tickets: list[str] = Field(default_factory=list)
    seats: list[TrainSeat] = Field(default_factory=list)
    transport_mode: TrainTransportMode | None = Field(None, alias="transportMode")
    applied_discount_id: str | None = Field(None, alias="appliedDiscountId")
    fare_condition_id: str | None = Field(None, alias="fareConditionId")
    comfort_class_id: str | None = Field(None, alias="comfortClassId")
    carrier_name: str | None = Field(None, alias="carrierName")
    fare_condition_ids: list[str] = Field(
        alias="fareConditionIds",
        default_factory=list,
    )


class TrainSegment(BaseModel):
    train_number: str | None = Field(None, alias="trainNumber")
    train_name: str | None = Field(None, alias="trainName")
    equipment: str | None = None
    logo: str | None = None
    carrier_name: str | None = Field(None, alias="carrierName")
    duration: int | None = None
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    transport_mode: TrainTransportMode | None = Field(None, alias="transportMode")


class TravelPolicyParameter(BaseModel):
    name: str | None = None
    description: str | None = None
    type: TravelPolicyParameterType | None = None
    values: list[str] = Field(default_factory=list)
    table: LookupTable | None = None
    required: bool | None = None
    min_value: float | None = Field(None, alias="minValue")
    max_value: float | None = Field(None, alias="maxValue")


class Summary1(BaseModel):
    empty: bool | None = None
    first: TripSummaryLine | None = None
    last: TripSummaryLine | None = None


class Trip(BaseModel):
    id: int | None = None
    nms: int | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    org_id: int | None = Field(None, alias="orgId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    arranger_ids: list[int] = Field(alias="arrangerIds", default_factory=list)
    booker_ids: list[int] = Field(alias="bookerIds", default_factory=list)
    granted_ids: list[int] = Field(alias="grantedIds", default_factory=list)
    invitee_ids: list[int] = Field(alias="inviteeIds", default_factory=list)
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    name: str | None = None
    description: str | None = None
    visibility: VisibilityType | None = None
    start_date: date | None = Field(None, alias="startDate")
    end_date: date | None = Field(None, alias="endDate")
    agency_billed_on: AwareOrNaiveDatetime | None = Field(None, alias="agencyBilledOn")
    total: float | None = None
    summary: list[TripSummaryLine] | Summary1 | None = None
    trip_board_flags: int | None = Field(None, alias="tripBoardFlags")
    draft_boards: int | None = Field(None, alias="draftBoards")
    pending_boards: int | None = Field(None, alias="pendingBoards")
    processing_boards: int | None = Field(None, alias="processingBoards")
    confirmed_boards: int | None = Field(None, alias="confirmedBoards")
    send_itinerary_at: int | None = Field(None, alias="sendItineraryAt")
    post_processed_on: int | None = Field(None, alias="postProcessedOn")
    ui_flags: int | None = Field(None, alias="uiFlags")
    agency_flags: int | None = Field(None, alias="agencyFlags")


class TripBoardRef(BaseModel):
    id: int | None = None
    nms: int | None = None
    trip_id: int | None = Field(None, alias="tripId")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    active: bool | None = None
    reservation_type: ReservationType | None = Field(None, alias="reservationType")
    provider_code: str | None = Field(None, alias="providerCode")
    ref: str | None = None
    vendor: str | None = None
    user_reward_program_id: dict[str, int] = Field(
        alias="userRewardProgramId",
        default_factory=dict,
    )
    booker_id: int | None = Field(None, alias="bookerId")
    amend_id: int | None = Field(None, alias="amendId")
    amend_reservation_ids: list[int] = Field(
        alias="amendReservationIds",
        default_factory=list,
    )
    reservation_ids: list[int] = Field(alias="reservationIds", default_factory=list)
    status: ReservationStatus | None = None
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    summary: list[TripSummaryLine] | Summary1 | None = None
    start_date: date | None = Field(None, alias="startDate")
    end_date: date | None = Field(None, alias="endDate")
    priced_on: AwareOrNaiveDatetime | None = Field(None, alias="pricedOn")
    currency: str | None = None
    due: float | None = None
    earlier_due: float | None = Field(None, alias="earlierDue")
    refund: float | None = None
    credit: float | None = None
    penalty: float | None = None
    total: float | None = None
    exception_on_id: int | None = Field(None, alias="exceptionOnId")
    exception_flags: int | None = Field(None, alias="exceptionFlags")
    fop_flags: int | None = Field(None, alias="fopFlags")
    trip_board_flags: int | None = Field(None, alias="tripBoardFlags")
    waypoint_flags: int | None = Field(None, alias="waypointFlags")
    waypoint_attrs: dict[str, str] = Field(alias="waypointAttrs", default_factory=dict)
    messages: list[str] = Field(default_factory=list)
    fops: list[TripBoardFop] = Field(default_factory=list)
    ui_flags: int | None = Field(None, alias="uiFlags")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )


class TripMedia(BaseModel):
    id: int | None = None
    nms: int | None = None
    trip_id: int | None = Field(None, alias="tripId")
    media_id: int | None = Field(None, alias="mediaId")
    media: Media | None = None
    index: int | None = None


class UPA(BaseModel):
    id: str | None = None
    headline: str | None = None
    description: str | None = None
    small_icon_url: str | None = Field(None, alias="smallIconUrl")
    large_icon_url: str | None = Field(None, alias="largeIconUrl")
    cta_text: str | None = Field(None, alias="ctaText")
    cta_url: str | None = Field(None, alias="ctaUrl")
    categories: list[str] = Field(default_factory=list)
    fees: list[FlightAttributeFee] = Field(default_factory=list)
    photos: list[UPAPhoto] = Field(default_factory=list)


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
    id: int | None = None
    nms: int | None = None
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    gender: Gender | None = None
    flags: int | None = None
    active: bool | None = None
    color: str | None = None
    picture_url: str | None = Field(None, alias="pictureUrl")
    status: UserAccountStatus | None = None
    full_name: str | None = Field(None, alias="fullName")
    short_name: str | None = Field(None, alias="shortName")


class UserAccount(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    first_name: str | None = Field(None, alias="firstName")
    middle_name: str | None = Field(None, alias="middleName")
    last_name: str | None = Field(None, alias="lastName")
    suffix: str | None = None
    gender: Gender | None = None
    dob: date | None = None
    primary_email: str | None = Field(None, alias="primaryEmail")
    phone_number: str | None = Field(None, alias="phoneNumber")
    preferences: UserAccountPreferences | None = None
    emergency_contact: EmergencyContact | None = Field(None, alias="emergencyContact")
    documents: UserDocuments | None = None
    status: UserAccountStatus | None = None
    kyc: UserAccountKycStatus | None = None
    role: UserRole | None = None
    agency_codes: list[str] = Field(alias="agencyCodes", default_factory=list)
    color: str | None = None
    picture_url: str | None = Field(None, alias="pictureUrl")
    flags: int | None = None
    agent_sines: list[str] = Field(alias="agentSines", default_factory=list)
    full_name: str | None = Field(None, alias="fullName")
    short_name: str | None = Field(None, alias="shortName")


class UserAccountListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[UserAccount] = Field(default_factory=list)


class UserAccountResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserAccount | None = None


class UserCreationValidationStatus(BaseModel):
    status: UserCreationValidationStatusEnum | None = None
    user_account: UserAccount | None = Field(None, alias="userAccount")
    user_account_email: UserAccountEmail | None = Field(None, alias="userAccountEmail")


class UserListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[User] = Field(default_factory=list)


class UserProfileInfo(BaseModel):
    org: Org | None = None
    sabre_org_profile: SabreOrgProfile | None = Field(None, alias="sabreOrgProfile")
    corporate_loyalty_programs: list[OrgLoyaltyProgram] = Field(
        alias="corporateLoyaltyPrograms",
        default_factory=list,
    )
    loyalty_programs: dict[str, LoyaltyProgram] = Field(
        alias="loyaltyPrograms",
        default_factory=dict,
    )
    org_credit_cards: list[CreditCard] = Field(
        alias="orgCreditCards",
        default_factory=list,
    )
    user_account: UserAccount | None = Field(None, alias="userAccount")
    org_user: OrgUser | None = Field(None, alias="orgUser")
    user_credit_cards: list[CreditCard] = Field(
        alias="userCreditCards",
        default_factory=list,
    )
    sabre_user_profile: SabreUserProfile | None = Field(None, alias="sabreUserProfile")
    home_address: AddressLocation | None = Field(None, alias="homeAddress")
    business_address: AddressLocation | None = Field(None, alias="businessAddress")
    rewards: dict[str, list[RewardProgramInfo]] = Field(default_factory=dict)
    primary_email: str | None = Field(None, alias="primaryEmail")
    org_email: str | None = Field(None, alias="orgEmail")
    org_arranger_emails: list[str] = Field(
        alias="orgArrangerEmails",
        default_factory=list,
    )


class UserResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: User | None = None


class UserTie(BaseModel):
    id: int | None = None
    src_user_id: int | None = Field(None, alias="srcUserId")
    dst_user_id: int | None = Field(None, alias="dstUserId")
    tie_type: UserTieType | None = Field(None, alias="tieType")


class UserTieResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: UserTie | None = None


class Wifi(BaseModel):
    cost: AmenityCost | None = None
    chance: WifiChance | None = None


class AdvanceChange(BaseModel):
    after_departure: AdvanceChangeInner | None = Field(None, alias="afterDeparture")
    anytime: AdvanceChangeInner | None = None
    before_departure: AdvanceChangeInner | None = Field(None, alias="beforeDeparture")
    id: str | None = None


class Approval(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    trip_id: int | None = Field(None, alias="tripId")
    trip_name: str | None = Field(None, alias="tripName")
    booker_id: int | None = Field(None, alias="bookerId")
    trip_board_id: int | None = Field(None, alias="tripBoardId")
    policy_ids: list[int] = Field(alias="policyIds", default_factory=list)
    booker_comment: str | None = Field(None, alias="bookerComment")
    approvals: list[ApprovalItem] = Field(default_factory=list)
    status: ApprovalStatus | None = None
    canceled_by: int | None = Field(None, alias="canceledBy")
    submitted_at: AwareOrNaiveDatetime | None = Field(None, alias="submittedAt")
    cancelled_by: int | None = Field(None, alias="cancelledBy")


class ApprovalList(BaseModel):
    approvals: list[Approval] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)
    approval: list[Approval] = Field(default_factory=list)


class ApprovalListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ApprovalList | None = None


class ApprovalResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Approval | None = None


class Cancellation(BaseModel):
    after_departure: CancellationInner | None = Field(None, alias="afterDeparture")
    anytime: CancellationInner | None = None
    before_departure: CancellationInner | None = Field(None, alias="beforeDeparture")
    id: str | None = None


class CarReservation(BaseModel):
    id: int | None = None
    ext: CarReservationExt | None = None
    trip_id: int | None = Field(None, alias="tripId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    rlk: str | None = None
    vendor: str | None = None
    label: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    in_policy: bool | None = Field(None, alias="inPolicy")
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    status: ReservationStatus | None = None
    ttl: AwareOrNaiveDatetime | None = None
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    flags: int | None = None
    type: ReservationType | None = None


class CarReservationResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: CarReservation | None = None


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
    ref_data: SearchFlightRefData | None = Field(None, alias="refData")
    segments: dict[str, Segment] = Field(default_factory=dict)
    origin_destination: OriginDestination | None = Field(
        None,
        alias="originDestination",
    )
    penalties: list[Penalty] = Field(default_factory=list)
    fare_type: FareType | None = Field(None, alias="fareType")
    fare_name: str | None = Field(None, alias="fareName")
    rate_code: str | None = Field(None, alias="rateCode")
    private_fare_type: str | None = Field(None, alias="privateFareType")
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    free_luggage_allowance: int | None = Field(None, alias="freeLuggageAllowance")
    ticket_penalties: int | None = Field(None, alias="ticketPenalties")
    ticket_perks: int | None = Field(None, alias="ticketPerks")


class FlightReservationExt(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    air_price: float | None = Field(None, alias="airPrice")
    seat_price: float | None = Field(None, alias="seatPrice")
    seat_taxes: float | None = Field(None, alias="seatTaxes")
    ancillary_price: float | None = Field(None, alias="ancillaryPrice")
    ancillary_taxes: float | None = Field(None, alias="ancillaryTaxes")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    od: FlightReservationOd | None = None
    ssr: list[FlightReservationSsr] = Field(default_factory=list)
    seats: list[FlightReservationSeat] = Field(default_factory=list)
    ancillaries: list[FlightReservationAncillary] = Field(default_factory=list)
    ticket_numbers: list[str] = Field(alias="ticketNumbers", default_factory=list)


class FtsResponse(BaseModel):
    orgs: list[Org] = Field(default_factory=list)
    user_accounts: list[UserAccount] = Field(alias="userAccounts", default_factory=list)


class FtsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FtsResponse | None = None


class FtsUsersByOrgResponse(BaseModel):
    users: list[User] = Field(default_factory=list)
    user_emails: dict[str, str] = Field(alias="userEmails", default_factory=dict)


class FtsUsersByOrgResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FtsUsersByOrgResponse | None = None


class GetTrainResponse(BaseModel):
    org_id: int | None = Field(None, alias="orgId")
    stations: dict[str, TrainStation] = Field(default_factory=dict)
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    org_projects: list[OrgProject] = Field(alias="orgProjects", default_factory=list)
    total_price: float | None = Field(None, alias="totalPrice")
    origin_destinations: list[TrainOriginDestinationInfo] = Field(
        alias="originDestinations",
        default_factory=list,
    )


class GetTrainResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: GetTrainResponse | None = None


class GetTripResponse(BaseModel):
    trip: Trip | None = None
    users: dict[str, User] = Field(default_factory=dict)


class GetTripResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: GetTripResponse | None = None


class HotelReservation(BaseModel):
    id: int | None = None
    ext: HotelReservationExt | None = None
    trip_id: int | None = Field(None, alias="tripId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    rlk: str | None = None
    vendor: str | None = None
    label: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    in_policy: bool | None = Field(None, alias="inPolicy")
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    status: ReservationStatus | None = None
    ttl: AwareOrNaiveDatetime | None = None
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    flags: int | None = None
    type: ReservationType | None = None


class HotelReservationListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[HotelReservation] = Field(default_factory=list)


class HotelReservationResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: HotelReservation | None = None


class ListCarReservationResponse(BaseModel):
    car_reservations: list[CarReservation] = Field(
        alias="carReservations",
        default_factory=list,
    )


class ListCarReservationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListCarReservationResponse | None = None


class ListOrgUserByOrgResponse(BaseModel):
    users: list[User] = Field(default_factory=list)
    user_emails: dict[str, str] = Field(alias="userEmails", default_factory=dict)
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)
    addresses: list[AddressLocation] = Field(default_factory=list)
    fields: list[FieldModel] = Field(default_factory=list)
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)
    org_user_fields: list[OrgUserField] = Field(
        alias="orgUserFields",
        default_factory=list,
    )


class ListOrgUserByOrgResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListOrgUserByOrgResponse | None = None


class ListOrgUserByPolicyResponse(BaseModel):
    users: list[User] = Field(default_factory=list)
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)


class ListOrgUserByPolicyResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListOrgUserByPolicyResponse | None = None


class ListOrgUserByUserResponse(BaseModel):
    orgs: list[Org] = Field(default_factory=list)
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)
    addresses: list[AddressLocation] = Field(default_factory=list)


class ListOrgUserByUserResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListOrgUserByUserResponse | None = None


class ListPolicyApprover(BaseModel):
    users: list[User] = Field(default_factory=list)
    org_users: dict[str, OrgUser] = Field(alias="orgUsers", default_factory=dict)


class ListPolicyApproverResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListPolicyApprover | None = None


class ListReservationResponse(BaseModel):
    reservations: list[Reservation] = Field(default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)


class ListReservationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListReservationResponse | None = None


class ListTripsResponse(BaseModel):
    trips: list[Trip] = Field(default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)


class ListTripsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListTripsResponse | None = None


class ListUserAccountsResponse(BaseModel):
    user_accounts: list[UserAccount] = Field(alias="userAccounts", default_factory=list)
    user_account_emails: list[UserAccountEmail] = Field(
        alias="userAccountEmails",
        default_factory=list,
    )


class ListUserAccountsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListUserAccountsResponse | None = None


class ListUserTieResponse(BaseModel):
    ties: list[UserTie] = Field(default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)


class ListUserTieResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListUserTieResponse | None = None


class MiscReservation(BaseModel):
    id: int | None = None
    ext: MiscReservationExt | None = None
    trip_id: int | None = Field(None, alias="tripId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    rlk: str | None = None
    vendor: str | None = None
    label: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    in_policy: bool | None = Field(None, alias="inPolicy")
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    status: ReservationStatus | None = None
    ttl: AwareOrNaiveDatetime | None = None
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    flags: int | None = None
    type: ReservationType | None = None


class Notification(BaseModel):
    id: int | None = None
    nms: int | None = None
    owner_id: int | None = Field(None, alias="ownerId")
    owner_type: ResourceType | None = Field(None, alias="ownerType")
    target_id: int | None = Field(None, alias="targetId")
    target_type: ResourceType | None = Field(None, alias="targetType")
    type: NotificationType | None = None
    read: bool | None = None
    seen: bool | None = None
    time: int | None = None
    ext: Ext | None = None
    count: int | None = None
    parents: list[ParentResource] = Field(default_factory=list)
    status: OperationStatus | None = None
    sample_user_ids: list[int] = Field(alias="sampleUserIds", default_factory=list)
    sample_msg_text: str | None = Field(None, alias="sampleMsgText")
    trip_name: str | None = Field(None, alias="tripName")


class NotificationResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Notification | None = None


class PolicyRule(BaseModel):
    id: int | None = None
    nms: int | None = None
    code: PolicyRuleSpecs | None = None
    active: bool | None = None
    policy_id: int | None = Field(None, alias="policyId")
    action: PolicyRuleAction | None = None
    vars: dict[str, dict[str, Any]] = Field(default_factory=dict)
    exceptions: list[PolicyRuleException] = Field(default_factory=list)


class PolicyRuleResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: PolicyRule | None = None


class PolicyRuleSpec(BaseModel):
    code: str | None = None
    description: str | None = None
    category: SearchCategory | None = None
    post: bool | None = None
    params: list[TravelPolicyParameter] = Field(default_factory=list)


class PolicyRuleSpecListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[PolicyRuleSpec] = Field(default_factory=list)


class Post(BaseModel):
    id: int | None = None
    nms: int | None = None
    active: bool | None = None
    wall_id: int | None = Field(None, alias="wallId")
    archive_on: int | None = Field(None, alias="archiveOn")
    followers: list[int] = Field(default_factory=list)
    msg: Msg | None = None
    ui_flags: int | None = Field(None, alias="uiFlags")
    users: dict[str, User] = Field(default_factory=dict)


class PostResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Post | None = None


class ReportByOrgResponse(BaseModel):
    users: list[User] = Field(default_factory=list)
    org_users: list[OrgUser] = Field(alias="orgUsers", default_factory=list)
    user_emails: dict[str, str] = Field(alias="userEmails", default_factory=dict)
    reports: list[dict[str, Any]] = Field(default_factory=list)


class ReportByOrgResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ReportByOrgResponse | None = None


class RespItineraryData(BaseModel):
    legs: list[RespItineraryLeg] = Field(default_factory=list)
    co2_emissions: float | None = Field(None, alias="co2Emissions")


class ReviewTripBoardRefsResponse(BaseModel):
    trip_board_ref_ids: list[int] = Field(alias="tripBoardRefIds", default_factory=list)
    users: dict[str, User] = Field(default_factory=dict)
    user_to_reward_program_ids: dict[str, list[int]] = Field(
        alias="userToRewardProgramIds",
        default_factory=dict,
    )
    vendor_to_reward_programs: dict[str, dict[str, RewardProgram]] = Field(
        alias="vendorToRewardPrograms",
        default_factory=dict,
    )
    org_projects: list[OrgProject] = Field(alias="orgProjects", default_factory=list)
    not_in_policy_reasons: list[Reason] = Field(
        alias="notInPolicyReasons",
        default_factory=list,
    )
    not_preferred_reasons: list[Reason] = Field(
        alias="notPreferredReasons",
        default_factory=list,
    )


class ReviewTripBoardRefsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ReviewTripBoardRefsResponse | None = None


class SearchTrainResponse(BaseModel):
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    stations: dict[str, TrainStation] = Field(default_factory=dict)
    ods: dict[str, TrainOriginDestination] = Field(default_factory=dict)
    segments: dict[str, TrainSegment] = Field(default_factory=dict)
    railcards: dict[str, Railcard] = Field(default_factory=dict)
    applied_discounts: dict[str, AppliedDiscount] = Field(
        alias="appliedDiscounts",
        default_factory=dict,
    )
    fare_conditions: dict[str, FareConditions] = Field(
        alias="fareConditions",
        default_factory=dict,
    )
    comfort_classes: dict[str, ComfortClass] = Field(
        alias="comfortClasses",
        default_factory=dict,
    )
    offers: list[TrainOffer] = Field(default_factory=list)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    next_page_ref: str | None = Field(None, alias="nextPageRef")
    prev_page_ref: str | None = Field(None, alias="prevPageRef")
    out_of_policies: list[OutOfPolicy] = Field(
        alias="outOfPolicies",
        default_factory=list,
    )
    od_index: int | None = Field(None, alias="odIndex")
    od_count: int | None = Field(None, alias="odCount")
    page_replaces_previous_results: bool | None = Field(
        None,
        alias="pageReplacesPreviousResults",
    )


class SearchTrainResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: SearchTrainResponse | None = None


class SeatMapRow(BaseModel):
    row: int | None = None
    exit_row: bool | None = Field(None, alias="exitRow")
    seats: list[SeatMapSeat] = Field(default_factory=list)


class SegmentAmenityData(BaseModel):
    seat: Seat | None = None
    power: Power | None = None
    wifi: Wifi | None = None
    entertainement: Entertainement | None = None
    food: Food | None = None
    beverage: Beverage | None = None
    aircraft: Aircraft | None = None
    layout: Layout | None = None


class SegmentInfo(BaseModel):
    airline: str | None = None
    flight_number: str | None = Field(None, alias="flightNumber")
    operating_airline: str | None = Field(None, alias="operatingAirline")
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    depart_time: AwareOrNaiveDatetime | None = Field(None, alias="departTime")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    duration: int | None = None
    uta_list: list[UTA] = Field(alias="utaList", default_factory=list)
    upa_list: list[UPA] = Field(alias="upaList", default_factory=list)
    flight_class: FlightClass | None = Field(None, alias="flightClass")
    flight_class_premium: bool | None = Field(None, alias="flightClassPremium")
    amenities: SegmentAmenityData | None = None
    real_time_info: RealTimeFlightInfo | None = Field(None, alias="realTimeInfo")
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")


class TrainReservationOd(BaseModel):
    duration: int | None = None
    arrival_station: str | None = Field(None, alias="arrivalStation")
    arrival_station_name: str | None = Field(None, alias="arrivalStationName")
    departure_station: str | None = Field(None, alias="departureStation")
    departure_station_name: str | None = Field(None, alias="departureStationName")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    fare_type: FareType | None = Field(None, alias="fareType")
    segments: list[TrainReservationSegment] = Field(default_factory=list)
    route_restriction: str | None = Field(None, alias="routeRestriction")
    fare_restriction: str | None = Field(None, alias="fareRestriction")
    railcard_ids: list[int] = Field(alias="railcardIds", default_factory=list)
    tickets: list[TrainReservationTicket] = Field(default_factory=list)
    seat_reservability: TrainSeatReservabilityType | None = Field(
        None,
        alias="seatReservability",
    )
    fare_name: str | None = Field(None, alias="fareName")
    requested_departure_station: str | None = Field(
        None,
        alias="requestedDepartureStation",
    )
    requested_arrival_station: str | None = Field(None, alias="requestedArrivalStation")
    allowed_departure_stations: list[str] = Field(
        alias="allowedDepartureStations",
        default_factory=list,
    )
    allowed_arrival_stations: list[str] = Field(
        alias="allowedArrivalStations",
        default_factory=list,
    )


class TripBoard(BaseModel):
    id: int | None = None
    nms: int | None = None
    trip_id: int | None = Field(None, alias="tripId")
    org_id: int | None = Field(None, alias="orgId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    notes: str | None = None
    status: TripBoardStatus | None = None
    status_changed_on: AwareOrNaiveDatetime | None = Field(
        None,
        alias="statusChangedOn",
    )
    start_date: date | None = Field(None, alias="startDate")
    end_date: date | None = Field(None, alias="endDate")
    summary: list[TripSummaryLine] | Summary1 | None = None
    exception_flags: int | None = Field(None, alias="exceptionFlags")
    processing_flags: int | None = Field(None, alias="processingFlags")
    trip_board_flags: int | None = Field(None, alias="tripBoardFlags")
    waypoint_flags: int | None = Field(None, alias="waypointFlags")
    ttl: AwareOrNaiveDatetime | None = None
    record_locators: list[str] = Field(alias="recordLocators", default_factory=list)
    owned_by: str | None = Field(None, alias="ownedBy")
    sync_interval: int | None = Field(None, alias="syncInterval")
    sync_on: AwareOrNaiveDatetime | None = Field(None, alias="syncOn")
    fees: list[TripBoardFee] = Field(default_factory=list)
    refs: list[TripBoardRef] = Field(default_factory=list)
    ui_flags: int | None = Field(None, alias="uiFlags")
    agency_flags: int | None = Field(None, alias="agencyFlags")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )


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
    up_from: int | None = Field(None, alias="upFrom")
    down_to: int | None = Field(None, alias="downTo")
    posts: list[Post] = Field(default_factory=list)
    walls: list[Wall] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)
    orgs: list[Org] = Field(default_factory=list)


class FeedResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FeedResponse | None = None


class FlightInfo(BaseModel):
    departure_station: str | None = Field(None, alias="departureStation")
    arrival_station: str | None = Field(None, alias="arrivalStation")
    depart_time: AwareOrNaiveDatetime | None = Field(None, alias="departTime")
    departure_time: AwareOrNaiveDatetime | None = Field(None, alias="departureTime")
    arrival_time: AwareOrNaiveDatetime | None = Field(None, alias="arrivalTime")
    duration: int | None = None
    segments: list[SegmentInfo] = Field(default_factory=list)
    fare_name: str | None = Field(None, alias="fareName")
    fare_type: FareType | None = Field(None, alias="fareType")
    restricted_fare: bool | None = Field(None, alias="restrictedFare")


class FlightItem(BaseModel):
    agency_code: str | None = Field(None, alias="agencyCode")
    flights: list[FlightInfo] = Field(default_factory=list)
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    reshop_reservation_ids: list[int] = Field(
        alias="reshopReservationIds",
        default_factory=list,
    )
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    in_policy: bool | None = Field(None, alias="inPolicy")
    airline: str | None = None
    rate_code: str | None = Field(None, alias="rateCode")
    seat_selection_available: bool | None = Field(None, alias="seatSelectionAvailable")
    transborder: bool | None = None
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")
    change_price: PriceSummary | None = Field(None, alias="changePrice")
    airline_status: VendorStatusType | None = Field(None, alias="airlineStatus")


class FlightReservation(BaseModel):
    id: int | None = None
    ext: FlightReservationExt | None = None
    trip_id: int | None = Field(None, alias="tripId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    rlk: str | None = None
    vendor: str | None = None
    label: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    in_policy: bool | None = Field(None, alias="inPolicy")
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    status: ReservationStatus | None = None
    ttl: AwareOrNaiveDatetime | None = None
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    flags: int | None = None
    type: ReservationType | None = None


class FlightReservationResponse(BaseModel):
    flight: FlightReservation | None = None
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)


class FlightReservationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FlightReservationResponse | None = None


class ListFlightReservationsResponse(BaseModel):
    reservations: list[FlightReservation] = Field(default_factory=list)
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)


class ListFlightReservationsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListFlightReservationsResponse | None = None


class ListNotificationsResponse(BaseModel):
    down_to: int | None = Field(None, alias="downTo")
    notifications: list[Notification] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)


class ListNotificationsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListNotificationsResponse | None = None


class Policy(BaseModel):
    id: int | None = None
    nms: int | None = None
    org_id: int | None = Field(None, alias="orgId")
    label: str | None = None
    type: PolicyType | None = None
    active: bool | None = None
    enforce_approval: bool | None = Field(None, alias="enforceApproval")
    action: PolicyAction | None = None
    message_for_reservation: dict[str, str] = Field(
        alias="messageForReservation",
        default_factory=dict,
    )
    policy_rules: list[PolicyRule] = Field(alias="policyRules", default_factory=list)
    user_count: int | None = Field(None, alias="userCount")
    guest_count: int | None = Field(None, alias="guestCount")
    approver_count: int | None = Field(None, alias="approverCount")


class PolicyListResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: list[Policy] = Field(default_factory=list)


class PolicyResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: Policy | None = None


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
    refs: list[str] = Field(default_factory=list)
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    items: dict[str, FlightItem] = Field(default_factory=dict)
    reservations: dict[str, FlightReservation] = Field(default_factory=dict)
    users: dict[str, User] = Field(default_factory=dict)
    user_to_reward_program_ids: dict[str, list[int]] = Field(
        alias="userToRewardProgramIds",
        default_factory=dict,
    )
    vendor_to_reward_programs: dict[str, dict[str, RewardProgram]] = Field(
        alias="vendorToRewardPrograms",
        default_factory=dict,
    )
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    total_price: float | None = Field(None, alias="totalPrice")
    currency: str | None = None


class ReviewFlightsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ReviewFlightsResponse | None = None


class SeatMapCabin(BaseModel):
    first_row: int | None = Field(None, alias="firstRow")
    last_row: int | None = Field(None, alias="lastRow")
    deck: SeatMapDeck | None = None
    rows: list[SeatMapRow] = Field(default_factory=list)
    column_layout: str | None = Field(None, alias="columnLayout")
    columns: list[SeatMapColumnInfo] = Field(default_factory=list)


class SeatMapSegment(BaseModel):
    reservation_id: int | None = Field(None, alias="reservationId")
    transaction_identifier: str | None = Field(None, alias="transactionIdentifier")
    segment_key: str | None = Field(None, alias="segmentKey")
    cabins: list[SeatMapCabin] = Field(default_factory=list)
    seat_types: dict[str, SeatType] = Field(alias="seatTypes", default_factory=dict)
    currency: str | None = None
    status: SeatMapSegmentStatus | None = None


class TrainReservationExt(BaseModel):
    co2_emissions: float | None = Field(None, alias="co2Emissions")
    consumers: list[ReservationConsumer] = Field(default_factory=list)
    od: TrainReservationOd | None = None
    carrier_code: str | None = Field(None, alias="carrierCode")
    discount_amount: float | None = Field(None, alias="discountAmount")
    railcards: list[Railcard] = Field(default_factory=list)
    supported_delivery_options: list[DeliveryOption] = Field(
        alias="supportedDeliveryOptions",
        default_factory=list,
    )
    delivery_option: str | None = Field(None, alias="deliveryOption")
    terms_and_conditions_acceptance: bool | None = Field(
        None,
        alias="termsAndConditionsAcceptance",
    )
    terms_and_conditions: str | None = Field(None, alias="termsAndConditions")
    terms_and_conditions_label: str | None = Field(
        None,
        alias="termsAndConditionsLabel",
    )
    terms_and_conditions_list: list[TermsAndConditions] = Field(
        alias="termsAndConditionsList",
        default_factory=list,
    )
    train_seat_preference_flags: int | None = Field(
        None,
        alias="trainSeatPreferenceFlags",
    )
    enabled_seat_preferences_flags: int | None = Field(
        None,
        alias="enabledSeatPreferencesFlags",
    )
    applied_discounts: list[AppliedDiscount] = Field(
        alias="appliedDiscounts",
        default_factory=list,
    )
    fare_conditions: list[FareConditions] = Field(
        alias="fareConditions",
        default_factory=list,
    )
    comfort_classes: list[ComfortClass] = Field(
        alias="comfortClasses",
        default_factory=list,
    )
    ticket_collection_codes: str | None = Field(None, alias="ticketCollectionCodes")
    transaction_id: str | None = Field(None, alias="transactionId")
    open_return_until: date | None = Field(None, alias="openReturnUntil")
    has_travelcard: bool | None = Field(None, alias="hasTravelcard")
    external_id: str | None = Field(None, alias="externalId")
    requested_railcard_ids: list[int] = Field(
        alias="requestedRailcardIds",
        default_factory=list,
    )


class ApprovalInfo(BaseModel):
    sent_approval: Approval | None = Field(None, alias="sentApproval")
    draft_approval: Approval | None = Field(None, alias="draftApproval")
    org_users: list[OrgUser] = Field(alias="orgUsers", default_factory=list)
    users: list[User] = Field(default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    ui_flags: int | None = Field(None, alias="uiFlags")


class ApprovalInfoResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ApprovalInfo | None = None


class FlightDetailInformation(BaseModel):
    airline_pref_level: int | None = Field(None, alias="airlinePrefLevel")
    flights: list[FlightInfo] = Field(default_factory=list)
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    in_policy: bool | None = Field(None, alias="inPolicy")
    org_id: int | None = Field(None, alias="orgId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    total_price: float | None = Field(None, alias="totalPrice")
    taxes_and_fees: float | None = Field(None, alias="taxesAndFees")
    rate_codes: list[str] = Field(alias="rateCodes", default_factory=list)
    rate_code_descr: str | None = Field(None, alias="rateCodeDescr")
    airline: str | None = None
    org_projects: list[OrgProject] = Field(alias="orgProjects", default_factory=list)
    seat_selection_available: bool | None = Field(None, alias="seatSelectionAvailable")
    airline_status: VendorStatusType | None = Field(None, alias="airlineStatus")


class FlightSeatMapResponse(BaseModel):
    segments: list[SeatMapSegment] = Field(default_factory=list)


class FlightSeatMapResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: FlightSeatMapResponse | None = None


class OfferPolicyInfo(BaseModel):
    orgs: list[Org] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    refs: list[RefPolicyInfo] = Field(default_factory=list)


class OfferPolicyInfoResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OfferPolicyInfo | None = None


class OrgUserPolicyData(BaseModel):
    org_user: OrgUser | None = Field(None, alias="orgUser")
    org_policies: list[Policy] = Field(alias="orgPolicies", default_factory=list)
    travel_policies: list[Policy] = Field(alias="travelPolicies", default_factory=list)
    guest_policies: list[Policy] = Field(alias="guestPolicies", default_factory=list)


class OrgUserPolicyDataResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: OrgUserPolicyData | None = None


class RespImpl(BaseModel):
    data: RespData | None = None
    itineraries: list[RespItinerary] = Field(default_factory=list)
    wifis: dict[str, Wifi] = Field(default_factory=dict)
    aircrafts: dict[str, Aircraft] = Field(default_factory=dict)
    seats: dict[str, Seat] = Field(default_factory=dict)
    foods: dict[str, FreshFood] = Field(default_factory=dict)
    beverages: dict[str, Beverage] = Field(default_factory=dict)
    powers: dict[str, Power] = Field(default_factory=dict)
    entertainments: dict[str, Entertainment] = Field(default_factory=dict)
    layouts: dict[str, Layout] = Field(default_factory=dict)


class TrainReservation(BaseModel):
    id: int | None = None
    ext: TrainReservationExt | None = None
    trip_id: int | None = Field(None, alias="tripId")
    booker_id: int | None = Field(None, alias="bookerId")
    user_ids: list[int] = Field(alias="userIds", default_factory=list)
    agency_code: str | None = Field(None, alias="agencyCode")
    provider_code: str | None = Field(None, alias="providerCode")
    agency_pnr: str | None = Field(None, alias="agencyPnr")
    vendor_pnr: str | None = Field(None, alias="vendorPnr")
    rlk: str | None = None
    vendor: str | None = None
    label: str | None = None
    start_date: AwareOrNaiveDatetime | None = Field(None, alias="startDate")
    end_date: AwareOrNaiveDatetime | None = Field(None, alias="endDate")
    currency: str | None = None
    total_price: float | None = Field(None, alias="totalPrice")
    org_id: int | None = Field(None, alias="orgId")
    org_project_id: int | None = Field(None, alias="orgProjectId")
    approval_policy_ids: list[int] = Field(
        alias="approvalPolicyIds",
        default_factory=list,
    )
    in_policy: bool | None = Field(None, alias="inPolicy")
    not_in_policy_reason: str | None = Field(None, alias="notInPolicyReason")
    created_on: AwareOrNaiveDatetime | None = Field(None, alias="createdOn")
    updated_at: AwareOrNaiveDatetime | None = Field(None, alias="updatedAt")
    status: ReservationStatus | None = None
    ttl: AwareOrNaiveDatetime | None = None
    not_preferred_reason: str | None = Field(None, alias="notPreferredReason")
    flags: int | None = None
    type: ReservationType | None = None


class TrainReservationResponse(BaseModel):
    train_reservation: TrainReservation | None = Field(None, alias="trainReservation")
    stations: dict[str, TrainStation] = Field(default_factory=dict)
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)


class TrainReservationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: TrainReservationResponse | None = None


class GetTripBoardsResponse(BaseModel):
    trip: Trip | None = None
    boards: list[TripBoard] = Field(default_factory=list)
    medias: list[TripMedia] = Field(default_factory=list)
    org: Org | None = None
    users: dict[str, User] = Field(default_factory=dict)
    car_reservations: dict[str, CarReservation] = Field(
        alias="carReservations",
        default_factory=dict,
    )
    flight_reservations: dict[str, FlightReservation] = Field(
        alias="flightReservations",
        default_factory=dict,
    )
    hotel_reservations: dict[str, HotelReservation] = Field(
        alias="hotelReservations",
        default_factory=dict,
    )
    misc_reservations: dict[str, MiscReservation] = Field(
        alias="miscReservations",
        default_factory=dict,
    )
    train_reservations: dict[str, TrainReservation] = Field(
        alias="trainReservations",
        default_factory=dict,
    )
    reward_programs: dict[str, RewardProgram] = Field(
        alias="rewardPrograms",
        default_factory=dict,
    )
    user_reward_programs: dict[str, MaskedUserRewardProgram] = Field(
        alias="userRewardPrograms",
        default_factory=dict,
    )
    airlines: dict[str, Airline] = Field(default_factory=dict)
    airports: dict[str, Airport] = Field(default_factory=dict)
    train_carriers: dict[str, TrainCarrier] = Field(
        alias="trainCarriers",
        default_factory=dict,
    )
    train_stations: dict[str, TrainStation] = Field(
        alias="trainStations",
        default_factory=dict,
    )
    fields: list[FieldModel] = Field(default_factory=list)
    field_values: list[FieldValue] = Field(alias="fieldValues", default_factory=list)
    reservation_fields: list[ReservationField] = Field(
        alias="reservationFields",
        default_factory=list,
    )
    target_resource_id: int | None = Field(None, alias="targetResourceId")


class GetTripBoardsResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: GetTripBoardsResponse | None = None


class ListTrainReservationResponse(BaseModel):
    train_reservations: list[TrainReservation] = Field(
        alias="trainReservations",
        default_factory=list,
    )
    carriers: dict[str, TrainCarrier] = Field(default_factory=dict)
    stations: dict[str, TrainStation] = Field(default_factory=dict)


class ListTrainReservationResponseResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: ListTrainReservationResponse | None = None


class RecordLocator(BaseModel):
    key: str | None = None
    pnr: str | None = None
    agency_code: str | None = Field(None, alias="agencyCode")
    arranger_ids: list[int] = Field(alias="arrangerIds", default_factory=list)
    trip_id: int | None = Field(None, alias="tripId")
    car_reservations: list[CarReservation] = Field(
        alias="carReservations",
        default_factory=list,
    )
    flight_reservations: list[FlightReservation] = Field(
        alias="flightReservations",
        default_factory=list,
    )
    hotel_reservations: list[HotelReservation] = Field(
        alias="hotelReservations",
        default_factory=list,
    )
    misc_reservations: list[MiscReservation] = Field(
        alias="miscReservations",
        default_factory=list,
    )
    train_reservations: list[TrainReservation] = Field(
        alias="trainReservations",
        default_factory=list,
    )
    fees: list[ServiceFee] = Field(default_factory=list)


class RecordLocatorResponse(BaseModel):
    status: ResponseStatus | None = None
    code: int | None = None
    error: str | None = None
    data: RecordLocator | None = None


Msg.model_rebuild()
