import pathlib
import string as pystring
from argparse import ArgumentParser
from typing import ClassVar

from locust import HttpUser, events, task

from snowfall.stdlib import string


@events.init_command_line_parser.add_listener  # type: ignore[misc]
def init_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--token",
        help="environment token to interact",
    )
    parser.add_argument(
        "--amount",
        help="amount of requests to make",
    )


class Accounts(HttpUser):
    # example command:
    # locust -f locustfile.py
    # --token $PAY_TOKEN --host https://api.pay.junction.dev -t 20s

    expected_currencies_list: ClassVar[list[str]] = [
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

    @task
    def test_list_accounts(self) -> None:
        headers = {
            "Authorization": "Bearer {0}".format(self.environment.parsed_options.token),
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
        self.client.get(
            url="/accounts",
            headers=headers,
        )

    @task
    def test_create_account(self) -> None:
        random_string_length = 32
        name = "test account perf {0}".format(
            string.random(
                random_string_length,
                pystring.ascii_letters + pystring.digits,
            ),
        )
        headers = {
            "Authorization": "Bearer {0}".format(self.environment.parsed_options.token),
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
        payload = {
            "data": {
                "type": "accounts",
                "attributes": {
                    "name": name,
                },
                "relationships": {
                    "contact": {
                        "data": {
                            "id": "00fafe5e-ad8e-47b1-b540-158b37793bb1",
                            "type": "contacts",
                        },
                    },
                },
            },
        }

        self.client.post(
            url="/accounts",
            headers=headers,
            json=payload,
        )

    @task
    def task_add_currency(self) -> None:  # noqa: WPS210
        account_id = "0"
        headers = {
            "Authorization": "Bearer {0}".format(self.environment.parsed_options.token),
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
        payload = {
            "data": {
                "type": "balances",
                "relationships": {
                    "currency": {
                        "data": {
                            "id": str(self.expected_currencies_list.pop(0)),
                            "type": "currencies",
                        },
                    },
                },
            },
        }

        response = self.client.post(
            url="/accounts/{0}/relationships/currencies".format(account_id),
            headers=headers,
            json=payload,
        )
        json_balance_id = response.json()
        balance_id = json_balance_id["data"]["id"]

        with pathlib.Path("add_currency.txt").open("a") as txt_file:
            txt_file.write(balance_id)
            txt_file.write("\n")

        if not self.expected_currencies_list:
            self.environment.runner.quit()
