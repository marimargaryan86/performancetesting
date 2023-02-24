python_sources(dependencies=["openapi/junction/mobile_api", ":populations"])
python_image(
    name="main",
    entry_point="main.py",
)
python_test_utils(
    name="test_utils", dependencies=["openapi/junction/mobile_api", ":fixtures"]
)
files(
    name="fixtures",
    sources=["fixtures/*", "fixtures/*/*"],
)
resource(
    name="populations",
    source=http_source(
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/cities_populations-3c5e1a28e451ea3dff8b9b0e7d10ef573b2330c22b81d8df5cbe4d0a9eac47d9.csv",
        len=7734155,
        sha256="3c5e1a28e451ea3dff8b9b0e7d10ef573b2330c22b81d8df5cbe4d0a9eac47d9",
        filename="cities_populations.csv",
    ),
)
python_tests(
    name="tests",
    dependencies=["python/snowfall/project/junction/service/mobile_api:fixtures"],
)
