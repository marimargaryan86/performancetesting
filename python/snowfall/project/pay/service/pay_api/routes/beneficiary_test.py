from typing import Sequence

import httpx

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.pay.service.accounts.v1alpha.models_pb2 import Account
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Company
from snowfall.project.pay.service.pay_api.repositories import BeneficiaryRepository
from snowfall.stdlib import money
from snowfall.stdlib.format import jsonapi


class TestBeneficiary(object):
    async def test_post_beneficiary(  # noqa: WPS210
        self,
        admin_client: httpx.AsyncClient,
        account: Account,
        company: Company,
        available_currencies: Sequence[money.Currency],
        beneficiaries_repository: BeneficiaryRepository,
    ) -> None:
        request = {
            "data": {
                "type": "beneficiaries",
                "attributes": {
                    "bankAccountHolderName": "bankAccountHolderName",
                    "email": "example@email.com",
                    "accountNumber": "32847346",
                    "beneficiaryAddress": {
                        "addressLines": [
                            "Street name 7",
                        ],
                        "countryCode": "GB",
                        "postalCode": "12345",
                        "city": "London",
                        "state": "California",
                    },
                    "bankDetails": {
                        "name": "BankName",
                        "bicSwift": "AAAABBCC123",
                        "iban": "GB06 BARC 1231 4512 7782 32",
                        "accountType": "savings",
                        "paymentTypes": "regular",
                        "address": {
                            "addressLines": [
                                "Street name 7",
                            ],
                            "countryCode": "GB",
                            "postalCode": "12345",
                            "city": "London",
                            "state": "California",
                        },
                    },
                },
                "relationships": {
                    "currency": {
                        "data": {
                            "id": available_currencies[-1].code,
                            "type": "currencies",
                        },
                    },
                    "account": {
                        "data": {
                            "id": account.id,
                            "type": "accounts",
                        },
                    },
                },
            },
        }

        response = await admin_client.post(
            "/beneficiaries",
            json=request,
        )
        payload = response.json()["data"]
        flatten_payload = jsonapi.flatten_resource(payload)
        flatten_request = jsonapi.flatten_resource(request["data"])
        assert payload["id"]
        assert flatten_payload["currency"] == flatten_request["currency"]
        assert flatten_payload["account"] == flatten_request["account"]

        beneficiary = await beneficiaries_repository.find_by_id(payload["id"])

        assert beneficiary is not None
        assert is_valid_uuid(beneficiary.created_by)
