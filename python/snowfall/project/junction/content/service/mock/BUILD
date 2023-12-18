python_sources(dependencies=[":stops", ":routes"])
python_tests(name="tests")
python_test_utils(name="test_utils")
resource(
    name="stops",
    source="stops.json",
)
resource(
    name="routes",
    source="routes.json",
)
python_image(
    name="main",
    entry_point="main.py",
)
