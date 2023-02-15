file(
    name="routes-whitelist",
    source="routes-whitelist.json",
)

docker_image(
    name="docker",
    dependencies=["golang:source_files", ":routes-whitelist"],
    image_tags=["{build_args.VERSION}"],
)

file(name="download-dataset", source="datasets.json")
python_tests(
    dependencies=[":routes-whitelist", ":download-dataset"],
    name="tests",
)
