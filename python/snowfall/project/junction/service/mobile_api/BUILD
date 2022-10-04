python_sources(dependencies=["openapi/junction/mobile_api"])
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
