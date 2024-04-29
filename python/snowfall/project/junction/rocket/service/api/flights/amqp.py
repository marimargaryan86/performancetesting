import datetime

from snowfall.project.junction.rocket.service.api.v1alpha import search_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import protocol


class SearchTaskProducer:
    def __init__(self, producer_obj: protocol.Producer):
        self._producer = producer_obj

    async def publish(
        self,
        search_id: str,
        search_request_json: str,
        reseller_id: str,
        expires_at: datetime.datetime,
    ) -> None:
        await self._producer.publish(
            search_pb2.SearchTask(
                search_id=search_id,
                search_request_data=search_request_json,
                reseller_id=reseller_id,
                expires_at=protobuf.datetime_to_protobuf(expires_at),
            ),
            "tasks.flight_search",
        )
