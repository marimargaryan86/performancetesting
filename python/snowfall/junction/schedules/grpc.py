from grpc import StatusCode, aio

from snowfall.junction.schedules.schedules import LegRepository, ScheduleRepository
from snowfall.junction.schedules.v1alpha import schedules_pb2, schedules_pb2_grpc
from snowfall.stdlib.transport.grpc import Service


class ScheduleService(Service, schedules_pb2_grpc.ScheduleServiceServicer):
    def __init__(
        self,
        legs: LegRepository,
        schedules: ScheduleRepository,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._legs = legs
        self._schedules = schedules

    def get_name(self) -> str:
        return schedules_pb2.DESCRIPTOR.services_by_name["ScheduleService"].full_name

    def register(self, server: aio.Server) -> None:
        schedules_pb2_grpc.add_ScheduleServiceServicer_to_server(self, server)

    async def GetSchedule(  # type: ignore[override] # noqa: N802
        self,
        request: schedules_pb2.GetScheduleRequest,
        context: aio.ServicerContext,
    ) -> schedules_pb2.GetScheduleResponse:
        schedule = await self._schedules.find_by_id(request.id)

        if not schedule:
            await context.abort(StatusCode.NOT_FOUND)

        return schedules_pb2.GetScheduleResponse(schedule=schedule)

    async def ListSchedules(  # type: ignore[override] # noqa: N802
        self,
        request: schedules_pb2.ListSchedulesRequest,
        context: aio.ServicerContext,
    ) -> schedules_pb2.ListSchedulesResponse:
        schedules_result = await self._schedules.find(
            ids=list(request.ids),
            cursor=request.page_token,
        )

        schedules_result.limit(request.page_size or self._default_page_size)

        return schedules_pb2.ListSchedulesResponse(
            schedules=[schedule async for schedule in schedules_result],
            next_page_token=await schedules_result.cursor(),
        )

    async def GetLeg(  # type: ignore[override] # noqa: N802
        self,
        request: schedules_pb2.GetLegRequest,
        context: aio.ServicerContext,
    ) -> schedules_pb2.GetLegResponse:
        leg = await self._legs.find_by_id(request.id)

        if not leg:
            await context.abort(StatusCode.NOT_FOUND)

        return schedules_pb2.GetLegResponse(leg=leg)

    async def ListLegs(  # type: ignore[override] # noqa: N802
        self,
        request: schedules_pb2.ListLegsRequest,
        context: aio.ServicerContext,
    ) -> schedules_pb2.ListLegsResponse:
        legs_result = await self._legs.find(
            ids=list(request.ids),
            cursor=request.page_token,
        )

        legs_result.limit(request.page_size or self._default_page_size)

        return schedules_pb2.ListLegsResponse(
            legs=[leg async for leg in legs_result],
            next_page_token=await legs_result.cursor(),
        )
