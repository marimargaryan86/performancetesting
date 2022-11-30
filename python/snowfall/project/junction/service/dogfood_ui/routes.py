from starlette import requests, responses

from snowfall.stdlib.persistence import filesystem


async def ui(_: requests.Request) -> responses.Response:
    layout_path = filesystem.resource_path(
        "snowfall.project.junction.service.dogfood_ui.routes",
        "layout.html",
    )

    with open(layout_path) as template:
        layout = str(template.read())

    return responses.Response(layout)
