python_image(
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":train_stations"])

resource(
    name="train_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/train_stations-c90cd292016f411cc9cbc18f27bafacc33c8d1f2d89ad4c5522ddb8fe7c9a0c7.json",
        len=1342307,
        sha256="c90cd292016f411cc9cbc18f27bafacc33c8d1f2d89ad4c5522ddb8fe7c9a0c7",
        filename="train_stations.json",
    ),
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=[":train_stations"])
