from typing import Sequence
from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, offers
from snowfall.project.junction.go.service.offers.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib.v1alpha import models_pb2 as common_pb2


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
        with pytest.raises(errors.NotFoundError):
            await offers_client.get(fixtures.NOT_FOUND)

    async def test_missing_offer_is_not_found_by_id(
        self,
        offers_client: offers.Client,
    ) -> None:
        offers_page = await offers_client.find_by_ids(
            [fixtures.NOT_FOUND],
            limit=1,
        )
        assert not offers_page.offers

    async def test_single_offer_is_found_by_id(
        self,
        offers_client: offers.Client,
    ) -> None:
        offers_page = await offers_client.find_by_ids(
            [fixtures.OFFERS[0]],
            limit=1,
        )
        assert offers_page.offers[0].id == fixtures.OFFERS[0]

    @pytest.mark.parametrize(
        ("types", "expected"),
        [
            (
                [],
                2,
            ),
            (
                [common_pb2.CabinClass.TYPE_ECONOMY],
                2,
            ),
            (
                [common_pb2.CabinClass.TYPE_FIRST],
                0,
            ),
        ],
    )
    async def test_cabin_class_filter(
        self,
        offers_client: offers.Client,
        types: Sequence[common_pb2.CabinClass.Type.ValueType],
        expected: int,
    ) -> None:
        offers_page = await offers_client.find_offers_by_offer_search(
            identifier=fixtures.OFFER_SEARCHES[0],
            cabin_classes=types,
        )
        assert len(offers_page.offers) == expected


class TestGrpcClient(object):
    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.UnhandledError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: type[Exception],
    ) -> None:
        stub = mock.create_autospec(grpc_pb2_grpc.OfferServiceStub)
        stub.GetOffer = mock.AsyncMock(side_effect=error)
        client = offers.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_offer_is_retrievable(self) -> None:
        proto = models_pb2.OfferAggregate(id=fixtures.OFFERS[0])
        stub = mock.create_autospec(grpc_pb2_grpc.OfferServiceStub)
        stub.GetOffer = mock.AsyncMock(
            return_value=grpc_pb2.GetOfferResponse(offer=proto),
        )
        client = offers.GrpcClient(stub)
        offer = await client.get(fixtures.OFFERS[0])
        assert offer.id == fixtures.OFFERS[0]
