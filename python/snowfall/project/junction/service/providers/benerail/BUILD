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
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/benerail_stations-9638216413d6749c370b7dd5cb21f517fd5ad2ed7ae50a5ad901f6cebbe52f73.json",
        len=2312063,
        sha256="9638216413d6749c370b7dd5cb21f517fd5ad2ed7ae50a5ad901f6cebbe52f73",
        filename="benerail_stations.json",
    ),
)
