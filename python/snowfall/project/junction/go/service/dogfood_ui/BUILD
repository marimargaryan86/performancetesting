python_sources(
    overrides={
        "main.py": {
            "dependencies": ["./static", "./templates", "vendor#jinja2"],
        },
        "locations.py": {
            "dependencies": [
                "python/snowfall/data:airports",
                ":benerail_stations",
                ":direct_ferries",
                ":distribusion",
                ":save_a_train",
            ],
        },
    },
)
python_image(
    name="main",
    entry_point="main.py",
)

resource(
    name="benerail_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/benerail_stations-c6581ed3d4b006240084cd4879e36553037e732f27d90bb9e77563be40fef528.json",
        len=2646124,
        sha256="c6581ed3d4b006240084cd4879e36553037e732f27d90bb9e77563be40fef528",
        filename="benerail_stations.json",
    ),
)

resource(
    name="direct_ferries",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/df-ports-864b8ea4b32d91b1009a3e1ed7a1789ce31b13e643ce94d2fa3a7e3576c406f9.json",
        len=95798,
        sha256="864b8ea4b32d91b1009a3e1ed7a1789ce31b13e643ce94d2fa3a7e3576c406f9",
        filename="direct_ferries.json",
    ),
)

resource(
    name="distribusion",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/distribusion_stations-50454d9147d33df2bb6815d093885368599d5b86901b9d992e38207a67bd9cc8.json",
        len=4569411,
        sha256="50454d9147d33df2bb6815d093885368599d5b86901b9d992e38207a67bd9cc8",
        filename="distribusion.json",
    ),
)

resource(
    name="save_a_train",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/train_stations-c90cd292016f411cc9cbc18f27bafacc33c8d1f2d89ad4c5522ddb8fe7c9a0c7.json",
        len=1342307,
        sha256="c90cd292016f411cc9cbc18f27bafacc33c8d1f2d89ad4c5522ddb8fe7c9a0c7",
        filename="save_a_train.json",
    ),
)
