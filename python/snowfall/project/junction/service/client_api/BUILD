python_sources(dependencies=["openapi/junction/client_api"])
python_test_utils(name="test_utils", dependencies=["openapi/junction/client_api"])
pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
    execution_mode="venv",
)
docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
