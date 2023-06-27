import random
from argparse import ArgumentParser
from typing import ClassVar

from locust import HttpUser, constant_pacing, events, task


@events.init_command_line_parser.add_listener  # type: ignore[misc]
def init_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--token",
        help="environment token to interact",
    )
    parser.add_argument(
        "--quotes",
        help="amount of quotes to produce",
    )


class Quotes(HttpUser):
    # example command:
    # locust -f locustfile_preprocessor.py
    # --token $PAY_TOKEN --host https://api.pay.junction.dev -t 10s
    # --headless --autostart --quotes $QUOTES_AMOUNT

    quotations_list: ClassVar[list[str]] = []
    wait_time = constant_pacing(3)  # type: ignore[no-untyped-call]

    @task
    def test_get_quotations(self) -> None:  # noqa: WPS210
        expected_currencies_list = [
            "AUD",
            "BHD",
            "BGN",
            "CAD",
            "CNY",
            "CZK",
            "DKK",
            "EUR",
            "HKD",
            "HUF",
            "ILS",
            "JPY",
            "KES",
            "KWD",
            "NZD",
            "NOK",
            "OMR",
            "PLN",
            "QAR",
            "RON",
            "SAR",
            "SGD",
            "ZAR",
            "SEK",
            "CHF",
            "THB",
            "TRY",
            "UGX",
            "GBP",
            "AED",
            "USD",
        ]
        payer_company_with_all_currencies = "dc8c23d0-ff4b-4c4e-b700-4ae934ff824d"
        beneficiary_company_with_all_currencies = "dded3966-5c57-46dc-a8f8-212ae4287bde"
        from_currency, to_currency = random.sample(expected_currencies_list, 2)

        payload = {
            "data": {
                "type": "quotes",
                "attributes": {
                    "amount": 1000,
                    "externalReference": "pay quotation api perf tests",
                },
                "relationships": {
                    "fromCurrency": {
                        "data": {
                            "id": from_currency,
                            "type": "currencies",
                        },
                    },
                    "payer": {
                        "data": {
                            "id": payer_company_with_all_currencies,
                            "type": "companies",
                        },
                    },
                    "beneficiary": {
                        "data": {
                            "id": beneficiary_company_with_all_currencies,
                            "type": "companies",
                        },
                    },
                    "toCurrency": {
                        "data": {"id": to_currency, "type": "currencies"},
                    },
                },
            },
        }

        headers = {
            "Authorization": "Bearer {0}".format(self.environment.parsed_options.token),
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
        response = self.client.post(
            url="/quotes",
            headers=headers,
            json=payload,
        )
        json_quotation_id = response.json()
        quotation_id = json_quotation_id["data"]["id"]
        self.quotations_list.append(quotation_id)
        with open("quotations.txt", "a") as txt_file:
            txt_file.write(quotation_id)
            txt_file.write("\n")
        if len(self.quotations_list) >= int(self.environment.parsed_options.quotes):
            self.environment.runner.quit()
