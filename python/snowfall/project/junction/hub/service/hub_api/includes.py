from collections.abc import Sequence

from starlette import requests

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.pay.adapter import transactions
from snowfall.stdlib.integration.starlette import includes


def _transactions_resolver(
    transactions_client: transactions.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.Transaction]:
        included_transactions = []
        for identifier in identifiers:
            transaction = await transactions_client.get(identifier)
            included_transactions.append(
                resources.Transaction.from_proto(
                    transaction=transaction,
                    request=request,
                ),
            )
        return included_transactions

    return wrapper


def register_resolvers(
    transactions_client: transactions.Client,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.Transaction,
            func=_transactions_resolver(transactions_client),
        ),
    )
    for resolver in resolvers:
        includes.add_resolver(resolver)
