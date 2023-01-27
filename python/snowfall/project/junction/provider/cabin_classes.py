from typing import Optional

import structlog
from pymongo import IndexModel

from snowfall.stdlib.persistence.mongo import mixins, repository
from snowfall.stdlib.v1alpha import models_pb2


class CabinMappingRepository(
    mixins.InsertMixin[models_pb2.CabinClassMapping],
    repository.ProtoRepository[models_pb2.CabinClassMapping],
):
    _proto = models_pb2.CabinClassMapping
    _logger = structlog.get_logger(__name__)
    _indexes = [
        IndexModel("fare_brand", background=True),
        IndexModel("operator", background=True),
    ]

    async def resolve_cabin_class(
        self,
        fare_brand: str,
        operator: str,
    ) -> models_pb2.CabinClass.Type.V:
        provider_mapping = await self._find_by_operator_mapping(
            fare_brand=fare_brand,
            operator=operator,
        )

        if provider_mapping:
            return provider_mapping.type

        unspecified_mapping = await self._create(
            models_pb2.CabinClassMapping(
                fare_brand=fare_brand,
                operator=operator,
                type=models_pb2.CabinClass.TYPE_UNSPECIFIED,
            ),
        )

        self._logger.warning(
            "Provider found UNSPECIFIED fare brand type.",
            fare_brand=fare_brand,
            operator=operator,
        )

        return unspecified_mapping.type

    async def _find_by_operator_mapping(
        self,
        fare_brand: str,
        operator: str,
    ) -> Optional[models_pb2.CabinClassMapping]:
        mapping = await self._execute(
            query=self._collection.find_one,
            filter={
                "fare_brand": {
                    "$eq": fare_brand,
                },
                "operator": {
                    "$eq": operator,
                },
            },
        )
        return mapping if mapping else None

    async def _create(
        self,
        document: models_pb2.CabinClassMapping,
    ) -> models_pb2.CabinClassMapping:
        new_mapping = models_pb2.CabinClassMapping(
            type=document.type,
            fare_brand=document.fare_brand,
            operator=document.operator,
        )

        return await self.insert(new_mapping)
