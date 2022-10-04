python_image(
    namespace="python.snowfall.project.junction.service.providers.save_a_train",
    name="main",
    entry_point="main.py",
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
