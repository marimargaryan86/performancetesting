python_sources()
python_tests(name="tests")
python_test_utils(name="test_utils")
pex_binary(
    name="main",
    dependencies=["./main.py", "vendor:uvicorn"],
    entry_point="uvicorn",
)
