import pytest_httpx

from snowfall.vendor.fluxir import client
from snowfall.vendor.fluxir.models import travel_services as travel_services_models


async def test_get_service_intents(
    httpx_mock: pytest_httpx.HTTPXMock,
    fluxir_client: client.FluxirClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/travel-services/service-intents?from=01-01-2024&to=01-02-2024&nationalityCountryCode=JOR&destinationCountryCode=ARE&tripPurpose=Business",
        status_code=200,
        json={
            "items": [
                {
                    "redirectUri": "https://travel.fluxir.com/applications/external?serviceIntentKey=Visa-Fluxir-ARE-2&from=01-01-2024&to=01-02-2024&origination=JOR&destination=ARE&tokenStoreKey=61cd48cf-9f64-4006-bf55-1e250ac7e053",
                    "title": "United Arab Emirates (the) Tourist one month ",
                    "description": "Single entry - 3 days processing time - Validity 2 Months",
                    "info": "A one month tourist visa for the United Arab Emirates allows an individual to visit the UAE for a period of up to 30 days. This type of visa is typically issued for single entry, meaning that the holder can only enter the UAE once during the validity of the visa. The purpose of the visit must be tourism or business, and the visa holder is not allowed to work or engage in any other activities that are not related to tourism or business.",
                    "fee": 96,
                    "appliersCount": "123",
                    "approvalRate": "98",
                    "stayDuration": "30",
                    "stayDurationUnit": "Days",
                    "validityPeriod": "2",
                    "validityPeriodUnit": "Months",
                    "expectedProcessingTime": "72",
                },
                {
                    "redirectUri": "https://travel.fluxir.com/applications/external?serviceIntentKey=Visa-Fluxir-ARE-4&from=01-01-2024&to=01-02-2024&origination=JOR&destination=ARE&tokenStoreKey=61cd48cf-9f64-4006-bf55-1e250ac7e053",
                    "title": "United Arab Emirates (the) tourism visa two month",
                    "description": "Single entry - 3 days processing time - Validity 2 Months",
                    "info": "tourism visa two month",
                    "fee": 220,
                    "appliersCount": "1",
                    "approvalRate": "100",
                    "stayDuration": "60",
                    "stayDurationUnit": "Days",
                    "validityPeriod": "2",
                    "validityPeriodUnit": "Months",
                    "expectedProcessingTime": "72",
                },
            ],
        },
    )

    httpx_mock.add_response(
        url="https://test_url/connect/token",
        status_code=200,
        json={
            "access_token": "access_token",
            "expires_in": 31536000,
            "token_type": "Bearer",
            "refresh_token": "refresh_token",
            "scope": "email offline_access profile TravelAide",
        },
    )

    params = {
        "from": "01-01-2024",
        "to": "01-02-2024",
        "nationality_country_code": "JOR",
        "destination_country_code": "ARE",
        "trip_purpose": "Business",
    }

    response = await fluxir_client.get_service_intents(
        travel_services_models.GetServiceIntentsRequest(
            **params,
        ),
    )

    assert len(response.items) == 2
