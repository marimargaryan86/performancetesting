import grpc

from snowfall.project.junction.plus.service.checkin.v1alpha import (
    checkin_pb2,
    checkin_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class CheckinService(
    service.Service,
    checkin_pb2_grpc.CheckinServiceServicer,
):
    def get_name(self) -> str:
        return checkin_pb2.DESCRIPTOR.services_by_name["CheckinService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        checkin_pb2_grpc.add_CheckinServiceServicer_to_server(
            self,
            server,
        )
