from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class PaymentUsersRepository(
    repository.ProtoRepository[credit_card_models_pb2.PaymentUser],
    mixins.FindByIdMixin[credit_card_models_pb2.PaymentUser],
    mixins.InsertMixin[credit_card_models_pb2.PaymentUser],
):
    _proto = credit_card_models_pb2.PaymentUser

    async def get(self, user_id: str) -> credit_card_models_pb2.PaymentUser | None:
        return await self._execute(
            self._collection.find_one,
            filter={"internal_user_id": user_id},
        )
