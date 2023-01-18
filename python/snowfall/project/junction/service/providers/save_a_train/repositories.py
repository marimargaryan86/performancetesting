from pymongo import IndexModel

from snowfall.project.junction.service.providers.save_a_train.v1alpha import (
    amqp_pb2 as provider_amqp_pb2,
)
from snowfall.stdlib.persistence.mongo import repository
from snowfall.stdlib.v1alpha import models_pb2


class ProviderCabinMappingRepository(
    repository.ProtoRepository[provider_amqp_pb2.CabinClassMapping],
):
    _proto = provider_amqp_pb2.CabinClassMapping
    _indexes = [
        IndexModel("mapping", background=True, unique=True),
    ]

    async def find_by_mapping(
        self,
        provider_cabin_class: str,
    ) -> provider_amqp_pb2.CabinClassMapping | None:
        return await self._execute(
            query=self._collection.find_one,
            filter={
                "mapping": {
                    "$eq": provider_cabin_class,
                },
            },
            filter_pre_cursor={},
        )

    async def create(
        self,
        cabin_class_type: models_pb2.CabinClass.Type.ValueType,
        provider_cabin_class: str,
    ) -> provider_amqp_pb2.CabinClassMapping:
        provider_cabin_class_mapping = provider_amqp_pb2.CabinClassMapping(
            type=cabin_class_type,
            mapping=provider_cabin_class,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(provider_cabin_class_mapping),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return provider_cabin_class_mapping
