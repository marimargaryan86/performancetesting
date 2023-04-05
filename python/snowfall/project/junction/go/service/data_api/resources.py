from __future__ import annotations

from snowfall.service.geodata.v1 import models_pb2
from snowfall.stdlib.integration.starlette import models


class CoordinateResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        coordinates: models_pb2.Location,
    ) -> CoordinateResource:
        return cls(
            id=coordinates.id,
            type="coordinates",
            attributes={
                "addressNumber": coordinates.address_number,
                "street": coordinates.street,
                "unitNumber": coordinates.unit_number,
                "unitType": coordinates.unit_type,
                "latitude": coordinates.coordinates.latitude,
                "longitude": coordinates.coordinates.longitude,
                "name": coordinates.name,
                "neighborhood": coordinates.neighborhood,
                "municipality": coordinates.municipality,
                "subregion": coordinates.subregion,
                "region": coordinates.region,
                "country": coordinates.country,
                "interpolated": coordinates.interpolated,
                "timezone": {"name": coordinates.time_zone.id},
            },
        )
