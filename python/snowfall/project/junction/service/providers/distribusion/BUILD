python_image(
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":stations"])

resource(
    name="stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/distribusion_stations-50454d9147d33df2bb6815d093885368599d5b86901b9d992e38207a67bd9cc8.json",
        len=4569411,
        sha256="50454d9147d33df2bb6815d093885368599d5b86901b9d992e38207a67bd9cc8",
        filename="stations.json",
    ),
)

python_tests(name="tests")
python_test_utils(name="test_utils", dependencies=[":stations"])
