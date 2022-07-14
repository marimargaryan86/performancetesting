python_sources(dependencies=["openapi/junction/mobile_api"])
pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
)
python_test_utils(
    name="test_utils", dependencies=["openapi/junction/mobile_api", ":fixtures"]
)
docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
files(
    name="fixtures",
    sources=["fixtures/*", "fixtures/*/*"],
)
