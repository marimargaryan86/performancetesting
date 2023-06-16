from collections.abc import Mapping

import httpx
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api import repository
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import string

_GUESTS_URL = "/guests"


class TestGuests(object):
    async def test_guest_created(
        self,
        http_client: httpx.AsyncClient,
        headers: Mapping[str, str],
        guests_repository: repository.UsersRepository,
        existing_guest: models_pb2.Guest,
    ) -> None:
        guest = await http_client.post(
            _GUESTS_URL,
            json={
                "data": {
                    "type": "guests",
                    "attributes": {},
                },
            },
        )

        guest_id = guest.json()["data"]["id"]
        saved_guest = await guests_repository.find_by_id(guest_id)
        assert saved_guest is not None

    async def test_guest_login(
        self,
        http_client: httpx.AsyncClient,
        existing_guest: models_pb2.Guest,
    ) -> None:
        resp = await self._post_sessions(
            http_client,
            existing_guest,
        )
        assert resp.status_code == status.HTTP_200_OK

        non_existing_guest = models_pb2.Guest(id=string.uuid())
        resp = await self._post_sessions(
            http_client,
            non_existing_guest,
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def _post_sessions(
        self,
        http_client: httpx.AsyncClient,
        guest: models_pb2.Guest,
    ) -> httpx.Response:
        return await http_client.post(
            "{base}/sessions".format(base=_GUESTS_URL),
            json={
                "data": {
                    "type": "guest-sessions",
                    "relationships": {
                        "guest": {
                            "data": {
                                "id": guest.id,
                                "type": "guests",
                            },
                        },
                    },
                },
            },
        )
