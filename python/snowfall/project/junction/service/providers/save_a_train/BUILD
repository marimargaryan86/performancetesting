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

resources(
    name="train_stations",
    sources=["train_stations.json"],
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=[":train_stations"])
