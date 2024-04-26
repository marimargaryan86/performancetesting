import httpx
from starlette import status

from snowfall.project.junction.hub.service.hub_api import crypto_manager
from snowfall.project.pay.fixtures import COMPANIES
from snowfall.stdlib.integration.starlette import testing


class TestCompanies:
    async def test_get_all_companies(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/companies",
            expected_ids=COMPANIES,
        )

    async def test_create_company(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = {
            "data": {
                "type": "companies",
                "attributes": {
                    "name": "Company Name",
                    "address": {
                        "addressLines": ["Street name 7"],
                        "countryCode": "GB",
                        "postalCode": "12345",
                        "city": "London",
                        "state": "California",
                    },
                    "fxMarkup": 5.6,
                    "processingMarkup": 5.6,
                    "salesMarkup": 5.6,
                    "feeAmounts": [{"currency": "EUR", "amount": 1337}],
                    "paymentType": "card",
                    "billingType": "percentage",
                    "paymentMethod": "transactional",
                    "applyMarkups": True,
                    "invoiceGenerationFrequency": 7,
                    "verticalFees": [
                        {
                            "verticalType": "hotel",
                            "billingType": "percentage",
                            "value": 5.6,
                        },
                        {
                            "verticalType": "air",
                            "billingType": "fixed",
                            "value": 12,
                        },
                    ],
                },
            },
        }
        response = await client.post(
            "/companies",
            json=payload,
        )

        assert response.status_code == status.HTTP_201_CREATED


class TestOnboardingTokens:
    async def test_create_onboarding_token(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        payload = {
            "data": {
                "type": "onboarding-tokens",
                "relationships": {
                    "company": {
                        "data": {
                            "id": "9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
                            "type": "companies",
                        },
                    },
                },
            },
        }

        response = await client.post(
            "/onboarding-tokens",
            json=payload,
        )

        assert response.status_code == status.HTTP_201_CREATED

    async def test_get_onboarding_token_company_details(
        self,
        client: httpx.AsyncClient,
        crypto_client: crypto_manager.CryptoManager,
    ) -> None:
        token = crypto_client.encrypt({
            "companyId": "9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
        })
        response = await client.get(
            "/onboarding-tokens/{token}".format(token=token),
        )

        assert response.status_code == status.HTTP_200_OK
