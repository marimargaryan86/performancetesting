from pydantic import BaseModel


class BenerailBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True
