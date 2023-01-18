import currencycloud
import lagom
from starlette import endpoints, requests, responses

from snowfall.project.pay.service.pay_api import pagination_helpers
from snowfall.stdlib import money

_ID_KEY = "id"
_TYPE_KEY = "type"
_DATA_KEY = "data"


class Transactions(endpoints.HTTPEndpoint):
    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        client: currencycloud.Client = lagom.injectable,
    ) -> responses.Response:
        mapped_params = pagination_helpers.map_query_params(
            dict(request.query_params),
            pagination_helpers.PAGINATION_PARAMS_MAPPING,
        )
        transactions = client.transactions.find(**mapped_params)

        next_url = pagination_helpers.get_next_link(
            request.url_for("Transactions"),
            transactions.pagination,
        )

        response = []

        for transaction in transactions:
            price = money.from_string(
                transaction.amount,
                money.Currency(transaction.currency),
            )
            completed_at = (
                transaction.completed_at if transaction.completed_at else None
            )

            response.append(
                {
                    _ID_KEY: transaction.id,
                    _TYPE_KEY: "transactions",
                    "attributes": {
                        "amount": price.amount,
                        "ref": transaction.related_entity_short_reference,
                        "completedAt": completed_at,
                        "createdAt": transaction.created_at,
                    },
                    "relationships": {
                        "currency": {
                            _DATA_KEY: {
                                _TYPE_KEY: "currencies",
                                _ID_KEY: transaction.currency,
                            },
                        },
                        "balance": {
                            _DATA_KEY: {
                                _TYPE_KEY: "balances",
                                _ID_KEY: transaction.balance_id,
                            },
                        },
                        "transactionType": {
                            _DATA_KEY: {
                                _TYPE_KEY: "transaction-types",
                                _ID_KEY: transaction.type,
                            },
                        },
                        "status": {
                            _DATA_KEY: {
                                _TYPE_KEY: "transaction-statuses",
                                _ID_KEY: transaction.status,
                            },
                        },
                    },
                },
            )

        return responses.JSONResponse(
            {"data": response, "links": next_url},
        )
