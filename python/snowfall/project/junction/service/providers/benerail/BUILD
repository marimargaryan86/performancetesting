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
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/benerail_stations-c6581ed3d4b006240084cd4879e36553037e732f27d90bb9e77563be40fef528.json",
        len=2646124,
        sha256="c6581ed3d4b006240084cd4879e36553037e732f27d90bb9e77563be40fef528",
        filename="benerail_stations.json",
    ),
)
