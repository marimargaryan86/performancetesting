import httpx

from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (
    PingRq,
    ServiceSoapGetPing,
    ServiceSoapGetPingInput,
    ServiceSoapGetPingOutput,
)
from snowfall.vendor.carnect.soap.soap_client import (
    AsyncSoapClient,
    AsyncSoapTransport,
    SoapLogger,
)


class CarnectClient(object):
    def __init__(self, http_client: httpx.AsyncClient, config: Config) -> None:
        self._config: Config = config
        self._transport = AsyncSoapTransport(
            http_client=http_client,
            timeout=self._config.timeout,
            soap_logger=SoapLogger(
                secret_words=(),
                export_files=False,
            ),
        )

        self._ping_client = AsyncSoapClient.create_client(
            ServiceSoapGetPing,
            self._transport,
        )

    async def ping(self, rq: PingRq) -> ServiceSoapGetPingOutput.Body:
        request = ServiceSoapGetPingInput(body=ServiceSoapGetPingInput.Body(ping_rq=rq))
        rs = await self._ping_client.send(
            request,
            headers=self._get_headers(ServiceSoapGetPing.soap_action),
        )
        return rs.body

    def _get_headers(self, soap_action: str) -> dict[str, str]:
        return {
            "SOAPAction": soap_action,
        }
