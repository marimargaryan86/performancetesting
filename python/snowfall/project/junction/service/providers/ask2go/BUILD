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
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/ask2go_stations-3a46ff151af895068bbfdbb3634a758b7b18b2d3723fb14bdb6bcbca2318bc8c.json",
        len=3094176,
        sha256="3a46ff151af895068bbfdbb3634a758b7b18b2d3723fb14bdb6bcbca2318bc8c",
        filename="ask2go_stations.json",
    ),
)
