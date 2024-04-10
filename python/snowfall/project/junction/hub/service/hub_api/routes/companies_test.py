import httpx
from starlette import status

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
