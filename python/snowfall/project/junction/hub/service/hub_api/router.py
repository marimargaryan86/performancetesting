from starlette import routing

from snowfall.project.junction.hub.service.hub_api.routes import users
from snowfall.stdlib.integration.starlette import routes


def get_routes() -> list[routing.BaseRoute]:
    user_handler = users.Users()

    return [
        routes.to_route(
            "/users",
            user_handler.list_,
            name="ListUsers",
        ),
        routes.to_route(
            "/users/{userId}",
            user_handler.view,
            name="ViewUser",
        ),
    ]
