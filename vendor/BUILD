__dependents_rules__(
    (
        ("//vendor#fakeredis",),
        "//python/snowfall/conftest.py",
        "!*",
    ),
    (
        ("//vendor#freezegun",),
        "**_test.py",
        "!*",
    ),
    (
        ("//vendor#mongomock-motor",),
        "//python/snowfall/conftest.py",
        "!*",
    ),
    (
        ("//vendor#structlog",),
        "python/snowfall/stdlib/logging/*.py",
        "!*",
    ),
    ("*", "*"),
)

pex_binary(
    name="check-jsonschema",
    script="check-jsonschema",
    dependencies=["vendor#check-jsonschema"],
)


python_requirements(
    module_mapping={
        "allure-python-commons": ["allure"],
        "antlr4-python3-runtime": ["antlr4"],
        "dnspython": ["dns"],
        "googleapis-common-protos": [
            "google.api",
            "google.cloud",
            "google.gapic",
            "google.logging",
            "google.longrunning",
            "google.rpc",
            "google.type",
        ],
        "grpcio-status": ["grpc_status"],
        "grpcio-testing": ["grpc_testing"],
        "matrix-nio": ["nio"],
        "pyshp": ["shapefile"],
        "types-aiobotocore-sqs": ["types_aiobotocore_sqs"],
    },
    overrides={
        "aiobotocore": {
            "dependencies": ["#types-aiobotocore", "#types-aiobotocore-sqs"]
        },
        "antlr4-python3-runtime": {"dependencies": ["#types-antlr4-python3-runtime"]},
        "fakeredis": {"dependencies": ["#lupa"]},
        "mongomock-motor": {"dependencies": ["#setuptools"]},
        "openapi-core": {
            "dependencies": ["#setuptools", "#rfc3339-validator", "#aioitertools"]
        },
        "pandas": {"dependencies": ["#pyarrow"]},
        "pyjwt": {"dependencies": ["#cryptography"]},
        "qrcode": {"dependencies": ["#Pillow"]},
        "starlette": {"dependencies": ["#python-multipart"]},
    },
)
