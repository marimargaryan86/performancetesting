from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.adapter import offers
from snowfall.junction.offers.v1alpha import offers_pb2, offers_pb2_grpc


@pytest.mark.asyncio
class TestDictClient(object):
    async def test_single_offer_is_retrievable(
        self,
        offers_client: offers.Client,
    ) -> None:
        offer = await offers_client.get(fixtures.OFFERS[0])
        assert offer.id == fixtures.OFFERS[0]

    async def test_missing_offer_throws_error(
        self,
        offers_client: offers.Client,
    ) -> None:
        with pytest.raises(offers.NotFoundError):
            await offers_client.get(fixtures.NOT_FOUND)


@pytest.mark.asyncio
class TestGrpcClient(object):
    @pytest.mark.parametrize(
        "error, expected",
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                offers.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                offers.UnknownError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: Type[Exception],
    ) -> None:
        stub = mock.create_autospec(offers_pb2_grpc.OfferServiceStub)
        stub.GetOffer = mock.AsyncMock(side_effect=error)
        client = offers.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_offer_is_retrievable(self) -> None:
        proto = offers_pb2.OfferAggregate(id=fixtures.OFFERS[0])
        stub = mock.create_autospec(offers_pb2_grpc.OfferServiceStub)
        stub.GetOffer = mock.AsyncMock(
            return_value=offers_pb2.GetOfferResponse(offer=proto),
        )
        client = offers.GrpcClient(stub)
        offer = await client.get(fixtures.OFFERS[0])
        assert offer.id == fixtures.OFFERS[0]
