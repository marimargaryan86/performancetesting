import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        contact: models_pb2.Contact,
    ) -> models_pb2.Contact:
        """Create contact."""

    @abc.abstractmethod
    async def get(
        self,
        contact_id: str,
    ) -> models_pb2.Contact:
        """Fetch contact."""

    @abc.abstractmethod
    async def find_by_company_id(
        self,
        company_id: str,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> grpc_pb2.ListCompanyContactsResponse:
        """Fetch contacts by company id."""

    @abc.abstractmethod
    async def update_reference(
        self,
        contact_id: str,
        external_reference: str,
    ) -> models_pb2.Contact:
        """Update contact external reference."""


class DictClient(Client):
    def __init__(self, contacts: Sequence[models_pb2.Contact]):
        self._contacts = {contact.id: contact for contact in contacts}

    async def create(
        self,
        contact: models_pb2.Contact,
    ) -> models_pb2.Contact:
        self._contacts[contact.id] = contact
        return contact

    async def get(self, contact_id: str) -> models_pb2.Contact:
        try:
            return self._contacts[contact_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def find_by_company_id(
        self,
        company_id: str,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> grpc_pb2.ListCompanyContactsResponse:
        page = sequence.paginate(
            sequence=list(self._contacts.values()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListCompanyContactsResponse(
            contacts=page.sequence,
            next_page_token=page.cursor,
        )

    async def update_reference(
        self,
        contact_id: str,
        external_reference: str,
    ) -> models_pb2.Contact:
        contact = self._contacts[contact_id]
        contact.external_reference = external_reference

        return contact


class GrpcClient(Client):
    def __init__(
        self,
        contact_stub: grpc_pb2_grpc.ContactsServiceStub,
        timeout: int = 5,
    ):
        self._client = contact_stub
        self._timeout = timeout

    async def create(
        self,
        contact: models_pb2.Contact,
    ) -> models_pb2.Contact:
        response = await errors.handle_grpc_errors(
            self._client.CreateContact(
                grpc_pb2.CreateContactRequest(contact=contact),
                timeout=self._timeout,
            ),
        )

        return response.contact

    async def get(self, contact_id: str) -> models_pb2.Contact:
        response = await errors.handle_grpc_errors(
            self._client.GetContact(
                grpc_pb2.GetContactRequest(id=contact_id),
                timeout=self._timeout,
            ),
        )

        return response.contact

    async def find_by_company_id(
        self,
        company_id: str,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> grpc_pb2.ListCompanyContactsResponse:
        # TODO(sargisa): handle INVALID_ARGUMENT
        request = grpc_pb2.ListCompanyContactsRequest(
            page_token=cursor or "",
            company_id=company_id,
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._client.ListCompanyContacts(request, timeout=self._timeout),
        )

    async def update_reference(
        self,
        contact_id: str,
        external_reference: str,
    ) -> models_pb2.Contact:
        response = await errors.handle_grpc_errors(
            self._client.UpdateContactReference(
                grpc_pb2.UpdateContactReferenceRequest(
                    contact_id=contact_id,
                    external_reference=external_reference,
                ),
                timeout=self._timeout,
            ),
        )

        return response.contact
