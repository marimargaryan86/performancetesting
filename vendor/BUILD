poetry_requirements(
    module_mapping={
        "grpcio": ["grpc"],
        "grpcio-reflection": ["grpc_reflection"],
        "protobuf": ["google.protobuf"],
    },
    overrides={
        "starlette": {"dependencies": [":requests"]},
    }
)
