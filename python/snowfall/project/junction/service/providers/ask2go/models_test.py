from snowfall.project.junction.go.service.orders.v1.models_pb2 import DocumentDetails
from snowfall.project.junction.service.providers.ask2go.models import (
    traveler_document_from_proto,
)


async def test_that_failure_creating_date_protobuf_returns_none_document() -> None:
    doc = traveler_document_from_proto(
        DocumentDetails(document_type=DocumentDetails.Type.TYPE_PASSPORT),
    )
    assert doc is None
