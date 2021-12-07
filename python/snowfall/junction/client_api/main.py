from snowfall.junction.client_api import bootstrap, loaders, validation

app = bootstrap.create_app(
    validator=validation.Validator(
        "openapi.json",
        loaders.PkgLoader("client_api"),
    ),
)
