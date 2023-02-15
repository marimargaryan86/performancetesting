from dataclasses import dataclass


@dataclass(frozen=True)
class Config(object):
    base_url: str = "https://ota2007a.micronnexus-staging.com/service.asmx"
    export_soap_requests: bool = False
    timeout: int = 90
    username: str = "CarnectNet"
    password: str = ""
    is_test: bool = True
