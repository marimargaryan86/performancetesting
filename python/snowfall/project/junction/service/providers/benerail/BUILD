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
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/benerail_stations-2c5c1574f08946669809539ce936ee6d4e7a65229fbdccbf627ea33434baf209.json",
        len=2324114,
        sha256="2c5c1574f08946669809539ce936ee6d4e7a65229fbdccbf627ea33434baf209",
        filename="benerail_stations.json",
    ),
)
