from collections.abc import Sequence

from snowfall.stdlib import money


class CurrencyRepository:
    def __init__(self, available_currencies: Sequence[money.Currency]):
        sorted_currencies = sorted(
            available_currencies,
            key=lambda curr: curr.code,
        )
        self._currencies = {curr.code: curr for curr in sorted_currencies}

    def find(self) -> Sequence[money.Currency]:
        return tuple(self._currencies.values())

    def find_by_id(self, currency_id: str) -> money.Currency | None:
        return self._currencies.get(currency_id)
