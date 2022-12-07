from pydantic import BaseModel


class DuffelRequestBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True
