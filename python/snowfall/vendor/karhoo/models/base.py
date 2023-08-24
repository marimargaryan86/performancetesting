from pydantic.v1 import BaseModel


class KarhooBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True
