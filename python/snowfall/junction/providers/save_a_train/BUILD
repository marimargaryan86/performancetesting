docker_image(
    name="docker",
    dependencies=[":main"],
    image_tags=["{build_args.VERSION}"],
)

pex_binary(
    name="main",
    entry_point="main.py",
    restartable=True,
)

python_sources(dependencies=[":train_stations"])


python_tests(
    name="tests",
)

python_test_utils(
    name="test_utils",
)

resources(
    name="train_stations",
    sources=["train_stations_coordinates.csv"],
)
