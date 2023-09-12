import base64
import functools
import hashlib

import lagom
from starlette import endpoints, requests, responses, templating

from snowfall.stdlib import string
from snowfall.stdlib.persistence import filesystem

_SESSION_TOKEN_LENGTH = 32


@functools.cache
def _hash_static_resources() -> dict[str, str]:
    hashes = {}
    static_path = filesystem.package_path(
        "snowfall.project.junction.go.service.dogfood_ui.static",
    )

    for static_file_path in static_path.glob("*"):
        if static_file_path.is_dir():
            continue

        with static_file_path.open("rb", buffering=0) as static_file:
            hashes[static_file_path.name] = base64.urlsafe_b64encode(
                hashlib.file_digest(
                    static_file,  # type: ignore[arg-type]
                    "sha512",
                ).digest(),
            ).decode()

    return hashes


class UI(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        template: templating.Jinja2Templates = lagom.injectable,
    ) -> responses.Response:
        return template.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "session_token": string.random(_SESSION_TOKEN_LENGTH),
                "hashes": _hash_static_resources(),
            },
        )
