import uuid as pyuuid
from argparse import ArgumentParser

from locust import HttpUser, constant_pacing, events, task


@events.init_command_line_parser.add_listener  # type: ignore[misc]
def init_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--token",
        help="environment token to interact",
    )


class Transactions(HttpUser):
    # example command:
    # locust -f locustfile.py
    # --token $PAY_TOKEN --host https://api.pay.junction.dev -t 20s

    quotations_list: list[str]
    wait_time = constant_pacing(1)  # type: ignore[no-untyped-call]

    def on_start(self) -> None:
        with open("quotations.txt") as txt_file:
            self.quotations_list = [line.strip() for line in txt_file]

    @task
    def test_transactions(self) -> None:  # noqa: WPS210
        if not self.quotations_list:
            self.environment.runner.quit()
        payload = {
            "data": {
                "type": "transactions",
                "attributes": {
                    "externalReference": str(pyuuid.uuid4()),
                    "invoiceReference": str(pyuuid.uuid4()),
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": str(self.quotations_list.pop(0)),
                            "type": "quotations",
                        },
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
            url="/transactions",
            headers=headers,
            json=payload,
        )
        json_transaction_id = response.json()
        transaction_id = json_transaction_id["data"]["id"]
        with open("transactions.txt", "a") as txt_file:
            txt_file.write(transaction_id)
            txt_file.write("\n")
