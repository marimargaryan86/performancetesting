file(
    name="airlines",
    source="airlines.json",
)

file(
    name="airports",
    source="airports.json",
)

docker_image(
    name="docker",
    dependencies=["golang:source_files", ":airlines", ":airports"],
    image_tags=["{build_args.VERSION}"],
)

resources(name="datasets", sources=["airlines.json", "airports.json"])
python_tests(
    dependencies=[":datasets"],
    name="tests",
)
