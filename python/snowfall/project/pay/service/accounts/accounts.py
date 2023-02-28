from snowfall.project.pay.service.accounts.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class AccountsRepository(
    mixins.InsertMixin[models_pb2.Account],
    mixins.FindByIdMixin[models_pb2.Account],
    repository.ProtoRepository[models_pb2.Account],
):
    _proto = models_pb2.Account


class ContactPersonsRepository(
    mixins.InsertMixin[models_pb2.ContactPerson],
    mixins.FindByIdMixin[models_pb2.ContactPerson],
    repository.ProtoRepository[models_pb2.ContactPerson],
):
    _proto = models_pb2.ContactPerson

    async def update_reference(
        self,
        contact_person: models_pb2.ContactPerson,
        external_reference: str,
    ) -> models_pb2.ContactPerson:
        return await self._execute(
            self._collection.update_one,
            filter={"_id": contact_person.id},
            update={
                "$set": {
                    "external_reference": external_reference,
                },
            },
        )
