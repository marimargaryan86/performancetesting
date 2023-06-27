import datetime
from collections.abc import Mapping, Sequence

import pymongo

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class CompaniesRepository(
    mixins.FindByIdMixin[models_pb2.Company],
    mixins.InsertMixin[models_pb2.Company],
    repository.ProtoRepository[models_pb2.Company],
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
            filter={"_id": company.id},
            replacement=replacement,
        )

        return company

    async def find_all(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Company]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )

    async def find_accountless(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Company]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_={"$or": [{"account_id": ""}, {"account_id": {"$exists": False}}]},
        )


class AccountsRepository(
    mixins.InsertMixin[models_pb2.Account],
    mixins.FindByIdMixin[models_pb2.Account],
    repository.ProtoRepository[models_pb2.Account],
):
    _proto = models_pb2.Account

    async def find(
        self,
        limit: int,
        filter_by: Sequence[str],
        cursor: str | None = None,
    ) -> resultset.ResultSet[models_pb2.Account]:
        query = {
            "status": {
                "$in": [
                    protobuf.slug_to_enum_value(models_pb2.Status, filter_status)
                    for filter_status in filter_by
                ],
            },
        }
        accounts = await self._find_with_cursor(
            cur=cursor or "",
            filter_=query,
        )
        accounts.limit(limit)
        return accounts

    async def update(
        self,
        account_id: str,
        new_values: Mapping[str, str | datetime.datetime | int],
    ) -> pymongo.results.UpdateResult:
        return await self._execute(
            self._collection.update_one,
            filter={"_id": account_id},
            update={"$set": new_values},
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


class BeneficiaryRepository(
    mixins.FindByIdMixin[models_pb2.Beneficiary],
    mixins.InsertMixin[models_pb2.Beneficiary],
    repository.ProtoRepository[models_pb2.Beneficiary],
):
    _proto = models_pb2.Beneficiary
    _default_page_size = 20

    async def find(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Beneficiary]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )

    async def update(
        self,
        document_id: str,
        beneficiary: models_pb2.Beneficiary,
    ) -> pymongo.results.UpdateResult:
        replacement = self._coder.encode(beneficiary)
        replacement.pop("_id")

        return await self._execute(
            self._collection.replace_one,
            filter={"_id": document_id},
            replacement=replacement,
        )
