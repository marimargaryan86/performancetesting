python_sources()
pex_binary(
    name="main",
    entry_point="main.py",
)

docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)
