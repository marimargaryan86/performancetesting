"""Contains the API base schema."""
import pydantic

from snowfall.vendor.ba_ndc.models.util import ba_ndc_utils


class BaseSchema(pydantic.BaseModel):
    """API base schema."""

    class Config(object):
        """Base schema configuration."""

        allow_population_by_field_name = True
        alias_generator = ba_ndc_utils.snake_to_camel
