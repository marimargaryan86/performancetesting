poetry_requirements(
    module_mapping={
        "grpcio": ["grpc"],
        "grpcio-reflection": ["grpc_reflection"],
        "protobuf": ["google.protobuf"],
        "setuptools": ["easy_install", "pkg_resources", "setuptools"],
    },
    overrides={
        "openapi-core": {"dependencies": [":setuptools"]},
        "starlette": {"dependencies": [":requests"]},
    }
)
