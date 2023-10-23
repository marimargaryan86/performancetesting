from typing import Any

import httpx

from snowfall.vendor.carnect.builders.reservation_builder import ReservationBuilder
from snowfall.vendor.carnect.config import Config
from snowfall.vendor.carnect.models.service import (
    PingRq,
    ServiceSoapGetPing,
    ServiceSoapGetPingInput,
    ServiceSoapGetPingOutput,
    ServiceSoapGetVehAvailRate,
    ServiceSoapGetVehAvailRateInput,
    ServiceSoapGetVehAvailRateOutput,
    ServiceSoapGetVehCancelReservation,
    ServiceSoapGetVehCancelReservationInput,
    ServiceSoapGetVehCancelReservationOutput,
    ServiceSoapGetVehLocationSearch,
    ServiceSoapGetVehLocationSearchInput,
    ServiceSoapGetVehLocationSearchOutput,
    ServiceSoapGetVehLocDetail,
    ServiceSoapGetVehLocDetailInput,
    ServiceSoapGetVehLocDetailOutput,
    ServiceSoapGetVehRateRule,
    ServiceSoapGetVehRateRuleInput,
    ServiceSoapGetVehRateRuleOutput,
    ServiceSoapGetVehReservation,
    ServiceSoapGetVehReservationInput,
    ServiceSoapGetVehReservationOutput,
    ServiceSoapGetVehRetReservation,
    ServiceSoapGetVehRetReservationInput,
    ServiceSoapGetVehRetReservationOutput,
    VehAvailRateRq,
    VehCancelResRq,
    VehLocationSearchRq,
    VehLocDetailRq,
    VehRateRuleRq,
    VehRetResRq,
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

        self._ping_client = self._create_client(ServiceSoapGetPing)
        self._loc_search_client = self._create_client(ServiceSoapGetVehLocationSearch)
        self._get_loc_detail_client = self._create_client(ServiceSoapGetVehLocDetail)
        self._get_avail_rate_client = self._create_client(ServiceSoapGetVehAvailRate)
        self._veh_rate_rule_client = self._create_client(ServiceSoapGetVehRateRule)
        self._cancel_reservation_client = self._create_client(
            ServiceSoapGetVehCancelReservation,
        )
        self._veh_ret_res_client = self._create_client(ServiceSoapGetVehRetReservation)
        self._reservation_client = self._create_client(ServiceSoapGetVehReservation)

    async def ping(self, rq: PingRq) -> ServiceSoapGetPingOutput.Body:
        rs = await self._ping_client.send(
            rq_object=ServiceSoapGetPingInput(
                body=ServiceSoapGetPingInput.Body(ping_rq=rq),
            ),
            headers=self._get_headers(ServiceSoapGetPing.soap_action),
        )
        return rs.body

    async def location_search(
        self,
        rq: VehLocationSearchRq,
    ) -> ServiceSoapGetVehLocationSearchOutput:
        return await self._loc_search_client.send(
            rq_object=ServiceSoapGetVehLocationSearchInput(
                body=ServiceSoapGetVehLocationSearchInput.Body(
                    veh_location_search_rq=rq,
                ),
            ),
            headers=self._get_headers(ServiceSoapGetVehLocationSearch.soap_action),
        )

    async def get_location_details(
        self,
        rq: VehLocDetailRq,
    ) -> ServiceSoapGetVehLocDetailOutput:
        return await self._get_loc_detail_client.send(
            rq_object=ServiceSoapGetVehLocDetailInput(
                body=ServiceSoapGetVehLocDetailInput.Body(veh_loc_detail_rq=rq),
            ),
            headers=self._get_headers(ServiceSoapGetVehLocDetail.soap_action),
        )

    async def get_avail_rate(
        self,
        rq: VehAvailRateRq,
    ) -> ServiceSoapGetVehAvailRateOutput:
        return await self._get_avail_rate_client.send(
            rq_object=ServiceSoapGetVehAvailRateInput(
                body=ServiceSoapGetVehAvailRateInput.Body(veh_avail_rate_rq=rq),
            ),
            headers=self._get_headers(ServiceSoapGetVehAvailRate.soap_action),
        )

    async def veh_rate_rules(
        self,
        rq: VehRateRuleRq,
    ) -> ServiceSoapGetVehRateRuleOutput:
        return await self._veh_rate_rule_client.send(
            rq_object=ServiceSoapGetVehRateRuleInput(
                body=ServiceSoapGetVehRateRuleInput.Body(veh_rate_rule_rq=rq),
            ),
            headers=self._get_headers(ServiceSoapGetVehAvailRate.soap_action),
        )

    async def cancel_reservation(
        self,
        rq: VehCancelResRq,
    ) -> ServiceSoapGetVehCancelReservationOutput:
        return await self._cancel_reservation_client.send(
            rq_object=ServiceSoapGetVehCancelReservationInput(
                body=ServiceSoapGetVehCancelReservationInput.Body(veh_cancel_res_rq=rq),
            ),
            headers=self._get_headers(ServiceSoapGetVehCancelReservation.soap_action),
        )

    async def retrieve_reservation(
        self,
        rq: VehRetResRq,
    ) -> ServiceSoapGetVehRetReservationOutput:
        return await self._veh_ret_res_client.send(
            rq_object=ServiceSoapGetVehRetReservationInput(
                body=ServiceSoapGetVehRetReservationInput.Body(veh_ret_res_rq=rq),
            ),
            headers=self._get_headers(ServiceSoapGetVehRetReservation.soap_action),
        )

    async def reservation(
        self,
        rq_builder: ReservationBuilder,
    ) -> ServiceSoapGetVehReservationOutput:
        if self._config.is_test:
            # Test env requirements:
            # http://doc.carnect.com/ota2007/getting_started.html#test-reservations
            rq_builder.primary_driver().surname("Test")
            rq_builder.primary_driver().given_name("Test")
            rq_builder.primary_driver().email("testcheck@carnect.com")

        return await self._reservation_client.send(
            rq_object=ServiceSoapGetVehReservationInput(
                body=ServiceSoapGetVehReservationInput.Body(
                    veh_res_rq=rq_builder.build(),
                ),
            ),
            headers=self._get_headers(ServiceSoapGetVehReservation.soap_action),
        )

    def _get_headers(self, soap_action: str) -> dict[str, str]:
        return {
            "SOAPAction": soap_action,
        }

    def _create_client(self, service: Any) -> AsyncSoapClient:
        return AsyncSoapClient.create_client(
            service=service,
            transport=self._transport,
            location=self._config.base_url,
        )
