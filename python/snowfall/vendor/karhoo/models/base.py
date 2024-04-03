from pydantic.v1 import BaseModel


class KarhooBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
