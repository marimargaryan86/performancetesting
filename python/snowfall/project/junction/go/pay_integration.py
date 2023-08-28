import pydantic

from snowfall.stdlib import service


class Settings(service.Settings):
    pay_admin_username: str
    pay_admin_password: str
    public_pay_api_dsn: pydantic.AnyUrl
    public_pay_admin_api_dsn: pydantic.AnyUrl
