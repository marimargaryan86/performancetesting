from typing import Any
from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, resellers
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2,
    resellers_pb2,
    resellers_pb2_grpc,
)


class TestDictClient:
    async def test_single_reseller_is_retrievable(
        self,
        resellers_client: resellers.Client,
    ) -> None:
        reseller = await resellers_client.get_reseller(fixtures.RESELLERS[0])
        assert reseller.id == fixtures.RESELLERS[0]

    async def test_single_reseller_is_retrievable_with_child_resellers(
        self,
        resellers_client: resellers.Client,
    ) -> None:
        reseller = await resellers_client.get_reseller(
            fixtures.RESELLERS[0],
            fetch_child_resellers=True,
        )

        assert reseller.id == fixtures.RESELLERS[0]
        assert fixtures.RESELLERS[1] in reseller.child_reseller_ids

    async def test_single_reseller_not_found(
        self,
        resellers_client: resellers.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await resellers_client.get_reseller("fake_id")

    async def test_resellers_are_retrievable(
        self,
        resellers_client: resellers.Client,
    ) -> None:
        response = await resellers_client.list_resellers()
        assert len(response.resellers) == 2

    async def test_reseller_created_successfully(
        self,
        resellers_client: resellers.Client,
    ) -> None:
        reseller = models_pb2.Reseller(
            name="test_reseller",
            company_id="69c57ea7-9e81-4956-930e-113e1cd99ccf",
            default_currency="USD",
            provider_ids=["a64aed02-6e1b-4a63-afc3-c3e9120a5a44"],
        )

        created_reseller = await resellers_client.create_reseller(reseller)
        assert created_reseller.name == "test_reseller"

        reseller = await resellers_client.get_reseller(created_reseller.id)
        assert reseller.id

    async def test_reseller_updated_successfully(
        self,
        resellers_client: resellers.Client,
    ) -> None:
        updated_reseller = await resellers_client.update_reseller(
            models_pb2.Reseller(
                id=fixtures.RESELLERS[0],
                name="updated_name",
                default_currency="USD",
                provider_ids=None,
            ),
        )

        assert updated_reseller.name == "updated_name"
        assert updated_reseller.default_currency == "USD"


class TestGrpcClient:
    @property
    def reseller(self) -> models_pb2.Reseller:
        return models_pb2.Reseller(id=fixtures.RESELLERS[0])

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
        client = self._create_client("GetReseller", side_effect=error)

        with pytest.raises(expected):
            await client.get_reseller(fixtures.NOT_FOUND)

    async def test_single_reseller_is_retrievable(self) -> None:
        client = self._create_client(
            "GetReseller",
            return_value=resellers_pb2.GetResellerResponse(reseller=self.reseller),
        )
        reseller = await client.get_reseller(fixtures.RESELLERS[0])

        assert reseller.id == fixtures.RESELLERS[0]

    async def test_resellers_are_retrievable(self) -> None:
        response = resellers_pb2.ListResellersResponse(
            resellers=[
                self.reseller,
            ],
        )
        client = self._create_client("ListResellers", return_value=response)
        response = await client.list_resellers(limit=10)

        assert len(response.resellers) == 1

    async def test_reseller_created_successfully(self) -> None:
        client = self._create_client(
            "CreateReseller",
            return_value=resellers_pb2.CreateResellerResponse(reseller=self.reseller),
        )
        new_reseller = models_pb2.Reseller(
            name="test_reseller",
            company_id="69c57ea7-9e81-4956-930e-113e1cd99ccf",
            default_currency="USD",
            provider_ids=["a64aed02-6e1b-4a63-afc3-c3e9120a5a44"],
        )
        reseller = await client.create_reseller(new_reseller)

        assert reseller.id

    async def test_reseller_updated_successfully(self) -> None:
        client = self._create_client(
            "UpdateReseller",
            return_value=resellers_pb2.UpdateResellerResponse(reseller=self.reseller),
        )
        updated_reseller = await client.update_reseller(
            models_pb2.Reseller(
                id=fixtures.RESELLERS[0],
            ),
        )

        assert updated_reseller.id == self.reseller.id

    def _create_client(self, mocked_method: str, **kwargs: Any) -> resellers.GrpcClient:
        stub = mock.create_autospec(resellers_pb2_grpc.ResellerServiceStub)
        setattr(stub, mocked_method, mock.AsyncMock(**kwargs))
        return resellers.GrpcClient(stub)
