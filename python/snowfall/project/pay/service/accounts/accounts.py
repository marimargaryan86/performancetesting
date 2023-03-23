from snowfall.project.pay.service.accounts.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class AccountsRepository(
    mixins.InsertMixin[models_pb2.Account],
    mixins.FindByIdMixin[models_pb2.Account],
    repository.ProtoRepository[models_pb2.Account],
):
    _proto = models_pb2.Account

    async def find(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Account]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )


class ContactsRepository(
    mixins.InsertMixin[models_pb2.Contact],
    mixins.FindByIdMixin[models_pb2.Contact],
    repository.ProtoRepository[models_pb2.Contact],
):
    _proto = models_pb2.Contact
    _default_page_size = 20

    async def update_reference(
        self,
        contact: models_pb2.Contact,
        external_reference: str,
    ) -> models_pb2.Contact:
        return await self._execute(
            self._collection.update_one,
            filter={"_id": contact.id},
            update={
                "$set": {
                    "external_reference": external_reference,
                },
            },
        )

    async def find_by_company_id(
        self,
        company_id: str,
        cursor: str | None,
        limit: int | None,
    ) -> resultset.ResultSet[models_pb2.Contact]:
        contacts = await self._find_with_cursor(
            cur=cursor or "",
            filter_={
                "company_id": company_id,
            },
        )

        contacts.limit(limit or self._default_page_size)

        return contacts
