import abc

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models import operator


class OperatorClient(abc.ABC):
    @abc.abstractmethod
    async def get_operators(self) -> operator.OperatorResponse:
        """Get all operators."""


class OperatorHttpClient(base.BaseClient, OperatorClient):
    async def get_operators(self) -> operator.OperatorResponse:
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

        return operator.OperatorResponse(**response_data)
