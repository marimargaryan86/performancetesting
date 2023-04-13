from typing import Sequence

from starlette import requests

from snowfall.project.pay.service.pay_api import repositories, resources
from snowfall.stdlib.integration.starlette import includes


def _transactions_resolver(
    transaction_repositories: repositories.TransactionRepository,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.Transaction]:
        transactions = []
        for identifier in identifiers:
            transaction = await transaction_repositories.find_by_id(identifier)
            if not transaction:
                raise ValueError(
                    "Transaction is not found for {0} id".format(identifier),
                )
            transactions.append(
                resources.Transaction.from_proto(
                    transaction=transaction,
                    request=request,
                ),
            )
        return transactions

    return wrapper


def register_resolvers(
    transaction_repositories: repositories.TransactionRepository,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.Transaction,
            func=_transactions_resolver(transaction_repositories),
        ),
    )
    for resolver in resolvers:
        includes.add_resolver(resolver)
