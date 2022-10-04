python_sources(dependencies=[":airports"])
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=[":airports"])
resources(
    name="airports",
    sources=["airport_coordinates.json"],
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
python_image(
    namespace="python.snowfall.project.junction.service.providers.ask2go",
    name="main",
    entry_point="main.py",
)
