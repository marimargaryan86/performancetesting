from __future__ import annotations

from typing import Any, Mapping

from snowfall.stdlib.integration.starlette import models


class PlaceResource(models.Resource):
    """Resource for a place."""


class OrderResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        order: Mapping[str, Any],
    ) -> OrderResource:
        return cls(**order)
