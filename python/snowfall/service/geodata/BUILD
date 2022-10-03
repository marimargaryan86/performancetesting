python_sources(dependencies=[":borders"])
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

resource(
    name="borders",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/world-administrative-boundaries-0932da19fd832994de5ad3068241c5833940482bbf43d6da7dcabbf1a1750a53.zip",
        len=2014345,
        sha256="0932da19fd832994de5ad3068241c5833940482bbf43d6da7dcabbf1a1750a53",
        filename="world-administrative-boundaries.zip",
    ),
)
