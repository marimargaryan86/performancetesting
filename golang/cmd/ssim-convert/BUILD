file(
    name="airports",
    source="airports.json",
)

docker_image(
    name="docker",
    dependencies=["golang:source_files", ":airports"],
    image_tags=["{build_args.VERSION}"],
)
