python_image(
    namespace="python.snowfall.project.junction.service.providers.save_a_train",
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":train_stations"])

resource(
    name="train_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/train_stations-f6bcecf4fbad745b444d552ce5929c58158522cb08acd62fc74d3bcda187dd13.json",
        len=1246284,
        sha256="f6bcecf4fbad745b444d552ce5929c58158522cb08acd62fc74d3bcda187dd13",
        filename="train_stations.json",
    ),
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=[":train_stations"])
