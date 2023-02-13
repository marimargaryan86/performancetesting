from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

__NAMESPACE__ = "http://www.opentravel.org/OTA/2003/05"


@dataclass
class Airport(object):
    city_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "CityID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    iata: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    latitude: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    longitude: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    state_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "state-code",
            "type": "Attribute",
        },
    )


@dataclass
class City(object):
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    region_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "RegionID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    state_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "state-code",
            "type": "Attribute",
        },
    )
    iata: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    latitude: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    longitude: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Country(object):
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    iso: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISO",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class ErrorMessage(object):
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    type: Optional[int] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


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


@dataclass
class Region(object):
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )
    country_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "countryID",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "required": True,
        },
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    state_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "state-code",
            "type": "Attribute",
        },
    )


@dataclass
class VehicleAirportRequest(object):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    region_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "RegionId",
            "type": "Element",
            "required": True,
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Element",
        },
    )
    city_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "CityID",
            "type": "Element",
            "required": True,
        },
    )
    country_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "CountryID",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class VehicleCityRequest(object):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    region_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "RegionId",
            "type": "Element",
            "required": True,
        },
    )
    country_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "CountryID",
            "type": "Element",
            "required": True,
        },
    )
    country_iso: Optional[str] = field(
        default=None,
        metadata={
            "name": "CountryISO",
            "type": "Element",
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Element",
        },
    )


@dataclass
class VehicleCountryRequest(object):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Element",
        },
    )


@dataclass
class VehicleRegionRequest(object):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Element",
        },
    )
    country_iso: Optional[str] = field(
        default=None,
        metadata={
            "name": "CountryISO",
            "type": "Element",
        },
    )


@dataclass
class ArrayOfAirport(object):
    airport: List[Airport] = field(
        default_factory=list,
        metadata={
            "name": "Airport",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfCity(object):
    city: List[City] = field(
        default_factory=list,
        metadata={
            "name": "City",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfCountry(object):
    country: List[Country] = field(
        default_factory=list,
        metadata={
            "name": "Country",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class ArrayOfErrorMessage(object):
    error_message: List[ErrorMessage] = field(
        default_factory=list,
        metadata={
            "name": "ErrorMessage",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
            "nillable": True,
        },
    )


@dataclass
class ArrayOfRegion(object):
    region: List[Region] = field(
        default_factory=list,
        metadata={
            "name": "Region",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class DestinationSoapGetAirportsInput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetAirportsInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_airport_request: Optional[VehicleAirportRequest] = field(
            default=None,
            metadata={
                "name": "VehicleAirportRequest",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class DestinationSoapGetCitiesInput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetCitiesInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_city_request: Optional[VehicleCityRequest] = field(
            default=None,
            metadata={
                "name": "VehicleCityRequest",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class DestinationSoapGetCountriesInput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetCountriesInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_country_request: Optional[VehicleCountryRequest] = field(
            default=None,
            metadata={
                "name": "VehicleCountryRequest",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class DestinationSoapGetRegionsInput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetRegionsInput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_region_request: Optional[VehicleRegionRequest] = field(
            default=None,
            metadata={
                "name": "VehicleRegionRequest",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )


@dataclass
class InformationHeader(InformationHeader1):
    class Meta(object):
        name = "informationHeader"
        namespace = "http://www.opentravel.org/OTA/2003/05"


@dataclass
class DestinationResponse(object):
    errors: Optional[ArrayOfErrorMessage] = field(
        default=None,
        metadata={
            "name": "Errors",
            "type": "Element",
            "namespace": "http://www.opentravel.org/OTA/2003/05",
        },
    )


@dataclass
class VehicleAirportResponse(DestinationResponse):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    airports: Optional[ArrayOfAirport] = field(
        default=None,
        metadata={
            "name": "Airports",
            "type": "Element",
        },
    )


@dataclass
class VehicleCityResponse(DestinationResponse):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    cities: Optional[ArrayOfCity] = field(
        default=None,
        metadata={
            "name": "Cities",
            "type": "Element",
        },
    )


@dataclass
class VehicleCountryResponse(DestinationResponse):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    countries: Optional[ArrayOfCountry] = field(
        default=None,
        metadata={
            "name": "Countries",
            "type": "Element",
        },
    )


@dataclass
class VehicleRegionResponse(DestinationResponse):
    class Meta(object):
        namespace = "http://www.opentravel.org/OTA/2003/05"

    regions: Optional[ArrayOfRegion] = field(
        default=None,
        metadata={
            "name": "Regions",
            "type": "Element",
        },
    )


@dataclass
class DestinationSoapGetAirportsOutput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetAirportsOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["DestinationSoapGetAirportsOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_airport_response: Optional[VehicleAirportResponse] = field(
            default=None,
            metadata={
                "name": "VehicleAirportResponse",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["DestinationSoapGetAirportsOutput.Body.Fault"] = field(
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
class DestinationSoapGetCitiesOutput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetCitiesOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["DestinationSoapGetCitiesOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_city_response: Optional[VehicleCityResponse] = field(
            default=None,
            metadata={
                "name": "VehicleCityResponse",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["DestinationSoapGetCitiesOutput.Body.Fault"] = field(
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
class DestinationSoapGetCountriesOutput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetCountriesOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["DestinationSoapGetCountriesOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_country_response: Optional[VehicleCountryResponse] = field(
            default=None,
            metadata={
                "name": "VehicleCountryResponse",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["DestinationSoapGetCountriesOutput.Body.Fault"] = field(
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
class DestinationSoapGetRegionsOutput(object):
    class Meta(object):
        name = "Envelope"
        namespace = "http://schemas.xmlsoap.org/soap/envelope/"

    body: Optional["DestinationSoapGetRegionsOutput.Body"] = field(
        default=None,
        metadata={
            "name": "Body",
            "type": "Element",
        },
    )
    header: Optional["DestinationSoapGetRegionsOutput.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
        },
    )

    @dataclass
    class Body(object):
        vehicle_region_response: Optional[VehicleRegionResponse] = field(
            default=None,
            metadata={
                "name": "VehicleRegionResponse",
                "type": "Element",
                "namespace": "http://www.opentravel.org/OTA/2003/05",
            },
        )
        fault: Optional["DestinationSoapGetRegionsOutput.Body.Fault"] = field(
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


class DestinationSoapGetAirports(object):
    style = "document"
    location = "https://ota2007a.micronnexus-staging.com/destination.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/GetAirports"
    input = DestinationSoapGetAirportsInput
    output = DestinationSoapGetAirportsOutput


class DestinationSoapGetCities(object):
    style = "document"
    location = "https://ota2007a.micronnexus-staging.com/destination.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/GetCities"
    input = DestinationSoapGetCitiesInput
    output = DestinationSoapGetCitiesOutput


class DestinationSoapGetCountries(object):
    style = "document"
    location = "https://ota2007a.micronnexus-staging.com/destination.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/GetCountries"
    input = DestinationSoapGetCountriesInput
    output = DestinationSoapGetCountriesOutput


class DestinationSoapGetRegions(object):
    style = "document"
    location = "https://ota2007a.micronnexus-staging.com/destination.asmx"
    transport = "http://schemas.xmlsoap.org/soap/http"
    soap_action = "http://www.opentravel.org/OTA/2003/05/GetRegions"
    input = DestinationSoapGetRegionsInput
    output = DestinationSoapGetRegionsOutput
