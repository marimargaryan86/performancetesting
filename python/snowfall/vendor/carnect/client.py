import httpx

from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (  # noqa: WPS235
    PingRq,
    ServiceSoapGetPing,
    ServiceSoapGetPingInput,
    ServiceSoapGetPingOutput,
    ServiceSoapGetVehAvailRate,
    ServiceSoapGetVehAvailRateInput,
    ServiceSoapGetVehAvailRateOutput,
    ServiceSoapGetVehLocationSearch,
    ServiceSoapGetVehLocationSearchInput,
    ServiceSoapGetVehLocationSearchOutput,
    ServiceSoapGetVehLocDetail,
    ServiceSoapGetVehLocDetailInput,
    ServiceSoapGetVehLocDetailOutput,
    ServiceSoapGetVehRateRule,
    ServiceSoapGetVehRateRuleInput,
    ServiceSoapGetVehRateRuleOutput,
    VehAvailRateRq,
    VehLocationSearchRq,
    VehLocDetailRq,
    VehRateRuleRq,
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
                export_files=config.export_soap_requests,
            ),
        )

        self._ping_client = AsyncSoapClient.create_client(
            ServiceSoapGetPing,
            self._transport,
            location=config.base_url,
        )
        self._location_search_client = AsyncSoapClient.create_client(
            ServiceSoapGetVehLocationSearch,
            self._transport,
            location=config.base_url,
        )
        self._get_veh_loc_detail_client = AsyncSoapClient.create_client(
            ServiceSoapGetVehLocDetail,
            self._transport,
            location=config.base_url,
        )
        self._get_avail_rate_client = AsyncSoapClient.create_client(
            ServiceSoapGetVehAvailRate,
            self._transport,
            location=config.base_url,
        )
        self._veh_rate_rule_client = AsyncSoapClient.create_client(
            ServiceSoapGetVehRateRule,
            self._transport,
            location=config.base_url,
        )

    async def ping(self, rq: PingRq) -> ServiceSoapGetPingOutput.Body:
        request = ServiceSoapGetPingInput(body=ServiceSoapGetPingInput.Body(ping_rq=rq))
        rs = await self._ping_client.send(
            request,
            headers=self._get_headers(ServiceSoapGetPing.soap_action),
        )
        return rs.body

    async def location_search(
        self,
        rq: VehLocationSearchRq,
    ) -> ServiceSoapGetVehLocationSearchOutput:
        request = ServiceSoapGetVehLocationSearchInput(
            body=ServiceSoapGetVehLocationSearchInput.Body(veh_location_search_rq=rq),
        )

        return await self._location_search_client.send(
            request,
            headers=self._get_headers(ServiceSoapGetVehLocationSearch.soap_action),
        )

    async def get_location_details(
        self,
        rq: VehLocDetailRq,
    ) -> ServiceSoapGetVehLocDetailOutput:
        request = ServiceSoapGetVehLocDetailInput(
            body=ServiceSoapGetVehLocDetailInput.Body(veh_loc_detail_rq=rq),
        )
        return await self._get_veh_loc_detail_client.send(
            request,
            headers=self._get_headers(ServiceSoapGetVehLocDetail.soap_action),
        )

    async def get_avail_rate(
        self,
        rq: VehAvailRateRq,
    ) -> ServiceSoapGetVehAvailRateOutput:
        request = ServiceSoapGetVehAvailRateInput(
            body=ServiceSoapGetVehAvailRateInput.Body(veh_avail_rate_rq=rq),
        )

        return await self._get_avail_rate_client.send(
            request,
            headers=self._get_headers(ServiceSoapGetVehAvailRate.soap_action),
        )

    async def veh_rate_rules(
        self,
        rq: VehRateRuleRq,
    ) -> ServiceSoapGetVehRateRuleOutput:
        request = ServiceSoapGetVehRateRuleInput(
            body=ServiceSoapGetVehRateRuleInput.Body(veh_rate_rule_rq=rq),
        )

        return await self._veh_rate_rule_client.send(
            request,
            headers=self._get_headers(ServiceSoapGetVehAvailRate.soap_action),
        )

    def _get_headers(self, soap_action: str) -> dict[str, str]:
        return {
            "SOAPAction": soap_action,
        }
