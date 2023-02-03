from pydantic.main import BaseModel


class BaseSchema(BaseModel):
    class Config(object):
        orm_mode = True
        allow_population_by_field_name = True
