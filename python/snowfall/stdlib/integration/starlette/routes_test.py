import httpx
from starlette import applications, routing, status

from snowfall.stdlib.integration.starlette import routes


class TestHealth(object):
    async def test_health_status_code(self, test_client: httpx.AsyncClient) -> None:
        response = await test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK


class TestProxy(object):
    async def test_proxy(
        self,
        test_app_without_spec: applications.Starlette,
        test_client_without_spec: httpx.AsyncClient,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.routes.append(
            routing.Route("/health", routes.Health, name="Health"),
        )

        test_app_without_spec.routes.append(
            routes.Proxy(test_client).to_route(),
        )

        response = await test_client_without_spec.get("/health")
        assert response.status_code == status.HTTP_200_OK

    async def test_proxy_with_prefix(
        self,
        test_app_without_spec: applications.Starlette,
        test_client_without_spec: httpx.AsyncClient,
        test_app: applications.Starlette,
        test_client: httpx.AsyncClient,
    ) -> None:
        test_app.routes.append(
            routing.Route("/health", routes.Health, name="Health"),
        )

        test_app_without_spec.routes.append(
            routes.Proxy(test_client, prefix="/prefix").to_route(),
        )

        response = await test_client_without_spec.get("/prefix/health")
        assert response.status_code == status.HTTP_200_OK
