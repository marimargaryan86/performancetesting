from pydantic import BaseModel


class DistribusionBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True
