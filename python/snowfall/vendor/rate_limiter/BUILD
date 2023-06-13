python_sources(
    overrides={
        (
            "gubernator_pb2.py",
            "gubernator_pb2.pyi",
            "gubernator_pb2_grpc.py",
            "gubernator_pb2_grpc.pyi",
        ): {
            "skip_autoflake": True,
            "skip_ruff": True,
        }
    }
)

python_tests(
    name="tests",
)
