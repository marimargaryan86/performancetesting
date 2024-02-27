python_sources(dependencies=["python/snowfall/data:airports", ":ask2go_stations"])
python_tests(name="tests", dependencies=[":fixtures", ":ask2go_stations"])
python_test_utils(name="test_utils", dependencies=["python/snowfall/data:airports"])
files(
    name="fixtures",
    sources=["fixtures/**"],
)
python_image(
    name="main",
    entry_point="main.py",
)

resource(
    name="ask2go_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/ask2go_stations-084eca6b645d07a6f51e5cdadcff69a0ca11116e06c5fb22f545e03d11d36708.json",
        len=1366659,
        sha256="084eca6b645d07a6f51e5cdadcff69a0ca11116e06c5fb22f545e03d11d36708",
        filename="ask2go_stations.json",
    ),
)
