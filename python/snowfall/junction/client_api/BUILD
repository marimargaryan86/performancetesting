python_sources(dependencies=["openapi:client_api"])
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils")
pex_binary(
    name="main",
    dependencies=["./main.py", "vendor:uvicorn"],
    entry_point="uvicorn",
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
