python_sources(dependencies=[":datasets"])
resources(name="datasets", sources=["datasets.json"])
python_image(
    namespace="python.snowfall.project.junction.service.data_pipeline",
    name="download",
    entry_point="download.py",
)
python_tests(
    name="tests",
)
