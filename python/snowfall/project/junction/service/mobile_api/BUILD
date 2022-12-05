python_sources(dependencies=["openapi/junction/mobile_api", ":populations"])
python_image(
    namespace="python.snowfall.project.junction.service.mobile_api",
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
        url="https://junction-build-artifacts.s3.eu-west-2.amazonaws.com/cities_populations-97e990b815ae30ecef25bd9a85aedd7a9622b42e27ab237d97b98e2db45f48aa.csv",
        len=6000491,
        sha256="97e990b815ae30ecef25bd9a85aedd7a9622b42e27ab237d97b98e2db45f48aa",
        filename="cities_populations.csv",
    ),
)
python_tests(
    name="tests",
    dependencies=["python/snowfall/project/junction/service/mobile_api:fixtures"],
)
