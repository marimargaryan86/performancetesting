python_image(
    name="main",
    entry_point="main.py",
)

python_sources(dependencies=[":train_stations"])

resource(
    name="train_stations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/train_stations-0562010d12ea37fe4c3f0805e6217953db63089ab67fe37d135a4a2b36d22494.json",
        len=1342307,
        sha256="0562010d12ea37fe4c3f0805e6217953db63089ab67fe37d135a4a2b36d22494",
        filename="train_stations.json",
    ),
)
files(
    name="fixtures",
    sources=["fixtures/*"],
)
python_tests(name="tests", dependencies=[":fixtures"])
python_test_utils(name="test_utils", dependencies=[":train_stations"])
