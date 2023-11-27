python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(
    name="test_utils",
)
files(
    name="fixtures",
    sources=["fixtures/**"],
)
python_image(
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":benerail_stations"])

resource(
    name="benerail_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/benerail_stations-107f14cfe0c5c023ee429c82f795b21f7028dda6510e36068ebe284dd29d4605.json",
        len=2321430,
        sha256="107f14cfe0c5c023ee429c82f795b21f7028dda6510e36068ebe284dd29d4605",
        filename="benerail_stations.json",
    ),
)
