python_sources(dependencies=["openapi/mobile_api"])
pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
)
python_tests(name="tests")
python_test_utils(name="test_utils", dependencies=["openapi/mobile_api"])
docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
