from pydantic.v1 import BaseModel


class DistribusionBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
