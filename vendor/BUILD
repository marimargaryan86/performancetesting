python_requirements(
    module_mapping={
        "grpcio": ["grpc"],
        "grpcio-health-checking": ["grpc_health"],
        "grpcio-reflection": ["grpc_reflection"],
        "grpcio-status": ["grpc_status"],
        "protobuf": ["google.protobuf"],
        "pyjwt": ["jwt"],
        "pytest-httpx": ["pytest_httpx"],
        "python-dateutil": ["dateutil"],
        "python-rapidjson": ["rapidjson"],
        "rfc3339-validator": ["rfc3339_validator"],
        "setuptools": ["easy_install", "pkg_resources", "setuptools"],
        "currency-cloud": ["currencycloud"],
    },
    overrides={
        "mongomock-motor": {"dependencies": ["#setuptools"]},
        "openapi-core": {"dependencies": ["#setuptools", "#rfc3339-validator"]},
        "protobuf": {"dependencies": ["#types-protobuf"]},
    },
)
