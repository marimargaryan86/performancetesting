import httpx
from google.protobuf import struct_pb2

from snowfall.service.authentication.v1 import identities_pb2, sessions_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ory import client


class NotFoundError(Exception):
    """Raised when a session is not found."""


class UnknownError(Exception):
    """Raised when an unknown error is caught."""


class Sessions:
    def __init__(self, ory_client: client.OryClient):
        self._client = ory_client

    async def get_session_for_cookie(self, cookie: str) -> sessions_pb2.Session:
        try:
            session = await self._client.get_session(cookie)
        except httpx.HTTPStatusError as err:
            if err.response.status_code == httpx.codes.NOT_FOUND.value:
                raise NotFoundError("Session not found.") from err

            raise UnknownError("Unknown error occurred.") from err

        metadata_public = struct_pb2.Struct()
        metadata_public.update(session.identity.metadata_public)

        return sessions_pb2.Session(
            id=session.identifier,
            active=session.active,
            expires_at=protobuf.datetime_to_protobuf(session.expires_at),
            identity=identities_pb2.Identity(
                id=session.identity.identifier,
                email=session.identity.traits.email,
                metadata_public=metadata_public,
            ),
        )
