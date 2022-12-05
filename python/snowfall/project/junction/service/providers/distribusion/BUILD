python_image(
    namespace="python.snowfall.project.junction.service.providers.distribusion",
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":stations"])

resources(
    name="stations",
    sources=["stations.json"],
)

python_tests(name="tests")
python_test_utils(name="test_utils", dependencies=[":stations"])
