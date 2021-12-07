python_sources(dependencies=["openapi:client_api"])
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils")
pex_binary(
    name="main",
    entry_point="main.py",
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
