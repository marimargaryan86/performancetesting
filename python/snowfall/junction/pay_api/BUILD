pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
)

python_sources(dependencies=["openapi/pay_api"])

python_test_utils(
    name="test_utils",
)

docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
