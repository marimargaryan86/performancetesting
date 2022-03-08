from grpc import aio

from snowfall.junction.schedules.schedules import ScheduleRepository
from snowfall.junction.schedules.v1alpha import schedules_pb2, schedules_pb2_grpc
from snowfall.transport.grpc import Service


class ScheduleService(Service, schedules_pb2_grpc.ScheduleServiceServicer):
    def __init__(self, schedules: ScheduleRepository, default_page_size: int):
        self._default_page_size = default_page_size
        self._schedules = schedules

    def get_name(self) -> str:
        return schedules_pb2.DESCRIPTOR.services_by_name["ScheduleService"].full_name

    def register(self, server: aio.Server) -> None:
        schedules_pb2_grpc.add_ScheduleServiceServicer_to_server(self, server)

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
