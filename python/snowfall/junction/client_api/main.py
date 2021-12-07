import uvicorn

from snowfall.junction.client_api import bootstrap, loaders, validation

if __name__ == "__main__":
    settings = bootstrap.Settings()
    app = bootstrap.create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
        ),
    )

    uvicorn.run(app, port=settings.http_port, access_log=False)
