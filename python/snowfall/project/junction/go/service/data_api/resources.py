from __future__ import annotations

from snowfall.service.geodata.v1 import models_pb2
from snowfall.stdlib.integration.starlette import models


class LocationResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        location: models_pb2.Location,
    ) -> LocationResource:
        return cls(
            id=location.id,
            type="locations",
            attributes={
                "addressNumber": location.address_number,
                "street": location.street,
                "unitNumber": location.unit_number,
                "unitType": location.unit_type,
                "latitude": location.coordinates.latitude,
                "longitude": location.coordinates.longitude,
                "name": location.name,
                "neighborhood": location.neighborhood,
                "municipality": location.municipality,
                "subregion": location.subregion,
                "region": location.region,
                "country": location.country,
                "interpolated": location.interpolated,
                "timezone": {"name": location.time_zone.id},
            },
        )
