from collections.abc import Sequence

import pymongo

from snowfall.project.pay.service.companies.v1 import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class CompaniesRepository(
    repository.ProtoRepository[models_pb2.Company],
    mixins.FindByIdMixin[models_pb2.Company],
    mixins.InsertMixin[models_pb2.Company],
):
    _proto = models_pb2.Company
    _indexes = (pymongo.IndexModel("name", background=True, unique=True),)

    async def update(
        self,
        company: models_pb2.Company,
    ) -> models_pb2.Company:
        replacement = self._coder.encode(company)

        await self._execute(
            self._collection.replace_one,
            filter={repository.mongo_id_key: company.id},
            replacement=replacement,
        )

        return company

    async def find_all(
        self,
        cursor: str | None,
        identifiers: Sequence[str] = (),
    ) -> resultset.ResultSet[models_pb2.Company]:
        if identifiers:
            filter_ = {
                repository.mongo_id_key: {
                    "$in": identifiers,
                },
            }
            return await self._find_with_cursor(
                cur=cursor or "",
                filter_=filter_,
            )

        return await self._find_with_cursor(
            cur=cursor or "",
        )

    async def find_accountless(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Company]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_={
                "$or": [{"account_id": ""}, {"account_id": {"$exists": False}}],
            },
        )


class ContactsRepository(
    repository.ProtoRepository[models_pb2.Contact],
    mixins.InsertMixin[models_pb2.Contact],
    mixins.FindByIdMixin[models_pb2.Contact],
):
    _proto = models_pb2.Contact
    _default_page_size = 20

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Contact]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    async def update_reference(
        self,
        contact: models_pb2.Contact,
    ) -> models_pb2.Contact:
        return await self._execute(
            self._collection.update_one,
            filter={repository.mongo_id_key: contact.id},
            update={
                "$set": {
                    "external_reference": contact.external_reference,
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
