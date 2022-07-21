from typing import Sequence

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models import operator


class OperatorClient(base.BaseClient):
    async def get_operators(self) -> Sequence[operator.Operator]:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method="get",
                    url="{0}/api/{1}/Operators".format(
                        self._config.api_url,
                        self._config.api_version,
                    ),
                ),
            )
        ).json()

        return [
            operator.Operator(**operator_data)
            for operator_data in response_data["data"]["operators"]
        ]
