docker_image(
    name="docker",
)

pex_binary(
    name="main",
    entry_point="main.py",
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
