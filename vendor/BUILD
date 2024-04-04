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
        "grpcio": ["grpc"],
        "grpcio-health-checking": ["grpc_health"],
        "grpcio-reflection": ["grpc_reflection"],
        "grpcio-status": ["grpc_status"],
        "grpcio-testing": ["grpc_testing"],
        "protobuf": ["google.protobuf"],
        "pyjwt": ["jwt"],
        "pyshp": ["shapefile"],
        "pytest-httpx": ["pytest_httpx"],
        "python-dateutil": ["dateutil"],
        "python-gitlab": ["gitlab"],
        "python-hcl2": ["hcl2"],
        "python-rapidjson": ["rapidjson"],
        "setuptools": ["easy_install", "pkg_resources", "setuptools"],
        "allure-python-commons": ["allure"],
        "matrix-nio": ["nio"],
        "types-aiobotocore-sqs": ["types_aiobotocore_sqs"],
    },
    overrides={
        "antlr4-python3-runtime": {"dependencies": ["#types-antlr4-python3-runtime"]},
        "aiobotocore": {
            "dependencies": ["#types-aiobotocore", "#types-aiobotocore-sqs"]
        },
        "fakeredis": {"dependencies": ["#lupa"]},
        "mongomock-motor": {"dependencies": ["#setuptools"]},
        "openapi-core": {"dependencies": ["#setuptools", "#rfc3339-validator"]},
        "pandas": {"dependencies": ["#pyarrow"]},
        "protobuf": {"dependencies": ["#types-protobuf"]},
        "pyjwt": {"dependencies": ["#cryptography"]},
        "qrcode": {"dependencies": ["#Pillow"]},
        "starlette": {"dependencies": ["#python-multipart"]},
    },
)
