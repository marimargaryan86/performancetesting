import contextlib

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

    async def test_url_replacement(
        self,
        test_app_without_spec: applications.Starlette,
        test_app: applications.Starlette,
    ) -> None:
        async with contextlib.AsyncExitStack() as stack:
            proxy_client = await stack.enter_async_context(
                httpx.AsyncClient(
                    base_url="https://proxy.com",
                    transport=httpx.ASGITransport(
                        app=test_app_without_spec,  # type: ignore[arg-type]
                        raise_app_exceptions=False,
                    ),
                ),
            )
            app_client = await stack.enter_async_context(
                httpx.AsyncClient(
                    base_url="http://app:8080",
                    transport=httpx.ASGITransport(
                        app=test_app,  # type: ignore[arg-type]
                        raise_app_exceptions=False,
                    ),
                ),
            )

            test_app.routes.append(
                routing.Route("/health", routes.Health, name="Health"),
            )

            test_app_without_spec.routes.append(
                routes.Proxy(app_client).to_route(),
            )

            response = await proxy_client.get("/health")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["links"]["self"] == "https://proxy.com/health"
