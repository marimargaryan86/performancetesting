import asyncio
import json
import types
from datetime import date, timedelta

import httpx
import structlog

from snowfall.stdlib.time import date_to_age
from snowfall.vendor.save_a_train.enums import PassengerType
from snowfall.vendor.save_a_train.exceptions import SATValidationError, SATValueError
from snowfall.vendor.save_a_train.models.booking import (
    BookingConfirmationResult,
    BookingResult,
    TicketInfo,
)
from snowfall.vendor.save_a_train.models.general_search import GeneralSearchResponse
from snowfall.vendor.save_a_train.models.misc import (
    VendorStation,
    VendorStationsResponse,
)
from snowfall.vendor.save_a_train.models.request import (
    CreateBookingRequest,
    CreateSearchRequest,
    GeneralSearchResultsRequest,
    GetTariffConditionsRequest,
    SearchResultRequest,
    SelectSearchResultRequest,
)
from snowfall.vendor.save_a_train.models.search import SearchResponse
from snowfall.vendor.save_a_train.models.search_result_details import (
    SearchResultDetails,
)
from snowfall.vendor.save_a_train.models.search_result_selection import (
    SearchResultSelectionResponse,
)
from snowfall.vendor.save_a_train.models.tariff_condition import (
    TariffConditionsResponse,
)

_ALL_STATIONS = types.MappingProxyType(
    {
        # Milan
        "SAT_IT_MI_CORPK": [
            "SAT_IT_MI_QEFCI",
            "SAT_IT_MI_SBFZC",
            "SAT_IT_MI_PFLRJ",
            "SAT_IT_MI_CJUPA",
            "SAT_IT_MI_APRMW",
            "SAT_IT_MI_BOUFZ",
            "SAT_IT_MI_GKBYM",
            "SAT_IT_FE_XJSDM",
            "SAT_IT_SO_CFPKX",
            "SAT_IT_MI_CMILH",
            "SAT_IT_MI_FGWKM",
            "SAT_IT_MI_SEGCW",
            "SAT_IT_MI_PABZX",
            "SAT_IT_MI_OXCEQ",
            "SAT_IT_MI_DAOIK",
            "SAT_IT_MI_YWSPI",
            "SAT_IT_MI_WYLVA",
            "SAT_IT_MI_BWSYJ",
            "SAT_IT_MI_LWBYR",
            "SAT_IT_MI_CIRFV",
            "SAT_IT_MI_QCTJI",
            "SAT_IT_MI_FGVIJ",
            "SAT_IT_MI_IKCMH",
            "SAT_IT_MI_CMLWP",
            "SAT_IT_MI_KUJFN",
            "SAT_IT_MI_UDESI",
            "SAT_IT_MI_WEZUL",
        ],
        # Paris
        "SAT_FR_PA_WXNGQ": [
            "SAT_FR_PA_JUAYV",
            "SAT_FR_PA_FQZRE",
            "SAT_FR_PA_SJPTG",
            "SAT_FR_PA_NQAHE",
            "SAT_FR_PA_CDJGK",
            "SAT_FR_PA_IEURS",
            "SAT_FR_PA_KDIEJ",
            "SAT_FR_PA_LQYTV",
            "SAT_FR_PA_UZYNA",
            "SAT_FR_PA_FHTKG",
            "SAT_FR_PA_OGFZW",
            "SAT_FR_PA_XBLMP",
            "SAT_FR_PA_ZBKAL",
            "SAT_FR_PA_CPFNI",
            "SAT_FR_PA_UERLX",
            "SAT_FR_PA_JCLTK",
            "SAT_FR_LE_PGOKY",
            "SAT_FR_LE_QJIAL",
        ],
        # Genoa
        "SAT_IT_GE_JMAZN": [
            "SAT_IT_GE_ATUJP",
            "SAT_IT_GE_IBCZH",
            "SAT_IT_GE_AOJNL",
            "SAT_IT_GE_ZRAXE",
            "SAT_IT_GE_UFRBD",
            "SAT_IT_GE_RFSUQ",
            "SAT_IT_GE_FXPRG",
            "SAT_IT_GE_CXJBO",
            "SAT_IT_GE_VFNQI",
            "SAT_IT_GE_QTPJD",
            "SAT_IT_GE_GSPFT",
            "SAT_IT_GE_MHYRU",
            "SAT_IT_GE_FQRVH",
            "SAT_IT_GE_MIKEX",
            "SAT_IT_GE_WYOSU",
            "SAT_IT_GE_WMUCZ",
            "SAT_IT_GE_GZBEL",
            "SAT_IT_GE_HCRZW",
            "SAT_IT_GE_QMXSW",
            "SAT_IT_VE_UZVTD",
            "SAT_IT_GE_ROQNT",
            "SAT_IT_GE_BSOMQ",
        ],
        # Rimini
        "SAT_IT_RI_RNQMC": [
            "SAT_IT_RI_WJCXV",
            "SAT_IT_RI_LXECM",
            "SAT_IT_RI_WFSUK",
            "SAT_IT_RI_QSMOU",
            "SAT_IT_RI_WUIKB",
        ],
        # Reggio Di Calabria
        "SAT_IT_RE_YQWXH": [
            "SAT_IT_RE_HWFVT",
            "SAT_IT_RE_NFGMS",
            "SAT_IT_RE_HVSTO",
            "SAT_IT_RE_SZDXQ",
            "SAT_IT_RE_JHKAS",
            "SAT_IT_RE_PDRCV",
            "SAT_IT_RE_XLHBE",
            "SAT_IT_RE_HDUNZ",
            "SAT_IT_RE_RCLWB",
            "SAT_IT_RE_VACRW",
            "SAT_IT_RE_ZPRKE",
            "SAT_IT_RE_XQKGV",
            "SAT_IT_RE_XGBVE",
        ],
        # Bologna
        "SAT_IT_BO_KXSZB": [
            "SAT_IT_BO_SOVAI",
            "SAT_IT_BO_RZUJO",
            "SAT_IT_BO_KHGSY",
            "SAT_IT_BO_LPSQJ",
            "SAT_IT_BO_SNPFI",
            "SAT_IT_BO_KMABS",
            "SAT_IT_BO_NEUVG",
            "SAT_IT_BO_KGCNL",
            "SAT_IT_BO_BIWMX",
            "SAT_IT_BO_XGMBS",
        ],
        # Catania
        "SAT_IT_CA_LNKYP": [
            "SAT_IT_CA_LNOEB",
            "SAT_IT_CA_VFDAQ",
            "SAT_IT_CA_JMCZK",
            "SAT_IT_CA_VFOLP",
        ],
        # Florence
        "SAT_IT_FI_QFKWG": [
            "SAT_IT_FI_OGDEY",
            "SAT_IT_FI_BOHWK",
            "SAT_IT_FI_NMJVX",
            "SAT_IT_FI_VJCOH",
            "SAT_IT_FI_HSZYB",
            "SAT_IT_FI_PRBID",
            "SAT_IT_FI_WKJIP",
            "SAT_IT_FI_JLVPD",
            "SAT_IT_FI_SZOBJ",
            "SAT_IT_FI_JADHU",
        ],
        # Benevento
        "SAT_IT_BE_XFSRC": [
            "SAT_IT_BE_IOAGL",
            "SAT_IT_BE_XBLDQ",
            "SAT_IT_BE_RJMGE",
            "SAT_IT_BE_NJAHE",
        ],
        # Bari
        "SAT_IT_BA_KHRVG": [
            "SAT_IT_BA_DVSUO",
            "SAT_IT_BA_OLUGM",
            "SAT_IT_BA_SRUAW",
            "SAT_IT_BA_IFSWG",
            "SAT_IT_PA_JPNDA",
            "SAT_IT_BA_GVDHX",
            "SAT_IT_BA_IWLOZ",
            "SAT_IT_BA_GUYCD",
            "SAT_IT_BA_STUHL",
            "SAT_IT_BA_AVOJI",
            "SAT_IT_ZO_SRGZL",
        ],
        # Turin
        "SAT_IT_TO_LIPOA": [
            "SAT_IT_TO_ZAMWU",
            "SAT_IT_TO_ZHXDJ",
            "SAT_IT_TU_ZTDFW",
            "SAT_IT_TO_GNMEQ",
            "SAT_IT_CI_IVTXD",
            "SAT_IT_TO_PRXOT",
            "SAT_IT_TO_NIAMH",
            "SAT_IT_TO_LRWXU",
        ],
        # Venice
        "SAT_IT_VE_ANEMH": [
            "SAT_IT_VE_DQSJV",
            "SAT_IT_VE_PDCSE",
            "SAT_IT_VE_IACBO",
            "SAT_IT_VE_THPRZ",
            "SAT_IT_VE_FQYNO",
        ],
        # Pisa
        "SAT_IT_PI_SYKMI": [
            "SAT_IT_PI_AEJXG",
            "SAT_IT_PI_LFYZU",
            "SAT_IT_PI_CPGSN",
        ],
        # Rome
        "SAT_IT_RO_VJWUO": [
            "SAT_IT_RO_UFWPE",
            "SAT_IT_RO_JXWUR",
            "SAT_IT_RO_NWKZD",
            "SAT_IT_RO_JDHFT",
            "SAT_IT_RO_YBMAF",
            "SAT_IT_RO_KALQU",
            "SAT_IT_RO_PJNOY",
            "SAT_IT_RO_BIDEX",
            "SAT_IT_RO_JKHAL",
            "SAT_IT_RO_HBRKA",
            "SAT_IT_RO_ENTBH",
            "SAT_IT_RO_DREOM",
            "SAT_IT_RO_HWCUR",
            "SAT_IT_RO_TLECK",
        ],
        # Civitavecchia
        "SAT_IT_CI_DOEQL": [
            "SAT_IT_CI_MWVHO",
            "SAT_IT_CI_BZXYH",
            "SAT_IT_CI_BNKVA",
        ],
        # Naples
        "SAT_IT_NA_ZSNVP": [
            "SAT_IT_NA_JUEIB",
            "SAT_IT_AF_WVXOP",
            "SAT_IT_NA_BZHOP",
            "SAT_IT_NA_ODUYR",
            "SAT_IT_NA_NQMHA",
            "SAT_IT_NA_VJMAT",
            "SAT_IT_NA_XVNEY",
            "SAT_IT_NA_LZRAC",
            "SAT_IT_NA_QHBLC",
            "SAT_IT_NA_UJFME",
            "SAT_IT_NA_WHSEV",
            "SAT_IT_NA_FGOAN",
            "SAT_IT_NA_EZTRC",
        ],
        # Palermo
        "SAT_IT_PA_WYQEI": [
            "SAT_IT_PA_FMTAG",
            "SAT_IT_PA_BJSWP",
            "SAT_IT_PA_UVSYI",
            "SAT_IT_LO_VQSRC",
            "SAT_IT_PU_KRYZH",
            "SAT_IT_GU_MGFYR",
        ],
        # Ancona
        "SAT_IT_AN_LBQVT": [
            "SAT_IT_AN_AHQSE",
            "SAT_IT_VI_CUMTL",
            "SAT_IT_AN_GSYUZ",
            "SAT_IT_AN_FNGMR",
            "SAT_IT_AN_DRSIZ",
            "SAT_IT_AN_LCWZF",
        ],
    },
)


def _get_passenger_type_by_age(age: int) -> str:
    passenger_min_age = 0
    passenger_max_age = 150
    if age < passenger_min_age or age > passenger_max_age:
        raise SATValueError("Invalid passenger age: {0}.".format(age))

    passenger_senior_min_age = 60
    passenger_youth_max_age = 25

    passenger_type = PassengerType.adult

    if age >= passenger_senior_min_age:
        passenger_type = PassengerType.senior

    if age <= passenger_youth_max_age:
        passenger_type = PassengerType.youth

    return "Search::PassengerType::{0}".format(passenger_type.value)


def _generate_passenger_type_attributes(
    date_of_birth: date,
) -> dict[str, str | int]:
    age = date_to_age(date_of_birth)
    return {
        "type": _get_passenger_type_by_age(age),
        "age": age,
    }


def _exception_message_from_response(response: httpx.Response) -> str:
    message = ""
    response_data = response.json()
    if isinstance(response_data, dict):
        message = "; ".join(response_data.values())
    return message


class SATClient(object):  # noqa: WPS214
    """Save A Train API client library."""

    def __init__(  # noqa: WPS211
        self,
        email: str,
        password: str,
        password_search: str,
        token: str | None,
        api_url: str,
        api_search_url: str,
        api_search_timeout: int,
        api_search_requests_limit: int,
        client: httpx.AsyncClient,
    ) -> None:
        """Construct Save A Train API client library.

        :param email: Email that identifies agent user, under whose privileges the
            requested operation executes
        :type email: str
        :param password: Password used to generate token for API requests
        :type password: str
        :param password_search: Password used to authorize Search API requests
        :type: str
        :param token: Secret key specific to each agent, used to authorize API requests
        :type token: str
        :param api_url: API base URL
        :type api_url: str
        :param api_search_url: Search API base URL
        :type api_search_url: str
        :type api_search_timeout: int
        """
        self._email = email
        self._password = password
        self._password_search = password_search or password
        self._token = token or ""
        self._api_url = api_url
        self._api_search_url = api_search_url
        self._api_search_timeout = api_search_timeout
        self._session = client
        self._semaphore = asyncio.BoundedSemaphore(api_search_requests_limit)
        self._all_stations = {
            station_id: global_station_id
            for global_station_id, station_ids in _ALL_STATIONS.items()
            for station_id in station_ids
        }
        self._logger = structlog.get_logger(__name__)

    async def get_vendor_stations(self) -> VendorStationsResponse:
        response = await self._session.get(
            "{0}vendor_stations".format(self._api_url),
            headers=self._auth_headers,
        )

        response.raise_for_status()

        response_data = response.json()

        return VendorStationsResponse(
            stations=[VendorStation(**station) for station in response_data],
        )

    async def get_general_search_results(
        self,
        request: GeneralSearchResultsRequest,
    ) -> GeneralSearchResponse:
        """Perform a search through Search API."""
        request_params = httpx.QueryParams(
            triptype=request.trip_type.value,
            passengers=request.number_of_passengers,
            ddate=(request.departure_date - timedelta(hours=1)).isoformat(),
            rdate=(
                (request.return_date - timedelta(hours=1)).isoformat()
                if request.return_date
                else ""
            ),
            email=self._email,
            password=self._password_search,
        )

        async with self._semaphore:
            # As per SAT docs it is preferable to use city's "all stations" variant
            response = await self._session.get(
                "{0}/{1}/{2}".format(
                    self._api_search_url,
                    self._all_stations.get(request.origin_id, request.origin_id),
                    self._all_stations.get(
                        request.destination_id,
                        request.destination_id,
                    ),
                ),
                params=request_params,
                timeout=self._api_search_timeout,
            )

        response.raise_for_status()

        response_data = response.json()
        if "errors" in response_data:
            raise SATValidationError(response_data)

        return GeneralSearchResponse(**response_data)

    async def create_token(self) -> str:
        """Create token.

        :raises httpx.TimeoutException: If request times out
        :raises httpx.HTTPStatusError: If request fails
        """
        request_params = {
            "email": self._email,
            "password": self._password,
        }

        response = await self._session.post(
            "{0}/sales_agent_sessions".format(self._api_url),
            params=request_params,
        )

        response.raise_for_status()

        response_data = response.json()

        return response_data["access_token"]

    async def create_search(self, request: CreateSearchRequest) -> SearchResponse:
        """Create a search."""
        body = {
            "search": {
                "departure_datetime": request.departure_datetime.strftime(
                    "%Y-%m-%d %H:%M",
                ),
                "route_attributes": {
                    "origin_station_attributes": {
                        "uid": request.origin_id,
                    },
                    "destination_station_attributes": {
                        "uid": request.destination_id,
                    },
                },
                "searches_passengers_attributes": {
                    str(number): {
                        "age": age,
                        "passenger_type_attributes": {
                            "type": _get_passenger_type_by_age(age),
                        },
                    }
                    for number, age in enumerate(request.passengers_ages)
                },
            },
        }

        self._logger.info("SAT book search request", request=json.dumps(body))

        response = await self._session.post(
            "{0}/searches".format(self._api_url),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return SearchResponse(**response_data)

    async def get_search_result_details(
        self,
        request: SearchResultRequest,
    ) -> SearchResultDetails:
        """Get search result's details: transfers and fares."""
        response = await self._session.get(
            "{0}/searches/{1}/results/{2}/sub_routes".format(
                self._api_url,
                request.search_id,
                request.search_result_id,
            ),
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return SearchResultDetails(**response_data)

    async def select_search_result(
        self,
        request: SelectSearchResultRequest,
    ) -> SearchResultSelectionResponse:
        """Confirm selection of search result, transfer and fare."""
        body = {
            "select_results_attributes": {
                "search_identifier": request.search_id,
                "result_id": request.search_result_id,
                "transfers_attributes": {
                    "0": {
                        "id": request.transfer_id,
                        "fare_id": request.fare_id,
                    },
                },
            },
        }

        self._logger.info("SAT select search request", request=json.dumps(body))

        response = await self._session.post(
            "{0}/searches/{1}/confirm_selection".format(
                self._api_url,
                request.search_id,
            ),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return SearchResultSelectionResponse(**response_data)

    async def get_tariff_conditions(
        self,
        request: GetTariffConditionsRequest,
    ) -> TariffConditionsResponse:
        """Get fare's tariff conditions."""
        response = await self._session.get(
            "{0}/searches/{1}/results/{2}/tariff_conditions/{3}".format(
                self._api_url,
                request.search_id,
                request.search_result_id,
                request.tariff_condition_id,
            ),
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return TariffConditionsResponse(**response_data)

    async def create_booking(self, request: CreateBookingRequest) -> BookingResult:
        """Create a booking for search identified by ``search_id``."""
        order_passenger = request.passengers[0]
        body = {
            "booking": {
                "search_identifier": request.search_id,
                "order_customer_attributes": {
                    "email": order_passenger.email,
                    "fname": order_passenger.first_name,
                    "lname": order_passenger.last_name,
                    "gender": order_passenger.gender.value,
                    "mobile": order_passenger.phone_number,
                },
                "passengers_attributes": {
                    str(number): {
                        "title": passenger.title.value,
                        "fname": passenger.first_name,
                        "lname": passenger.last_name,
                        "birthdate": passenger.date_of_birth.isoformat(),
                        "country": passenger.country,
                        "gender": passenger.gender.value,
                        "passenger_type_attributes": (
                            _generate_passenger_type_attributes(
                                passenger.date_of_birth,
                            )
                        ),
                    }
                    for number, passenger in enumerate(request.passengers)
                },
                "seat_preference_attributes": {
                    "seat_preference_outbound": request.seat_preference_code,
                    "seat_preference_inbound": None,
                },
            },
        }

        self._logger.info("SAT booking request", request=json.dumps(body))

        response = await self._session.post(
            "{0}/bookings".format(self._api_url),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        return BookingResult(**response.json())

    async def confirm_booking(self, search_id: str) -> BookingConfirmationResult:
        """Confirm booking.

        :param search_id: Search identifier
        :raises httpx.TimeoutException: If request times out
        :raises httpx.HTTPStatusError: If request fails
        """
        body = {
            "booking": {
                "search_identifier": search_id,
            },
        }

        response = await self._session.post(
            "{0}/bookings/confirm".format(self._api_url),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return BookingConfirmationResult(**response_data)

    async def get_ticket(self, search_id: str) -> TicketInfo:
        """Get ticket information.

        :param search_id: Search identifier
        :raises httpx.TimeoutException: If request times out
        :raises httpx.HTTPStatusError: If request fails
        """
        response = await self._session.get(
            "{0}/order_images/{1}".format(self._api_url, search_id),
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.NOT_FOUND:
            raise SATValueError()

        response.raise_for_status()

        response_data = response.json()

        return TicketInfo(**response_data)

    @property
    def _auth_headers(self) -> dict[str, str]:
        """Generate auth header for API requests."""
        return {
            "X-Agent-Email": self._email,
            "X-Agent-Token": self._token,
        }
