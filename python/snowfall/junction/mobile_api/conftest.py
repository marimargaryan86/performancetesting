import http
from typing import Mapping, Optional, Sequence

import pytest
from lagom.integrations import starlette
from motor import motor_asyncio
from starlette import applications, testclient
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import bootstrap, jwt_generator, repository, smtp
from snowfall.stdlib.integration.starlette import middlewares, validation
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.junction import client


def _create_app(
    dependencies: starlette.StarletteIntegration,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return bootstrap.create_app(
        dependencies=dependencies,
        custom_middlewares=custom_middlewares,
    )


@pytest.fixture
def jwt_gen() -> jwt_generator.JwtGenerator:
    return jwt_generator.JwtGenerator(
        "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS2dJQkFBS0NBZ0VBenJGSVFRUytOdlJBYjkwT2UzUmhGdVFLTWxzTEE1aDJFMitWcWREcUZtbm9CTlNEClVpa0tBV2s3azNzSCtYVXp4VmptK1hqL3ZNYWM2d2pHT05ZVlB2NjNzT2txQ3grLzNyWHNrVlU2SWtmbWt1QksKNkd5bjAyTDcxbWVrNFpzL0JVWXQwLzRFSkNRM0QxM0pybmlyK25qVExraHhHLzNHNXBPcFVvNFlLcHZRZ3BSOQovL1FxOEcxOENUNEtDVDR2bGJCQXFKako3YkZwMzg4U3FiWjdmRTZsNGR3aE53a0tPM0hyV0RYNElBZFI4ZHJlClVIbTFsSEhQNjg4c1l6ZzQ5VUhkMlVJbmRvaGlxZkNKSlBvajFmL0NiczhZYVBXNEZpWUd4TGZPTDFIdkxwSmgKM1V4K255eFE3NGgrSXE4dEhack82bXlva0FYRy9mdjFENVFCZVlFb2pHYkVWQSt3cEw3M0s3MnR2QTNsQzIxeApSVUNRUG52WUYvUC96ekxwRzZIclozcGVNcFYwTmpVKzBMdTI1Q09GSmVsakdGVG9iS2ltYWJnenFuelVTWklvCjlhdWRyVEV2bVZYK3Y3UGkyOTkzN01kQUcwR0xxUlBlWjhzdlVTUHphQmNrOHllMnVFTXhGUjBEa2hjQ0QzdE0KaGpsV01ma3JWeWJjVHZvWWlUUjU1UncvY3ZTRzdXcytNelFKWFZDUkE5enA3ZUt4K05mWUt0Mk1waEhGdmFQWAp3eWQ3RzlIejBhb3RLMmlrOGR1SFVTTzBJQTA5Ni80YWpaTE5PWVZRK3RHdlRlS3VoK1BYNjB6YWtTYWg5aW1RCmd2UzQzSXB5bDhSWXVNMDRPTXUwRE9FZk8wenZvZHJ3ZktreFBuN3RIeCtWbW8raC9kend0NTArRHJFQ0F3RUEKQVFLQ0FnQkdYS2VDS3NFdUovdi9tTHNqWDd6bGMvL2NvSTJoVGJkMGFsb0Nrekg5SzFSbXdJbHI0TGlkUGx1ZgpteFJkNFg0Y1FtVnVxN2d6WlZGcDJYVFJTRiszTURNTU1ITzFrYnRaYjRqMitKSnZ0UlpURGJPeVo3ckNCVUpCCi9NcHVXdEViVklhcFVpSEt3K0ZTZzlUeVpmWDFzRWdEeTNsbDFBQnY0ZmlVTi9jV0dqRGpJdlc1dWo4YjFjbVIKdytMYXZxYW9TSFhhYnhqZXA3U3BFZThDZ3pLS1lLT3J2YW80K0FUWnM3QXdPVDhjZUNGM09kRFFpSDQ5NkhpbApoOE5PaTRjb1JxSGxJZFlaVGRoNGpYL0NiTHppVHN5N3VCaFJNc1RXRlYvY2U4M2U0ZitRVlJpbm96Qy9zdkJpCmVvNmw5QWhodVorU3dpYW4wSytyS3FpRUF4aDB6V0tNcG45L1VoMmpZWldiQlBkRVh4VGhETTcxY3dVaVd0RXcKY1E4bEdjQnM4THhYcWdHbDJ6NDgxR0F4bDBIcFJmQUNwS0RYa1o1MzNQeGdXODdlMTBrc0ZaUVZQR1ZJc094VwpOU1pMWkVQYWJick9DRmRjRk0xaTVQazExNDZ0dmFGQ2xzcUgwWVZzRkNBOFZPQmV2dERuZGFaN3RGUmlucjRiCk96b3NUQk42RFVTc0EyWU4rRWZqVFhKdlNWSUNWMEVLVTR3RHFJZThGY0VtZVlBRFBIWjVsaTRCSERuRHBDMkwKNlVsWExteFNlWG9HdndkaUIxbEZCMnVncVY0ak5YaFlqblBwam9iS0FZRjJ5TVBQRkY4VHUvNUtQZHlRclBzMwp4blR3c2c5NHpWL3ZxVTQvaUhUMDNqZXk0czhzQnU2ck1uMHZKSFl1UUtVZlNncVpnUUtDQVFFQStLRnhkNFo1CkpPeGxTelZpSEpHRFFZRXNsMyszcHJxK0JPUXoyRm1BRHB5b3U0emJ6UDY4TmhPeFBlVDIwOFNrT1B0MzRadkQKYXVLZjJQZjJacFJOV0JHbjZEcXV6MUUza2NsUzEzSlhxY2dITkszWG9ITDZSL2VNU2dnazczV1puVFRaaHVOcwpXQjIvWWwyeUtTdlJIQW9TTkVEaHRqTm9vZDRNOGw5RjAzTmRQV0ZDMWRoV1RhQ0JiSXc0OUUvdXA2bTVsSHM4Ckd5OHE4c3VqZWxYSXVVYUp6a3Z6Ni9vTjByQ0pVS1BBZGpBSnVySWo1NTViTXc1Z3B2eDNROHZ6NjI5c2hzOXcKK01wckdKNWZxdjN3OG1oMy9tUHY1ZVhhZ3RBODVSSDI3S3B6aHJpdE9qOHhOcEVTY2lVUTU0Z1o4MFJnQVUwQQphZXVhTjdlbXR1ejMyUUtDQVFFQTFOR2ZFSnU0VmpvMm1rY1NEUW1wMThnV3VKRjc4LzdMZkpTZEpWRHByQ1FxCkx0b0NMd1dNWk1yQVNJTFcwRzNOaWRDRWpiZUtUOThYSm9UZnJ2MUQzK09kNy9oalc2OCtjelhRK2dLY3YyblEKZnNJbEZwVkQ1dWRtTFNNNVUxVGMwTVI1cmRNbis4NkVnZHVTL3VWMWZIKzFhcSs4NWVpcTkxSEQ2Yi9OQlZOSgplRE55Yk1BWUF5aDVrTXMyb2FoRklVSEl4ZVNBcVZickJmZVN6eElYWVE5d1JuWXRLVmRWazZtaXZOamkwSE9RCnZVdXZRTzBGajZHZkJkNktHWUE0bCtPOFY3aUJNL2UwZ2pTKzVnTzd0OXc1dUszMXpxWUxRcnJoRDQyNStKcFEKWVBMZTJJbmd2MXplbzlZM3A5ZVBTQ0phaW54RDdrQnIzKzg5SEJhZW1RS0NBUUVBcnZXOHlTV0IvbSt6NERiUwpzZFBjRDY1ODJLZHhid3llUndiblRPbSthWW5vV3dLR2NqMFg2TjMycmQxL3JBb0dubXFuTThYT3dGcDFyZExnCk85TkVraUxxaTBzd1ZJZU1tVFNZN1M5emJQQnIwYkE3dXBidWROSklrSmdtbGJPbHc3QzdHbWJUaVRaMXhSeTIKRUs3YTJlWmtaUXo3U0tIb2tXK1dvTUJXZkxRRCt2dUVjc05vQi94WTF5L2RyRjdMVElUdEtRV0hpSUdxc1d5SAp2OEM2SFZiOEJvWUFRaUNXdFpxeEptUDFQYllVUXFLMURYcXNKc09KVkRqNUhHWmJZV1BwZFB4cFBVb0VEekR6CmxYcFpvZHZPQk9BQ296OGFnMDlTYXNnM2dOZDVzR1lvMElKRGVXaWhHRjNwQldVTERkc2h6QWlKci8reGFGLysKRzErcUVRS0NBUUVBcFNONzBJRmxDdFBsSnRYYk5lNjNzazc3QW9FeHMrV1V0TGtGTDcyWGRSSWpBWFA5bWNzdQpZOC9JWVB2V0FLb1RnY3NoOEczcGo0ekhCQWE3STZnM0VQWW95ZHJ1RG1qdmhxck4zQkpHMjJrYWRpSGtjWitsCnJ2a0VHaVpwQnpha21nSzdnSnlIUENmR1BwWEpmSzFFK3pTRjY2RXViU0NiK1ltakFqRG93Q2NlclgwT1gwQzMKNFV0NCtWZ1dybDVLTmtJN3J3TmVxd2hkR3FZL2J4clV0V1lyY3lHa2JaM3RNOFhBRjlZY09qQlNzZkNXcjBTOAp1ZlZwMWo0VzN5N1Z1MWJtQVJPVWZtVEoxdmRpNGswblRzWStyQVdnNVplR3lXTUYzUEhXeXdmRE0xZUNnSGlNCnd6RW5PZTZ5QlRXSll5bjFJOXpGUVkwUHFCYVdUc05ta1FLQ0FRRUFob3JmL0d0NGhVMlhHY1RQcHYrSmQvN3IKUDFrOUZ4M3YxeVZ6QWc1RWxrekl4OC95ckovNmJNd1p4Sjc4SXRRcGozME1udTRVWXEvM3RvOUp0elpxSk81awpPaXcyVzBTQktJb002ZWJrdzg4VUpDMlVackRXS0tqM2VKd1krME5CbGsyZVFmNloxaG1yL1huSEhSMXFwZktxClBUa3RFTVhtaEpmTWJ6TVFZL2dKTDVTd08wL2dlVEpTN2xvbzAvUzRJdmh6ZEg3bTVFb3VieXVrTkI4eTQ1RnkKbFBKZmFmcTlVL24vR2tMcENsZ3lhb0ZycWhjZklwMmhwdXBxeWloeXVsQ1liTWxISVBQbXZhbWdFM0dBMHhnNgoxb0hnYTFRNjUzZmVqeENlSkY1UzJXODBQbmY1QnRIbG5sYm42S1pHV2hxTW16aWl3Tis1OGxVQzZzMzN0Zz09Ci0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==",
        "1.0.0",
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
    }


@pytest.fixture()
def api_url() -> str:
    return "http://localhost:8000"


@pytest.fixture()
def token() -> str:
    return "random_token"


@pytest.fixture()
def junction_client(
    api_url: str,
    token: str,
) -> client.JunctionClient:
    return client.JunctionClient(
        api_url=api_url,
        token=token,
    )


@pytest.fixture
def places_repository() -> repository.PlacesRepository:
    mongo = motor_asyncio.AsyncIOMotorClient(
        "mongodb://localhost:27017",  # nosec
    )["test"]
    return repository.PlacesRepository(
        mongo["places"],
    )


@pytest.fixture()
def app(  # noqa: WPS211
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    otp_repository: repository.OtpRepository,
    smtp_client: smtp.EmailClient,
    orders_repository: repository.OrdersRepository,
    junction_client: client.JunctionClient,
    jwt_gen: jwt_generator.JwtGenerator,
) -> applications.Starlette:
    return _create_app(
        bootstrap.create_dependencies(
            orders_repository,
            junction_client,
            places_repository,
            users_repository,
            otp_repository,
            smtp_client,
            jwt_gen,
        ),
        [
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "openapi.json",
                    filesystem.PkgLoader("mobile_api"),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
        ],
    )


@pytest.fixture()
def http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> testclient.TestClient:
    http_client = testclient.TestClient(app)
    http_client.headers.update(headers)

    return http_client
